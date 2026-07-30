# AI / LLMs

TronLink's developer documentation is published in machine-readable form so AI agents and LLM-based tools can discover, read, and integrate it directly.

!!! info "Allowed uses vs. crawler policy"
    This site is curated for **retrieval / RAG / inference-time grounding** — the `llms.txt` and `llms-full.txt` bundles below are the canonical ingestion points for that case, and they are explicitly maintained for AI use.

    Training-time bulk crawling is a separate question and is governed by the site's `robots.txt` plus the `Content-Signal` directives served at the edge. Some training-only user-agents are currently disallowed there; if you need a different policy for your use case, contact us rather than parsing the bundles to circumvent the signal.

## Available endpoints

> **URL ≠ source filename.** Source files carry `.en` / `.zh` suffixes (`llms.zh.txt`, `llms-full.en.txt`, `llms-full.zh.txt`) so the mkdocs i18n plugin can route them. **In the deployed site the suffix is stripped** — Chinese variants live under `/zh/`. Use the deployed URLs below; the source-name URLs (e.g. `/llms-full.en.txt`) return 404.

| Endpoint (deployed URL) | Description |
| --- | --- |
| [/llms.txt](../../llms.txt) | Curated English index of key pages ([llmstxt.org](https://llmstxt.org/) format) |
| [/zh/llms.txt](../../zh/llms.txt) | Curated Chinese index — same layout, links into `/zh/` pages |
| [/llms-full.txt](../../llms-full.txt) | Every English page concatenated for single-fetch ingestion (built from `docs/llms-full.en.txt`) |
| [/zh/llms-full.txt](../../zh/llms-full.txt) | Every Chinese page concatenated for single-fetch ingestion (built from `docs/llms-full.zh.txt`) |
| [/reference/mcp-tools.json](../../reference/mcp-tools.json) | Static machine-readable snapshot of every MCP tool contract — name, description, `inputSchema` — captured from the published npm servers via `tools/list` |
| [/AGENTS.txt](https://docs.tronlink.org/AGENTS.txt) | Orientation file for AI agents — entry points, topic map, SSOT boundaries (mirrored at `/AGENTS.md` and `/CLAUDE.md`) |
| [/.well-known/security.txt](https://docs.tronlink.org/.well-known/security.txt) | RFC 9116 vulnerability-disclosure pointer (also served at `/security.txt`) |

Production URLs: `https://docs.tronlink.org/llms.txt`, `https://docs.tronlink.org/zh/llms.txt`, and the matching `llms-full.txt` bundles under each locale root.

## Which file should I use?

| Use case | URL |
| --- | --- |
| Navigate / find the right English page | `/llms.txt` — short, link-only map |
| Navigate / find the right Chinese page | `/zh/llms.txt` — same layout, Chinese descriptions |
| Ingest the whole English documentation in one request | `/llms-full.txt` |
| Ingest the whole Chinese documentation in one request | `/zh/llms-full.txt` |
| Read the full MCP tool contracts without spawning a server | `/reference/mcp-tools.json` — static snapshot; the running server's `tools/list` is the SSOT |

Start with the index for your language and follow its links; fetch a full bundle when you need everything at once. The Chinese index points at `/zh/` slugs; the English index points at root-level slugs.

## Add to your AI tool

- **Cursor** — Settings → Features → Docs → *Add new doc*, paste `https://docs.tronlink.org/llms.txt`.
- **Claude / MCP-capable agents** — TronLink ships MCP servers for live wallet and chain access; see [MCP Server TronLink](mcp-server-tronlink.md) and [MCP TronLink Signer](mcp-tronlink-signer.md) for host configuration. For documentation context, point the tool at the `llms.txt` URL above.
- **Other tools** — any tool that accepts a custom documentation URL can use the `llms.txt` / `llms-full.txt` endpoints.

## Coverage

The bundle covers the full documentation, including the AI/agent tooling:

- [MCP Server TronLink](mcp-server-tronlink.md) — on-chain, multi-sig, and GasFree tools (Playwright + Direct API)
- [TronLink MCP Core](tronlink-mcp-core.md) — framework library: schemas, tool definitions, flow recipes
- [TronLink Skills](tronlink-skills.md) — read-only agent skill set (wallet, token, market, swap, resource, staking)
- [MCP TronLink Signer](mcp-tronlink-signer.md) — MCP server wrapping the signer SDK
- [TronLink Signer](tronlink-signer.md) — standalone signer SDK
- [TronLink CLI](tronlink-cli.md) — command-line tool

Plus the DApp integration, mobile (DeepLink), and Reference (networks, glossary, FAQ) sections.

## Notes for agents

- Start from `llms.txt` — it is the authoritative map. Don't enumerate the site blindly.
- For tool calls, branch on the structured `error.code` / `error.retryable`, never on the human-readable `message`.
- Read operations are safe to retry; signing / Remote Write operations require user approval (HITL) and must not be auto-retried — see each tool's Safety section.
- Default to testnets (`nile` / `shasta`) when experimenting; use `mainnet` only for real funds.
