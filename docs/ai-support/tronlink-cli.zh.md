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

所有选项**名称**不区分大小写（例如 `--toAddress`、`--TOADDRESS`、`--toaddress` 完全等价），`--type` / `--network` / `--resource` 的枚举**取值**同样会做大小写归一（`--type TRC20` 也能用）。TRON base58 地址与合约地址是大小写敏感的数据——请原样传入。

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

> **默认网络是 `mainnet`。** 省略 `--network` 会动真实资金。以下示例统一钉死 `--network nile`;只有确认要上主网时才去掉。

示例：

```bash
tronlink transfer --type trx --toAddress TYqx5gm3p3wLDE9Bv8TBJAbK4ELNbSLfJV --amount 100 --network nile
tronlink transfer --type trc20 --contract <trc20-contract> --toAddress TYqx5gm3p3wLDE9Bv8TBJAbK4ELNbSLfJV --amount 50 --network nile
tronlink transfer --type trc721 --contract TContractAddr --toAddress TRecipient --tokenId 12345 --network nile
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
  [--call-value <trx>] [--fee-limit <trx>] [--network nile]   # fee-limit 单位 TRX,默认 100

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

## 交易预览 {#transaction-preview}

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

TRC10/TRC20/TRC721 与 `trigger` 的预览还会额外显示 `Contract`、`Decimals`、`FeeLimit` 三行。`FeeLimit`(如 `100 TRX`)是能量不足时该合约调用**最多燃烧的 TRX 上限**——审批前请先核对。

## 广播

默认情况下，签名后的交易由签名器（TronLink）广播。使用 `--local-broadcast` 可让 CLI 通过自身的 TronWeb 实例进行本地广播：

```bash
# 默认：签名器签名后广播
tronlink transfer --type trx --toAddress TYqx5gm3p3wLDE9Bv8TBJAbK4ELNbSLfJV --amount 100 --network nile

# CLI 在本地广播
tronlink transfer --type trx --toAddress TYqx5gm3p3wLDE9Bv8TBJAbK4ELNbSLfJV --amount 100 --network nile --local-broadcast
```

**两条路径是互斥的，而不是冗余。** 加 `--local-broadcast` 后，签名器只返回已签名交易**不再广播**；CLI 用自己的 TronWeb 提交一次。同一条已签名 payload 不会被本次命令重复提交。

若网络抖动导致 CLI 本地广播与签名器残留的广播都打到节点（例如断线重连时重复提交同一份已签名负载），第二次提交会被节点拒绝——TRON 节点按交易 ID 去重，结果只会是一次入块 + 一次 `DUP_TRANSACTION_ERROR` 类失败，绝不会出现两次链上效果。已确认入块后再看到此类错误视为良性；尚未确认前出现则按网络类失败处理，先用区块浏览器核对再决定是否重试。

## 输入校验 {#input-validation}

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

读操作以扁平顶层对象返回查询数据（余额、资源等），例如单代币余额查询：

```json
{
  "Address": "TNPeeaaFB7K9cmo4uQpcU32zGK8G1NYqeL",
  "Network": "nile",
  "TokenID": "1000587",
  "Balance": "12.5"
}
```
稳定键为:写操作的 `Status` / `TxID` / `Explorer` 与各读命令的数据键;错误输出为 stderr 上的 `status` / `error`(见[错误](#errors))。键名在同一大版本内保持稳定。

## 退出码 {#exit-codes}

已发布的 CLI(v1.0.x)只使用**两个**退出码:

| 退出码 | 含义 |
| :---: | --- |
| `0` | 成功——查询返回,或交易已签名并广播 |
| `1` | 任何失败——校验、用户拒绝、超时、链上失败或网络错误 |

**目前没有按失败类别细分的退出码**:脚本无法只凭退出状态区分失败类型。失败类别由 CLI 打到 **stderr** 的结构化错误行承载(见[错误](#errors))——请按"退出状态 + 该行的 `error` 消息"分支。

> **重试策略。** 读命令(`balance` / `resource` / `--constant` trigger)始终可安全重试。写/签名命令(transfer、stake、delegate、vote、写型 trigger)退出 `1` 时**无法判断**交易是否已到达网络——绝不自动重试;先通过区块浏览器或 `balance` 对账,确认上一笔未落账后再重新发起。

## 错误 {#errors}

`--json` 模式下,失败会向 **stderr** 打印一行结构化错误(stdout 保持干净,只承载成功输出):

```json
{ "status": "error", "error": "Transaction cancelled by user in TronLink" }
```

`error` 字符串来自内部分类器,每类失败有稳定措辞(v1.0.1):

| 失败类别 | `error` 消息(按前缀匹配) | 可否重试 |
| --- | --- | --- |
| 用户拒绝 | `Transaction cancelled by user in TronLink` | 否——用户已拒绝 |
| 审批超时 | `TronLink approval timed out. Please try again` | 仅当确认未广播——写操作先对账再重发 |
| 余额不足 | `Insufficient balance: …` | 否——先补足资金 |
| 地址非法 | `Invalid TRON address provided` | 否——修正输入 |
| 签名器断连 | `Signer disconnected (browser closed?) …` | 先对账——交易可能已发出也可能未发出 |
| 网络失败 | `Network connection failed. Check your internet connection` | 是——偶发;写操作先确认上一笔未落账 |
| 广播失败 | `Transaction broadcast failed: …` | 否——先链上对账 |
| 链上执行失败 | 原始消息,通常含 `OUT_OF_ENERGY` / `REVERT` / `FAILED` | 否——交易已最终化,先解决根因 |
| 未分类 | 底层原始错误消息 | 视为未知——写操作对账后再考虑重试 |

请按 `error` 字符串的**前缀**匹配——尾部可能拼接底层节点/RPC 消息。最后两类**没有稳定前缀**:没有任何已知前缀命中时,一律落入「先对账」的兜底路径(写操作在链上确认前视结果为未知)。重复提交会在原始消息中表现为节点的 `DUP_TRANSACTION_ERROR`——首笔已确认入块后出现属良性。结构化的 `error.code` / `error.retryable` 信封与按类退出码在 v1.0.x 中**尚未实现**,不要按它们写脚本。

## 安全与副作用 {#safety-side-effects}

| 副作用 | 命令 |
| --- | --- |
| **只读**（Network Read，不签名） | `balance`、`resource`、常量 `trigger`（`--constant`） |
| **远程写**（签名 + 广播） | `transfer`、`stake`、`unstake`、`withdraw`、`delegate`、`reclaim`、`vote`、`reward`、可写 `trigger` |

- **人工确认（HITL）：** 每个写命令都会本地构建交易、展示[交易预览](#transaction-preview)，并要求在 TronLink 浏览器页面显式审批后才签名。私钥永不离开 TronLink。
- **写操作不自动重试：** 见上方重试策略。
- **测试网优先：** CLI 在省略 `--network` 时默认 **mainnet**——开发阶段务必显式传 `--network nile` / `shasta`,只有动用真实资金时才用 `--network mainnet`。
- **没有无人值守签名路径：** 每个写命令都需要一个正在运行的浏览器和用户在 TronLink 审批页上的人工点击。headless CI 或服务器环境里只有带 `--address` 的读命令可用;不存在 service-account 或密钥文件签名模式。

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
tronlink balance --address TNPeeaaFB7K9cmo4uQpcU32zGK8G1NYqeL --network nile --json

# 2. 发送 10 TRX（会打开浏览器签名，需等待返回）
tronlink transfer --type trx --toAddress TRecipientAddress --amount 10 --network nile --json

# 3. 验证结果 — 输出包含 TxID 和浏览器链接
# { "Status": "Success", "TxID": "abc...", "Explorer": "https://nile.tronscan.org/#/transaction/abc..." }
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
    - **退出状态** —— 当前公开面是 `0` 成功 / `1` 失败。将 `1` 细分为按类退出码属于向后兼容的 minor 变更；脚本请把任何非零状态一律当失败。
    - **`--json` 输出 key** —— 成功键（`Status`、`TxID`、`Explorer` 及各读命令数据键）与 stderr 错误行的 `status` / `error` 键。minor 允许新增可选字段；改名 / 删除属于 major。
    - [错误](#errors)一节列出的分类 `error` 消息前缀。
- **不稳定契约**（随时可能变化）：
    - 未带 `--json` 的人类可读 stdout 文本。
    - 提示、横幅、颜色码的具体文本。
    - stderr 日志行格式（自动化请用 `--json`）。
- **`--json` 是自动化契约。** 如果脚本调用本 CLI，**必须**传 `--json` 并基于结构化字段分支；纯文本输出供人阅读，minor 之间会漂移。
- **废弃窗口。** 被标 deprecated 的子命令 / flag 至少在 **一个 minor 周期** 内继续可用，使用时 stderr 打印 `[DEPRECATED]`；移除最早发生在下一个 major。
- **升级后校验。** 重新 `tronlink --help` + 依赖的子命令 `--help`，并对一条读操作 + 一条 preview-only 写操作的 `--json` 结构抽查一次再恢复自动化。
