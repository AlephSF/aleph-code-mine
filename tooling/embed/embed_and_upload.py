#!/usr/bin/env python3
"""
Embedding pipeline for aleph-code-mine docs → Qdrant code_standards collection.

Pipeline:
  1. Parse markdown + frontmatter
  2. Two-stage chunking (MarkdownHeaderTextSplitter → RecursiveCharacterTextSplitter)
  3. Generate contextual prefixes via DeepSeek V3 (Together.ai)
  4. Embed with BGE-large-en-v1.5
  5. Upsert to Qdrant + orphan cleanup

Usage:
  python embed_and_upload.py               # embed all docs, upload to QDRANT_URL
  python embed_and_upload.py --local       # use http://localhost:6333
  python embed_and_upload.py --dry-run     # parse/chunk/prefix only, skip upload
  python embed_and_upload.py --docs-dir /path/to/docs  # override docs path
"""

import argparse
import hashlib
import json
import logging
import os
import re
import sys
import uuid
from pathlib import Path
from typing import Any

import frontmatter
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PayloadSchemaType,
    PointStruct,
    VectorParams,
)
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

COLLECTION_NAME = "code_standards"
VECTOR_SIZE = 1024
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200
TOGETHER_MODEL_DEFAULT = "deepseek-ai/DeepSeek-V3"
PREFIX_CACHE_FILE = Path(__file__).parent / ".prefix_cache.json"
UUID_NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")  # URL namespace

# Frontmatter fields to index in Qdrant payload
PAYLOAD_INDEX_FIELDS = {
    "category": PayloadSchemaType.KEYWORD,
    "audience": PayloadSchemaType.KEYWORD,
    "doc_type": PayloadSchemaType.KEYWORD,
    "stack": PayloadSchemaType.KEYWORD,
    "priority": PayloadSchemaType.KEYWORD,
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Step 1: Parse & Chunk
# ---------------------------------------------------------------------------

HEADER_SPLITS = [
    ("#", "h1"),
    ("##", "h2"),
    ("###", "h3"),
    ("####", "h4"),
]

RECURSIVE_SEPARATORS = ["\n## ", "\n### ", "\n#### ", "\n\n", "\n", " ", ""]

CODE_BLOCK_RE = re.compile(r"```(\w+)?", re.MULTILINE)


def detect_language(text: str) -> str | None:
    """Return the first fenced-code language found in text, or None."""
    match = CODE_BLOCK_RE.search(text)
    if match and match.group(1):
        return match.group(1)
    return None


def parse_and_chunk(md_path: Path, docs_root: Path) -> list[dict[str, Any]]:
    """Parse a markdown file and return a list of chunk dicts with metadata."""
    post = frontmatter.load(str(md_path))
    meta: dict[str, Any] = dict(post.metadata)
    body: str = post.content

    relative_path = md_path.relative_to(docs_root).as_posix()

    # Stage 1: split on markdown headings
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=HEADER_SPLITS,
        strip_whitespace=True,
    )
    header_docs = header_splitter.split_text(body)

    # Stage 2: recursively split large chunks
    char_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=RECURSIVE_SEPARATORS,
    )

    chunks: list[dict[str, Any]] = []
    for hdoc in header_docs:
        sub_chunks = char_splitter.split_text(hdoc.page_content)
        heading_meta = hdoc.metadata  # keys: h1, h2, h3, h4

        for sub in sub_chunks:
            text = sub.strip()
            if not text:
                continue

            # Build heading breadcrumb for context
            breadcrumb_parts = [
                heading_meta.get("h1"),
                heading_meta.get("h2"),
                heading_meta.get("h3"),
                heading_meta.get("h4"),
            ]
            breadcrumb = " > ".join(p for p in breadcrumb_parts if p)

            # Code detection
            has_code = "```" in text
            language = detect_language(text) if has_code else None

            chunk: dict[str, Any] = {
                "text": text,
                "source_file": relative_path,
                "breadcrumb": breadcrumb,
                "has_code": has_code,
                **meta,
            }
            if language:
                chunk["language"] = language

            chunks.append(chunk)

    return chunks


def load_all_docs(docs_root: Path) -> list[dict[str, Any]]:
    """Walk docs_root and return all chunks from all markdown files."""
    md_files = sorted(docs_root.rglob("*.md"))
    log.info("Found %d markdown files", len(md_files))

    all_chunks: list[dict[str, Any]] = []
    for md_path in md_files:
        try:
            chunks = parse_and_chunk(md_path, docs_root)
            all_chunks.extend(chunks)
        except Exception as exc:
            log.warning("Skipping %s: %s", md_path, exc)

    log.info("Total chunks: %d", len(all_chunks))
    return all_chunks


# ---------------------------------------------------------------------------
# Step 2: Contextual Prefixes
# ---------------------------------------------------------------------------

def chunk_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def load_prefix_cache() -> dict[str, str]:
    if PREFIX_CACHE_FILE.exists():
        try:
            return json.loads(PREFIX_CACHE_FILE.read_text())
        except json.JSONDecodeError:
            log.warning("Prefix cache corrupted, starting fresh")
    return {}


def save_prefix_cache(cache: dict[str, str]) -> None:
    PREFIX_CACHE_FILE.write_text(json.dumps(cache, indent=2))


def generate_prefix(client: OpenAI, model: str, doc_context: str, chunk_text: str) -> str:
    """Call Together.ai to generate a 50-100 token situational prefix."""
    prompt = (
        "Given the document context below, write a concise 50-100 token situational "
        "prefix that describes what this specific chunk is about. The prefix will be "
        "prepended to the chunk before embedding to improve retrieval accuracy. "
        "Output ONLY the prefix text, no quotes or labels.\n\n"
        f"DOCUMENT CONTEXT:\n{doc_context[:2000]}\n\n"
        f"CHUNK:\n{chunk_text[:1000]}"
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=120,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


def build_doc_context(chunks: list[dict[str, Any]], source_file: str) -> str:
    """Reconstruct a brief document summary from its chunks."""
    doc_chunks = [c for c in chunks if c["source_file"] == source_file]
    title = doc_chunks[0].get("title", "") if doc_chunks else ""
    category = doc_chunks[0].get("category", "") if doc_chunks else ""
    stack = doc_chunks[0].get("stack", "") if doc_chunks else ""
    # First two chunks give enough context
    sample = "\n\n".join(c["text"][:400] for c in doc_chunks[:2])
    return f"Title: {title}\nCategory: {category}\nStack: {stack}\n\n{sample}"


def add_contextual_prefixes(
    chunks: list[dict[str, Any]],
    together_api_key: str,
    model: str,
) -> list[str]:
    """
    Return a list of prefixed texts, one per chunk.
    Uses cache to avoid regenerating unchanged chunks.
    """
    client = OpenAI(
        api_key=together_api_key,
        base_url="https://api.together.xyz/v1",
    )
    cache = load_prefix_cache()

    # Pre-build doc contexts (one per source file)
    doc_contexts: dict[str, str] = {}
    for chunk in chunks:
        sf = chunk["source_file"]
        if sf not in doc_contexts:
            doc_contexts[sf] = build_doc_context(chunks, sf)

    prefixed_texts: list[str] = []
    new_entries = 0

    for chunk in chunks:
        text = chunk["text"]
        key = chunk_hash(text)

        if key not in cache:
            try:
                prefix = generate_prefix(client, model, doc_contexts[chunk["source_file"]], text)
            except Exception as exc:
                log.warning("Prefix generation failed for chunk (using empty prefix): %s", exc)
                prefix = ""
            cache[key] = prefix
            new_entries += 1

        prefix = cache[key]
        prefixed_texts.append(f"{prefix}\n\n{text}" if prefix else text)

    if new_entries:
        save_prefix_cache(cache)
        log.info("Generated %d new prefixes (cache saved)", new_entries)
    else:
        log.info("All prefixes served from cache")

    return prefixed_texts


# ---------------------------------------------------------------------------
# Step 3: Embed
# ---------------------------------------------------------------------------

def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed texts with BGE-large-en-v1.5 (no instruction prefix for documents)."""
    log.info("Loading BGE-large-en-v1.5 model...")
    model = SentenceTransformer("BAAI/bge-large-en-v1.5")
    log.info("Encoding %d chunks...", len(texts))
    vectors = model.encode(texts, batch_size=32, show_progress_bar=True, normalize_embeddings=True)
    return [v.tolist() for v in vectors]


# ---------------------------------------------------------------------------
# Step 4: Upload to Qdrant
# ---------------------------------------------------------------------------

def point_id(source_file: str, chunk_index: int) -> str:
    """Deterministic UUID5 for idempotent upserts."""
    return str(uuid.uuid5(UUID_NAMESPACE, f"{source_file}:{chunk_index}"))


def ensure_collection(client: QdrantClient) -> None:
    """Create collection if it doesn't exist; ensure payload indexes exist."""
    existing = {c.name for c in client.get_collections().collections}

    if COLLECTION_NAME not in existing:
        log.info("Creating collection '%s'", COLLECTION_NAME)
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )
    else:
        log.info("Collection '%s' already exists", COLLECTION_NAME)

    # Create payload indexes (idempotent)
    for field, schema_type in PAYLOAD_INDEX_FIELDS.items():
        try:
            client.create_payload_index(
                collection_name=COLLECTION_NAME,
                field_name=field,
                field_schema=schema_type,
            )
        except Exception:
            pass  # Index likely already exists


def upsert_points(
    client: QdrantClient,
    chunks: list[dict[str, Any]],
    vectors: list[list[float]],
) -> None:
    """Upsert all points in batches."""
    points: list[PointStruct] = []
    for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
        payload = {k: v for k, v in chunk.items() if k != "text"}
        # Ensure tags is always a list (serializable)
        if "tags" in payload and not isinstance(payload["tags"], list):
            payload["tags"] = list(payload["tags"])
        points.append(
            PointStruct(
                id=point_id(chunk["source_file"], i),
                vector=vector,
                payload=payload,
            )
        )

    batch_size = 100
    for start in range(0, len(points), batch_size):
        batch = points[start : start + batch_size]
        client.upsert(collection_name=COLLECTION_NAME, points=batch)
        log.info("Upserted points %d–%d", start, start + len(batch) - 1)

    log.info("Upserted %d points total", len(points))


def cleanup_orphans(client: QdrantClient, live_source_files: set[str]) -> None:
    """
    Delete points whose source_file no longer exists in docs/.
    Only touches points that have a source_file payload field.
    """
    log.info("Scanning for orphaned points...")
    orphan_ids: list[str] = []
    offset = None

    while True:
        result, next_offset = client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="source_file",
                        match=MatchValue(value="*"),  # any non-null value
                    )
                ]
            ),
            limit=500,
            offset=offset,
            with_payload=["source_file"],
            with_vectors=False,
        )

        for point in result:
            sf = point.payload.get("source_file") if point.payload else None
            if sf and sf not in live_source_files:
                orphan_ids.append(point.id)

        if next_offset is None:
            break
        offset = next_offset

    if orphan_ids:
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=orphan_ids,
        )
        log.info("Deleted %d orphaned points", len(orphan_ids))
    else:
        log.info("No orphaned points found")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Embed aleph-code-mine docs into Qdrant")
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=Path(__file__).parent.parent.parent / "docs",
        help="Path to docs root (default: ../../docs relative to this script)",
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Use http://localhost:6333 instead of QDRANT_URL env var",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse, chunk, and prefix only — skip embedding and Qdrant upload",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    docs_root = args.docs_dir.resolve()

    if not docs_root.exists():
        log.error("docs-dir not found: %s", docs_root)
        sys.exit(1)

    # --- Step 1: Parse & Chunk ---
    log.info("=== Step 1: Parsing and chunking docs from %s", docs_root)
    chunks = load_all_docs(docs_root)
    if not chunks:
        log.error("No chunks produced — check docs directory")
        sys.exit(1)

    # --- Step 2: Contextual Prefixes ---
    together_api_key = os.environ.get("TOGETHER_API_KEY")
    together_model = os.environ.get("TOGETHER_MODEL", TOGETHER_MODEL_DEFAULT)

    if together_api_key:
        log.info("=== Step 2: Generating contextual prefixes via %s", together_model)
        prefixed_texts = add_contextual_prefixes(chunks, together_api_key, together_model)
    else:
        log.warning("TOGETHER_API_KEY not set — skipping contextual prefixes")
        prefixed_texts = [c["text"] for c in chunks]

    if args.dry_run:
        log.info("=== Dry run complete — %d chunks produced, skipping embed + upload", len(chunks))
        for i, chunk in enumerate(chunks[:3]):
            print(f"\n--- Chunk {i} ({chunk['source_file']}) ---")
            print(f"Breadcrumb: {chunk.get('breadcrumb', '')}")
            print(f"Has code: {chunk.get('has_code', False)}")
            print(prefixed_texts[i][:300])
        return

    # --- Step 3: Embed ---
    log.info("=== Step 3: Embedding %d chunks", len(prefixed_texts))
    vectors = embed_texts(prefixed_texts)

    # --- Step 4: Upload ---
    qdrant_url = "http://localhost:6333" if args.local else os.environ.get("QDRANT_URL")
    qdrant_api_key = None if args.local else os.environ.get("QDRANT_API_KEY")

    if not qdrant_url:
        log.error("QDRANT_URL env var not set and --local not specified")
        sys.exit(1)

    log.info("=== Step 4: Uploading to Qdrant at %s", qdrant_url)
    client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

    ensure_collection(client)
    upsert_points(client, chunks, vectors)

    live_source_files = {c["source_file"] for c in chunks}
    cleanup_orphans(client, live_source_files)

    log.info("=== Done. %d points in '%s'", len(chunks), COLLECTION_NAME)


if __name__ == "__main__":
    main()
