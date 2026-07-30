# TronLink Skills

## Overview

**GitHub**: [https://github.com/TronLink/tronlink-skills](https://github.com/TronLink/tronlink-skills)

**TronLink Wallet Skills** is an AI Agent skill set that provides complete TRON blockchain wallet and DeFi functionality through natural language. Designed for Claude Code, Cursor, OpenCode, Codex CLI, and other AI agents.

**Key Highlights:**
- **6 skills, 40 commands** covering wallet, token research, market data, swaps, resources, staking, and a `health-check` diagnostic
- **Zero npm dependencies** — uses native Node.js 18+ `fetch` and `crypto`; the `crypto` usage is limited to Base58Check address encoding/validation — **no key handling, no signing** (verified against the public v1.1.0: the package contains no signing code path)
- **TRON-specific domain knowledge** — dedicated handling of Energy + Bandwidth resource model
- **Multi-platform support** — Claude Code, Cursor, OpenCode, Codex CLI, LangChain/CrewAI
- **Read-only & safe** — all 40 commands are query-only; no private keys, no signing, anywhere in the package
- **MCP server wrapper** for structured AI agent integration

---

## Why TronLink Skills?

TRON has a fundamentally different fee model than EVM chains. Instead of unified gas, TRON uses **Energy** (for smart contracts) and **Bandwidth** (for all transactions). No existing AI agent skill properly covers:

- TRON's unique resource model and cost optimization strategies
- Stake 2.0 (freezing TRX to obtain resources and earn rewards)
- Super Representative (SR) voting mechanics
- DEX aggregation across SunSwap V2/V3 and Sun.io
- The 14-day unfreezing wait period and its implications

TronLink Skills fills this gap with deep TRON-specific domain knowledge.

---

## Architecture

```text
Natural Language Input
         |
         v
AI Agent (Claude Code / Cursor / OpenCode / Custom)
         |
         v
tron_api.mjs (Node.js 18+, native fetch, zero dependencies)
    ├── Zero npm dependencies
    ├── TronGrid HTTP API (public or with API key) — chain state, balances, resources
    ├── Tronscan API (apilist.tronscanapi.com) — token metadata, transfers, market rows
    ├── SUN.io smart-router API — swap quotes / routes (per-network endpoints)
    └── CoinGecko API — USD price data
         |
         v
Structured JSON → Agent interprets → Natural language response
```

---

## The 6 Skills

### 1. tron-wallet (8 commands)

> Added in 1.1.0 (read-only): `wallet-approvals`, `wallet-overview`.

Wallet queries and account information.

| Command | Description |
|---------|-------------|
| `wallet-balance` | TRX balance and frozen amounts |
| `token-balance` | Check TRC-20 token balance |
| `wallet-tokens` | List all token holdings |
| `tx-history` | Recent transaction history |
| `account-info` | Full account details |
| `validate-address` | Address format validation |

**Features:** Handles both Base58Check (T...) and hex address formats, supports known token symbols, auto-converts decimals.

**When NOT to use:** Sending TRX/tokens — the package has no send capability; use the [signer SDK](tronlink-signer.md) or [MCP Server TronLink](mcp-server-tronlink.md). For deep token-level analytics (rug-pull / liquidity locks), prefer `tron-token`.

### 2. tron-token (8 commands)

> Added in 1.1.0 (read-only): `token-overview`.

Token research and security analysis.

| Command | Description |
|---------|-------------|
| `token-info` | Metadata, supply, issuer, socials |
| `token-search` | Find tokens by name/symbol |
| `contract-info` | ABI, bytecode, verification status |
| `token-holders` | Top holders and holder analysis |
| `trending-tokens` | Highest volume tokens (24h) |
| `token-rankings` | Sort by market cap, volume, holders, gainers/losers |
| `token-security` | Security audit (honeypot, proxy, owner permissions) |

**Features:** Detects rug pulls, analyzes holder concentration, checks liquidity locks.

**When NOT to use:** Per-account balances or transaction history — that's `tron-wallet`. Real-time price/volume — that's `tron-market`.

### 3. tron-market (8 commands)

Real-time market data and whale monitoring.

| Command | Description |
|---------|-------------|
| `token-price` | Current price USD/TRX, 24h change |
| `kline` | OHLCV candlestick data (1m to 1w intervals) |
| `trade-history` | Recent DEX trades |
| `dex-volume` | Buy/sell volume, trade count |
| `whale-transfers` | Large transfers (configurable threshold) |
| `large-transfers` | TRX whale activity |
| `pool-info` | Liquidity pools (SunSwap V2/V3 TVL, APY) |
| `market-overview` | TRON network stats (price, cap, volume, active accounts) |

**Features:** Multi-DEX aggregation, smart money signal detection, K-line analysis.

**When NOT to use:** Quotes or routes for swapping right now — that's `tron-swap` (which factors in slippage). Static token metadata — `tron-token`.

### 4. tron-swap (3 commands)

DEX swap quotes and route optimization.

| Command | Description |
|---------|-------------|
| `swap-quote` | Expected output, price impact, slippage |
| `swap-route` | Optimal route across SunSwap V2/V3, Sun.io (multi-hop) |
| `tx-status` | Track transaction status |

**Features:** Aggregates liquidity from multiple sources, estimates Energy cost, handles multi-hop routes.

**When NOT to use:** Executing the swap — quotes are read-only and there is no execute command; the swap itself goes through [MCP Server TronLink](mcp-server-tronlink.md) (`tl_chain_swap_v3`) or the signer SDK. Historical trade data — `tron-market`.

### 5. tron-resource (9 commands)

> Added in 1.1.0 (read-only): `bandwidth-price`, `tx-cost`, `chain-params`.

Energy & Bandwidth management — TRON-specific.

| Command | Description |
|---------|-------------|
| `resource-info` | Current Energy/Bandwidth available and staked |
| `estimate-energy` | Energy cost for smart contract calls |
| `estimate-bandwidth` | Bandwidth cost (free daily allowance: 600) |
| `energy-price` | Current SUN cost per Energy unit |
| `energy-rental` | Query rental marketplace options |
| `optimize-cost` | Personalized recommendation (freeze vs. rent vs. burn) |

**Features:** Decision tree logic for cost optimization, tracks daily free bandwidth, calculates TRX burn equivalent.

**When NOT to use:** Actually freezing TRX to acquire Energy/Bandwidth — that's a Remote Write; use the signer SDK / MCP Server. SR voting strategy after freezing — see `tron-staking`.

### 6. tron-staking (3 commands)

Stake 2.0 queries and SR information.

| Command | Description |
|---------|-------------|
| `sr-list` | List SRs with votes, block rate, APY |
| `staking-info` | Frozen amount, votes, unclaimed rewards, pending unfreezes |
| `staking-apy` | Calculate estimated annual yield |

**Features:** Stake 2.0 status queries, APY calculation, SR commission tracking.

**When NOT to use:** Performing the freeze/vote/unfreeze actions — those are Remote Writes; route through the signer SDK / MCP Server. Calculating Energy cost per operation — `tron-resource`.

---

## Skill ↔ MCP Tool Map

`scripts/mcp_server.mjs` (the wrapper from [Method 2](#method-2-mcp-server)) exposes **39 of the 40 commands** as MCP tools — every signature, every input field, every output shape is generated from the same `tron_api.mjs` implementation, so the CLI and the MCP tool are guaranteed equivalent. The single CLI-only command (`swap-route`, an alias of `swap-quote`) stays reachable through Method 1 (skill prompt) and Method 3 (direct CLI). Use this table when an agent needs to route a user request to a specific tool or when you're inspecting `tools/list` output.

| Skill | CLI command | MCP tool name | Side effect | Retryable |
|---|---|---|---|:---:|
| `tron-wallet` | `wallet-balance` | `tron_wallet_balance` | Network Read | Yes |
| `tron-wallet` | `token-balance` | `tron_token_balance` | Network Read | Yes |
| `tron-wallet` | `wallet-tokens` | `tron_wallet_tokens` | Network Read | Yes |
| `tron-wallet` | `tx-history` | `tron_tx_history` | Network Read | Yes |
| `tron-wallet` | `account-info` | `tron_account_info` | Network Read | Yes |
| `tron-wallet` | `validate-address` | `tron_validate_address` | Local (pure) | Yes |
| `tron-token` | `token-info` | `tron_token_info` | Network Read | Yes |
| `tron-token` | `token-search` | `tron_token_search` | Network Read | Yes |
| `tron-token` | `contract-info` | `tron_contract_info` | Network Read | Yes |
| `tron-token` | `token-holders` | `tron_token_holders` | Network Read | Yes |
| `tron-token` | `trending-tokens` | `tron_trending_tokens` | Network Read | Yes |
| `tron-token` | `token-rankings` | `tron_token_rankings` | Network Read | Yes |
| `tron-token` | `token-security` | `tron_token_security` | Network Read | Yes |
| `tron-market` | `token-price` | `tron_token_price` | Network Read | Yes |
| `tron-market` | `kline` | `tron_kline` | Network Read | Yes |
| `tron-market` | `trade-history` | `tron_trade_history` | Network Read | Yes |
| `tron-market` | `dex-volume` | `tron_dex_volume` | Network Read | Yes |
| `tron-market` | `whale-transfers` | `tron_whale_transfers` | Network Read | Yes |
| `tron-market` | `large-transfers` | `tron_large_transfers` | Network Read | Yes |
| `tron-market` | `pool-info` | `tron_pool_info` | Network Read | Yes |
| `tron-market` | `market-overview` | `tron_market_overview` | Network Read | Yes |
| `tron-swap` | `swap-quote` | `tron_swap_quote` | Network Read | Yes |
| `tron-swap` | `swap-route` | — _(CLI-only alias of `swap-quote`)_ | Network Read | Yes |
| `tron-swap` | `tx-status` | `tron_tx_status` | Network Read | Yes |
| `tron-resource` | `resource-info` | `tron_resource_info` | Network Read | Yes |
| `tron-resource` | `estimate-energy` | `tron_estimate_energy` | Network Read | Yes |
| `tron-resource` | `estimate-bandwidth` | `tron_estimate_bandwidth` | Network Read | Yes |
| `tron-resource` | `energy-price` | `tron_energy_price` | Network Read | Yes |
| `tron-resource` | `energy-rental` | `tron_energy_rental` | Network Read | Yes |
| `tron-resource` | `optimize-cost` | `tron_optimize_cost` | Network Read | Yes |
| `tron-staking` | `sr-list` | `tron_sr_list` | Network Read | Yes |
| `tron-staking` | `staking-info` | `tron_staking_info` | Network Read | Yes |
| `tron-staking` | `staking-apy` | `tron_staking_apy` | Network Read | Yes |

**Totals.** 40 CLI commands · 39 MCP tools · 1 CLI-only command (`swap-route`, an alias of `swap-quote`). 1.1.0 additions not yet detailed in the table above (all Network Read, exposed as `tron_<command>`): `wallet-approvals`, `wallet-overview`, `token-overview`, `bandwidth-price`, `tx-cost`, `chain-params`, `health-check`. Every command is read-only — no signing, no broadcast, no fund movement (verified against the public v1.1.0). To execute a transaction, route to [MCP Server TronLink](mcp-server-tronlink.md) (`tl_chain_*`) or [signer SDK](tronlink-signer.md) (`sendTrx`, `sendTrc20`, `sign*`).

### Intent → Skill → Tool Routing

Pick a skill first by the **kind of question**, then a command by the **field the user asked about**. Common intents:

| User says (intent) | Skill | Command / MCP tool |
|---|---|---|
| "What's the TRX balance of T…?" / "How many tokens in this wallet?" | `tron-wallet` | `wallet-balance` · `tron_wallet_balance` |
| "Is `Tabcd…` a valid TRON address?" | `tron-wallet` | `validate-address` · `tron_validate_address` |
| "Show recent transactions for T…" | `tron-wallet` | `tx-history` · `tron_tx_history` |
| "Is this token safe / a honeypot?" | `tron-token` | `token-security` · `tron_token_security` |
| "Who are the top holders of USDT?" | `tron-token` | `token-holders` · `tron_token_holders` |
| "What's the contract ABI of …?" | `tron-token` | `contract-info` |
| "What are the top-volume tokens today?" | `tron-token` | `trending-tokens` · `tron_trending_tokens` |
| "What's TRX / USDT price?" | `tron-market` | `token-price` · `tron_token_price` |
| "Show 1h K-line for SUN" | `tron-market` | `kline` · `tron_kline` |
| "Recent SunSwap trades for USDT?" | `tron-market` | `trade-history` |
| "What's the TVL of SUN/TRX pool?" | `tron-market` | `pool-info` |
| "How much USDT will I get for 100 TRX?" | `tron-swap` | `swap-quote` · `tron_swap_quote` |
| "What's the cheapest route TRX → JST?" | `tron-swap` | `swap-route` (CLI only) |
| "Did transaction `0xabc…` succeed?" | `tron-swap` | `tx-status` · `tron_tx_status` |
| "How much Energy / Bandwidth do I have?" | `tron-resource` | `resource-info` · `tron_resource_info` |
| "Should I freeze, rent, or burn?" | `tron-resource` | `optimize-cost` · `tron_optimize_cost` |
| "How much Energy does a USDT transfer cost?" | `tron-resource` | `estimate-energy` · `tron_estimate_energy` |
| "Where can I rent Energy?" | `tron-resource` | `energy-rental` |
| "List the current Super Representatives" | `tron-staking` | `sr-list` · `tron_sr_list` |
| "What's my staking position?" | `tron-staking` | `staking-info` · `tron_staking_info` |
| "If I stake 10000 TRX, what's my APY?" | `tron-staking` | `staking-apy` · `tron_staking_apy` |

If the request implies **changing on-chain state** (transfer, swap execution, freeze, vote, claim), this skill set is the wrong layer — see the routing notes under each skill's "When NOT to use".

### ❌ When NOT to route here (negative examples)

Skills are **read-only**. If the user intent implies a signed / Remote Write action, do **not** dispatch to a skill — the underlying command will succeed but only as a query/estimate, and the user's actual goal will go unfulfilled. Route to the signer SDK or `mcp-server-tronlink` instead:

| User says (intent) | ❌ Wrong route (looks plausible, but read-only) | ✅ Correct route |
|---|---|---|
| "Send 100 TRX to `T…`" | `tron-wallet wallet-balance` then stop — this only checks the balance, never sends. | [signer SDK](tronlink-signer.md) `sendTrx` (HITL) or [`mcp-server-tronlink`](mcp-server-tronlink.md) `tl_chain_send` |
| "Freeze 1000 TRX to get Energy" | `tron-resource optimize-cost` — this only computes the recommendation. | `mcp-server-tronlink` `tl_chain_stake` (Remote Write — Direct-API signs with the agent-wallet, password-gated rather than browser-HITL) |
| "Vote 5000 votes for SR `T…`" | `tron-staking sr-list` — only reads the SR list, no vote is cast. | `mcp-server-tronlink` `tl_chain_stake` / signer SDK `signTransaction` |
| "Approve USDT spending for the SunSwap router" | `tron-token token-info` / `contract-info` — pure metadata, no approval is broadcast. | [signer SDK](tronlink-signer.md) `signTransaction` or `mcp-server-tronlink` `tl_chain_send` |
| "Swap 100 TRX for USDT now" | `tron-swap swap-quote` — only quotes price, never executes. | `mcp-server-tronlink` `tl_chain_swap_v3` **for TRC20-input swaps only** — TRX-input swaps are unusable in its 0.1.1 (known bug, see its Swap safety); for TRX→token use the [signer SDK](tronlink-signer.md) `signTransaction` with a router call. Always pass `slippage` explicitly; there is no min-out parameter |
| "Claim my staking rewards" | `tron-staking staking-info` — only shows the pending balance. | `mcp-server-tronlink` `tl_chain_stake` (withdraw / claim) or signer SDK |

**Heuristic.** If the user's verb is *send / freeze / unfreeze / vote / unvote / approve / swap (execute) / claim / sign / broadcast*, the answer never starts in this Skills set. Skills can still **precede** the write (quote, estimate cost, validate address, check balance) — just don't claim a Skills call finished the user's request.

---

## Recommended Skill Workflows

### Balance & Token Check
```text
tron-wallet (check balance) → tron-wallet (list tokens) → tron-resource (check energy status)
```

### Research & Swap Quote
```text
tron-token (search) → tron-market (price/chart) → tron-resource (check energy) → tron-swap (get quote)
```

### Staking Analysis
```text
tron-wallet (check balance) → tron-staking (staking info) → tron-staking (APY estimate) → tron-staking (SR list)
```

### Resource Optimization
```text
tron-resource (check status) → tron-resource (estimate cost) → tron-resource (optimize-cost)
```

---

## TRON Resource Model Reference

### Energy vs. Bandwidth

| Resource | Consumed By | Free Allowance | How to Get |
|----------|-------------|----------------|------------|
| **Bandwidth** | ALL transactions | 600/day | Freeze TRX or burn TRX |
| **Energy** | Smart contracts only | None | Freeze TRX, rent, or burn TRX |

### Cost Examples

> **Effective as of 2026-05.** Energy figures shift with contract upgrades (notably USDT TRC-20) and network parameters; the bandwidth/energy unit prices used to derive the TRX-burned column also change. Treat these as **order-of-magnitude reference**, not contractual values. Source: TronGrid / Tronscan transaction samples and TRON network parameters. For runtime accuracy, call the `tron-resource` skill's `estimate-energy` / `estimate-bandwidth` commands.

| Operation | Bandwidth | Energy | TRX Burned (no resources) |
|-----------|-----------|--------|---------------------------|
| TRX transfer | ~267 | 0 | 0 (within free limit) |
| USDT transfer | ~345 | ~65,000 | ~13-27 TRX |
| SunSwap swap | ~345 | ~65,000-200,000 | ~13-40 TRX |
| Token approve | ~345 | ~30,000 | ~6-12 TRX |

### Stake 2.0 Key Facts
- Freeze TRX → Get Energy or Bandwidth → Vote for SR → Earn rewards
- Unfreezing has **14-day wait** before withdrawal
- Votes reset if you unfreeze; must re-vote after re-freezing
- 1 frozen TRX ≈ 4.5 Energy/day — **dynamic**: depends on total network stake; use `tron-resource estimate-energy` for the live value. Effective figure as of 2026-05.
- Voting rewards claimable every 6 hours

---

## Which Mode to Use

| You are… | Use | Why |
| --- | --- | --- |
| In Claude Code, want zero setup | Method 1 (skills auto-discovery) | Full 40-command surface, no registration |
| In Claude Desktop / an MCP-only client | Method 2 (MCP server) | 39 tools over MCP; only `swap-route` (a `swap-quote` alias) unavailable |
| Scripting / CI, no agent involved | Method 3 (direct CLI) | Plain `node` invocations, `--json`-style structured output |
| About to **sign or move funds** | Not this package — [signer SDK](tronlink-signer.md), [`mcp-server-tronlink`](mcp-server-tronlink.md), or [CLI](tronlink-cli.md) | Skills are strictly read-only |

## Integration Methods

### Method 1: Claude Code (Recommended)

```bash
# Clone and use directly
git clone https://github.com/TronLink/tronlink-skills.git
# or the one-line installer (installs to ~/.tronlink-skills and registers the MCP server):
#   curl -sSL https://raw.githubusercontent.com/TronLink/tronlink-skills/main/install.sh | sh
cd tronlink-skills
claude   # Auto-discovers SKILL.md files
```

No `npm install` needed for read-only operations.

### Method 2: MCP Server

```bash
# Register as MCP server
claude mcp add tronlink-skills -- node /path/to/tronlink-skills/scripts/mcp_server.mjs   # the directory cloned in Method 1

# Provides 39 MCP tools callable by Claude Desktop / Claude Code
# (see "Skill ↔ MCP Tool Map" above for the per-command mapping; only swap-route is CLI-only)
```

Claude Desktop (`claude_desktop_config.json`) equivalent:

```json
{
  "mcpServers": {
    "tronlink-skills": {
      "command": "node",
      "args": ["/absolute/path/to/tronlink-skills/scripts/mcp_server.mjs"]
    }
  }
}
```

> **MCP-mode coverage.** 39 of the 40 commands are exposed over MCP as `tron_<command>`; only `swap-route` (an alias of `swap-quote`) is CLI-only, via Method 1 (skills) or Method 3 (direct CLI).

### Method 3: Manual CLI

```bash
# Direct command execution
node scripts/tron_api.mjs wallet-balance --address TAddress...
node scripts/tron_api.mjs token-price --token USDT
node scripts/tron_api.mjs swap-quote --from TRX --to USDT --amount 100
```

### Method 4: Other AI Platforms

| Platform | Integration |
|----------|-------------|
| **Cursor / Windsurf** | Clone repo, use MCP or direct skill reading |
| **Codex CLI** | Symlink to `~/.agents/skills/tronlink-skills` |
| **OpenCode** | Register plugin, symlink skills |
| **LangChain / CrewAI** | Wrap `tron_api.mjs` as a Tool |

#### Cursor (or Windsurf, same schema)

`~/.cursor/mcp.json`:

```jsonc
{
  "mcpServers": {
    "tronlink-skills": {
      "command": "node",
      "args": ["/absolute/path/to/tronlink-skills/scripts/mcp_server.mjs"]
    }
  }
}
```

#### Codex CLI

```bash
# Symlink the skills bundle into the agent's discovery path
ln -s "$(pwd)/tronlink-skills" ~/.agents/skills/tronlink-skills
# Verify discovery
codex skills list | grep tron
```

#### OpenCode

`~/.config/opencode/config.json`:

```jsonc
{
  "plugins": {
    "tronlink-skills": { "path": "/absolute/path/to/tronlink-skills" }
  }
}
```

#### LangChain / CrewAI (Python)

```python
from langchain_core.tools import Tool
import subprocess, json

def tron_call(cmd: str) -> dict:
    out = subprocess.check_output(
        ["node", "scripts/tron_api.mjs", *cmd.split()],
        cwd="/absolute/path/to/tronlink-skills",
    )
    return json.loads(out)

tron_wallet_balance = Tool.from_function(
    func=lambda addr: tron_call(f"wallet-balance --address {addr}"),
    name="tron_wallet_balance",
    description="TRX balance and frozen amounts. Address is a TRON Base58 (T...) string.",
)
```

### Quick Setup Script

```bash
# Auto-install for all AI environments
bash install.sh

# Clean uninstall
bash uninstall.sh
```

---

## Configuration

### Environment Variables

```bash
# Optional: TronGrid API key for higher rate limits
export TRONGRID_API_KEY="your-api-key"

# Optional: Tronscan API key — higher rate limits for metadata/market queries
export TRONSCAN_API_KEY="your-api-key"

# Optional: Switch network (default: mainnet)
export TRON_NETWORK="mainnet"    # or "shasta" / "nile"
```

### Network Support

| Network | URL | Use Case |
|---------|-----|----------|
| Mainnet | https://api.trongrid.io | Production |
| Shasta | https://api.shasta.trongrid.io | Testing |
| Nile | https://nile.trongrid.io | Testing |

### Built-In Token Shortcuts

| Symbol | Contract Address |
|--------|------------------|
| TRX | Native (no contract) |
| USDT | TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t |
| USDC | TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8 |
| WTRX | TNUC9Qb1rRpS5CbWLmNMxXBjyFoydXjWFR |
| BTT | TAFjULxiVgT4qWk6UZwjqwZXTSaGaqnVp4 |
| JST | TCFLL5dx5ZJdKnWuesXxi1VPwjLVmWZZy9 |
| SUN | TSSMHYeV2uE9qYH95DqyoCuNCzEL1NvU3S |
| WIN | TLa2f6VPqDgRE67v1736s7bJ8Ray5wYjU7 |

---

### Credential hygiene

`TRONGRID_API_KEY` / `TRONSCAN_API_KEY` are optional (public endpoints work unauthenticated at lower rate limits). When set, keep them in the environment or the host's secret manager — never commit them to a repo or an agent-readable config; both are sent only as request headers to their respective APIs and are never echoed in command output.

## Project Structure

```text
tronlink-skills/
├── README.md                          # Main documentation
├── package.json                       # Node.js manifest
├── install.sh                         # Auto-install for all AI environments
├── uninstall.sh                       # Clean uninstall
│
├── scripts/
│   ├── tron_api.mjs                   # Main CLI (40 commands, zero dependencies)
│   └── mcp_server.mjs                 # MCP protocol server wrapper
│
├── skills/                            # Skill definitions (auto-discovered)
│   ├── tron-wallet/SKILL.md
│   ├── tron-token/SKILL.md
│   ├── tron-market/SKILL.md
│   ├── tron-swap/SKILL.md
│   ├── tron-resource/SKILL.md
│   └── tron-staking/SKILL.md
│
├── docs/
│   ├── claude-integration-guide.md    # 3 integration methods
│   ├── resource-model.md              # Energy & Bandwidth deep dive
│   ├── staking-guide.md               # Stake 2.0 & APY explanation
│   └── integration-guide.sh
│
├── .claude-plugin/                    # Claude Code plugin config
├── .cursor-plugin/                    # Cursor IDE plugin config
├── .opencode/                         # OpenCode config
├── .codex/                            # Codex CLI setup
├── .claude/                           # Pre-configured test commands
├── _meta.json                         # Metadata for skill registries
└── LICENSE                            # MIT
```

---

## Dependencies

| Dependency | Required? | Purpose |
|------------|-----------|---------|
| Node.js >= 18 | Yes | Runtime (native fetch, crypto) |
| npm install | Not needed | All operations work without any npm dependencies |

---

## Data Sources & Freshness

All data is fetched **live at query time** from the public APIs above — there is no local database and no background sync. The only in-process cache is TRC20 token metadata (symbol/name/decimals), held for the lifetime of one script invocation. Consequences for agents:

- Prices, K-lines, DEX volume, and pool TVL/APY are as fresh as the upstream API (Tronscan / SUN.io / CoinGecko) at call time — quote **immediately** before acting on a number, and never treat an earlier answer as current.
- Different commands may draw the same figure from different upstreams; small discrepancies between sources are normal, not a bug.
- Queried addresses are sent to these public APIs as URL parameters; nothing is persisted locally, but treat the query itself as visible to those services.

## Security Model

| Aspect | Implementation |
|--------|----------------|
| Read-only design | All 40 commands are queries — no private keys, no signing, no fund movements (verified against the public v1.1.0 source) |
| Side effects | Every command is **Network Read**: it calls public APIs but changes no state. All commands are safe to retry; no human-in-the-loop confirmation is needed |
| No secrets required | Only optional TRONGRID_API_KEY for higher rate limits |
| Rate limits | Public TronGrid API; use TRONGRID_API_KEY for higher limits |
| Error handling | Failures are query errors: rate limit (retryable, back off), network errors (retryable), invalid address/parameters (not retryable — fix the input). To execute a transaction (transfer, swap, stake), use the [signer SDK](tronlink-signer.md) or [MCP Server TronLink](mcp-server-tronlink.md) — these skills never sign or broadcast |

---

## Address Format Support

Both formats are supported and auto-normalized across all commands:

| Format | Example | Description |
|--------|---------|-------------|
| Base58Check | `T...` (34 chars) | Standard display format |
| Hex | `41...` (42 hex chars) | Internal representation |

---

## Key Design Decisions

1. **Zero Dependencies** — No npm install required, making it lightweight and instant for AI agents
2. **Read-Only & Safe** — All commands are queries only, no private keys or signing involved
3. **TRON-Specific Domain Knowledge** — Dedicated skills for Energy/Bandwidth and Stake 2.0, acknowledging TRON's unique architecture
4. **Multi-Format Address Support** — Handles both Base58Check and hex formats transparently
5. **Token Symbol Resolution** — Common tokens have built-in shortcuts; unknown contracts work by address
6. **Cost Optimization Recommendations** — The `optimize-cost` command provides personalized strategies
7. **MCP Server Wrapper** — Provides structured integration for Claude Desktop and modern AI agents

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/TronLink/tronlink-skills.git
cd tronlink-skills

# 2. Use with Claude Code (no install needed for reads)
claude
> "What's the TRX balance of TAddress...?"
> "Show me the top trending tokens on TRON"
> "How much Energy do I need to send USDT?"
> "What's the best way to get Energy — freeze, rent, or burn?"

# 3. Or use directly
node scripts/tron_api.mjs wallet-balance --address TAddress...
node scripts/tron_api.mjs token-price --token USDT
node scripts/tron_api.mjs optimize-cost --address TAddress...
```

## Version & License

- **Package:** `tronlink-skills` v1.1.0 — public repo `package.json`; not published to npm, install via `install.sh` or a plain clone. Docs verified against commit `7b37eaf0`.
- **License:** MIT — `SPDX-License-Identifier: MIT`
- **Changelog / releases:** [https://github.com/TronLink/tronlink-skills/releases](https://github.com/TronLink/tronlink-skills/releases) — no GitHub-tagged releases yet; track changes by commit until the first tag.

### Compatibility & migration policy

Skills are at **v1.0.x**, so standard semver applies — only **major** bumps may break the public surface.

- **Stable contracts** (won't change in a minor or patch):
    - The 40 CLI command names and their required / optional flags (`tron_api.mjs <command> [...]`).
    - The 39 MCP tool names (`tron_*` form) and their `inputSchema` keys — see [Skill ↔ MCP Tool Map](#skill-mcp-tool-map).
    - Exit codes: `0` success, `1` query error / invalid input, `2` unsupported / unknown command.
    - The **Network Read** side-effect classification — no command will ever become a Remote Write without a major bump.
- **Volatile contracts** (may change in a minor):
    - The exact field layout of JSON `stdout` payloads — new fields can be added in any minor; renames or removals are major. Use a tolerant parser.
    - Built-in token-symbol shortcut list (`USDT`, `USDC`, `WTRX`, …) — symbols may be added in any minor; existing mappings won't be repointed in a minor.
    - Heuristics and thresholds (`whale-transfers` default cutoff, `optimize-cost` decision tree weights, etc.).
- **Subset relationship.** The MCP tool subset (currently 39 of 40) may **grow** in a minor (a previously CLI-only command exposed as an MCP tool); it will not **shrink** in a minor.
- **Deprecation window.** A command / tool marked deprecated continues to work for at least one minor cycle; the runtime prints a `STDERR: [DEPRECATED]` warning. Removal lands no earlier than the next major.
- **Verifying after upgrade.** Re-run `tron_api.mjs --help` and (if using MCP) `tools/list` to confirm the names you depend on are still present. The MCP `serverInfo.version` exposed during `initialize` should match the bumped `package.json` version.
