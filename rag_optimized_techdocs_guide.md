# RAG-optimized technical documentation: a complete architecture guide

**Your documentation pipeline—BAAI/bge-large-en-v1.5 with Qdrant, chunked at 1500 characters via LangChain's RecursiveCharacterTextSplitter—is well-configured, but how you author and structure documents determines whether retrieval actually works.** The most critical insight from this research: each chunk must be semantically self-contained because vector search returns isolated fragments, not full documents. This principle drives every recommendation below, from section sizing and heading hierarchy to metadata strategies and auto-generated linting docs. The good news is that techniques optimized for RAG retrieval also produce better human-readable documentation—clear headings, focused sections, explicit context, and consistent terminology serve both audiences.

---

## Your chunk size hits the embedding model's sweet spot

Your **1500-character chunk size translates to roughly 375 tokens**, which sits inside the optimal range for bge-large-en-v1.5. The model has a hard maximum of **512 tokens**—anything beyond is silently truncated with no graceful degradation. Industry benchmarks from Chroma's research show that 400-token chunks with 10–20% overlap achieve **88–89% recall**, which your configuration closely mirrors.

This means every `##` section in your Markdown should target **≤1,500 characters** (roughly 250–350 words). When a section fits within a single chunk, the embedding captures one coherent semantic unit. When sections spill across chunks, topics get muddled—as Weaviate's documentation puts it, "like trying to describe a book by averaging all its chapters." If a topic genuinely needs more space, use `###` subsections that each stay under 1,500 characters, giving the splitter clean fallback boundaries.

Your **200-character overlap (13.3%)** falls within the industry-standard 10–20% range and requires no adjustment. One important behavior to note: when RecursiveCharacterTextSplitter splits at a `\n## ` boundary, overlap does not bleed across section boundaries. This is desirable—you don't want unrelated sections contaminating each other's embeddings. If your docs contain significant code, consider testing 250 characters (17%) since code-heavy content benefits from slightly higher overlap.

Your separator hierarchy (`["\n## ", "\n### ", "\n#### ", "\n\n", "\n", " ", ""]`) correctly mirrors the heading cascade. The splitter first attempts to break at `##`, then falls back to `###`, then `####`, then paragraphs, then lines. This means your heading structure directly controls chunk boundaries. Author accordingly: **treat `##` headings as primary chunk boundaries, `###` as fallback split points within large sections, and `####` as fine-grained divisions**.

---

## Self-contained chunks require deliberate authoring discipline

The single highest-impact optimization is making every chunk meaningful in isolation. Anthropic's 2024 research on contextual retrieval demonstrated that prepending **50–100 tokens of chunk-specific context** reduced retrieval failures by **49%**, and by **67%** when combined with reranking. You can implement this at two levels: authoring-time and pipeline-time.

**At authoring time**, follow these rules. Never start a section with pronouns like "It" or "This tool"—always use the specific technology name. Instead of writing "It supports hot reload," write "**Vite supports hot reload** for React components." Repeat the technology name and category naturally within each section's first sentence. A chunk that reads "To configure the cache TTL, set the `maxAge` property" is nearly useless without context; "To configure **Redis cache TTL** in the application's caching layer, set the `maxAge` property in `redis.config.ts`" retrieves accurately against a wide range of queries.

**At pipeline time**, consider Anthropic's contextual retrieval approach: use an LLM to generate a brief contextual prefix for each chunk before embedding. The prefix situates the chunk within its parent document—for example, "This section describes Vite's hot module replacement configuration within the Build Tools documentation." At roughly $1 per million document tokens with prompt caching, this is cost-effective for documentation-scale corpora. An alternative is LlamaIndex's "small-to-big" pattern: embed small, precise chunks for matching but return the parent section to the LLM for synthesis.

**For cross-references**, make them self-descriptive rather than purely navigational. Instead of "For caching, see [Redis](./redis.md)," write "For caching, **Redis** is the primary key-value store (see Redis documentation for connection pooling configuration)." The chunk must make sense if the link is never followed. Store related document IDs in chunk metadata (`related_docs: ["redis", "caching-patterns"]`) so your retrieval pipeline can optionally fetch associated content.

---

## Document granularity and metadata drive retrieval precision

**Favor many small, focused documents over fewer large ones.** When each document covers a single tool, pattern, or standard, the entire document often fits within one or two chunks, and the frontmatter metadata precisely describes the content. Large documents covering multiple topics create chunks where metadata (category, tags) may not accurately describe the specific chunk's content, degrading filtered retrieval.

Your Docusaurus frontmatter schema should exploit Qdrant's filterable HNSW indexes. A recommended schema:

```yaml
---
title: "Vite configuration standards"
category: "build-tools"
subcategory: "bundlers"
tags: ["vite", "hmr", "esm", "frontend"]
priority: "high"
audience: "frontend"
complexity: "intermediate"
doc_type: "tool-standard"          # standard | guide | reference | decision
last_updated: "2026-01-15"
---
```

Create **payload indexes** in Qdrant on `category`, `audience`, `doc_type`, and `tags` for efficient pre-filtering. Use `category` as the primary filter dimension with `must` conditions. Use `tags` with `should` conditions for OR matching. Leverage `priority` with Qdrant's Formula query to boost high-priority documents: `score = similarity × (1 + priority_weight)`. Use `last_updated` with range filters to exclude stale content. Qdrant's query planner automatically optimizes filter execution—low-cardinality filters like your 5–10 categories bypass HNSW entirely and use payload indexes, which is faster and cheaper.

**Consider two-stage splitting with LangChain's MarkdownHeaderTextSplitter.** First split by markdown headers to produce header-aware sections with metadata like `{'Header 2': 'Configuration', 'Header 3': 'Environment Variables'}`, then apply RecursiveCharacterTextSplitter within each section for size enforcement. This preserves heading context as retrievable metadata on every chunk.

---

## Code examples help retrieval when paired with natural language

Code blocks create a tension in RAG systems: they provide precise, unique keywords (function names, API calls, config keys) that boost both semantic and keyword matching, but large blocks dilute the embedding with syntax tokens that weaken conceptual retrieval. The resolution is structural.

**Short code snippets (1–5 lines) should be inline with explanatory prose.** A chunk containing "Install Vite using npm: `npm install vite`" embeds well for both natural language queries ("how to install Vite") and exact queries ("npm install vite"). **Longer code blocks (>10 lines) should occupy their own `###` subsection** with a descriptive heading and a 1–2 sentence natural language explanation. Never let a code block exist without accompanying prose—the embedding model (bge-large-en-v1.5 was not trained on code specifically) needs natural language to create a useful vector.

Tag chunks containing code with metadata like `has_code: true` and `language: "javascript"` to enable filtered retrieval. For Qdrant's hybrid search capability, consider adding sparse vectors (BM25) alongside dense vectors in the same collection—this captures exact keyword matches that semantic search might miss in code-heavy queries.

---

## BGE-large-en-v1.5 requires specific handling for optimal results

The model produces **1024-dimensional embeddings** using CLS pooling and a BERT WordPiece tokenizer. Three operational details matter for your pipeline.

**Instruction prefixes**: For retrieval tasks, prepend `"Represent this sentence for searching relevant passages: "` to queries only. **Never add prefixes to documents.** The v1.5 release specifically improved retrieval without instructions—BAAI states "no instruction only has a slight degradation in retrieval performance compared with using instruction"—so test both configurations on your actual queries and measure the difference.

**Markdown formatting impact**: No formal studies exist, but the BERT tokenizer treats markdown syntax (`##`, `**`, ```` ``` ````) as regular tokens consuming budget without adding semantic value. Light markdown (headers, bullet lists) provides useful structural hints from the model's pre-training on web text. Heavy markdown (nested code fences, complex tables, excessive bold) wastes tokens. Consider stripping ` ``` ` delimiters from code blocks before embedding while preserving them in the stored document.

**Similarity score interpretation**: Scores from this model cluster in the **0.6–1.0 range** due to contrastive learning with temperature=0.01. A score of 0.5 does not indicate dissimilarity—use relative ordering rather than absolute thresholds. If you must filter by score, set thresholds at **0.8–0.9**.

The model's most significant limitation is its **512-token context window**. Newer alternatives like BGE-M3 (8,192 tokens), Nomic-Embed (8,192 tokens), and OpenAI text-embedding-3-small (8,191 tokens) offer dramatically longer contexts. For your documentation use case with 1,500-character chunks, the 512-token limit is adequate. But if you ever need to embed longer passages or reduce chunking complexity, BGE-M3 (same MIT license, same organization) is the natural upgrade path.

---

## Auto-generating linting documentation from configs

No existing tool generates unified documentation from a project's specific linting configuration across ESLint, PHPCS, and Stylelint. The available tools are designed for plugin authors, not end-user projects. Here's what exists and how to build what's missing.

**ESLint** has the richest ecosystem. `eslint-doc-generator` (maintained by eslint-community, ~10,600 weekly npm downloads) generates README tables and rule notices from plugin `meta` objects. Wikimedia's `eslint-docgen` goes further by auto-generating good/bad code examples from test cases. For programmatic access, the `Linter#getRules()` method (ESLint ≤v8) returns a Map of all rules with full metadata including `docs.description`, `type`, `fixable`, and JSON Schema options. In ESLint v9+ flat config, import plugin modules directly and iterate their `.rules` export.

**PHPCS** has a built-in documentation generator: `phpcs --standard=PSR2 --generator=markdown` produces Markdown output from XML doc files in each standard's `Docs/` directory. The explain mode (`phpcs -e --standard=YourStandard`) lists all active sniff codes. PHPCSDevTools validates documentation completeness. The main limitation: PHPCS sniffs lack the rich programmatic metadata of ESLint rules—descriptions come from XML doc files or PHPDoc comments on sniff classes.

**Stylelint** has the least tooling. No dedicated documentation generator exists. Rules expose minimal metadata (`url`, `deprecated`, `fixable` since v15.3) with no `description` field. Use `stylelint.resolveConfig(filePath)` to get the effective config, then scrape descriptions from the official docs URL in `meta.url`, or maintain a static mapping.

**The recommended approach for a unified config-to-docs pipeline:**

1. Parse each linter's config using its native API to resolve the effective ruleset (handling `extends`, `overrides`, plugins)
2. For each active rule, extract metadata: name, severity, options, description, fixable status, documentation URL
3. Generate one Markdown file per rule following a consistent template (see below)
4. Layer in project-specific rationale ("Why we use this rule") manually or via comments in the config
5. Run generation on CI/CD so docs stay synchronized with config changes

**Per-rule document template optimized for RAG retrieval:**

```markdown
---
title: "no-unused-vars"
category: "eslint-rules"
tags: ["eslint", "variables", "cleanup"]
linter: "eslint"
severity: "error"
fixable: false
---

## ESLint rule: no-unused-vars

Disallows declaring variables that are never used in the codebase.
This rule is set to **error** severity because unused variables indicate
incomplete refactoring and increase cognitive load during code review.

### Configuration

Severity: `error`. Options: `{ "vars": "all", "args": "after-used",
"ignoreRestSiblings": true }`.

### Incorrect usage

Variables declared but never referenced trigger this rule:
`const unused = 42; // ERROR: 'unused' is defined but never used`

### Correct usage

All declared variables must be referenced:
`const used = 42; console.log(used);`
```

This template keeps each rule under 1,500 characters, includes frontmatter for filtered retrieval, pairs code with natural language, and repeats the rule name and linter context for self-contained chunks.

---

## Documentation architecture for dual human and AI consumption

The emerging industry pattern converges on a **docs-as-code pipeline with multiple output formats**: Markdown in Git → human-readable portal (Docusaurus) → AI-consumable formats (llms.txt, MCP server, vector index). The organizations doing this best—GitLab, Spotify/Backstage, Google—share common architectural principles.

**Use a hybrid taxonomy.** Organize standards by technology (JavaScript, PHP, CSS) for coding-specific rules, by concern (security, accessibility, performance) for cross-cutting standards, and use faceted metadata to enable discovery across both dimensions. This serves humans who browse by familiar category and AI that retrieves by metadata filter. The Airbnb JavaScript Style Guide demonstrates effective technology-based organization: rules grouped by language feature (Types, References, Objects, Destructuring) with consistent "do this / don't do this" patterns. Google's Style Guides organize purely by language across 17+ guides. GitLab's handbook organizes by workflow (code review, deployment, incident management). Your best approach combines all three with metadata facets.

**For MCP server integration**, several proven patterns exist. Context7 serves version-specific library documentation directly into AI prompts. Qdrant's own MCP server provides real-time documentation context via vector search. GitBook automatically exposes an MCP server at `/~gitbook/mcp` for every published space. The canonical architecture: developer asks a question in their IDE → MCP protocol routes to a search tool → RAG finds relevant chunks via Qdrant → results pass back as context for the response. Key design principles include combining semantic search with keyword boost for exact technical terms, grouping results by relevance gaps rather than arbitrary top-K, and using tool descriptions to tell the AI when to search (e.g., "Use this tool ALWAYS before writing frontend code").

**The llms.txt standard**, proposed by Jeremy Howard in September 2024, places a structured Markdown file at `/llms.txt` as a navigational index for LLMs, with `/llms-full.txt` containing the complete documentation compiled into a single file. Adoption is accelerating—Anthropic, Mintlify, Cursor, Vercel, and DatoCMS have all published llms.txt files. GitBook auto-generates them for every published space. For Docusaurus, you'd generate these files in your build pipeline.

**CLAUDE.md files** provide project-level context to Claude Code. Structure yours as a concise overview: build/test commands, code style preferences (linking to your full standards docs), architecture overview, domain terminology, and MCP server configuration pointing to your Qdrant-backed documentation search. Support a hierarchy: root `CLAUDE.md` for project-wide context, directory-level files for module-specific standards. Keep it concise—every word consumes context tokens.

---

## Conclusion

The architecture that emerges from this research is clear: **write focused, self-contained Markdown documents with rich frontmatter metadata, sized so each meaningful section fits within a single 1,500-character chunk.** Your embedding pipeline is well-configured—the 375-token chunk size sits in the optimal range for bge-large-en-v1.5, and your separator hierarchy correctly prioritizes heading boundaries.

Three non-obvious insights stand out. First, Anthropic's contextual retrieval technique (prepending LLM-generated context to chunks before embedding) delivers a **49% improvement in retrieval accuracy** and is worth implementing even with well-authored documents. Second, the gap in linting documentation tooling is real—no tool generates project-specific config documentation across linters, making a custom pipeline necessary but architecturally straightforward using each linter's metadata API. Third, the convergence of llms.txt, MCP servers, and CLAUDE.md means your documentation pipeline should output to multiple formats from a single Markdown source: Docusaurus for humans, Qdrant vector index for RAG retrieval, llms.txt for direct LLM consumption, and MCP endpoints for IDE integration. This multi-format output from a single source is the defining pattern of documentation architecture in 2025–2026.