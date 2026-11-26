# mcp-tronlink-signer

**GitHub**: https://github.com/TronLink/mcp-tronlink-signer

MCP Server that exposes [tronlink-signer](https://github.com/TronLink/mcp-tronlink-signer/tree/main/packages/tronlink-signer) as MCP tools for Claude and other AI clients. Sign TRON transactions via TronLink browser wallet with user approval — private keys never leave the wallet.

## Setup

### Claude Code

```bash
claude mcp add -s user tronlink-signer -- npx mcp-tronlink-signer
```

### Claude Desktop / Cursor

```json
{
  "mcpServers": {
    "tronlink-signer": {
      "command": "npx",
      "args": ["mcp-tronlink-signer"]
    }
  }
}
```

### From Source

```bash
git clone https://github.com/TronLink/mcp-tronlink-signer.git
cd mcp-tronlink-signer
pnpm install && pnpm build
```

Then point to the built CLI:

```bash
claude mcp add -s user tronlink-signer -- node /path/to/packages/mcp-tronlink-signer/dist/cli.js
```

## MCP Tools

| Tool | Description | Parameters | Side effect | Auto-retry safe? |
| ---- | ----------- | ---------- | --- | :---: |
| `connect_wallet` | Connect TronLink wallet | `network?` | Local Write (caches session) | Yes — user re-approves if needed |
| `send_trx` | Send TRX to an address | `to`, `amount`, `network?` | **Remote Write** | **No** — verify on-chain before re-issuing |
| `send_trc20` | Send TRC20 tokens | `contractAddress`, `to`, `amount`, `decimals?`, `network?` | **Remote Write** | **No** — same as `send_trx` |
| `sign_message` | Sign a message | `message`, `network?` | Local Write (signs only; no broadcast) | Yes — re-prompts the user |
| `sign_typed_data` | Sign EIP-712 typed data | `typedData`, `network?` | Local Write (signs only) | Yes — re-prompts the user |
| `sign_transaction` (`broadcast=false`) | Sign a raw transaction | `transaction`, `broadcast=false`, `network?` | Local Write | Yes — re-prompts the user |
| `sign_transaction` (`broadcast=true`) | Sign + broadcast | `transaction`, `broadcast=true`, `network?` | **Remote Write** | **No** — verify on-chain before re-issuing |
| `get_balance` | Get TRX balance | `address`, `network?` | Network Read | Yes |

All tools support an optional `network` parameter (`mainnet` / `nile` / `shasta`), defaulting to `mainnet`.

**Human-in-the-loop.** Every tool that signs (`send_trx`, `send_trc20`, `sign_message`, `sign_typed_data`, `sign_transaction`) opens the TronLink approval page in the browser. The AI agent **cannot** sign without the user clicking Approve. Treat Remote Write tools as requiring confirmation in production.

## MCP Resources

| URI | Description |
| --- | ----------- |
| `wallet://networks` | Available networks and their configurations |
| `wallet://config` | Current signer configuration |

## MCP Prompts

| Prompt | Description |
| ------ | ----------- |
| `send-trx` | Guided workflow for sending TRX |
| `check-balance` | Guided workflow for checking balance |
| `send-token` | Guided workflow for sending TRC20 tokens |

## How It Works

1. AI agent calls an MCP tool (e.g., `send_trx`) — a signing notice is shown in the CLI
2. The server delegates to `tronlink-signer`, which opens a **single browser tab** for approval (reuses existing tab if open)
3. The approval page discovers TronLink via **TIP-6963** protocol
4. Auto-unlocks wallet and switches network if needed
5. `connect_wallet` auto-completes if the wallet is already connected
6. Transaction details are parsed into human-readable format (TRX transfer, TRC20, TRC721 NFT, stake, delegate, vote, etc.)
7. User reviews and approves in the browser
8. TronLink signs the transaction — private keys never leave the wallet
9. Result is returned to the AI agent — the page stays open for the next operation

## End-to-End Example

A typical `send_trx` flow, from the user's prompt to the on-chain result:

**1. User → agent**

> "Send 5 TRX to TJRabc…xyz on nile."

**2. Agent → MCP tool call**

```json
{
  "name": "send_trx",
  "arguments": { "to": "TJRabc...xyz", "amount": 5, "network": "nile" }
}
```

**3. Approval (human-in-the-loop)** — the server opens the TronLink approval page; the user reviews "Send 5 TRX → TJRabc…xyz (Nile)" and clicks **Approve**. Clicking Reject returns an error result `Error: USER_REJECTED` (do not re-issue without asking the user).

**4. MCP tool → agent (result)**

```json
{
  "txId": "0a1b2c...",
  "status": "success"
}
```

**5. Agent → user**

> "Sent 5 TRX — confirmed on-chain (tx `0a1b2c…`)."

> Branch on `isError` and the `status` field of the JSON result. Errors carry only message text (see [Errors](#errors)). `status: "pending"` means the broadcast succeeded but confirmation timed out — reconcile with `get_balance` or an explorer lookup rather than resending (see [Errors](#errors)).

## Cancellation

All signing tools support MCP cancellation. If the AI client cancels a pending tool call (e.g., user presses Ctrl+C in Claude Code), the in-flight request is automatically aborted and the browser approval page is not opened for already-cancelled requests.

## Transaction Confirmation

When `sign_transaction` is called with `broadcast: true`, the server automatically polls for on-chain confirmation after broadcast and returns the execution status (`success`, `pending`, or `failed`). If the transaction fails on-chain (e.g., `OUT_OF_ENERGY`, Solidity revert), the result has `status: "failed"` with the decoded reason in `error`, and is flagged `isError: true`.

## Errors

In v0.1.4, errors are returned as an MCP tool result with `isError: true` and a single text item `Error: <message>`. There is no structured `code` or `retryable` field. Known messages:

| Result | Retryable | When |
| --- | :---: | --- |
| `Error: USER_REJECTED` | No | User clicked Reject on the signer approval page. |
| `Error: Confirmation declined by user` | No | User rejected in the TronLink extension popup. |
| `Error: CANCELLED_BY_CALLER` | Check first | The MCP client cancelled the call (e.g., Ctrl+C). If it was cancelled after broadcast, the transaction may already be on chain. |
| `Error: TIMEOUT: Request timed out after 5 minutes` | Check first | No result within 5 minutes. Re-issuing re-opens the prompt. |
| `Error: WALLET_CHANGED: <reason>` | Check first | The TronLink account or network changed, or the wallet disconnected; pending requests were cleared. |
| JSON result with `"status": "failed"` (`isError: true`) | No | Broadcast succeeded but on-chain execution failed (`OUT_OF_ENERGY`, Solidity revert). The transaction is final; address the root cause and submit a new tx. |
| Other `Error: <message>` | No — inspect | Input validation errors, a broadcast rejected by the node, network errors, etc. The text is passed through. |

**Retry policy.** Read calls (`get_balance`) are safe to re-issue. A rejection means the user declined — do not re-issue without asking. For `send_trx`, `send_trc20`, and `sign_transaction` with `broadcast: true`, treat any error (including `CANCELLED_BY_CALLER` and `TIMEOUT`) as an unknown outcome — confirm with `get_balance` or an explorer lookup before re-issuing.

## Security Boundaries

| Boundary | Guarantee | Agent / operator obligation |
|---|---|---|
| **Prompt injection** | Tool inputs are consumed verbatim as call arguments; the server does not re-prompt an LLM with them. The TronLink approval page renders parsed transaction fields, not the agent's free-text. | Treat any on-chain string returned (memos, revert reasons) as untrusted; branch on `txId` / `status`, not on prose. |
| **Local HTTP listener** | The local approval server **binds to `127.0.0.1` only** (port `TRON_HTTP_PORT`, default 3386, auto-increments on conflict). It never accepts off-host connections. Each server session has a unique ID; old browser tabs from previous sessions are invalidated automatically. | Do not port-forward 3386 over a network. Do not run two copies of this server with the same `TRON_HTTP_PORT` on a shared box. |
| **Outbound host allowlist (SSRF)** | The signer only talks to TronGrid endpoints listed in [Networks](#environment-variables) and to the local browser. Tools do not accept user-supplied URLs that get fetched. | Pin `TRON_NETWORK` and (optionally) `TRON_API_KEY` to known values in production. |
| **API key handling (token passthrough)** | `TRON_API_KEY` is read from env at startup and used only on the outbound leg to TronGrid. It is **not** returned in any tool response, error `details`, or MCP resource. The server does not accept Authorization headers from MCP clients and forward them upstream. | Store the key in the MCP host's secret manager, not in plain `mcpServers` config committed to git. |
| **HITL is mandatory for signing** | Every signing tool (`send_trx`, `send_trc20`, `sign_message`, `sign_typed_data`, `sign_transaction`) opens the TronLink approval page. **There is no programmatic bypass.** Private keys never leave TronLink. | Operators do not need to enforce HITL — it is structural. Do not attempt to harden by removing the browser layer. |
| **Browser tab hijacking** | The approval page authenticates each request against the server session ID and ignores stale tabs. Heartbeat detection closes the session on browser disconnect. | If the same user runs multiple agents, ensure each spawns its own signer instance; cross-instance request mixing is prevented by session ID, but UI confusion is not. |
| **Confused deputy** | The signer acts under the connected TronLink account; there is no per-call authorization scope from the MCP client. | One signer instance = one TronLink account; do not multiplex multiple end users through the same instance. |

## Environment Variables

| Variable | Description | Default |
| -------- | ----------- | ------- |
| `TRON_NETWORK` | Default network (mainnet/nile/shasta) | `mainnet` |
| `TRON_HTTP_PORT` | Local HTTP server port | `3386` |
| `TRON_API_KEY` | TronGrid API key (optional) | - |

## Version & License

- **Package:** `mcp-tronlink-signer` v0.1.4
- **License:** MIT — `SPDX-License-Identifier: MIT`
- **Changelog / releases:** [https://github.com/TronLink/mcp-tronlink-signer/releases](https://github.com/TronLink/mcp-tronlink-signer/releases)

### Inline changelog

This page mirrors a downstream README; for the source of truth see the GitHub releases above and the `CHANGELOG.md` in each package. Entries below cover the **MCP-visible** surface (tools, schema, security boundaries) — internal refactors are omitted.

#### v0.1.4 _(npm-only, not GitHub-tagged at time of writing)_

Patch-only. No new tools, no breaking input/output shapes. Verify against `list_tools` after upgrade.

#### v0.1.3 _(npm-only, not GitHub-tagged at time of writing)_

Patch-only. No new tools, no breaking input/output shapes.

#### v0.1.2 — 2026-04-15

Co-released with `tronlink-signer@0.1.2`. **Major UX overhaul** on the approval flow; no breaking MCP tool schemas.

- **New** — `sign_transaction` accepts `broadcast: true` to sign and broadcast in one step (was sign-only previously).
- **New** — `connect_wallet` auto-completes when the wallet is already connected; no extra approval round-trip.
- **New** — Transaction parsing: TRX transfer, TRC10, TRC20, TRC721 NFT, stake/unstake, delegate, vote, etc. are rendered in human-readable form on the approval page.
- **Improved** — Single-page approval flow: one persistent browser tab with heartbeat-based liveness; stale tabs across server restarts are invalidated automatically.
- **Improved** — TRC20 amount validation now uses BigInt-based decimal conversion (handles 0-decimal and >18-decimal edge cases).
- **Improved** — `send_trx` and `sign_transaction` return real broadcast errors instead of empty messages on submission failure.
- **Migration** — None required; MCP tool schemas are unchanged.

#### v0.1.1 — 2026-04-15

- Initial npm release of `tronlink-signer@0.1.1` + `mcp-tronlink-signer@0.1.1`.
- Per-package README with usage instructions and API documentation.
- npm package metadata (keywords, repository, license, files).
- Copyright notice added to LICENSE.

### Compatibility & migration policy

- **Semver.** Pre-1.0: a **minor** bump (0.x → 0.y) may introduce breaking changes; a **patch** bump (0.1.x → 0.1.y) will not change MCP tool names or input schemas. Post-1.0: standard semver — major-only breaking changes.
- **Deprecations.** [mcp-tronlink-signer 0.1.4](https://www.npmjs.com/package/mcp-tronlink-signer/v/0.1.4) exposes no deprecation flag for its registered tools. Before upgrading, review the target release notes and compare the tool names and input fields returned by `tools/list`.
- **Stable contracts.** Tool names and `status` values (`success` / `pending` / `failed`) are part of the public surface — they don't change in a patch.
- **Volatile contracts.** Error `message` text (match the known values under [Errors](#errors) and treat others as unknown), log line formats, and the layout of the browser approval page are **not** part of the public surface and may change at any time.
- **Verifying after upgrade.** Re-call `list_tools` and confirm the names + schemas you depend on are still present before resuming a workflow.
