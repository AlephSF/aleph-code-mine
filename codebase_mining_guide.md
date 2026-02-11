# Mining your codebases with LLMs to generate coding standards

**You can systematically extract coding patterns from multiple repositories using Claude Code's agentic capabilities combined with deterministic static analysis tools, then synthesize these findings into structured, opinionated standards documents through an iterative human-AI workflow.** The most effective approach treats the LLM as a first-draft engine—not an oracle—using targeted codebase traversal, cross-project comparison matrices, and a document template modeled on the Airbnb style guide's proven convention-rationale-example format. This process works because modern AI coding assistants like Claude Code can read files, search across directories, spawn sub-agents for parallel exploration, and produce structured markdown output, while humans provide the irreplaceable context about *why* certain decisions were made. The result is a living documentation system where the LLM does the heavy lifting of pattern discovery and document drafting, and the team refines and ratifies the output.

---

## A phased codebase analysis strategy that avoids boiling the ocean

The single biggest mistake is asking an LLM to "analyze this codebase for patterns" in one pass. Large codebases exceed context windows, and unfocused analysis produces shallow, generic observations. Instead, use Anthropic's official **Explore → Plan → Execute** framework adapted for pattern extraction.

**Phase 1: Structural reconnaissance.** Start every analysis session by having Claude Code map the project's skeleton without reading implementation details. The prompt should be explicit: *"Read the project's package.json, tsconfig, folder structure, and README. Explain the architecture and tech stack. Do not read implementation files yet."* This gives you and the LLM a shared mental model of the codebase. Claude Code's built-in `Glob` and `Bash` tools (running `tree`, `find`, etc.) handle this efficiently. For multi-repo analysis, use the `--add-dir` flag to bring **3–4 project directories into a single session**.

**Phase 2: Domain-targeted deep dives.** Break the codebase into analysis domains and tackle one per session. Each domain gets its own focused prompt with specific extraction goals:

- **Components**: props interface patterns (inline vs. separate type files), composition patterns, naming conventions, render patterns, error boundary usage
- **Hooks**: custom hook inventory, dependency array patterns, cleanup conventions, how hooks compose with each other
- **Data layer**: API client structure, error handling for async operations, caching strategies, data transformation/normalization patterns
- **Utilities**: naming conventions, pure function patterns, shared abstraction approaches
- **Styling**: CSS methodology, responsive patterns, theme/token usage
- **Testing**: file co-location, naming conventions, mocking strategies, what gets tested

A well-constructed domain prompt looks like: *"Find all custom hooks in src/ (files matching use*.ts or use*.tsx). For each, document its purpose, dependencies, return value structure, and how it composes with other hooks. Group by category: data fetching, UI state, side effects, form handling. Show the most common patterns with code examples."*

**Phase 3: Convention synthesis.** After completing domain deep dives, have Claude Code produce a consolidated pattern report. This is where the LLM shines—synthesizing observations across dozens of files into a coherent picture of "how this team writes code." The key technique is to **always ask for both the pattern and its frequency**: a convention used in 90% of components is a team standard; one used in 30% is a contested practice worth discussing.

The **"Document & Clear" pattern** from practitioner Shrivu Shankar is essential for large codebases. Have Claude dump its analysis into a `.md` file, run `/clear` to reset the context window, then start a new session by pointing Claude at the analysis file to continue. This creates durable "external memory" for multi-session analysis work.

---

## The tooling pipeline that makes LLM analysis dramatically better

Raw LLM analysis is probabilistic and can hallucinate patterns that don't exist. **Deterministic tools provide the structured data scaffolding that makes LLM interpretation reliable.** The ideal pipeline runs quantitative tools first, then feeds their output to the LLM as grounding context.

**For JavaScript/TypeScript/React/Next.js codebases**, the recommended toolchain is:

- **Repomix** (`npx repomix --compress`) generates an LLM-optimized codebase summary using Tree-sitter to extract structural elements—function signatures, class definitions, key types—with roughly **70% token reduction** while preserving architecture. This compressed representation is the single most efficient way to give an LLM a "bird's eye view."
- **react-scanner** statically analyzes React component usage and prop patterns, outputting JSON like `{"Button": {"instances": 10, "props": {"variant": 5, "type": 3}}}`. This tells you which components are most used and their common prop combinations—data an LLM cannot reliably count on its own.
- **dependency-cruiser** validates and visualizes module dependencies with custom rules. Its JSON output includes every module, its dependencies, and any architectural violations. The `ddot` output summarizes at the folder level, producing exactly the kind of high-level architecture map an LLM needs.
- **Semgrep** is the most powerful pattern detection tool for this use case. Custom YAML rules can match any code pattern with metavariables and semantic understanding. Example: write a rule to find all instances of `useEffect` without cleanup functions, or all API calls that don't handle errors. The output includes file paths, line numbers, and matched code—**perfect structured input for LLMs**.
- **ts-morph** provides programmatic AST navigation. Write scripts to extract all component prop interfaces, all hook signatures, or all exported function types into JSON catalogs.
- **scc** (faster alternative to cloc) produces per-file complexity metrics and DRYness percentages, helping identify which files need the most pattern analysis attention.

**For PHP/WordPress codebases**, substitute:

- **PHPStan with the WordPress extension** (`szepeviktor/phpstan-wordpress`) for static analysis, with type inference that reveals architectural patterns
- **PHP_CodeSniffer with WPCS** (WordPress Coding Standards ruleset) for conventions compliance
- **nikic/php-parser** for AST extraction—custom PHP scripts can extract all `add_action()`/`add_filter()` registrations, custom post types, REST API endpoints, and class hierarchies
- **Semgrep** works across both stacks, supporting PHP alongside JavaScript/TypeScript

The general pipeline: run `scc` for a quantitative overview → run `dependency-cruiser` or `madge` for architecture graphs → run `react-scanner` or custom AST scripts for pattern catalogs → run `Semgrep` for targeted pattern detection → package everything via `Repomix` → feed all structured outputs to the LLM as context alongside the actual code.

---

## Cross-project synthesis: finding the signal across 3–4 repositories

Comparing patterns across projects requires a structured methodology. The approach that works best is building a **pattern comparison matrix**—a table mapping common concerns against each project's implementation—then using the LLM to analyze differences and recommend standards.

**Step 1: Build the pattern inventory.** For each domain (components, hooks, data fetching, error handling, etc.), extract representative examples from each project. Use Claude Code with `--add-dir` pointing at all repos simultaneously. A focused prompt works far better than a broad one: *"Compare how Projects A, B, and C handle API error responses. Show the actual code pattern from each project. Identify: (1) what's common across all three, (2) where they diverge, (3) which approach best aligns with Next.js 14+ conventions."*

**Step 2: Classify divergences.** Not all differences are problems. Some represent legitimate evolution—Project C may use newer patterns because it started later. Others represent drift—teams independently inventing different solutions to the same problem. The LLM can help classify these, but **the human must provide context** about project timelines, team composition, and intentional architectural decisions. A useful framing for the team: for each divergent pattern, decide to **converge** (pick one standard), **allow variants** (document both with guidance on when to use each), or **deprecate** (mark one as legacy with migration timeline).

**Step 3: Track pattern evolution.** Git history analysis reveals whether patterns improved or degraded over time. Tools like **GitEvo** analyze code evolution metrics across commits, detecting preference shifts (e.g., migration from `var` to `const`, adoption of server components). A practical approach: use `git log` with date ranges to sample code at different points, then feed historical samples to the LLM with the prompt *"Here is how our error handling looked in 2023 vs. 2025. What conventions changed? Was this intentional improvement or drift?"*

**Step 4: Generate the unified standard.** Once decisions are made, prompt the LLM to produce the reconciled standard with code examples drawn from the "winner" project for each pattern, plus "bad" examples from the deprecated approaches. This grounds the standards in actual team code rather than abstract ideals.

The practical constraint is context window size. Even with **200K tokens**, you can't fit three full codebases. The mitigation is strategic sampling: use Repomix compressed output for the high-level view, then pull specific files for detailed comparison on a per-domain basis.

---

## The interactive Claude Code workflow that actually works

The most effective practitioner workflows share a common structure: the human steers and provides context while the AI does the mechanical work of traversal and pattern identification. Here is the refined workflow based on multiple practitioner reports.

**Session setup.** Create a `CLAUDE.md` file in the analysis directory (not the project root) with the analysis objectives, tech stack details, and any known conventions. Claude Code reads this automatically. Keep it concise—research shows frontier LLMs reliably follow about **150–200 instructions**, and Claude Code's system prompt already consumes ~50. Focus on what matters: *"We're analyzing 3 Next.js 14 projects to extract coding standards. The projects use TypeScript strict mode, Tailwind CSS, and React Server Components. Key areas: component patterns, hooks, data fetching, error handling."*

**Custom slash commands** stored in `.claude/commands/` eliminate repetitive prompting. Create reusable analysis commands:

```markdown
# .claude/commands/analyze-domain.md
Analyze all files related to $ARGUMENTS across the loaded projects.
For each project, identify the dominant patterns with code examples.
Create a comparison table showing similarities and differences.
Recommend which pattern to standardize on with rationale.
```

Usage: `/analyze-domain data fetching` or `/analyze-domain error handling`.

**The human-AI dialogue pattern.** The most productive sessions follow this rhythm: the AI presents findings → the human provides context ("we chose that pattern because of X constraint") → the AI incorporates context and refines → the human validates or redirects. Critically, **tell Claude Code to ask you questions** when it encounters patterns it can't explain. The prompt *"When you find a pattern that seems unusual or inconsistent, stop and ask me why before drawing conclusions"* prevents the LLM from confidently misinterpreting intentional architectural decisions.

**Prompting strategies that consistently work well:**

- **"Show, don't tell"**: Show the LLM one example of a pattern and ask it to find all similar instances. LLMs excel at mimicry—*"Here's how we implement data fetching in ProjectA/src/hooks/useUsers.ts. Find all hooks across all three projects that follow a similar pattern, and note any that deviate."*
- **Frequency-first analysis**: Ask for pattern counts before descriptions. *"How many components use inline prop types vs. separate interface files? Give me the numbers before the analysis."* This grounds the conversation in facts.
- **Persona assignment**: *"You are a senior React architect conducting a code audit. Focus on architectural consistency, not formatting."* This shifts output from superficial observations to structural insights.
- **Explicit output format**: Specify exactly what you want. *"Output a markdown table with columns: Pattern Name, Frequency (% of files), Example File, Description, Recommendation."*

**Sub-agent fan-out** is Claude Code's most powerful feature for large analysis tasks. It can spawn multiple read-only "Explore" sub-agents that work in parallel: *"Have one sub-agent analyze the component architecture while another analyzes the data layer patterns."* Each agent works in isolated context and reports back findings, effectively multiplying throughput.

---

## The standards document structure that teams actually follow

Analysis of the most successful industry style guides—**Airbnb's JavaScript guide**, **Google's language-specific guides**, and **WordPress Coding Standards**—reveals a consistent structure that works. The Airbnb format is the gold standard for individual rules; Google's Pros/Cons/Decision format works best for architectural decisions.

**The per-rule template** that maximizes both scannability and depth:

```markdown
### 4.3 Use named exports for all components

**Status:** 📝 Convention | **Source:** 🤖 Detected in 94% of components
**Linter Rule:** `import/no-default-export`

Always use named exports for React components. Default exports
make refactoring harder and reduce IDE autocompletion reliability.

**Why:** Named exports enforce consistent import naming across the
codebase and produce better error messages during refactoring.
In Projects A and B, default exports led to 3 different import
names for the same component.

// ❌ Bad
export default function UserProfile() { ... }

// ✅ Good  
export function UserProfile() { ... }

**Exceptions:** Next.js page components require default exports
per framework convention.
```

This template works because every rule includes **what** (the convention), **why** (rationale derived from actual team experience), **how** (code examples from the real codebase), and **when not** (exceptions). The status indicators—✅ Enforced by tooling, 📝 Convention requiring manual review, ⚠️ Recommendation, 🤖 Auto-detected from code, 👤 Requires team input—are critical for LLM-generated drafts because they tell human reviewers exactly what needs validation.

**The document-level structure** should be organized by domain rather than language feature for framework-specific guides. A React/Next.js standards document works best with these sections:

1. **Overview & principles** (team philosophy, scope)
2. **Project structure** (directory layout, file naming, module organization)
3. **Component patterns** (structure, props, composition, render patterns)
4. **Hooks & state management** (custom hooks, effect patterns, memoization)
5. **Data fetching & API integration** (client patterns, error handling, caching)
6. **TypeScript conventions** (type vs. interface, generics, strictness)
7. **Styling** (methodology, naming, responsive, tokens)
8. **Error handling** (boundaries, try/catch, user-facing errors)
9. **Testing** (organization, patterns, coverage, mocking)
10. **Tooling configuration** (ESLint/Prettier/TypeScript config summaries)

Each section should open with a **one-paragraph summary** of the team's approach, then dive into individual numbered rules. Google's approach of separating **rules** (strict mandates) from **guidelines** (strong suggestions with flexibility) prevents the frustration that comes from over-standardization.

**Critical design decisions for LLM-generated drafts:**

- **Tag confidence levels.** Mark each standard as "observed in N% of files" so reviewers can distinguish universal team conventions from emerging or contested patterns. A pattern in 95% of files is a de facto standard; one in 40% is a discussion point.
- **Include a decision log appendix.** For every non-obvious choice, record why the team chose this approach. This is where human context is irreplaceable and where LLM-generated drafts need the most augmentation.
- **Build in versioning.** Use semver (v0.1.0 for initial LLM draft, v1.0.0 after team ratification) with a changelog at the top. This signals that the document is alive and evolving.
- **Generate multiple output formats simultaneously.** The same standards should exist as human-readable markdown, a `CLAUDE.md` file for each project, ESLint/Prettier configuration, and a PR review checklist. Ask the LLM to produce all four from the same source of truth.

---

## The complete end-to-end workflow: four weeks to living standards

Bringing all the pieces together into a practical timeline:

**Week 1 — Discovery and extraction.** Clone all repositories into a local analysis directory. Run quantitative tools first: `scc` for code metrics, `dependency-cruiser` for architecture graphs, `react-scanner` for component usage statistics, `Semgrep` for targeted pattern detection. Generate Repomix compressed summaries for each project. Then use Claude Code with `--add-dir` to begin domain-by-domain analysis across all projects, producing a raw pattern inventory in markdown.

**Week 2 — Cross-project analysis and reconciliation.** Build the pattern comparison matrix. For each domain, have Claude Code compare approaches across projects and produce a recommendations document with pros/cons for each divergent pattern. Present this to the team. Make decisions: converge, allow variants, or deprecate. Record decisions in ADR (Architecture Decision Record) format.

**Week 3 — Document generation and multi-format output.** Feed the reconciled decisions back to Claude Code with the per-rule template. Generate the full standards document, section by section, with code examples pulled from actual project code. Simultaneously generate `CLAUDE.md` files, ESLint configurations, and PR checklists. Have multiple team members review the draft, providing the human context (rationale, history, constraints) that the LLM couldn't infer.

**Week 4 — Rollout and living documentation setup.** Publish shared lint/format configuration as an npm package (or Composer package for PHP). Add `CLAUDE.md` files to each repository. Set up CI checks that enforce machine-checkable standards. Schedule quarterly reviews where you re-run the analysis pipeline against current code to detect drift. Use the prompt: *"Review our standards document against these recent code samples. What standards are being followed? Violated? What new patterns emerged that aren't documented?"*

---

## Conclusion

The key insight from this entire process is that **LLMs and deterministic tools serve complementary roles that neither can fill alone**. Static analysis tools like Semgrep, react-scanner, and dependency-cruiser provide the quantitative ground truth—exact counts, dependency graphs, pattern frequencies. LLMs provide the interpretive layer—recognizing that three syntactically different code blocks implement the same architectural pattern, or that a team's error handling evolved from callbacks to async/await to server actions across project generations.

The most underutilized technique is **feeding structured tool output to the LLM as context before asking for analysis**. An LLM told "react-scanner found Button used 247 times with `variant` prop in 89% of instances" produces dramatically better component standards than one asked to "analyze Button usage." Similarly, the most underutilized Claude Code feature is **sub-agent fan-out**—spawning parallel exploration agents to analyze different domains simultaneously, then synthesizing findings in the main session.

For teams with existing hand-written standards (like the CSS, TypeScript, and React/Next.js docs mentioned), the highest-value activity isn't rewriting what exists but **running the analysis pipeline to find the gap**: patterns that are consistently followed in code but not yet documented. These implicit conventions are where the real standards live, and they're exactly what LLM-powered codebase analysis is best at surfacing.