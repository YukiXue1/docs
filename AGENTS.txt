# AGENTS.md

This repository is the **public documentation site** for TronLink developer integrations. It is *not* the source code of TronLink itself, the MCP servers, the CLI, or the Signer SDK — those live in separate repositories listed below.

If you are an AI coding agent or an autonomous tool reading this for orientation, start with the curated index, not by enumerating files.

## Entry points for AI agents

- **Curated index:** [docs/llms.txt](docs/llms.txt) — short, link-only map of the documentation, following [llmstxt.org](https://llmstxt.org/). Use this first.
- **Single-fetch full text:** [docs/llms-full.txt](docs/llms-full.txt) — every English page concatenated for one-shot ingestion. The header records the generating commit SHA, UTC timestamp, page count, and a rough token estimate; check those before relying on the content.
- **Human-readable site:** [https://docs.tronlink.org/](https://docs.tronlink.org/)

## Topic map

| Surface | Doc |
| --- | --- |
| DApp integration in the browser (TIP-6963 / `eth_requestAccounts` / `tronWeb`) | [docs/dapp/getting-started.en.md](docs/dapp/getting-started.en.md) + [docs/plugin-wallet/*](docs/plugin-wallet/) |
| Mobile DeepLink (`tronlinkoutside://`) | [docs/mobile/deeplink.en.md](docs/mobile/deeplink.en.md) |
| AI-agent tooling overview | [docs/ai-support/ai-llms.en.md](docs/ai-support/ai-llms.en.md) |
| MCP server (production) | [docs/ai-support/mcp-server-tronlink.en.md](docs/ai-support/mcp-server-tronlink.en.md) |
| MCP framework / SSOT error codes | [docs/ai-support/tronlink-mcp-core.en.md](docs/ai-support/tronlink-mcp-core.en.md) |
| MCP signer wrapper (HITL signing) | [docs/ai-support/mcp-tronlink-signer.en.md](docs/ai-support/mcp-tronlink-signer.en.md) |
| Signer SDK (browser-approval signing) | [docs/ai-support/tronlink-signer.en.md](docs/ai-support/tronlink-signer.en.md) |
| Read-only Skills package | [docs/ai-support/tronlink-skills.en.md](docs/ai-support/tronlink-skills.en.md) |
| CLI (transactions via browser approval) | [docs/ai-support/tronlink-cli.en.md](docs/ai-support/tronlink-cli.en.md) |
| Networks, addresses, glossary, FAQ | [docs/reference/](docs/reference/) |

## Source-of-truth boundaries

- **Error codes & retry semantics:** the SSOT is [docs/ai-support/tronlink-mcp-core.en.md#error-codes](docs/ai-support/tronlink-mcp-core.en.md#error-codes). Downstream docs link into it; do not duplicate the table.
- **Per-tool input schemas:** the SSOT is the running MCP server's `list_tools` (returns `inputSchema` per tool). Doc tables are a summary, not a contract.
- **Versions:** each AI-support page ends with `Version & License` keyed to the corresponding upstream `package.json`.

## Upstream code repositories (not in this repo)

- [github.com/TronLink/mcp-server-tronlink](https://github.com/TronLink/mcp-server-tronlink)
- [github.com/TronLink/tronlink-mcp-core](https://github.com/TronLink/tronlink-mcp-core)
- [github.com/TronLink/mcp-tronlink-signer](https://github.com/TronLink/mcp-tronlink-signer) (monorepo includes `tronlink-signer`)
- [github.com/TronLink/tronlink-cli](https://github.com/TronLink/tronlink-cli)
- [github.com/TronLink/tronlink-skills](https://github.com/TronLink/tronlink-skills)

If you need to change runtime behavior (tool schemas, error codes, transaction logic), open a PR there. PRs to this repo should only update prose, examples, and diagrams.

## How to refresh derived files

```bash
python3 scripts/gen_llms_full.py
```

This regenerates `docs/llms-full.txt` with a fresh commit SHA, timestamp, and token estimate. Run it after any change under `docs/`.
