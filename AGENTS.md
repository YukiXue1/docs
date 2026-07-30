# AGENTS.md

This repository is the **public documentation site** for TronLink developer integrations. It is *not* the source code of TronLink itself, the MCP servers, the CLI, or the Signer SDK — those live in separate repositories listed below.

If you are an AI coding agent or an autonomous tool reading this for orientation, start with the curated index, not by enumerating files.

> This is the repository-root variant with repository-relative links. The deployed site serves the same file at [https://docs.tronlink.org/AGENTS.txt](https://docs.tronlink.org/AGENTS.txt) (source: `docs/AGENTS.txt`; mirrored at `/AGENTS.md` and `/CLAUDE.md` at deploy time) with absolute URLs so links survive HTTP fetching. Keep the two in sync when editing either.

## Entry points for AI agents

- **Curated index:** [docs/llms.txt](docs/llms.txt) — short, link-only map of the documentation, following [llmstxt.org](https://llmstxt.org/). Use this first.
- **Single-fetch full text:** [docs/llms-full.txt](docs/llms-full.txt) — every English page concatenated for one-shot ingestion. The header records the generating commit SHA, UTC timestamp, page count, and a rough token estimate; check those before relying on the content.
- **Static MCP tool contracts:** [docs/reference/mcp-tools.json](docs/reference/mcp-tools.json) — every MCP tool definition (name, description, `inputSchema`) captured from the published npm servers via `tools/list`, for agents that need the full contract without spawning a server. (MCP `annotations` would be captured too; the current servers publish none.)
- **Human-readable site:** [https://docs.tronlink.org/](https://docs.tronlink.org/)

## Topic map

| Surface | Doc |
| --- | --- |
| DApp integration in the browser (TIP-6963 / `eth_requestAccounts` / `tronWeb`) | [docs/dapp/getting-started.en.md](docs/dapp/getting-started.en.md) + [docs/plugin-wallet/*](docs/plugin-wallet/) |
| Mobile DeepLink (`tronlinkoutside://`) | [docs/mobile/deeplink.en.md](docs/mobile/deeplink.en.md) |
| AI-agent tooling overview | [docs/ai-support/ai-llms.en.md](docs/ai-support/ai-llms.en.md) |
| Cross-surface security invariants & vulnerability disclosure | [docs/ai-support/security-model.en.md](docs/ai-support/security-model.en.md) |
| MCP server (production) | [docs/ai-support/mcp-server-tronlink.en.md](docs/ai-support/mcp-server-tronlink.en.md) |
| MCP framework / SSOT error codes | [docs/ai-support/tronlink-mcp-core.en.md](docs/ai-support/tronlink-mcp-core.en.md) |
| MCP signer wrapper (HITL signing) | [docs/ai-support/mcp-tronlink-signer.en.md](docs/ai-support/mcp-tronlink-signer.en.md) |
| Signer SDK (browser-approval signing) | [docs/ai-support/tronlink-signer.en.md](docs/ai-support/tronlink-signer.en.md) |
| Skills package (read-only MCP tools; CLI adds raw-key write commands) | [docs/ai-support/tronlink-skills.en.md](docs/ai-support/tronlink-skills.en.md) |
| CLI (transactions via browser approval) | [docs/ai-support/tronlink-cli.en.md](docs/ai-support/tronlink-cli.en.md) |
| Cross-surface error-code map (DApp / DeepLink / MCP / CLI, with retryable flags) | [docs/reference/error-code-map.en.md](docs/reference/error-code-map.en.md) |
| Networks, addresses, glossary, FAQ | [docs/reference/](docs/reference/) |

## Source-of-truth boundaries

- **Error codes & retry semantics:** the SSOT is [docs/ai-support/tronlink-mcp-core.en.md#error-codes](docs/ai-support/tronlink-mcp-core.en.md#error-codes). Downstream docs link into it; do not duplicate the table.
- **Per-tool input schemas:** the SSOT is the running MCP server's `list_tools` (returns `inputSchema` per tool). [docs/reference/mcp-tools.json](docs/reference/mcp-tools.json) is a stamped static snapshot of that output; doc tables are a summary, not a contract.
- **Versions:** each AI-support page ends with `Version & License` keyed to the corresponding upstream `package.json`.

## Continuous verification (enforced in CI)

- **Doc ↔ schema parity:** [scripts/check_doc_schema_parity.py](scripts/check_doc_schema_parity.py) runs on every push and PR and daily on a schedule ([.github/workflows/check-doc-schema-parity.yml](.github/workflows/check-doc-schema-parity.yml)). It diffs the inline JSON Schema mirrors in the MCP server doc against the upstream Zod schemas (`tronlink-mcp-core` `src/mcp-server/schemas.ts`); an upstream rename or required/optional drift fails the build, so published schema mirrors cannot silently rot. (The published servers emit no schema-version marker on the wire; this CI check is the guard.)
- **Post-deploy link check:** every deploy ends with `scripts/gen_llms_full.py --verify`, probing the llms endpoints, the agent-entry mirrors, the `security.txt` pointer, and sampled index links for HTTP 200.

## Security disclosures

Report vulnerabilities privately to tronlink@tronlink.org with a `[SECURITY]` subject prefix — never in a public issue. Machine-readable pointer: [https://docs.tronlink.org/.well-known/security.txt](https://docs.tronlink.org/.well-known/security.txt) (RFC 9116); full policy: [SECURITY.md](SECURITY.md).

## Upstream code repositories (not in this repo)

- [github.com/TronLink/mcp-server-tronlink](https://github.com/TronLink/mcp-server-tronlink)
- [github.com/TronLink/tronlink-mcp-core](https://github.com/TronLink/tronlink-mcp-core)
- [github.com/TronLink/mcp-tronlink-signer](https://github.com/TronLink/mcp-tronlink-signer) (monorepo includes `tronlink-signer`)
- [github.com/TronLink/tronlink-cli](https://github.com/TronLink/tronlink-cli)
- [github.com/TronLink/tronlink-skills](https://github.com/TronLink/tronlink-skills)

If you need to change runtime behavior (tool schemas, error codes, transaction logic), open a PR there. PRs to this repo should only update prose, examples, and diagrams.

## How to refresh derived files

```bash
python3 scripts/gen_llms_full.py     # llms-full bundles + index header stamps
python3 scripts/dump_mcp_tools.py    # static MCP tool contracts (docs/reference/mcp-tools.json)
```

Run the first after any change under `docs/` (CI also runs it automatically at deploy time); run the second when an upstream npm package publishes a new version.
