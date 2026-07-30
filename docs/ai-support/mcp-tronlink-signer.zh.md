# mcp-tronlink-signer

**GitHub**: https://github.com/TronLink/mcp-tronlink-signer

将 [tronlink-signer](https://github.com/TronLink/mcp-tronlink-signer/tree/main/packages/tronlink-signer) 封装为 MCP 工具的服务器，供 Claude 及其他 AI 客户端使用。通过 TronLink 浏览器钱包对 TRON 交易进行签名，需用户在浏览器中授权确认 — 私钥始终留在钱包中，不会对外暴露。

## 配置

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

### 从源码构建

```bash
git clone https://github.com/TronLink/mcp-tronlink-signer.git
cd mcp-tronlink-signer
pnpm install && pnpm build
```

然后指向构建产物：

```bash
claude mcp add -s user tronlink-signer -- node /path/to/packages/mcp-tronlink-signer/dist/cli.js
```

## MCP 工具

| 工具 | 说明 | 参数 | 副作用 | 可自动重试 |
| ---- | ---- | ---- | --- | :---: |
| `connect_wallet` | 连接 TronLink 钱包 | `network?` | Local Write（缓存 session） | 可——必要时让用户重新授权 |
| `send_trx` | 向指定地址发送 TRX | `to`、`amount`、`network?` | **Remote Write** | **不可**——重发前先确认链上状态 |
| `send_trc20` | 发送 TRC20 代币 | `contractAddress`、`to`、`amount`、`decimals?`、`network?` | **Remote Write** | **不可**——同 `send_trx` |
| `sign_message` | 对消息进行签名 | `message`、`network?` | Local Write（只签名不广播） | 可——会重新弹审批 |
| `sign_typed_data` | 对 TIP-712（TRON 版 EIP-712）结构化数据签名 | `typedData`、`network?` | Local Write（只签名） | 可——会重新弹审批 |
| `sign_transaction`（`broadcast=false`） | 仅签名 | `transaction`、`broadcast=false`、`network?` | Local Write | 可——会重新弹审批 |
| `sign_transaction`（`broadcast=true`） | 签名 + 广播 | `transaction`、`broadcast=true`、`network?` | **Remote Write** | **不可**——重发前先确认链上状态 |
| `get_balance` | 查询 TRX 余额 | `address`、`network?` | Network Read | 可 |

所有工具均支持可选的 `network` 参数（`mainnet` / `nile` / `shasta`），默认使用 `mainnet`。

> **Typed-data 注意。** `typedData` 是透传的——schema 不校验 `domain` / `types` / `message` 结构。调用前请自行核对 `typedData.domain.chainId` 与 `network` 参数一致(mainnet `728126428`、Nile `3448148188`、Shasta `2494104990`),且 `verifyingContract` 是目标合约——domain 不匹配会导致签名被跨网络重放。

> **原始交易过期。** 传给 `sign_transaction` 的预构建 `transaction` 带 `raw_data.expiration`(TronWeb 默认约构建后 60 秒),而审批窗口最长 5 分钟。用户在交易过期后才 Approve 会导致广播失败(expired)——请在调用前才构建原始交易，或有意延长 expiration。重播**同一份**已签名负载是幂等的(同 txId,节点去重);重建再重签则是**一笔新交易**——那才是要避免的双花路径。

**人工确认（HITL）。** 所有涉及签名的工具（`send_trx`、`send_trc20`、`sign_message`、`sign_typed_data`、`sign_transaction`）都会打开 TronLink 浏览器审批页。AI agent **无法**在用户点击 Approve 之前签名。生产环境必须把 Remote Write 工具视为需要确认。

**没有无人值守路径。** 签名需要一个正在运行的浏览器和用户的人工点击——headless CI 或服务器环境里只有 `get_balance` 可用；不存在 service-account 签名模式。

**仔细核对审批内容。** 地址投毒攻击依赖首尾字符相同的相似地址——请在审批页核对**完整**的 base58 收款地址(而非只看首尾),并确认网络标识与金额后再点 Approve。

## MCP 资源

| URI | 说明 |
| --- | ---- |
| `wallet://networks` | 可用网络及其配置信息 |
| `wallet://config` | 当前签名器配置 |

## MCP 提示词

| 提示词 | 说明 |
| ------ | ---- |
| `send-trx` | 发送 TRX 的引导式工作流 |
| `check-balance` | 查询余额的引导式工作流 |
| `send-token` | 发送 TRC20 代币的引导式工作流 |

## 工作原理

1. AI 智能体调用 MCP 工具（如 `send_trx`）— CLI 中会显示签名提示
2. 服务器将请求委托给 `tronlink-signer`，后者打开**单个浏览器标签页**用于授权（如已打开则复用现有标签）
3. 授权页面通过 **TIP-6963** 协议发现 TronLink 钱包
4. 自动解锁钱包，并在需要时切换网络
5. 如果钱包已连接，`connect_wallet` 会自动完成
6. 交易详情会被解析为人类可读的格式（TRX 转账、TRC20、TRC721 NFT、质押、委托、投票等）
7. 用户在浏览器中查看并批准
8. TronLink 完成交易签名 — 私钥始终留在钱包中
9. 结果返回给 AI 智能体 — 页面保持打开以便处理下一次操作

## 端到端示例

一个典型的 `send_trx` 流程，从用户提问到链上结果：

**1. 用户 → 智能体**

> 「在 nile 上给 TJRabc…xyz 转 5 个 TRX。」

**2. 智能体 → MCP 工具调用**

```json
{
  "name": "send_trx",
  "arguments": { "to": "TJRabc...xyz", "amount": 5, "network": "nile" }
}
```

**3. 审批（人工确认 HITL）** —— 服务打开 TronLink 审批页；用户核对「Send 5 TRX → TJRabc…xyz (Nile)」后点击 **Approve**。若点击 Reject 则返回 `USER_REJECTED`（不可重试）。

**4. MCP 工具 → 智能体（结果）**

```json
{
  "txId": "0a1b2c...",
  "status": "success"
}
```

**5. 智能体 → 用户**

> 「已发送 5 TRX——链上已确认（交易 `0a1b2c…`）。」

> 请基于 `status` 与上述消息标记分支——v0.1.x 尚未实现结构化的 `error.code` 字段。`status: "pending"` 表示广播成功但确认超时——应用 `get_balance` 或浏览器查询对账，而不是重发(见[错误](#errors)）。

## 取消

所有签名工具均支持 MCP 取消机制。如果 AI 客户端取消了一个待处理的工具调用（例如用户在 Claude Code 中按下 Ctrl+C），进行中的请求会被自动中止，对于已被取消的请求不会打开浏览器授权页面。

## 交易确认

当调用 `sign_transaction` 且 `broadcast: true` 时，服务器会在广播后自动轮询链上确认状态，并返回执行结果（`success` 或 `pending`）。如果交易在链上失败（如 `OUT_OF_ENERGY`、Solidity revert），错误信息会连同解码后的原因一并返回给 AI 智能体。

## 错误 {#errors}

线上行为(v0.1.x):签名工具把序列化的 `BroadcastResult` 作为 text content 返回——`status` 为 `"failed"` 时会置 MCP 的 `isError` 标志:

```json
{ "txId": "0abc…", "status": "failed", "error": "REVERT: …" }
```

意外失败则返回纯文本 `Error: <message>` 并置 `isError: true`。**目前没有结构化的 `error.code` / `retryable` 字段**——下表中的条件名是本文档用于归类失败的分类法。只有 `USER_REJECTED` 与 `CANCELLED_BY_CALLER` 会逐字出现在线上文本里(另有审批超时的 `timed out after 5 minutes` 措辞);其余条件请结合 `status` 与消息内容判断。不要按 `error.code` 写脚本。

下表的 **Retryable** 列是按条件给出的 agent 指引,不是线上字段。框架层 `TL_*` 码(属 `mcp-server-tronlink`,非本 server)统一以 [TronLink MCP Core 错误码](tronlink-mcp-core.md#error-codes) 为准；signer 特有错误如下：

| 条件 | Retryable | 何时发生 |
| --- | :---: | --- |
| `USER_REJECTED` | 否 | 用户在 TronLink 审批页点击 Reject。 |
| `TIMEOUT` | 先对账 | 5 分钟窗口内未收到完成回执（0.1.4 写死，不可配置）。通常是用户从未审批、什么都没签——但计时器包住**整个**往返、用户点击 Approve 时并不取消，临近截止的审批仍可能完成签名与广播，而调用方收到 `TIMEOUT`（迟到的结果被丢弃）。请按 `BROWSER_DISCONNECTED` 同样处理：任何写操作先上链确认再决定是否重发。 |
| `BROWSER_DISCONNECTED` | 先对账 | 审批页被关闭或心跳丢失。若断在用户审批**之前**,未签名，重发安全；若断在审批**之后**,已签名交易可能已被广播。仅凭该错误码无法区分两种情况——写操作先用 `get_balance` / 区块浏览器对账后再重发。 |
| `NETWORK_ERROR` | 是 | TronGrid / RPC 请求失败，偶发性故障。 |
| `BROADCAST_FAILED` | 否 | 签名成功但节点拒绝提交。**禁止**自动重试——签名可能已被其他节点接受。 |
| `ON_CHAIN_FAILED` | 否 | 广播成功但链上执行失败（`OUT_OF_ENERGY`、Solidity revert、`FAILED`）。该交易已最终化；先解决根因再发送新交易。这是 SDK 层 `status: "failed"` 在 MCP 层的呈现——本层的 `status` 只会是 `success` / `pending`。 |
| `INVALID_INPUT` | 否 | 工具输入校验失败。修正参数。 |
| `CANCELLED_BY_CALLER` | 否 | MCP 客户端取消调用（如用户按 Ctrl+C）。会逐字出现在错误文本中。 |

**重试策略。** 只读调用（`get_balance`）与签名前失败（`USER_REJECTED`、`INVALID_INPUT`、`CANCELLED_BY_CALLER`）agent 可安全用修正后的输入重发。任何签名 + 广播路径——一旦请求离开 server，结果就必须视为未知，先用 `get_balance` 或区块浏览器确认后再考虑重发。

## 安全边界 {#security-boundaries}

| 边界 | 保证 | Agent / 运维方义务 |
|---|---|---|
| **Prompt 注入** | 工具输入按原始值作为调用参数，server 不会再次提交给 LLM。TronLink 审批页渲染的是解析后的交易字段，不是 agent 的自由文本。 | 链上拿到的字符串（备注、revert 原因）视为不可信；分支应基于 `txId` / `status` / `code`，而非 prose。 |
| **本地 HTTP listener** | 本地审批 server **仅绑定 `127.0.0.1`**（端口 `TRON_HTTP_PORT`，默认 3386，被占用时自增），永远不接受跨主机连接。每个 server session 有唯一 ID，前一次 session 的浏览器标签会被自动失效。 | 不要把 3386 端口转发到外网。同一台机器不要用相同 `TRON_HTTP_PORT` 跑两份。 |
| **出站 host 白名单（SSRF）** | signer 只与 [Networks](#environment-variables) 列出的 TronGrid 端点以及本地浏览器通信，工具不接受会被原样请求的用户 URL。 | 生产环境钉死 `TRON_NETWORK`、`TRON_API_KEY`。 |
| **API key 处理（token passthrough）** | `TRON_API_KEY` 仅在启动时从 env 读取，仅用于到 TronGrid 的出站；**不**会出现在任何工具响应、错误 `details` 或 MCP resource 中。server 不接受 MCP 客户端传入的 Authorization header 并转发到上游。 | API key 放进 MCP host 的 secret manager，不要写进会提交 git 的 `mcpServers` 配置。 |
| **签名必须 HITL** | 所有签名工具（`send_trx`、`send_trc20`、`sign_message`、`sign_typed_data`、`sign_transaction`）都会打开 TronLink 审批页，**不存在程序化绕过**。私钥始终留在 TronLink。 | 不需要运维额外强制 HITL——这是结构性保证。不要试图通过移除浏览器层来"加固"。 |
| **浏览器标签劫持** | 审批页基于 server session ID 验证每次请求，过期的标签会被忽略；心跳检测会在断连时关闭 session。 | 同一用户跑多个 agent 时，请让每个 agent 启动自己的 signer 实例；跨实例的请求串扰由 session ID 屏蔽，但 UI 层混淆不防。 |
| **Confused deputy** | signer 以已连接的 TronLink 账户身份执行，没有来自 MCP 客户端的逐次授权 scope。 | 一个 signer 实例 = 一个 TronLink 账户，不要把多个终端用户复用到同一个实例。 |

## 环境变量 {#environment-variables}

| 变量名 | 说明 | 默认值 |
| ------ | ---- | ------ |
| `TRON_NETWORK` | 默认网络（mainnet / nile / shasta） | `mainnet` |
| `TRON_HTTP_PORT` | 本地 HTTP 服务端口 | `3386` |
| `TRON_API_KEY` | TronGrid API Key（可选） | - |

## 排错 {#troubleshooting}

- **审批页始终打不开**——server 会打开系统默认浏览器；端口被占用时会自动递增，因此重发工具调用即可，不要假设固定端口。确认主机有桌面浏览器（headless 主机无法签名）。
- **`BROWSER_DISCONNECTED`**——审批页被关闭。重发即可重新打开；写操作先链上对账（见[错误](#errors)）。
- **5 分钟后 `TIMEOUT`**——多数情况是从未审批；但临近截止的 Approve 仍可能已广播（见错误表），重发写操作前先上链查这笔交易。5 分钟窗口在 0.1.4 中写死，没有任何选项或环境变量可调。
- **点了 Approve 但交易失败**——钱包锁定、`network` 参数配错，或预构建交易已过期（见上方原始交易过期说明）。解锁 TronLink、核对 `network`、在调用前才构建原始交易。
- **验证安装**——`list_tools` 应返回上表 7 个工具。（0.1.4 的响应不带 `meta.schemaVersion` 等 meta 字段——不要以此作为安装判据。）

## 版本与许可证

- **包：** `mcp-tronlink-signer` v0.1.4
- **许可证：** MIT —— `SPDX-License-Identifier: MIT`
- **变更记录 / 发布：** [https://github.com/TronLink/mcp-tronlink-signer/releases](https://github.com/TronLink/mcp-tronlink-signer/releases)

### 内联 changelog {#inline-changelog}

本页是下游 README 镜像；以 GitHub releases 与各包 `CHANGELOG.md` 为准。下方条目只覆盖 **MCP 可见面**（工具、schema、安全边界），内部重构不列。

#### v0.1.4 _(仅 npm，截至本文写就尚未在 GitHub 打 tag)_

仅 patch 修复。无新工具、无破坏性输入/输出 shape 变化。升级后用 `list_tools` 复核。

#### v0.1.3 _(仅 npm，截至本文写就尚未在 GitHub 打 tag)_

仅 patch 修复。无新工具、无破坏性输入/输出 shape 变化。

#### v0.1.2 — 2026-04-15

与 `tronlink-signer@0.1.2` 同步发布。**审批流大改版**；MCP 工具 schema 无破坏性变化。

- **新增** —— `sign_transaction` 支持 `broadcast: true` 同步签名 + 广播（此前仅签名）。
- **新增** —— `connect_wallet` 在钱包已连接时自动完成，无需再走一次审批。
- **新增** —— 交易解析：TRX 转账、TRC10、TRC20、TRC721 NFT、质押/解冻、委托、投票等在审批页以人类可读形式呈现。
- **改进** —— 单页审批流：一个常驻浏览器标签 + 心跳检测；server 重启后旧标签自动失效。
- **改进** —— TRC20 金额校验改用 BigInt 小数转换（处理 0 位小数、>18 位小数等边界）。
- **改进** —— `send_trx`、`sign_transaction` 在提交失败时返回真实的 broadcast 错误，不再是空消息。
- **迁移** —— 若你基于 `status` 与文档消息标记分支，无需迁移；将来引入结构化 `error.code` 字段时会是增量变更（见 [错误](#errors)）。

#### v0.1.1 — 2026-04-15

- `tronlink-signer@0.1.1` + `mcp-tronlink-signer@0.1.1` 首次 npm 发布。
- 各包 README，含用法与 API 文档。
- npm package metadata（keywords、repository、license、files）。
- LICENSE 增加版权声明。

### 兼容性与迁移策略

- **语义化版本。** 1.0 之前：**minor** 升级（0.x → 0.y）允许破坏性变更；**patch** 升级（0.1.x → 0.1.y）不变更 MCP 工具名、输入 schema 或 `status` 取值。1.0 之后：标准 semver，仅 major 允许破坏。
- **废弃窗口。** 当某工具或入参字段被废弃时，下一 minor 至少保留旧形式与新形式并存 **一个 minor 周期**，schema 内置 `meta.deprecated` 标记；移除最早发生在再下一周期。
- **稳定契约。** 工具名、`status` 取值（`success` / `pending`）以及逐字标记 `USER_REJECTED` / `CANCELLED_BY_CALLER` 属于公开面，patch 不会动。
- **不稳定契约。** `message` 自然语言文本、日志行格式、审批页的视觉布局 **不属于** 公开面，随时可能变化。
- **升级后校验。** 升级后 **必须** 重新 `list_tools` 确认你依赖的名字 + schema 仍存在，再继续工作流。
