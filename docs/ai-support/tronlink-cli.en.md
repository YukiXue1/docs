# TronLink CLI

**GitHub**: [https://github.com/TronLink/tronlink-cli](https://github.com/TronLink/tronlink-cli)

CLI tool for TRON blockchain operations via TronLink wallet signing.

All transactions are built locally and signed through the TronLink browser extension — private keys never leave TronLink.

## Requirements

- Node.js >= 20
- TronLink browser extension installed
- Browser running (write operations open TronLink for signing)

**Bundled runtime (pinned by `@tronlink/tronlink-cli@1.0.1`):**

- `tronweb` `6.2.2` — used by `transactionBuilder`, the ABI v2 trigger path, `TronWeb.isAddress()`, and local broadcast. TronWeb 6.x exposes the ethers-backed ABI v2 encoder that powers tuple / nested-array / arrays-of-tuples in `trigger`; earlier TronWeb majors do not. If you ever bump this dep, re-test every `trigger` example.
- `tronlink-signer` `0.1.4` — the local signing bridge to the browser extension. Same SDK documented in [tronlink-signer](tronlink-signer.md).

Effective as of 2026-05; source: each package's `package.json`.

## Installation

```bash
# From npm
npm install -g @tronlink/tronlink-cli

# Local development
npm install
npm run build
npm link
```

After installation, the `tronlink` command is available globally.

## Global Options

| Option              | Default | Description                                                |
| ------------------- | ------- | ---------------------------------------------------------- |
| `--local-broadcast` | off     | CLI broadcasts locally instead of letting signer broadcast |
| `--json`            | off     | Output as JSON for scripts / AI agents                     |
| `--api-key <key>`   | -       | TronGrid API key (or set `TRON_API_KEY` env)               |
| `--timeout <ms>`    | 300000  | Signing/connection timeout in milliseconds                 |
| `--port <n>`        | 3386    | TronLink Signer HTTP port                                  |

All option **names** are case-insensitive (e.g. `--toAddress`, `--TOADDRESS`, `--toaddress` are equivalent), and the enum **values** of `--type` / `--network` / `--resource` are case-normalized too (`--type TRC20` works). TRON base58 addresses and contract addresses are case-sensitive data — pass them exactly as given.

## Commands

### Query (Read)

Read commands support two modes:

- **With `--address`**: queries directly via TronGrid, no wallet connection needed. Defaults to mainnet if `--network` is omitted.
- **Without `--address`**: prompts TronLink approval to read the current wallet address (defaults to mainnet if `--network` is omitted).

```bash
# Query all token balances
tronlink balance --address <address> [--network mainnet]
tronlink balance                                          # connects wallet

# Query a specific TRC20 token balance (decimals auto-detected)
tronlink balance --address <address> --token <contract> [--decimals 6] [--network mainnet]

# Query a specific TRC10 token balance (decimals auto-detected)
tronlink balance --address <address> --tokenId <id> [--decimals 6] [--network mainnet]

# Query energy & bandwidth
tronlink resource --address <address> [--network nile]
tronlink resource                                         # connects wallet
```

**Mainnet tokens queried**: TRX, USDT, USDD, USDC, SUN, JST, BTT, WIN, WTRX
**Nile tokens queried**: TRX, USDT
**Shasta tokens queried**: TRX

### Transfer

```bash
# TRX (amount in TRX, not sun)
tronlink transfer --type trx --toAddress <to> --amount <amount> [--network nile]

# TRC10 (decimals auto-detected or specify --decimals)
tronlink transfer --type trc10 --tokenId <id> --toAddress <to> --amount <amount> [--decimals 6] [--network nile]

# TRC20 (decimals auto-detected; optional --fee-limit in TRX, default 100)
tronlink transfer --type trc20 --contract <contract> --toAddress <to> --amount <amount> [--decimals 6] [--fee-limit 150] [--network nile]

# TRC721 NFT (optional --fee-limit in TRX, default 100)
tronlink transfer --type trc721 --contract <contract> --toAddress <to> --tokenId <id> [--fee-limit 150] [--network nile]
```

> **The default network is `mainnet`.** Omitting `--network` moves real funds. The examples below pin `--network nile`; drop it only when you intend mainnet.

Examples:

```bash
tronlink transfer --type trx --toAddress TYqx5gm3p3wLDE9Bv8TBJAbK4ELNbSLfJV --amount 100 --network nile
tronlink transfer --type trc20 --contract <trc20-contract> --toAddress TYqx5gm3p3wLDE9Bv8TBJAbK4ELNbSLfJV --amount 50 --network nile
tronlink transfer --type trc721 --contract TContractAddr --toAddress TRecipient --tokenId 12345 --network nile
```

Parameter validation per type:

| Type   | Required                                 | Not allowed                                           |
| ------ | ---------------------------------------- | ----------------------------------------------------- |
| trx    | `--toAddress`, `--amount`                | `--tokenId`, `--contract`, `--decimals`, `--fee-limit`|
| trc10  | `--toAddress`, `--amount`, `--tokenId`   | `--contract`, `--fee-limit`                           |
| trc20  | `--toAddress`, `--amount`, `--contract`  | `--tokenId`                                           |
| trc721 | `--toAddress`, `--contract`, `--tokenId` | `--amount`, `--decimals`                              |

### Trigger Smart Contract

Call any smart contract method. Arguments are a JSON array aligned by position to the types in `--method`.

```bash
# Writeable call (signed + broadcast)
tronlink trigger \
  --contract <address> \
  --method 'transfer(address,uint256)' \
  --args '["TRecipient...","1000000"]' \
  [--call-value <trx>] [--fee-limit <trx>] [--network nile]   # fee-limit in TRX, default 100

# Constant (read-only) call — returns raw hex from constant_result
tronlink trigger \
  --contract <address> \
  --method 'balanceOf(address)' \
  --args '["TQuery..."]' \
  --constant [--address <addr>] [--network nile]
```

Examples:

```bash
# TRC20 approve
tronlink trigger --contract TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t \
  --method 'approve(address,uint256)' \
  --args '["TSpender...","1000000"]'

# Batch swap with tuple array
tronlink trigger --contract TDex... \
  --method 'swap((address,uint256)[],uint256)' \
  --args '[[["T...","100"],["T...","200"]],"999"]' --fee-limit 200

# Payable call (with --call-value)
tronlink trigger --contract TPay... --method 'deposit()' --args '[]' --call-value 5

# Read-only query
tronlink trigger --contract TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t \
  --method 'balanceOf(address)' --args '["TQuery..."]' --constant --address TQuery...
```

Notes:

- `--method` takes the Solidity function signature. Names on parameters are optional and ignored: `transfer(address to, uint256 amount)` works the same as `transfer(address,uint256)`.
- Structured types are fully supported: tuples, nested arrays, arrays of tuples (e.g. `swap((address,uint256)[],uint256)`). Encoding goes through TronWeb's ABI v2 path (ethers under the hood).
- `--args` must be a JSON array aligned by position to the method's top-level inputs. Tuples are nested JSON arrays (not objects); use strings for `uint256`/`int256` to avoid JS precision loss.
- Writeable calls run a pre-flight simulation on chain (`triggerConstantContract`) before signing. Contract reverts, insufficient TRX for call-value + fee, and fee-limit overruns are caught before a transaction is ever submitted.
- `--constant` skips signing and broadcast. Pass `--address` to avoid a wallet prompt when the owner address doesn't matter. Decoded output is not provided — use a Solidity ABI decoder on the returned hex.

### Staking (Stake 2.0)

```bash
# Stake TRX for energy or bandwidth
tronlink stake --amount <amount> --resource <energy|bandwidth> [--network nile]

# Unlock staked TRX
tronlink unstake --amount <amount> --resource <energy|bandwidth> [--network nile]

# Withdraw unfrozen TRX (after 14-day unlock period)
tronlink withdraw [--network nile]
```

### Resource Delegation

```bash
# Delegate energy or bandwidth (lock-period in days, supports decimals e.g. 1.5)
tronlink delegate --toAddress <to> --amount <amount> --resource <energy|bandwidth> [--lock-period <days>] [--network nile]

# Reclaim delegated resources
# Partial reclaim is allowed: if some delegations are past their lock period and
# others are still locked, you can reclaim up to the unlocked total. The precheck
# reports how much is unlocked and when the next batch unlocks if the request
# exceeds the unlocked amount.
tronlink reclaim --fromAddress <from> --amount <amount> --resource <energy|bandwidth> [--network nile]
```

### Voting

```bash
# Vote for super representatives (format: address:count, supports multiple)
tronlink vote --votes <address:count...> [--network nile]

# Claim voting rewards
tronlink reward [--network nile]
```

Examples:

```bash
tronlink vote --votes TXxx:5 TYyy:3 TZzz:2
tronlink reward
```

## Transaction Signing

Write operations (transfer, stake, delegate, vote, etc.) require TronLink approval in the browser:

1. CLI builds the transaction locally and displays a preview
2. Browser opens the TronLink Signer approval page
3. User reviews and clicks Approve or Reject
4. Result is returned to the CLI

The browser window is reused across multiple commands — only one browser tab is needed per session. Closing the browser tab ends the session.

Multiple concurrent commands are supported. The browser UI shows each pending request as its own tab; approve them in any order.

Cancelling a command (Ctrl+C) cancels only that transaction. Other queued transactions are unaffected.

## Transaction Preview

All write operations display a preview before signing:

```text
Transaction Preview
┌───────────┬────────────────────────────────────────┐
│ Action    │ Transfer TRX                           │
│ Network   │ nile                                   │
│ From      │ TXxx...                                │
│ To        │ TYyy...                                │
│ Amount    │ 100 TRX                                │
│ Broadcast │ Signer                                 │
└───────────┴────────────────────────────────────────┘
Awaiting TronLink approval...
```

For TRC10/TRC20/TRC721 and `trigger`, the preview additionally shows `Contract`, `Decimals`, and `FeeLimit` rows. `FeeLimit` (e.g. `100 TRX`) is the **maximum TRX burned** for the contract call if energy is insufficient — verify it before approving.

## Broadcast

By default, signed transactions are broadcast by the signer (TronLink). Use `--local-broadcast` to have the CLI broadcast locally via its own TronWeb instead:

```bash
# Default: signer broadcasts after signing
tronlink transfer --type trx --toAddress TYqx5gm3p3wLDE9Bv8TBJAbK4ELNbSLfJV --amount 100 --network nile

# CLI broadcasts locally
tronlink transfer --type trx --toAddress TYqx5gm3p3wLDE9Bv8TBJAbK4ELNbSLfJV --amount 100 --network nile --local-broadcast
```

**The two paths are mutually exclusive, not redundant.** Setting `--local-broadcast` tells the signer to return the signed transaction **without** broadcasting; the CLI then sends it once via its own TronWeb. The same signed payload is never submitted twice from this CLI in a single command.

If a network race causes the CLI's local broadcast and a stale signer broadcast to both reach the network (e.g. flapping connectivity re-submitting the same signed payload), the second submission is rejected by the node — TRON nodes deduplicate by transaction id, so you will see one block-inclusion plus one `DUP_TRANSACTION_ERROR`-class failure, not two on-chain effects. Treat any such error after a confirmed first inclusion as benign; treat it before confirmation as a network-class failure — reconcile with an explorer before retrying.

## Input Validation

All inputs are validated before connecting to TronLink:

- **Amounts**: non-negative numbers only, no scientific notation, no multiple decimals
- **TRX amounts**: must be > 0, within safe integer range after sun conversion
- **TRC20/TRC10 amounts**: decimal places must not exceed the token's decimals. Decimals auto-detected from chain if `--decimals` is omitted
- **Addresses**: valid TRON address format (verified via `TronWeb.isAddress()`)
- **Contract existence**: verified on the specified network before querying decimals
- **Vote counts**: positive integers, no duplicate SR addresses
- **Network**: must be `mainnet`, `nile`, or `shasta`
- **Decimals**: non-negative integer (0-77)
- **Fee limit**: positive number in TRX (TRC20/TRC721/trigger)
- **Call value** (trigger only): non-negative number in TRX; `0` is allowed and equivalent to omitting it
- **Method signature** (trigger): must be `name(type1,type2,...)`; parameter names are optional and ignored
- **Args** (trigger): valid JSON array whose length matches the method's top-level input count
- **Transfer type validation**: missing required params or extra inapplicable params are rejected with clear errors

Invalid inputs are rejected immediately with a clear error before any wallet interaction.

## Output Formats

**Table (default):** Human-readable table output.

**JSON (`--json`):** Machine-readable output for scripts and AI agents. Always pass `--json` for automation.

A successful write command returns:

```json
{
  "Status": "Success",
  "TxID": "0abc...",
  "Explorer": "https://tronscan.org/#/transaction/0abc..."
}
```

Read commands return the queried data (balances, resources, etc.) as a flat top-level object, e.g. a single-token balance query:

```json
{
  "Address": "TNPeeaaFB7K9cmo4uQpcU32zGK8G1NYqeL",
  "Network": "nile",
  "TokenID": "1000587",
  "Balance": "12.5"
}
```
 The stable keys are `Status` / `TxID` / `Explorer` for writes and the per-command data keys for reads; error output uses `status` / `error` on stderr (see [Errors](#errors)). Key names are stable within a major version.

## Exit Codes

The published CLI (v1.0.x) uses **two** exit codes:

| Exit code | Meaning |
| :---: | --- |
| `0` | Success — query returned, or transaction signed and broadcast |
| `1` | Any failure — validation, user rejection, timeout, on-chain failure, or network error |

There are **no per-class exit codes yet**: a script cannot distinguish failure classes from the exit status alone. The failure class is carried in the structured error line printed to **stderr** (see [Errors](#errors)) — branch on the exit status plus that line's `error` message.

> **Retry policy.** Read commands (any `balance` / `resource` / `--constant` trigger) are always safe to retry. For write/signing commands (transfer, stake, delegate, vote, writeable trigger), exit `1` does **not** tell you whether the transaction reached the network — never auto-retry; first reconcile via an explorer or `balance`, and re-issue only if the previous tx did not land.

## Errors

In `--json` mode, failures print a single structured line to **stderr** (stdout stays clean for the success payload):

```json
{ "status": "error", "error": "Transaction cancelled by user in TronLink" }
```

The `error` string comes from an internal classifier with a stable phrase per failure class (v1.0.1):

| Failure class | `error` message (match on prefix) | Safe to retry? |
| --- | --- | --- |
| User rejected | `Transaction cancelled by user in TronLink` | No — user declined |
| Approval timeout | `TronLink approval timed out. Please try again` | Only if nothing was broadcast — reconcile before re-issuing a write |
| Insufficient balance | `Insufficient balance: …` | No — fund the account first |
| Invalid address | `Invalid TRON address provided` | No — fix the input |
| Signer disconnected | `Signer disconnected (browser closed?) …` | Reconcile first — the tx may or may not have been sent |
| Network failure | `Network connection failed. Check your internet connection` | Yes — transient; for writes, confirm the previous tx didn't land first |
| Broadcast failed | `Transaction broadcast failed: …` | No — reconcile on-chain |
| On-chain execution failure | raw message, typically containing `OUT_OF_ENERGY` / `REVERT` / `FAILED` | No — the tx is final; fix the root cause |
| Unclassified | the raw underlying error message | Treat as unknown — reconcile before retrying writes |

Match on the **prefix** of the `error` string — the tail may embed the underlying node/RPC message. The last two classes have **no stable prefix**: when no known prefix matches, fall through to the reconcile-first default (treat the outcome of any write as unknown until confirmed on-chain). Duplicate submissions surface as a `DUP_TRANSACTION_ERROR` node message in the raw text — benign after a confirmed first inclusion. A structured `error.code` / `error.retryable` envelope and per-class exit codes are **not implemented** in v1.0.x; do not script against them.

## Safety & Side Effects

| Side effect | Commands |
| --- | --- |
| **Read-only** (Network Read, no signing) | `balance`, `resource`, constant `trigger` (`--constant`) |
| **Remote Write** (signs + broadcasts) | `transfer`, `stake`, `unstake`, `withdraw`, `delegate`, `reclaim`, `vote`, `reward`, writeable `trigger` |

- **Human-in-the-loop:** every write command builds the transaction locally, shows a [Transaction Preview](#transaction-preview), and requires explicit approval on the TronLink browser page before signing. Private keys never leave TronLink.
- **No auto-retry on writes:** see the retry policy above.
- **Testnet-first:** the CLI itself defaults to `mainnet` when `--network` is omitted — always pass `--network nile` / `shasta` while developing, and `--network mainnet` only for real funds.
- **No unattended signing path:** every write command requires a live browser and a human click on the TronLink approval page. In headless CI or on a server, only read commands with `--address` work; there is no service-account or key-file signing mode.

## Supported Networks

| Network | API Endpoint                     | Explorer                      |
| ------- | -------------------------------- | ----------------------------- |
| mainnet | `https://api.trongrid.io`        | `https://tronscan.org`        |
| nile    | `https://nile.trongrid.io`       | `https://nile.tronscan.org`   |
| shasta  | `https://api.shasta.trongrid.io` | `https://shasta.tronscan.org` |

## How It Works

1. CLI parses command and validates all inputs
2. For read operations with `--address`: queries TronGrid directly
3. For write/read without `--address`: connects to the TronLink browser extension for wallet info
4. Builds unsigned transaction using local TronWeb `transactionBuilder`
5. Pre-flight check: runs on all write commands (transfer, stake, unstake, delegate, reclaim, vote, trigger). Verifies TRX / token / staked / delegated balances, simulates contract calls to catch reverts, estimates energy & bandwidth burn, validates SR addresses (vote), NFT ownership (TRC721), and delegation unlock times (reclaim) before signing
6. Sends transaction to TronLink for signing (browser approval page)
7. Broadcasts: signer broadcasts by default, or CLI broadcasts locally with `--local-broadcast`. In both modes the CLI polls `getUnconfirmedTransactionInfo` until the tx is packed into a block (~3s), and surfaces OUT_OF_ENERGY / REVERT / FAILED as errors
8. Outputs result

## AI / Agent Usage

TronLink CLI supports AI agent integration via `--json` output. All commands return structured JSON for easy parsing.

### Prerequisites

- `tronlink` installed globally (`npm i -g @tronlink/tronlink-cli`)
- TronLink browser extension installed and unlocked
- Browser running (write operations open TronLink for signing)

### Rules

1. Always append `--json` to get machine-readable output
2. Write operations (transfer, stake, vote, etc.) will open the browser for user signing — wait for the command to return (default timeout: 5 minutes)
3. Read operations with `--address` don't need wallet connection, faster for lookups
4. Use `--network` to specify network; when omitted, commands default to mainnet
5. Cancelling a command (Ctrl+C) cancels only that transaction, not the signing session

### AI Command Reference

#### Query (no signing needed)

```bash
# Check all token balances
tronlink balance --address <address> --network mainnet --json

# Check a specific TRC20 token balance
tronlink balance --address <address> --token <contract> --network mainnet --json

# Check a specific TRC10 token balance
tronlink balance --address <address> --tokenId <id> --network mainnet --json

# Check energy & bandwidth
tronlink resource --address <address> --network mainnet --json
```

#### Transfer (requires signing)

```bash
# TRX
tronlink transfer --type trx --toAddress <to> --amount <amount> --json

# TRC20 (decimals auto-detected)
tronlink transfer --type trc20 --contract <contract> --toAddress <to> --amount <amount> --json

# TRC10 (decimals auto-detected)
tronlink transfer --type trc10 --tokenId <id> --toAddress <to> --amount <amount> --json

# TRC721 NFT
tronlink transfer --type trc721 --contract <contract> --toAddress <to> --tokenId <id> --json
```

#### Trigger Smart Contract

```bash
# Writeable call (opens TronLink for signing)
tronlink trigger --contract <contract> \
  --method 'transfer(address,uint256)' \
  --args '["<to>","<rawAmount>"]' --json

# Constant (read-only) call — returns hex, decode with any Solidity decoder
tronlink trigger --contract <contract> \
  --method 'balanceOf(address)' \
  --args '["<address>"]' --constant --address <address> --json
```

#### Staking

```bash
tronlink stake --amount <amount> --resource energy --json
tronlink unstake --amount <amount> --resource energy --json
tronlink withdraw --json
```

#### Resource Delegation

```bash
tronlink delegate --toAddress <to> --amount <amount> --resource energy --json
tronlink reclaim --fromAddress <from> --amount <amount> --resource energy --json
```

#### Voting

```bash
tronlink vote --votes <addr:count...> --json
tronlink reward --json
```

### Common Token Contracts

| Token | Network | Contract                            |
| ----- | ------- | ----------------------------------- |
| USDT  | mainnet | TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t |
| USDD  | mainnet | TXDk8mbtRbXeYuMNS83CfKPaYYT8XWv9Hz |
| USDC  | mainnet | TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8 |

### Example: AI Transfer Flow

```bash
# 1. Check balance first
tronlink balance --address TNPeeaaFB7K9cmo4uQpcU32zGK8G1NYqeL --network nile --json

# 2. Send 10 TRX (opens browser for signing, wait for return)
tronlink transfer --type trx --toAddress TRecipientAddress --amount 10 --network nile --json

# 3. Verify result — output includes TxID and explorer URL
# { "Status": "Success", "TxID": "abc...", "Explorer": "https://nile.tronscan.org/#/transaction/abc..." }
```

### Notes

- All write commands block until the user approves/rejects in TronLink browser popup
- If the user rejects or the signing times out (5 min), the command exits with an error
- Cancelling a CLI command (Ctrl+C) cancels only that transaction — other queued transactions continue
- Use `--timeout <ms>` to adjust the signing timeout
- Amounts use string-based math internally — no floating point precision issues

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `Signer disconnected (browser closed?)` | The TronLink signer approval tab was closed or lost its connection | Keep the approval tab open for the whole session; re-issue the command — for a write, reconcile on-chain first (see [Errors](#errors)) |
| Command hangs, then `TronLink approval timed out` | Nobody clicked Approve within the window (default 5 min) | Approve faster, or raise `--timeout <ms>`; nothing was signed, re-issuing is safe |
| Signer fails to start / port clash | Another process occupies port `3386` | Pass `--port <n>` — the CLI pins one fixed port to talk to its embedded signer, so the standalone signer's auto-increment behavior does not apply here |
| `Network connection failed` | Connectivity, TronGrid outage, or mainnet rate limiting | Retry with backoff; set `TRON_API_KEY` for mainnet quota |
| Script captures no error output | The error line goes to **stderr**, success JSON to stdout | Capture both streams; branch on exit status + the stderr `error` prefix |
| Read works, write never prompts | Browser not running / not reachable from the CLI host | Writes need a live local browser — see the no-unattended-path note in [Safety](#safety-side-effects) |

## Version & License

- **Package:** `@tronlink/tronlink-cli` v1.0.1
- **License:** MIT — `SPDX-License-Identifier: MIT`
- **Changelog / releases:** [https://github.com/TronLink/tronlink-cli/releases](https://github.com/TronLink/tronlink-cli/releases) — no GitHub-tagged releases yet for v1.0.x; track changes by commit until the first tag.

### Compatibility & migration policy

The CLI is at **v1.0.x**, so standard semver applies — only **major** bumps may break the public surface that scripts depend on.

- **Stable contracts** (won't change in a minor or patch):
    - Subcommand names and their required positional / flag arguments.
    - **Exit status** — `0` success / `1` failure is the public surface today. Splitting `1` into per-class codes would be an additive minor change; treat any nonzero status as failure.
    - **`--json` output keys** — success keys (`Status`, `TxID`, `Explorer`, per-command data keys) and the stderr error line's `status` / `error` keys. New optional fields can be added in a minor; renames / removals are major.
    - The classified `error` message prefixes listed in [Errors](#errors).
- **Volatile contracts** (may change at any time):
    - Human-readable stdout text without `--json`.
    - The exact wording of prompts, banner output, color codes.
    - Log line formats on stderr (parse `--json` instead).
- **`--json` is the automation contract.** If you are scripting against this CLI, always pass `--json` and branch on structured fields. Plain-text output is for humans and will drift across minor releases.
- **Deprecation window.** Deprecated subcommands / flags are kept for at least one minor cycle alongside their replacement; the CLI prints `[DEPRECATED]` to stderr when they are used. Removal lands no earlier than the next major.
- **Verifying after upgrade.** Re-run `tronlink --help` and any subcommand `--help` you depend on; spot-check the `--json` schema for one read and one preview-only write before resuming automation.
