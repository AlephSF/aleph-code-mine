---
title: "Node Version Management with .nvmrc"
category: "tooling-config"
subcategory: "environment"
tags: ["nodejs", "nvm", "nvmrc", "version-management", "consistency"]
stack: "js-nextjs"
priority: "medium"
audience: "fullstack"
complexity: "beginner"
doc_type: "standard"
source_confidence: "67%"
last_updated: "2026-02-11"
---

# Node Version Management with .nvmrc

## Overview

.nvmrc files specify Node.js version requirements, ensuring team consistency. 67% of Next.js projects (helix, policy-node) use .nvmrc, while kariusdx lacks version enforcement (critical gap for team collaboration).

**De Facto Standard:** Use .nvmrc with LTS or Current version, place file in project root, document version in README.

## Core Pattern: .nvmrc in Project Root

### LTS Version (Helix)

```bash
# .nvmrc
v18.17.0
```

**Source Evidence:** helix-dot-com-next/.nvmrc
**Node.js Version:** 18.17.0 (LTS - Long Term Support)
**Release Date:** August 2023
**Support Until:** April 2025

**Why LTS:**
- Stable, production-ready
- Security updates guaranteed
- Next.js 15 supports Node.js 18.x

### Current Version (Policy-node)

```bash
# .nvmrc
v22.13.1
```

**Source Evidence:** policy-node/.nvmrc
**Node.js Version:** 22.13.1 (Current)
**Release Date:** December 2024
**Support Until:** April 2026 (becomes LTS in October 2025)

**Why Current:**
- Latest features (native fetch, test runner, WebSocket)
- Next.js 14+ optimized for Node.js 20+
- Performance improvements (V8 12.0+)

### Critical Gap: Kariusdx (No .nvmrc)

Kariusdx (Next.js 12) has **no .nvmrc file**:

```bash
# kariusdx-next/ directory
ls -la .nvmrc
# File not found
```

**Consequences:**
- Team members may use different Node.js versions (14, 16, 18, 20, 22)
- "Works on my machine" bugs (version-specific behavior)
- CI/CD inconsistency (GitHub Actions may use different version)
- Next.js 12 requires Node.js 12.22.0+ (no upper bound enforcement)

**Recommendation:** Add `.nvmrc` with `v18.17.0` (LTS, safe for Next.js 12)

## Usage: Automatic Version Switching

### With nvm (Node Version Manager)

```bash
# Install nvm (macOS/Linux)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Navigate to project
cd helix-dot-com-next

# Auto-switch to version in .nvmrc
nvm use
# Found '/path/to/helix-dot-com-next/.nvmrc' with version <v18.17.0>
# Now using node v18.17.0 (npm v9.6.7)
```

### With fnm (Fast Node Manager - Rust-based)

```bash
# Install fnm (macOS/Linux/Windows)
brew install fnm

# Auto-switch on directory change
cd helix-dot-com-next
# Using Node v18.17.0
```

### With Volta (Rust-based, cross-platform)

```bash
# Install Volta
curl https://get.volta.sh | bash

# Volta reads .nvmrc automatically
cd helix-dot-com-next
# Using Node v18.17.0
```

## Integration with CI/CD

### GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Reads .nvmrc automatically
      - uses: actions/setup-node@v4
        with:
          node-version-file: '.nvmrc'

      - run: npm install
      - run: npm run lint
      - run: npm run build
```

**Benefit:** CI uses exact same Node.js version as local development

### GitLab CI

```yaml
# .gitlab-ci.yml
image: node:18.17.0  # Match .nvmrc version

test:
  script:
    - npm install
    - npm run lint
    - npm run build
```

## Version Selection Strategy

### Next.js 12 (Kariusdx)

```bash
# Recommended .nvmrc for Next.js 12
v18.17.0
```

**Why:**
- Next.js 12 requires Node.js 12.22.0+ (released 2020)
- Node.js 18 is LTS (supported until April 2025)
- Avoid Node.js 20+ (may have breaking changes for Next.js 12)

### Next.js 14 (Policy-node)

```bash
# Recommended .nvmrc for Next.js 14
v20.11.0  # or v22.13.1
```

**Why:**
- Next.js 14 requires Node.js 18.17+
- Node.js 20 is LTS (supported until April 2026)
- Node.js 22 is Current (becomes LTS October 2025)

### Next.js 15 (Helix)

```bash
# Recommended .nvmrc for Next.js 15
v18.17.0  # or v20.11.0
```

**Why:**
- Next.js 15 requires Node.js 18.18+
- Node.js 18 still in LTS (until April 2025)
- Can upgrade to Node.js 20 for performance

## Enforcement via package.json engines

```json
// package.json (policy-node)
{
  "engines": {
    "node": ">=20.0.0",
    "npm": ">=10.0.0"
  }
}
```

**Adoption:** 33% (policy-node only)

**Benefits:**
- npm warns if using unsupported version
- Hosting platforms (Vercel, Netlify) respect engines field
- Documents minimum version requirement

**Combined with .nvmrc:**

```bash
# .nvmrc
v22.13.1

# package.json
{
  "engines": {
    "node": ">=20.0.0"
  }
}
```

**.nvmrc:** Exact version for development
**engines:** Minimum version for deployment

## Auto-switching Configuration

### Shell Integration (zsh/bash)

```bash
# Add to ~/.zshrc or ~/.bashrc

# nvm auto-switch
autoload -U add-zsh-hook
load-nvmrc() {
  local node_version="$(nvm version)"
  local nvmrc_path="$(nvm_find_nvmrc)"

  if [ -n "$nvmrc_path" ]; then
    local nvmrc_node_version=$(nvm version "$(cat "${nvmrc_path}")")

    if [ "$nvmrc_node_version" = "N/A" ]; then
      nvm install
    elif [ "$nvmrc_node_version" != "$node_version" ]; then
      nvm use
    fi
  elif [ "$node_version" != "$(nvm version default)" ]; then
    nvm use default
  fi
}
add-zsh-hook chpwd load-nvmrc
load-nvmrc
```

**Benefit:** Automatically switches Node.js version when entering project directory

## Migration Path: Kariusdx → .nvmrc

```bash
# 1. Check current Node.js version team uses
node -v
# v18.17.0

# 2. Create .nvmrc
cd kariusdx-next
echo "v18.17.0" > .nvmrc

# 3. Add engines to package.json
npm pkg set engines.node=">=18.17.0"

# 4. Document in README
cat >> README.md << 'EOF'

## Node.js Version

Node.js 18.17.0 (LTS) is required for this project.

**With nvm:**
```bash
nvm use
```

**With fnm:**
```bash
fnm use
```
EOF

# 5. Commit
git add .nvmrc package.json README.md
git commit -m "Add .nvmrc for Node.js version consistency"
```

## Anti-Patterns to Avoid

### Don't: Use Outdated Node.js Versions

```bash
# ❌ Bad: Node.js 14 EOL April 2023
v14.21.3
```

**Problem:** Security vulnerabilities, no updates

### Don't: Use Version Ranges

```bash
# ❌ Bad: Ambiguous, defeats consistency
>=18.0.0
```

**Problem:** Team members may use 18.0.0, 18.17.0, 20.0.0 (inconsistent)

### Don't: Omit .nvmrc and engines

```json
// ❌ Bad: No version enforcement
{
  "name": "my-project"
  // Missing engines field
}
```

**Problem:** Developers use arbitrary Node.js versions, production may fail

## References

- **nvm GitHub:** https://github.com/nvm-sh/nvm
- **fnm GitHub:** https://github.com/Schniz/fnm
- **Node.js Release Schedule:** https://nodejs.org/en/about/previous-releases
- **package.json engines:** https://docs.npmjs.com/cli/v10/configuring-npm/package-json#engines

---

**Analysis Date:** February 11, 2026
**Projects Analyzed:** helix-dot-com-next (v15), kariusdx-next (v12), policy-node (v14)
**Pattern Instances:**
- .nvmrc adoption: 2/3 projects (67%)
- No .nvmrc (gap): 1/3 projects (33% - kariusdx)
- engines field: 1/3 projects (33% - policy-node)
