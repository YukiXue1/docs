# TronLink Developer Documentation

This is the official developer documentation for the TronLink wallet, providing comprehensive development guides and API references.

## 🤖 For AI Agents

If you are an AI agent (Claude, Cursor, Codex, etc.) reading this repo, start here:

- [`AGENTS.md`](AGENTS.md) — orientation: topic map, SSOT boundaries (error codes, schemas, versions), upstream package pointers.
- [`docs/llms.txt`](docs/llms.txt) / [`docs/llms.zh.txt`](docs/llms.zh.txt) — curated [llmstxt.org](https://llmstxt.org/) indexes. **Source filenames** carry `.en`/`.zh` suffixes; **deployed URLs** strip them: `/llms.txt` (EN) and `/zh/llms.txt` (ZH).
- [`docs/llms-full.en.txt`](docs/llms-full.en.txt) / [`docs/llms-full.zh.txt`](docs/llms-full.zh.txt) — every page concatenated for single-fetch ingestion. Deployed at `/llms-full.txt` (EN) and `/zh/llms-full.txt` (ZH).
- [`docs/ai-support/`](docs/ai-support/) — MCP servers, Skills, CLI, signer SDK. Live AI/agent surface; see [`ai-llms.en.md`](docs/ai-support/ai-llms.en.md) for the overview.

Branch on structured `error.code` / `error.retryable`, never on prose. Sign / Remote Write tools require user approval (HITL) and must not be auto-retried — see each tool's Safety section.

## 📖 Documentation Contents

- **Introduction** - Overview of TronLink and the TRON ecosystem
- **HD Wallet** - Documentation related to HD wallets
- **TronLink App** - Mobile integration guide
  - Asset Management
  - DeepLink
  - DApp Support
- **TronLink Wallet Extension** - Browser extension development
  - Request TronLink Extension
  - Receive messages from TronLink
- **DApp** - Decentralized application development
  - Start Developing
  - Multi-Signature Transfer
  - Message Signature
  - General Transfer
  - Stake2.0
- **AI Support** - AI agent tooling and machine-readable documentation
  - AI / LLMs (entry point + `llms.txt` / `llms-full.*.txt` endpoints)
  - MCP Server TronLink (52 tools: on-chain, multi-sig, GasFree)
  - TronLink MCP Core (framework library, SSOT for error codes & schemas)
  - TronLink Skills (read-only agent skills, 33 commands / 25 MCP tools)
  - MCP TronLink Signer & TronLink Signer SDK (HITL signing)
  - TronLink CLI

## 🚀 Getting Started

### Local Development

1. Clone the repository
```bash
git clone https://github.com/TronLink/docs.git
cd docs
```

2. Install dependencies
```bash
nvm install
nvm use
pip install -r requirements.txt
```

Node.js is pinned to 24.22.1 in `.nvmrc` for local development and CI.
The documentation is built with Python and MkDocs.

3. Start the local server
```bash
mkdocs serve
```

4. Visit http://localhost:8000 to view the documentation.

### Build the Documentation

```bash
mkdocs build
```

The built files will be output to the site/ directory.


## 🔧 Tech Stack

- [MkDocs](https://www.mkdocs.org/) - Static site generator
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) - Theme
- [GitHub Pages](https://pages.github.com/) - Hosting service
- [GitHub Actions](https://github.com/features/actions) - CI/CD for deployment


## 🤝 Contact Us

- Official Website: https://www.tronlink.org/

## 📚 Related Links

- [TronLink Official Site](https://www.tronlink.org/)
- [TRON Official Site](https://tron.network/)
- [TRON Developer Center](https://developers.tron.network/)











  
    

 





