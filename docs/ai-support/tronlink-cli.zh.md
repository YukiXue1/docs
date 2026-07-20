# TronLink CLI

**GitHub**: [https://github.com/TronLink/tronlink-cli](https://github.com/TronLink/tronlink-cli)

通过 TronLink 钱包签名实现 TRON 区块链操作的命令行工具。

所有交易均在本地构建，并通过 TronLink 浏览器扩展进行签名 — 私钥始终不会离开 TronLink。

## 环境要求

- Node.js >= 20
- 已安装 TronLink 浏览器扩展
- 浏览器处于运行状态（写操作会打开 TronLink 进行签名）

**捆绑运行时（由 `@tronlink/tronlink-cli@1.0.1` 钉版）：**

- `tronweb` `6.2.2` —— 用于 `transactionBuilder`、ABI v2 的 `trigger` 路径、`TronWeb.isAddress()` 与本地广播。TronWeb 6.x 引入了 ethers 驱动的 ABI v2 编码器，是 `trigger` 支持 tuple / 嵌套数组 / 数组 tuple 的前提，更早的 major 版本不支持。**升级此依赖前请重测所有 `trigger` 示例**。
- `tronlink-signer` `0.1.4` —— 本地签名桥接浏览器扩展，与 [tronlink-signer](tronlink-signer.md) 是同一个 SDK。

数据截至 2026-05；来源：各包 `package.json`。

## 安装

```bash
# 通过 npm 安装
npm install -g @tronlink/tronlink-cli

# 本地开发
npm install
npm run build
npm link
```

安装完成后，可在全局使用 `tronlink` 命令。

## 全局选项

| 选项 | 默认值 | 说明 |
| ---- | ------ | ---- |
| `--local-broadcast` | 关闭 | 由 CLI 本地广播，而不是让签名器广播 |
| `--json` | 关闭 | 以 JSON 格式输出，便于脚本/AI 智能体处理 |
| `--api-key <key>` | - | TronGrid API Key（也可设置 `TRON_API_KEY` 环境变量） |
| `--timeout <ms>` | 300000 | 签名/连接超时时间（毫秒） |
| `--port <n>` | 3386 | TronLink Signer HTTP 服务端口 |

所有选项名称均**不区分大小写**（例如 `--toAddress`、`--TOADDRESS`、`--toaddress` 完全等价）。

## 命令

### 查询（读操作）

读命令支持两种模式：

- **传入 `--address`**：直接通过 TronGrid 查询，无需连接钱包。如未传 `--network`，默认查询主网。
- **不传 `--address`**：通过 TronLink 授权读取当前钱包地址（如未传 `--network`，默认主网）。

```bash
# 查询所有代币余额
tronlink balance --address <address> [--network mainnet]
tronlink balance                                          # 连接钱包

# 查询指定 TRC20 代币余额（自动检测精度）
tronlink balance --address <address> --token <contract> [--decimals 6] [--network mainnet]

# 查询指定 TRC10 代币余额（自动检测精度）
tronlink balance --address <address> --tokenId <id> [--decimals 6] [--network mainnet]

# 查询能量与带宽
tronlink resource --address <address> [--network nile]
tronlink resource                                         # 连接钱包
```

**主网查询代币**：TRX, USDT, USDD, USDC, SUN, JST, BTT, WIN, WTRX
**Nile 查询代币**：TRX, USDT
**Shasta 查询代币**：TRX

### 转账

```bash
# TRX（金额单位为 TRX，而非 sun）
tronlink transfer --type trx --toAddress <to> --amount <amount> [--network nile]

# TRC10（自动检测精度，或通过 --decimals 指定）
tronlink transfer --type trc10 --tokenId <id> --toAddress <to> --amount <amount> [--decimals 6] [--network nile]

# TRC20（自动检测精度；可选 --fee-limit 单位为 TRX，默认 100）
tronlink transfer --type trc20 --contract <contract> --toAddress <to> --amount <amount> [--decimals 6] [--fee-limit 150] [--network nile]

# TRC721 NFT（可选 --fee-limit 单位为 TRX，默认 100）
tronlink transfer --type trc721 --contract <contract> --toAddress <to> --tokenId <id> [--fee-limit 150] [--network nile]
```

示例：

```bash
tronlink transfer --type trx --toAddress TYqx5gm3p3wLDE9Bv8TBJAbK4ELNbSLfJV --amount 100
tronlink transfer --type trc20 --contract TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t --toAddress TYqx5gm3p3wLDE9Bv8TBJAbK4ELNbSLfJV --amount 50
tronlink transfer --type trc721 --contract TContractAddr --toAddress TRecipient --tokenId 12345
```

各类型的参数校验：

| 类型 | 必需参数 | 不允许的参数 |
| ---- | -------- | ------------ |
| trx | `--toAddress`, `--amount` | `--tokenId`, `--contract`, `--decimals`, `--fee-limit` |
| trc10 | `--toAddress`, `--amount`, `--tokenId` | `--contract`, `--fee-limit` |
| trc20 | `--toAddress`, `--amount`, `--contract` | `--tokenId` |
| trc721 | `--toAddress`, `--contract`, `--tokenId` | `--amount`, `--decimals` |

### 调用智能合约

调用任意智能合约方法。`--args` 是一个 JSON 数组，按位置与 `--method` 中的参数类型对应。

```bash
# 写操作（签名 + 广播）
tronlink trigger \
  --contract <address> \
  --method 'transfer(address,uint256)' \
  --args '["TRecipient...","1000000"]' \
  [--call-value <trx>] [--fee-limit <trx>] [--network nile]

# 常量（只读）调用 — 返回 constant_result 的原始 hex
tronlink trigger \
  --contract <address> \
  --method 'balanceOf(address)' \
  --args '["TQuery..."]' \
  --constant [--address <addr>] [--network nile]
```

示例：

```bash
# TRC20 approve
tronlink trigger --contract TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t \
  --method 'approve(address,uint256)' \
  --args '["TSpender...","1000000"]'

# 含 tuple 数组的批量 swap
tronlink trigger --contract TDex... \
  --method 'swap((address,uint256)[],uint256)' \
  --args '[[["T...","100"],["T...","200"]],"999"]' --fee-limit 200

# Payable 调用（携带 --call-value）
tronlink trigger --contract TPay... --method 'deposit()' --args '[]' --call-value 5

# 只读查询
tronlink trigger --contract TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t \
  --method 'balanceOf(address)' --args '["TQuery..."]' --constant --address TQuery...
```

说明：

- `--method` 接收 Solidity 函数签名。参数名为可选并被忽略：`transfer(address to, uint256 amount)` 与 `transfer(address,uint256)` 等价。
- 完整支持结构化类型：tuple、嵌套数组、tuple 数组（如 `swap((address,uint256)[],uint256)`）。编码走 TronWeb 的 ABI v2 路径（底层使用 ethers）。
- `--args` 必须是 JSON 数组，长度与方法的顶层入参数量一致。tuple 用嵌套 JSON 数组（不是对象）表示；`uint256`/`int256` 请用字符串以避免 JS 精度丢失。
- 写操作在签名前会先在链上做一次 pre-flight 模拟（`triggerConstantContract`）。合约 revert、call-value + 手续费余额不足、超出 fee-limit 都会在交易上链前被拦截。
- `--constant` 跳过签名与广播。如果不关心 owner 地址，可传 `--address` 避免唤起钱包授权。返回结果不会自动解码 — 请用任意 Solidity ABI 解码器解析返回的 hex。

### 质押（Stake 2.0）

```bash
# 质押 TRX 以获取能量或带宽
tronlink stake --amount <amount> --resource <energy|bandwidth> [--network nile]

# 解锁已质押的 TRX
tronlink unstake --amount <amount> --resource <energy|bandwidth> [--network nile]

# 提取已解冻的 TRX（在 14 天解锁期之后）
tronlink withdraw [--network nile]
```

### 资源代理

```bash
# 代理能量或带宽（锁定期单位为天，支持小数如 1.5）
tronlink delegate --toAddress <to> --amount <amount> --resource <energy|bandwidth> [--lock-period <days>] [--network nile]

# 回收已代理的资源
# 支持部分回收：当一部分代理已过锁定期、另一部分仍在锁定中时，可回收至已解锁的总量为止。
# 若申请数量超出已解锁总量，预检查会报告当前已解锁多少，以及下一批将在何时解锁。
tronlink reclaim --fromAddress <from> --amount <amount> --resource <energy|bandwidth> [--network nile]
```

### 投票

```bash
# 为超级代表投票（格式：address:count，支持多个）
tronlink vote --votes <address:count...> [--network nile]

# 领取投票奖励
tronlink reward [--network nile]
```

示例：

```bash
tronlink vote --votes TXxx:5 TYyy:3 TZzz:2
tronlink reward
```

## 交易签名

写操作（转账、质押、代理、投票等）需要在浏览器中通过 TronLink 进行授权：

1. CLI 在本地构建交易并显示预览
2. 浏览器打开 TronLink Signer 授权页面
3. 用户审核后点击 **批准** 或 **拒绝**
4. 结果返回 CLI

多个命令会复用同一个浏览器窗口 — 每个会话只需要一个浏览器标签页。关闭该标签页即结束当前会话。

支持多个命令并发执行，浏览器 UI 中每个待处理请求会以独立标签呈现，可按任意顺序进行授权。

取消某个命令（Ctrl+C）只会取消该笔交易，其他排队中的交易不受影响。

## 交易预览

所有写操作在签名前都会显示预览：

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

## 广播

默认情况下，签名后的交易由签名器（TronLink）广播。使用 `--local-broadcast` 可让 CLI 通过自身的 TronWeb 实例进行本地广播：

```bash
# 默认：签名器签名后广播
tronlink transfer --type trx --toAddress TYqx5gm3p3wLDE9Bv8TBJAbK4ELNbSLfJV --amount 100

# CLI 在本地广播
tronlink transfer --type trx --toAddress TYqx5gm3p3wLDE9Bv8TBJAbK4ELNbSLfJV --amount 100 --local-broadcast
```

**两条路径是互斥的，而不是冗余。** 加 `--local-broadcast` 后，签名器只返回已签名交易**不再广播**；CLI 用自己的 TronWeb 提交一次。同一条已签名 payload 不会被本次命令重复提交。

若网络抖动导致 CLI 本地广播与签名器残留的广播都打到节点（例如断线重连、同一 nonce 的两次 CLI 调用），第二次提交会被节点拒绝——TRON 节点按交易 ID 去重，结果只会是一次入块 + 一次 `DUP_TRANSACTION_ERROR` 类失败，绝不会出现两次链上效果。已确认入块后再看到此类错误视为良性；尚未确认前出现则按退出码 `5`（网络）处理，先用区块浏览器核对再决定是否重试。

所有输入在连接 TronLink 前会进行校验：

- **金额**：仅支持非负数字，不允许科学计数法或多个小数点
- **TRX 金额**：必须 > 0，转换为 sun 后需在安全整数范围内
- **TRC20/TRC10 金额**：小数位数不能超过该代币的精度。如未传入 `--decimals`，会从链上自动检测
- **地址**：必须为有效的 TRON 地址格式（通过 `TronWeb.isAddress()` 校验）
- **合约存在性**：在查询精度前会先在指定网络上验证
- **投票数量**：正整数，且不允许重复的 SR 地址
- **网络**：必须为 `mainnet`、`nile` 或 `shasta`
- **精度**：非负整数（0-77）
- **手续费上限**：以 TRX 为单位的正数（适用于 TRC20/TRC721/trigger）
- **Call value**（仅 trigger）：以 TRX 为单位的非负数；允许 `0`，等同于不传
- **方法签名**（trigger）：必须为 `name(type1,type2,...)`；参数名为可选且会被忽略
- **Args**（trigger）：合法的 JSON 数组，长度需与方法顶层入参数量一致
- **转账类型校验**：缺少必需参数或包含不适用的额外参数将被明确报错拒绝

无效输入会在任何钱包交互发生之前立即被拒绝并提示明确错误。

## 输出格式

**表格（默认）**：人类可读的表格输出。

**JSON（`--json`）**：面向脚本和 AI 智能体的机器可读输出。自动化场景请始终带上 `--json`。

写操作成功时返回：

```json
{
  "Status": "Success",
  "TxID": "0abc...",
  "Explorer": "https://tronscan.org/#/transaction/0abc..."
}
```

读操作在同一顶层对象下返回查询数据（余额、资源等）。字段名在同一大版本内保持稳定。

## 退出码

CLI 以下面的稳定退出码退出，自动化脚本可据此对失败类型做分支，无需解析自然语言。`--json` 模式下，同一分类也会出现在输出中。

| 退出码 | 类别 | 含义 | 可重试 |
| :---: | --- | --- | :---: |
| `0` | 成功 | 查询返回，或交易已签名并广播 | n/a |
| `1` | 输入非法 | 在任何钱包交互前校验失败（见「输入校验」） | 否——修正输入 |
| `2` | 用户拒绝 | 用户在 TronLink 审批页点击 Reject | 否——用户已拒绝 |
| `3` | 签名超时 | 在 `--timeout <ms>` 内未审批（默认 5 分钟） | 是——但**已在途**的广播除外 |
| `4` | 链上失败 | 广播成功但执行失败（`OUT_OF_ENERGY`、`REVERT`、`FAILED`） | 否——该交易已最终化，先解决根因 |
| `5` | 网络错误 | TronGrid / RPC 请求失败（偶发） | 是；写命令需先确认上一笔未上链 |

> **重试策略。** 读命令（`balance` / `resource` / `--constant trigger`）始终可安全重试。写/签名命令（transfer、stake、delegate、vote、写型 trigger）在「已提交但结果未知」时**不得**自动重试——重新发起会再次弹审批，可能重复提交。仅在通过区块浏览器或 `balance` 确认上一笔未落账后再重试。

## 错误

agent 应基于上面的退出码分支。下表把 CLI 在 stderr 与 `--json` 输出中提到的具体条件映射到对应退出码：

| 条件 | 退出码 |
| --- | :---: |
| 参数解析 / 类型 / 取值校验失败 | `1` |
| 用户在 TronLink 审批页点击 Reject | `2` |
| `--timeout` 超时未审批 | `3` |
| 节点返回 `OUT_OF_ENERGY` | `4` |
| `REVERT`（Solidity revert） | `4` |
| `FAILED`（其他链上失败） | `4` |
| TronGrid / RPC 不可达、5xx 或超时 | `5` |

## 安全与副作用 {#safety-side-effects}

| 副作用 | 命令 |
| --- | --- |
| **只读**（Network Read，不签名） | `balance`、`resource`、常量 `trigger`（`--constant`） |
| **远程写**（签名 + 广播） | `transfer`、`stake`、`unstake`、`withdraw`、`delegate`、`reclaim`、`vote`、`reward`、可写 `trigger` |

- **人工确认（HITL）：** 每个写命令都会本地构建交易、展示「交易预览」，并要求在 TronLink 浏览器页面显式审批后才签名。私钥永不离开 TronLink。
- **写操作不自动重试：** 见上方重试策略。
- **默认低风险：** 优先用测试网（`--network nile` / `shasta`）；只有动用真实资金时才用 `--network mainnet`。

## 支持的网络

| 网络 | API 节点 | 区块链浏览器 |
| ---- | -------- | ------------ |
| mainnet | `https://api.trongrid.io` | `https://tronscan.org` |
| nile | `https://nile.trongrid.io` | `https://nile.tronscan.org` |
| shasta | `https://api.shasta.trongrid.io` | `https://shasta.tronscan.org` |

## 工作原理

1. CLI 解析命令并校验所有输入
2. 对于带 `--address` 的读操作：直接通过 TronGrid 查询
3. 对于写操作或不带 `--address` 的读操作：连接 TronLink 浏览器扩展以获取钱包信息
4. 使用本地 TronWeb `transactionBuilder` 构建未签名交易
5. Pre-flight 校验：所有写命令（transfer、stake、unstake、delegate、reclaim、vote、trigger）在签名前会执行此步——校验 TRX / 代币 / 已质押 / 已委托余额，模拟合约调用以捕获 revert，估算能量与带宽消耗，校验 SR 地址（vote）、NFT 所有权（TRC721）、委托解锁时间（reclaim）
6. 将交易发送给 TronLink 进行签名（浏览器授权页面）
7. 广播：默认由签名器广播；使用 `--local-broadcast` 时由 CLI 在本地广播。两种模式下 CLI 都会轮询 `getUnconfirmedTransactionInfo` 直至交易被打包入块（约 3 秒），并将 OUT_OF_ENERGY / REVERT / FAILED 作为错误抛出
8. 输出结果

## AI / 智能体使用

TronLink CLI 通过 `--json` 输出支持 AI 智能体集成。所有命令都会返回结构化 JSON，便于解析。

### 前置条件

- 已全局安装 `tronlink`（`npm i -g @tronlink/tronlink-cli`）
- 已安装并解锁 TronLink 浏览器扩展
- 浏览器处于运行状态（写操作会打开 TronLink 进行签名）

### 使用规则

1. 始终追加 `--json` 以获取机器可读输出
2. 写操作（转账、质押、投票等）会打开浏览器供用户签名 — 需等待命令返回（默认超时：5 分钟）
3. 带 `--address` 的读操作无需连接钱包，查询更快
4. 通过 `--network` 指定网络；如果省略，所有命令都默认使用主网
5. 取消命令（Ctrl+C）只会取消该笔交易，不会终止签名会话

### AI 命令参考

#### 查询（无需签名）

```bash
# 查询所有代币余额
tronlink balance --address <address> --network mainnet --json

# 查询指定 TRC20 代币余额
tronlink balance --address <address> --token <contract> --network mainnet --json

# 查询指定 TRC10 代币余额
tronlink balance --address <address> --tokenId <id> --network mainnet --json

# 查询能量与带宽
tronlink resource --address <address> --network mainnet --json
```

#### 转账（需要签名）

```bash
# TRX
tronlink transfer --type trx --toAddress <to> --amount <amount> --json

# TRC20（自动检测精度）
tronlink transfer --type trc20 --contract <contract> --toAddress <to> --amount <amount> --json

# TRC10（自动检测精度）
tronlink transfer --type trc10 --tokenId <id> --toAddress <to> --amount <amount> --json

# TRC721 NFT
tronlink transfer --type trc721 --contract <contract> --toAddress <to> --tokenId <id> --json
```

#### 调用智能合约

```bash
# 写操作（会唤起 TronLink 进行签名）
tronlink trigger --contract <contract> \
  --method 'transfer(address,uint256)' \
  --args '["<to>","<rawAmount>"]' --json

# 常量（只读）调用 — 返回 hex，可用任意 Solidity 解码器解析
tronlink trigger --contract <contract> \
  --method 'balanceOf(address)' \
  --args '["<address>"]' --constant --address <address> --json
```

#### 质押

```bash
tronlink stake --amount <amount> --resource energy --json
tronlink unstake --amount <amount> --resource energy --json
tronlink withdraw --json
```

#### 资源代理

```bash
tronlink delegate --toAddress <to> --amount <amount> --resource energy --json
tronlink reclaim --fromAddress <from> --amount <amount> --resource energy --json
```

#### 投票

```bash
tronlink vote --votes <addr:count...> --json
tronlink reward --json
```

### 常用代币合约

| 代币 | 网络 | 合约地址 |
| ---- | ---- | -------- |
| USDT | mainnet | TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t |
| USDD | mainnet | TXDk8mbtRbXeYuMNS83CfKPaYYT8XWv9Hz |
| USDC | mainnet | TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8 |

### 示例：AI 转账流程

```bash
# 1. 先查询余额
tronlink balance --address TNPeeaaFB7K9cmo4uQpcU32zGK8G1NYqeL --network mainnet --json

# 2. 发送 10 TRX（会打开浏览器签名，需等待返回）
tronlink transfer --type trx --toAddress TRecipientAddress --amount 10 --network mainnet --json

# 3. 验证结果 — 输出包含 txId 和浏览器链接
# { "Status": "Success", "TxID": "abc...", "Explorer": "https://tronscan.org/#/transaction/abc..." }
```

### 注意事项

- 所有写命令都会阻塞，直到用户在 TronLink 浏览器弹窗中批准或拒绝
- 如用户拒绝或签名超时（5 分钟），命令会以错误退出
- 取消 CLI 命令（Ctrl+C）只会取消该笔交易 — 其他排队中的交易将继续执行
- 使用 `--timeout <ms>` 可调整签名超时时间
- 金额内部使用基于字符串的运算 — 不存在浮点精度问题

## 版本与许可证

- **包：** `@tronlink/tronlink-cli` v1.0.1
- **许可证：** MIT —— `SPDX-License-Identifier: MIT`
- **变更记录 / 发布：** [https://github.com/TronLink/tronlink-cli/releases](https://github.com/TronLink/tronlink-cli/releases) —— 截至当前 v1.0.x 尚无 GitHub tag 发布；打 tag 之前请直接看 commit 历史。

### 兼容性与迁移策略

CLI 已进入 **v1.0.x**，适用标准 semver——只有 **major** 升级允许破坏脚本依赖的公开面。

- **稳定契约**（minor / patch 不会动）：
    - 子命令名与其必填位置参数 / flag。
    - **Exit code** —— Exit Codes 表中的每一条都属于公开面。minor 允许为此前的通用失败新增 code；重新分配已有数字属于 major。
    - **`--json` 输出 key** —— 顶层 key（`ok`、`error.code`、`error.retryable`、`txid` 等）以及 `error` 下的结构。minor 允许新增可选字段；改名 / 删除属于 major。
    - `error.code` 枚举（与 [TronLink MCP Core](tronlink-mcp-core.md#error-codes) 共享 SSOT）。
- **不稳定契约**（随时可能变化）：
    - 未带 `--json` 的人类可读 stdout 文本。
    - 提示、横幅、颜色码的具体文本。
    - stderr 日志行格式（自动化请用 `--json`）。
- **`--json` 是自动化契约。** 如果脚本调用本 CLI，**必须**传 `--json` 并基于结构化字段分支；纯文本输出供人阅读，minor 之间会漂移。
- **废弃窗口。** 被标 deprecated 的子命令 / flag 至少在 **一个 minor 周期** 内继续可用，使用时 stderr 打印 `[DEPRECATED]`；移除最早发生在下一个 major。
- **升级后校验。** 重新 `tronlink-cli --help` + 依赖的子命令 `--help`，并对一条读操作 + 一条 preview-only 写操作的 `--json` 结构抽查一次再恢复自动化。
