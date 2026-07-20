# Error Code Map

TronLink agents traverse up to five error-code dialects when a single user request crosses the DApp provider → DeepLink → MCP → Signer MCP → CLI surfaces. This page is a single horizontal join keyed by **business meaning**; use it to translate a code from one dialect to its peers and to decide whether retrying is safe.

> The per-surface tables linked in the column headers remain the SSOT. This page is a navigation aid — when in doubt, branch on the structured field of the surface you actually called (`error.code` for MCP and the Signer MCP; the JS error `code` for the provider; the callback `code` for DeepLink; exit status + the stderr `error` message prefix for the CLI).

| Business meaning | DApp provider ([EIP-1474][provider]) | DeepLink ([5-digit][deeplink]) | MCP ([`TL_*`][mcp]) | Signer MCP ([codes][signer]) | CLI ([exit + stderr class][cli]) | Retryable? |
| --- | :---: | :---: | :---: | :---: | :---: | :---: |
| **User rejected / cancelled** the signing or connection prompt | `4001` | `300` (Transaction canceled) | — (HITL — re-prompt only on a fresh tool call) | `USER_REJECTED`, `CANCELLED` | `1` · `Transaction cancelled by user in TronLink` | **No** |
| **Invalid input** / malformed params | thrown by `tronWeb` builder | `10001`–`10020`, `10024`, `10025` | `TL_INVALID_INPUT` | `INVALID_INPUT` | `1` · validation error (before any wallet interaction) | **No** — fix the payload |
| **Method / capability not supported** | `4200` | `10003`, `10008`, `10009`, `10011`, `10023` | `TL_CAPABILITY_NOT_AVAILABLE` | — | — | **No** |
| **Wallet authorization mismatch** (initiator ≠ current wallet) | provider returns empty `accounts[]` | `10021`, `10022` | — | — | — | **No** — re-authorize |
| **No wallet / no session / signer gone** | provider not injected (`window.tron` undefined) | `10016` | `TL_NO_ACTIVE_SESSION` | `BROWSER_DISCONNECTED` (approval page closed — for writes, reconcile on-chain first) | `1` · `Signer disconnected (browser closed?)` | **No** — re-initialize first; for a write, reconcile before re-issuing |
| **Rate-limited / wallet locked** | `-32000` (`eth_requestAccounts` within 20 s while locked) | — | `TL_CHAIN_QUERY_FAILED` (TronGrid HTTP 429) | — | — | **Yes** — wait and retry |
| **Network / RPC transient** (TronGrid, RPC error) | TronGrid HTTP error in `tronWeb` call | — | `TL_CHAIN_QUERY_FAILED`, `TL_GASFREE_QUERY_FAILED`, `TL_MULTISIG_QUERY_FAILED` | `NETWORK_ERROR` | `1` · `Network connection failed` | **Yes** |
| **On-chain execution failed** (post-broadcast: `REVERT`, `OUT_OF_ENERGY`, `FAILED`) | thrown by `sendRawTransaction` or surfaces via `getTransactionInfo` | — | `TL_CHAIN_SEND_FAILED`, `TL_CHAIN_SWAP_FAILED`, `TL_GASFREE_SEND_FAILED`, `TL_MULTISIG_SUBMIT_FAILED` | `BROADCAST_FAILED`, `ON_CHAIN_FAILED` | `1` · raw node message (`OUT_OF_ENERGY` / `REVERT`) or `Transaction broadcast failed:` | **No** — the tx is final; fix the root cause; never auto-retry writes |
| **Timeout** (user didn't sign in time, element not found) | call resolves slowly; no canonical code | — | `TL_WAIT_TIMEOUT`, `TL_NAVIGATION_FAILED` | `TIMEOUT` (approval window only — nothing was signed) | `1` · `TronLink approval timed out` | **Maybe** — safe for reads; for writes that may have been broadcast, reconcile via `tronWeb.trx.getTransactionInfo` / `tl_chain_get_tx` before retrying. (Signer `TIMEOUT` is always pre-sign, so re-issuing it is safe) |
| **Internal / unexpected** | `-32603` (Internal error) | — | `TL_INTERNAL_ERROR`, `TL_LAUNCH_FAILED` | — | `1` · unclassified raw message | **Yes once** — retry once then escalate with logs |

[provider]: ../dapp/getting-started.md#request-authorization
[deeplink]: ../mobile/deeplink.md#result-code
[mcp]: ../ai-support/tronlink-mcp-core.md#error-codes
[signer]: ../ai-support/mcp-tronlink-signer.md#errors
[cli]: ../ai-support/tronlink-cli.md#errors

## How to use this map

1. Receive an error from any surface, look up its row, and read across to find the corresponding code (or absence) on the other surfaces.
2. The **Retryable?** column is the agent-safety hint:
    - **No** — auto-retry will fail or do harm. The most dangerous case is "On-chain execution failed", where the tx is already final on-chain.
    - **Yes** — transient; back off (exponential, max 3 retries) and retry the original call.
    - **Maybe** — read-only retry is OK; **never auto-retry writes** without first reconciling with on-chain state.
3. The DeepLink and CLI columns have many gaps because those surfaces only cover a slice of the lifecycle — DeepLink is mobile-only and lives on a separate trust boundary; the CLI (v1.0.x) exits `0`/`1` only, so its class lives in the stderr `error` message prefix shown above (see [CLI Errors][cli]). Use the most specific surface available.

## Notes for downstream MCP servers

Downstream MCP servers should reuse the `TL_*` codes for framework-level conditions. The Signer's server-specific codes (`USER_REJECTED`, `TIMEOUT`, `BROWSER_DISCONNECTED`, …) predate this rule and form its own **documented dialect**, joined in the Signer MCP column above. If a **new** business meaning emerges, add a row here and a `TL_*` constant in `tronlink-mcp-core` (the SSOT) first; do not mint further ad-hoc codes in consuming servers.
