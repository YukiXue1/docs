# TronLink Skills

## 概述

**GitHub**: [https://github.com/TronLink/tronlink-skills](https://github.com/TronLink/tronlink-skills)

> **版本范围。** 本页的命令说明（6 大技能、33 个命令）基于 **v1.0.x** 编写。默认分支（即 `git clone` 和 `install.sh` 安装的版本）现为 **v1.1.0**（commit `b12b5868`）：新增 7 个只读命令（共 40 个），并要求精确版本 **Node.js 24.22.3**。详见文末「版本与许可证」；以你本地安装版本的 `tron_api.mjs --help` / MCP `tools/list` 为准。

**TronLink Wallet Skills** 是一套 AI Agent 技能集，通过自然语言提供完整的 TRON 区块链钱包和 DeFi 功能。专为 Claude Code、Cursor、OpenCode、Codex CLI 及其他 AI 代理设计。

**核心亮点：**
- **6 大技能，33 个命令**，涵盖钱包、代币研究、市场数据、兑换、资源和质押
- **零 npm 依赖**：使用原生 Node.js `fetch` 和 `crypto`（要求精确版本 Node.js 24.22.3，见下方「依赖项」），无需 `npm install`
- **TRON 专属领域知识** — 专门处理能量 + 带宽资源模型
- **多平台支持** — Claude Code、Cursor、OpenCode、Codex CLI、LangChain/CrewAI
- **纯只读安全设计**：所有命令均为查询操作，不涉及私钥或签名
- **MCP 服务封装**：为结构化 AI 代理集成提供标准接口

---

## 为什么需要 TronLink Skills？

TRON 的费用模型与 EVM 链有根本性不同。TRON 不使用统一的 Gas，而是使用**能量**（用于智能合约）和**带宽**（用于所有交易）。现有的 AI Agent 技能集均未覆盖：

- TRON 独特的资源模型和成本优化策略
- Stake 2.0（冻结 TRX 获取资源并赚取奖励）
- 超级代表（SR）投票机制
- 跨 SunSwap V2/V3 和 Sun.io 的 DEX 聚合
- 14 天解冻等待期及其影响

TronLink Skills 以深度 TRON 领域知识填补了这一空白。

---

## 架构设计

```text
自然语言输入
         |
         v
AI 代理 (Claude Code / Cursor / OpenCode / 自定义)
         |
         v
tron_api.mjs (Node.js 24.22.3, 原生 fetch, 零依赖)
    ├── 零 npm 依赖
    ├── TronGrid HTTP API（公共或带 API Key）
    └── Tronscan API 用于代币元数据
         |
         v
结构化 JSON → Agent 解读 → 自然语言回复
```

---

## 6 大技能详解

### 1. tron-wallet（6 个命令）

钱包查询与账户信息。

| 命令 | 说明 |
|------|------|
| `wallet-balance` | TRX 余额和冻结金额 |
| `token-balance` | 查询 TRC-20 代币余额 |
| `wallet-tokens` | 列出所有代币持仓 |
| `tx-history` | 最近交易历史 |
| `account-info` | 完整账户详情 |
| `validate-address` | 地址格式验证 |

**特点：** 同时支持 Base58Check（T...）和 hex 地址格式，内置常用代币符号，自动转换精度。

**何时不要用：** 转出 TRX 或 TRC-20 代币并由用户在浏览器中批准时，使用 [Signer SDK](tronlink-signer.zh.md) 的 `sendTrx` 或 `sendTrc20`。使用本地 agent 钱包时，调用 [mcp-server-tronlink](mcp-server-tronlink.zh.md) 的 `tl_chain_send`。代币风险与流动性分析使用 `tron-token`。

### 2. tron-token（7 个命令）

代币研究与安全分析。

| 命令 | 说明 |
|------|------|
| `token-info` | 元数据、发行量、发行方、社交链接 |
| `token-search` | 按名称/符号搜索代币 |
| `contract-info` | ABI、字节码、验证状态 |
| `token-holders` | 顶级持有者和持有者分析 |
| `trending-tokens` | 24 小时最高交易量代币 |
| `token-rankings` | 按市值、交易量、持有者、涨跌幅排序 |
| `token-security` | 安全审计（蜜罐、代理、所有者权限） |

**特点：** 检测 Rug Pull、分析持有者集中度、检查流动性锁定。

**何时不要用：** 单账户余额或交易历史——那是 `tron-wallet` 的活；实时价格/成交量——那是 `tron-market` 的活。

### 3. tron-market（8 个命令）

实时市场数据和巨鲸监控。

| 命令 | 说明 |
|------|------|
| `token-price` | 当前 USD/TRX 价格，24 小时变化 |
| `kline` | OHLCV K 线数据（1 分钟到 1 周） |
| `trade-history` | 最近 DEX 交易 |
| `dex-volume` | 买卖量、交易笔数 |
| `whale-transfers` | 大额转账（可配置阈值） |
| `large-transfers` | TRX 巨鲸活动 |
| `pool-info` | 流动性池（SunSwap V2/V3 TVL、APY） |
| `market-overview` | TRON 网络统计（价格、市值、交易量、活跃账户） |

**特点：** 多 DEX 聚合、智能资金信号检测、K 线分析。

**何时不要用：** 立刻执行 swap 报价或路径——那是 `tron-swap`（会算上滑点）；静态代币元数据——`tron-token`。

### 4. tron-swap（3 个命令）

DEX 兑换报价与路由优化。

| 命令 | 说明 |
|------|------|
| `swap-quote` | 预期产出、价格影响、滑点 |
| `swap-route` | 跨 SunSwap V2/V3、Sun.io 的最优路径（含多跳） |
| `tx-status` | 追踪交易状态 |

**特点：** 聚合多源流动性、估算能量成本、处理多跳路由。

**何时不要用：** 执行兑换时，调用 [mcp-server-tronlink](mcp-server-tronlink.zh.md) 的 `tl_chain_swap_v3`，将 `action` 设为 `"execute"`，并按用户确认的滑点百分比填写 `slippage`。历史成交数据使用 `tron-market`。

### 5. tron-resource（6 个命令）

能量与带宽管理 — TRON 专属。

| 命令 | 说明 |
|------|------|
| `resource-info` | 当前可用能量/带宽及已质押量 |
| `estimate-energy` | 智能合约调用的能量成本 |
| `estimate-bandwidth` | 带宽成本（每日免费额度：600） |
| `energy-price` | 当前每单位能量的 SUN 成本 |
| `energy-rental` | 查询租赁市场选项 |
| `optimize-cost` | 个性化建议（冻结 vs. 租赁 vs. 燃烧） |

**特点：** 成本优化决策树逻辑、追踪每日免费带宽、计算 TRX 燃烧等值。

**何时不要用：** 冻结 TRX 获取能量或带宽时，调用 [mcp-server-tronlink](mcp-server-tronlink.zh.md) 的 `tl_chain_stake`，将 `action` 设为 `"freeze"`。投票前查询超级代表信息可使用 `tron-staking`。

### 6. tron-staking（3 个命令）

Stake 2.0 查询与 SR 信息。

| 命令 | 说明 |
|------|------|
| `sr-list` | SR 列表，含投票数、出块率、APY |
| `staking-info` | 冻结金额、投票、未领奖励、待解冻 |
| `staking-apy` | 计算预估年化收益率 |

**特点：** Stake 2.0 状态查询、APY 计算、SR 佣金追踪。

**何时不要用：** 投票使用 [TronLink CLI](tronlink-cli.zh.md) 的 `tronlink vote`，领取投票奖励使用同一 CLI 的 `tronlink reward`。冻结或解冻 TRX 使用 [mcp-server-tronlink](mcp-server-tronlink.zh.md) 的 `tl_chain_stake`。估算能量消耗使用 `tron-resource`。

---

<a id="skill-mcp-tool-map"></a>

## Skill ↔ MCP 工具映射

在 v1.0.x 命令集中，`scripts/mcp_server.mjs` 将 **33 个 CLI 命令中的 25 个** 暴露为 MCP 工具。包装层运行对应的 CLI 命令，以文本形式返回 MCP 工具结果。其余 8 个命令可通过 Skills 或 CLI 使用。

| Skill | CLI 命令 | MCP 工具名 | 副作用 | 可重试 |
|---|---|---|---|:---:|
| `tron-wallet` | `wallet-balance` | `tron_wallet_balance` | Network Read | 可 |
| `tron-wallet` | `token-balance` | `tron_token_balance` | Network Read | 可 |
| `tron-wallet` | `wallet-tokens` | `tron_wallet_tokens` | Network Read | 可 |
| `tron-wallet` | `tx-history` | `tron_tx_history` | Network Read | 可 |
| `tron-wallet` | `account-info` | `tron_account_info` | Network Read | 可 |
| `tron-wallet` | `validate-address` | `tron_validate_address` | Local（纯函数） | 可 |
| `tron-token` | `token-info` | `tron_token_info` | Network Read | 可 |
| `tron-token` | `token-search` | `tron_token_search` | Network Read | 可 |
| `tron-token` | `contract-info` | — _(仅 CLI)_ | Network Read | 可 |
| `tron-token` | `token-holders` | `tron_token_holders` | Network Read | 可 |
| `tron-token` | `trending-tokens` | `tron_trending_tokens` | Network Read | 可 |
| `tron-token` | `token-rankings` | `tron_token_rankings` | Network Read | 可 |
| `tron-token` | `token-security` | `tron_token_security` | Network Read | 可 |
| `tron-market` | `token-price` | `tron_token_price` | Network Read | 可 |
| `tron-market` | `kline` | `tron_kline` | Network Read | 可 |
| `tron-market` | `trade-history` | — _(仅 CLI)_ | Network Read | 可 |
| `tron-market` | `dex-volume` | — _(仅 CLI)_ | Network Read | 可 |
| `tron-market` | `whale-transfers` | `tron_whale_transfers` | Network Read | 可 |
| `tron-market` | `large-transfers` | — _(仅 CLI)_ | Network Read | 可 |
| `tron-market` | `pool-info` | — _(仅 CLI)_ | Network Read | 可 |
| `tron-market` | `market-overview` | `tron_market_overview` | Network Read | 可 |
| `tron-swap` | `swap-quote` | `tron_swap_quote` | Network Read | 可 |
| `tron-swap` | `swap-route` | — _(仅 CLI)_ | Network Read | 可 |
| `tron-swap` | `tx-status` | `tron_tx_status` | Network Read | 可 |
| `tron-resource` | `resource-info` | `tron_resource_info` | Network Read | 可 |
| `tron-resource` | `estimate-energy` | `tron_estimate_energy` | Network Read | 可 |
| `tron-resource` | `estimate-bandwidth` | — _(仅 CLI)_ | Network Read | 可 |
| `tron-resource` | `energy-price` | `tron_energy_price` | Network Read | 可 |
| `tron-resource` | `energy-rental` | — _(仅 CLI)_ | Network Read | 可 |
| `tron-resource` | `optimize-cost` | `tron_optimize_cost` | Network Read | 可 |
| `tron-staking` | `sr-list` | `tron_sr_list` | Network Read | 可 |
| `tron-staking` | `staking-info` | `tron_staking_info` | Network Read | 可 |
| `tron-staking` | `staking-apy` | `tron_staking_apy` | Network Read | 可 |

上表涵盖 v1.0.x 的 33 个只读 CLI 命令，其中 25 个也可通过 MCP 调用。需要发起交易时，按下方路由示例选择工具。

### 用户提问 → Skill → 工具路由

先按"问的是什么类"挑 skill，再按"问的是哪个字段"挑命令。常见提问对照：

| 用户提问（意图） | Skill | 命令 / MCP 工具 |
|---|---|---|
| 「T… 这个地址有多少 TRX？」/「钱包里有什么代币？」 | `tron-wallet` | `wallet-balance` · `tron_wallet_balance` |
| 「`Tabcd…` 是合法的 TRON 地址吗？」 | `tron-wallet` | `validate-address` · `tron_validate_address` |
| 「T… 最近的交易？」 | `tron-wallet` | `tx-history` · `tron_tx_history` |
| 「这个代币安全吗 / 是不是蜜罐？」 | `tron-token` | `token-security` · `tron_token_security` |
| 「USDT 的大户是谁？」 | `tron-token` | `token-holders` · `tron_token_holders` |
| 「这个合约的 ABI 是？」 | `tron-token` | `contract-info`（仅 CLI） |
| 「今日成交量最高的代币？」 | `tron-token` | `trending-tokens` · `tron_trending_tokens` |
| 「TRX / USDT 现在价格？」 | `tron-market` | `token-price` · `tron_token_price` |
| 「SUN 的 1 小时 K 线」 | `tron-market` | `kline` · `tron_kline` |
| 「SunSwap 上 USDT 的最近成交？」 | `tron-market` | `trade-history`（仅 CLI） |
| 「SUN/TRX 池子的 TVL 是多少？」 | `tron-market` | `pool-info`（仅 CLI） |
| 「100 TRX 可以换多少 USDT？」 | `tron-swap` | `swap-quote` · `tron_swap_quote` |
| 「TRX → JST 最便宜的路径是？」 | `tron-swap` | `swap-route`（仅 CLI） |
| 「交易 `0xabc…` 成功了吗？」 | `tron-swap` | `tx-status` · `tron_tx_status` |
| 「我还有多少能量 / 带宽？」 | `tron-resource` | `resource-info` · `tron_resource_info` |
| 「我应该冻结、租赁还是燃烧？」 | `tron-resource` | `optimize-cost` · `tron_optimize_cost` |
| 「一笔 USDT 转账要多少能量？」 | `tron-resource` | `estimate-energy` · `tron_estimate_energy` |
| 「在哪租能量？」 | `tron-resource` | `energy-rental`（仅 CLI） |
| 「现在 SR 列表」 | `tron-staking` | `sr-list` · `tron_sr_list` |
| 「我的质押状态？」 | `tron-staking` | `staking-info` · `tron_staking_info` |
| 「质押 10000 TRX 的 APY 是多少？」 | `tron-staking` | `staking-apy` · `tron_staking_apy` |

若意图涉及**改变链上状态**（转账、执行 swap、freeze、投票、领奖），说明这里已不是合适的入口——请回看每个 skill 的"何时不要用"小节。

### ❌ 不要走这里（反例）

Skills 提供查询和估算。涉及签名或广播时，按下表选择工具。[TronLink CLI](tronlink-cli.zh.md) 和 signer SDK 通过浏览器请求用户批准。MCP Server 的直连链上工具使用本地 agent 钱包签名，宿主应用须在调用前取得用户确认。

| 用户提问（意图） | ❌ 误路由（看起来合理，但只读） | ✅ 正确路由 |
|---|---|---|
| 「给 `T…` 转 100 TRX」 | `tron-wallet wallet-balance` 就停下——只查了余额，没转。 | [signer SDK](tronlink-signer.zh.md) `sendTrx`（HITL）或 [`mcp-server-tronlink`](mcp-server-tronlink.zh.md) `tl_chain_send` |
| 「冻 1000 TRX 换能量」 | `tron-resource optimize-cost`——只算了建议，没冻。 | [mcp-server-tronlink](mcp-server-tronlink.zh.md) 的 `tl_chain_stake`（`action="freeze"`，`amount_trx=1000`，`resource="ENERGY"`） |
| 「给 SR `T…` 投 5000 票」 | `tron-staking sr-list`——只读了 SR 列表，没投票。 | [TronLink CLI](tronlink-cli.zh.md) 的 `tronlink vote --votes <SR_ADDRESS>:5000` |
| 「给 SunSwap 路由器授权 USDT 额度」 | `tron-token token-info` / `contract-info`——纯元数据查询，没发送 approve。 | [TronLink CLI](tronlink-cli.zh.md) 的 `tronlink trigger --contract <USDT_CONTRACT> --method 'approve(address,uint256)' --args '["<ROUTER_ADDRESS>","1000000"]'`。代币合约和路由器地址须对应所选网络。路由器是被授权方；USDT 精度为 6 时，`1000000` 表示授权 1 USDT。 |
| 「现在把 100 TRX 换成 USDT」 | `tron-swap swap-quote`——只报了价，没执行。 | [mcp-server-tronlink](mcp-server-tronlink.zh.md) 的 `tl_chain_swap_v3`（`action="execute"`，`slippage` 填用户确认的滑点百分比） |
| 「领取我的投票奖励」 | `tron-staking staking-info`——只看了待领数量。 | [TronLink CLI](tronlink-cli.zh.md) 的 `tronlink reward` |

**判断口诀。** 用户动词只要出现 *send / freeze / unfreeze / vote / unvote / approve / swap（执行）/ claim / sign / broadcast*，答案就**不在**这个 Skills 集里起步。Skills 仍然可以做**前置**（报价、估算成本、校验地址、查余额）——只是别声称"Skills 调用完成了用户的请求"。

---

## 推荐技能组合工作流

### 余额与代币查询
```text
tron-wallet（查余额）→ tron-wallet（列出代币）→ tron-resource（检查能量状态）
```

### 研究与兑换报价
```text
tron-token（搜索）→ tron-market（价格/K线）→ tron-resource（检查能量）→ tron-swap（获取报价）
```

### 质押分析
```text
tron-wallet（查余额）→ tron-staking（质押信息）→ tron-staking（APY 估算）→ tron-staking（SR 列表）
```

### 资源优化
```text
tron-resource（检查状态）→ tron-resource（估算成本）→ tron-resource（optimize-cost）
```

---

## TRON 资源模型参考

### 能量 vs. 带宽

| 资源 | 消耗场景 | 免费额度 | 获取方式 |
|------|----------|----------|----------|
| **带宽** | 所有交易 | 600/天 | 冻结 TRX 或燃烧 TRX |
| **能量** | 仅智能合约 | 无 | 冻结 TRX、租赁或燃烧 TRX |

### 成本示例

> **数据截至 2026-05。** 能量数字会随合约升级（尤其是 USDT TRC-20）和网络参数变化；TRX 燃烧列用到的带宽/能量单价也会变。**仅作量级参考**，不是契约值。数据来源：TronGrid / Tronscan 交易采样与 TRON 网络参数。需要实时数值请用 `tron-resource` 的 `estimate-energy` / `estimate-bandwidth` 命令。

| 操作 | 带宽 | 能量 | TRX 燃烧量（无资源时） |
|------|------|------|------------------------|
| TRX 转账 | ~267 | 0 | 0（在免费额度内） |
| USDT 转账 | ~345 | ~65,000 | ~13-27 TRX |
| SunSwap 兑换 | ~345 | ~65,000-200,000 | ~13-40 TRX |
| 代币授权 | ~345 | ~30,000 | ~6-12 TRX |

### Stake 2.0 要点
- 冻结 TRX → 获取能量或带宽 → 投票给 SR → 赚取奖励
- 解冻需 **14 天等待期** 才能提取
- 解冻后投票重置；重新冻结后需重新投票
- 1 冻结 TRX ≈ 每天 4.5 能量——**动态值**：取决于全网总质押量；实时数请用 `tron-resource estimate-energy`。数据截至 2026-05。
- 投票奖励每 6 小时可领取一次

---

## 集成方式

### 方式一：Claude Code（推荐）

```bash
# 克隆后直接使用
git clone https://github.com/TronLink/tronlink-skills.git
cd tronlink-skills
nvm install && nvm use
claude   # 自动发现 SKILL.md 文件
```

只读操作无需 `npm install`。

### 方式二：MCP 服务器

```bash
# 注册为 MCP 服务器
claude mcp add tronlink -- node ~/.tronlink-skills/scripts/mcp_server.mjs

# 提供 25 个 MCP 工具，可被 Claude Desktop / Claude Code 直接调用
# （逐项对照见上文 "Skill ↔ MCP 工具映射"；剩余 8 个命令仅 CLI 可用）
```

### 方式三：命令行直接使用

```bash
# 直接执行命令
node scripts/tron_api.mjs wallet-balance --address T地址...
node scripts/tron_api.mjs token-price --token USDT
node scripts/tron_api.mjs swap-quote --from TRX --to USDT --amount 100
```

#### 处理 Skills CLI 和 MCP 错误

在 Skills v1.1.0（`b12b5868`）中，未知 CLI 命令或缺少必填参数会向 stderr 输出原因，并以 `1` 退出。命令也可能以 `0` 退出，同时在 stdout 返回错误。例如，`staking-apy --amount 0` 返回的 JSON 包含 `error`、`status: 400` 和 `parameter: "amount"`。调用查询命令时，先检查退出码，再解析 stdout 中的 JSON；确认没有 `error` 后再使用结果。[Skills CLI 实现](https://github.com/TronLink/tronlink-skills/blob/b12b58685ec38febc21843d2173dd43d969b8eb0/scripts/tron_api.mjs)

通过 MCP 调用 `tools/call` 时，先检查 JSON-RPC 错误（未知工具返回 `-32602`）。对于已识别的工具，再解析 `result.content[0].text` 中的 JSON，检查其中的 `error` 字段。包装层可以在这段文本中返回命令错误，同时省略 `isError` 标记。[Skills MCP 实现](https://github.com/TronLink/tronlink-skills/blob/b12b58685ec38febc21843d2173dd43d969b8eb0/scripts/mcp_server.mjs)

### 方式四：其他 AI 平台

| 平台 | 集成方式 |
|------|----------|
| **Cursor / Windsurf** | 克隆仓库，使用 MCP 或直接读取技能文件 |
| **Codex CLI** | 软链接到 `~/.agents/skills/tronlink-skills` |
| **OpenCode** | 注册插件，软链接技能 |
| **LangChain / CrewAI** | 将 `tron_api.mjs` 封装为 Tool |

#### Cursor（Windsurf 配置同构）

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
# 将 skills 目录软链到 agent 发现路径
ln -s "$(pwd)/tronlink-skills" ~/.agents/skills/tronlink-skills
# 验证识别
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

#### LangChain / CrewAI（Python）

```python
from langchain_core.tools import Tool
import subprocess, json

def tron_call(cmd: str) -> dict:
    out = subprocess.check_output(
        ["node", "scripts/tron_api.mjs", *cmd.split()],
        cwd="/absolute/path/to/tronlink-skills",
    )
    result = json.loads(out)
    if isinstance(result, dict) and "error" in result:
        raise RuntimeError(result["error"])
    return result

tron_wallet_balance = Tool.from_function(
    func=lambda addr: tron_call(f"wallet-balance --address {addr}"),
    name="tron_wallet_balance",
    description="TRX 余额与冻结量，地址为 TRON Base58（T...）字符串。",
)
```

### 快速安装脚本

```bash
# 自动安装到所有 AI 环境
bash install.sh

# 清洁卸载
bash uninstall.sh
```

---

## 配置说明

### 环境变量

```bash
# 可选：TronGrid API Key，获取更高请求频率
export TRONGRID_API_KEY="your-api-key"

# 可选：切换网络（默认：mainnet）
export TRON_NETWORK="mainnet"    # 或 "shasta" / "nile"
```

### 网络支持

| 网络 | 地址 | 用途 |
|------|------|------|
| 主网 | https://api.trongrid.io | 生产环境 |
| Shasta 测试网 | https://api.shasta.trongrid.io | 测试 |
| Nile 测试网 | https://nile.trongrid.io | 测试 |

### 内置代币快捷符号

| 符号 | 合约地址 |
|------|----------|
| TRX | 原生代币（无合约） |
| USDT | TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t |
| USDC | TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8 |
| WTRX | TNUC9Qb1rRpS5CbWLmNMxXBjyFoydXjWFR |
| BTT | TAFjULxiVgT4qWk6UZwjqwZXTSaGaqnVp4 |
| JST | TCFLL5dx5ZJdKnWuesXxi1VPwjLVmWZZy9 |
| SUN | TSSMHYeV2uE9qYH95DqyoCuNCzEL1NvU3S |
| WIN | TLa2f6VPqDgRE67v1736s7bJ8Ray5wYjU7 |

---

## 项目结构

```text
tronlink-skills/
├── README.md                          # 主文档
├── package.json                       # Node.js 配置文件
├── install.sh                         # 全环境自动安装脚本
├── uninstall.sh                       # 清洁卸载脚本
│
├── scripts/
│   ├── tron_api.mjs                   # 主 CLI（33 个命令，零依赖）
│   └── mcp_server.mjs                 # MCP 协议服务封装
│
├── skills/                            # 技能定义（自动发现）
│   ├── tron-wallet/SKILL.md
│   ├── tron-token/SKILL.md
│   ├── tron-market/SKILL.md
│   ├── tron-swap/SKILL.md
│   ├── tron-resource/SKILL.md
│   └── tron-staking/SKILL.md
│
├── docs/
│   ├── claude-integration-guide.md    # 3 种集成方式
│   ├── resource-model.md              # 能量与带宽深度解析
│   ├── staking-guide.md               # Stake 2.0 与 APY 说明
│   └── integration-guide.sh
│
├── .claude-plugin/                    # Claude Code 插件配置
├── .cursor-plugin/                    # Cursor IDE 插件配置
├── .opencode/                         # OpenCode 配置
├── .codex/                            # Codex CLI 安装说明
├── .claude/                           # 预配置测试命令
├── _meta.json                         # 技能注册元数据
└── LICENSE                            # MIT
```

---

## 依赖项

| 依赖 | 是否必需？ | 用途 |
|------|-----------|------|
| Node.js 24.22.3（精确版本；默认分支 v1.1.0） | 是 | 运行时（原生 fetch、crypto）。默认分支通过 `.nvmrc` 与 `package.json` 的 `engines` 固定该版本；`install.sh` 检测到其他版本会直接报错退出。安装前先执行 `nvm install 24.22.3 && nvm use 24.22.3`。 |
| npm install | 不需要 | 所有操作均无需安装任何 npm 依赖 |

---

## 安全模型

| 方面 | 实现方式 |
|------|----------|
| 纯只读设计 | 所有命令均为查询操作——不涉及私钥、签名或资金移动 |
| 副作用 | 每个命令都是 **Network Read**：调用公共 API,但不改变任何状态。所有命令均可安全重试,无需人工确认（HITL） |
| 无需密钥 | 仅可选 TRONGRID_API_KEY 用于提高请求频率 |
| 频率限制 | 公共 TronGrid API；使用 TRONGRID_API_KEY 获取更高限额 |
| 错误处理 | 失败均为查询类错误：限流（可重试,需退避）、网络错误（可重试）、地址/参数非法（不可重试——修正输入）。 |

---

## 地址格式支持

所有命令均支持并自动归一化两种格式：

| 格式 | 示例 | 说明 |
|------|------|------|
| Base58Check | `T...`（34 字符） | 标准显示格式 |
| Hex | `41...`（42 个十六进制字符） | 内部表示格式 |

---

## 关键设计决策

1. **零依赖** — 无需 npm install，对 AI Agent 而言轻量且即时
2. **纯只读安全设计** — 所有命令均为查询操作，不涉及私钥或签名
3. **TRON 专属领域知识** — 为能量/带宽和 Stake 2.0 提供专门技能，尊重 TRON 独特架构
4. **多格式地址支持** — 透明处理 Base58Check 和 hex 两种格式
5. **代币符号解析** — 常用代币有内置快捷方式；未知合约可直接使用地址
6. **成本优化建议** — `optimize-cost` 命令提供个性化策略
7. **MCP 服务封装** — 为 Claude Desktop 和现代 AI Agent 提供结构化集成

---

## 快速开始

```bash
# 1. 克隆
git clone https://github.com/TronLink/tronlink-skills.git
cd tronlink-skills
nvm install && nvm use

# 2. 配合 Claude Code 使用（只读操作无需安装）
claude
> "查一下 T地址... 的 TRX 余额"
> "展示 TRON 上最热门的代币"
> "发送 USDT 需要多少能量？"
> "获取能量最好的方式是什么——冻结、租赁还是燃烧？"

# 3. 或直接使用命令行
node scripts/tron_api.mjs wallet-balance --address T地址...
node scripts/tron_api.mjs token-price --token USDT
node scripts/tron_api.mjs optimize-cost --address T地址...
```

## 版本与许可证

- **包：** `tronlink-skills` v1.0.1——本页命令表所描述的版本。
- **默认分支：** v1.1.0（commit `b12b5868`，`package.json` 中 `version: 1.1.0`），`git clone` / `install.sh` 安装的就是该版本。与 v1.0.1 相比，影响 agent 的差异：
    - 新增 7 个只读命令（同时以 `tron_<command>` 形式暴露为 MCP 工具）：`wallet-approvals`, `wallet-overview`, `token-overview`, `bandwidth-price`, `tx-cost`, `chain-params`, `health-check`。共 40 个命令，仍全部为 Network Read。
    - 此提交的 [`.nvmrc`](https://github.com/TronLink/tronlink-skills/blob/b12b58685ec38febc21843d2173dd43d969b8eb0/.nvmrc) 指定 Node.js 24.22.3。复现[旧提交 `7d2d58cb`](https://github.com/TronLink/tronlink-skills/blob/7d2d58cb/.nvmrc) 时使用 Node.js 24.22.1。在检出的仓库根目录运行 `nvm install && nvm use`，即可按该提交的配置选择版本。
- **许可证：** MIT —— `SPDX-License-Identifier: MIT`
- **变更记录 / 发布：** [https://github.com/TronLink/tronlink-skills/releases](https://github.com/TronLink/tronlink-skills/releases) —— 截至当前 v1.0.x 尚无 GitHub tag 发布；打 tag 之前请直接看 commit 历史。

### 兼容性与迁移策略

Skills 已进入 **v1.0.x**，适用标准 semver——只有 **major** 升级允许破坏公开面。

- **稳定契约**（minor / patch 不会动）：
    - 33 个 CLI 命令名与其必填 / 可选 flag（`tron_api.mjs <command> [...]`）。
    - [Skill ↔ MCP 工具映射](#skill-mcp-tool-map) 列出的 25 个 MCP 工具名（`tron_*` 形式）及其 `inputSchema` 字段名。
    - `Network Read` 副作用分级——任何命令未经 major 升级都不会变成 Remote Write。
- **不稳定契约**（minor 允许变化）：
    - JSON `stdout` 输出的具体字段——新增字段任意 minor 都允许；改名或删除属于 major。请用宽容解析。
    - 内置代币 symbol 快捷表（`USDT`、`USDC`、`WTRX`…）——minor 允许新增 symbol；已存在的映射 minor 不会重指。
    - 启发式与阈值（`whale-transfers` 默认阈值、`optimize-cost` 决策树权重等）。
- **子集关系。** MCP 工具子集（目前 25 / 33）可能在 minor 中 **扩大**（CLI-only 命令被新增为 MCP 工具）；不会在 minor 中 **缩小**。
- **废弃窗口。** 被标 deprecated 的命令 / 工具至少在 **一个 minor 周期** 内继续可用；移除最早发生在下一个 major。
- **升级后校验。** 重新 `tron_api.mjs --help`，使用 MCP 时再跑 `tools/list`，确认依赖的名字仍在。MCP `initialize` 阶段返回的 `serverInfo.version` 应与升级后的 `package.json` 版本一致。
