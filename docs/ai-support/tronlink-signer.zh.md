# tronlink-signer

**GitHub**: https://github.com/TronLink/mcp-tronlink-signer/tree/main/packages/tronlink-signer

通过 TronLink 浏览器钱包签署 TRON 交易的独立 SDK。私钥始终留在 TronLink 中，所有签名操作均通过本地授权页面在浏览器内完成。

## 安装

```bash
npm install tronlink-signer
```

## 快速开始

```ts
import { TronSigner } from "tronlink-signer";

const signer = new TronSigner();
await signer.start();

const { address, network } = await signer.connectWallet();
const { txId, status } = await signer.sendTrx("TXxx...", 1); // status: "success" | "pending" | "failed"
// 注意：MCP 封装层（mcp-tronlink-signer）会把 status:"failed" 转为
// ON_CHAIN_FAILED 错误——在 MCP 层 `status` 只会是 "success" | "pending"。
// 同一底层事件，不同层的信封不同。
const { txId: txId2, status: s2 } = await signer.signTransaction(tx, "nile", true); // 广播 + 自动确认
const { balance } = await signer.getBalance("TXxx...");

await signer.stop();
```

## API

### `new TronSigner(config?: Partial<AppConfig>)`

创建一个新的签名实例。若未传入配置，则通过 `loadConfig()` 从环境变量中读取。

### `signer.start(): Promise<void>`

启动用于浏览器授权的本地 HTTP 服务。

### `signer.stop(): Promise<void>`

停止服务并清除所有待处理请求。

### `signer.getConfig(): AppConfig`

返回当前配置信息。

### `signer.connectWallet(network?, options?): Promise<{ address: string; network: string }>`

打开浏览器连接 TronLink 并获取钱包地址与当前网络。如果钱包已连接（同一浏览器标签页仍打开），则会无需用户交互自动完成。

### `signer.sendTrx(to, amount, network?, options?): Promise<BroadcastResult>`

向指定地址发送 TRX，会打开浏览器授权页面供用户确认。返回 `{ txId, status, error? }`，其中 `status` 为 `"success"`、`"pending"` 或 `"failed"`（参见[广播结果](#broadcast-result)）。

| 参数 | 类型 | 说明 |
| ---- | ---- | ---- |
| `to` | `string` | 接收方 TRON 地址（base58 格式） |
| `amount` | `string \| number` | 发送的 TRX 数量 |
| `network` | `TronNetwork` | 可选，网络覆盖参数 |
| `options` | `SignerOptions` | 可选，传入 `{ signal }` 可启用取消功能 |

### `signer.sendTrc20(contractAddress, to, amount, decimals?, network?, options?): Promise<BroadcastResult>`

发送 TRC20 代币，会打开浏览器授权页面。返回 `{ txId, status, error? }` — 参见[广播结果](#broadcast-result)。

| 参数 | 类型 | 说明 |
| ---- | ---- | ---- |
| `contractAddress` | `string` | TRC20 代币合约地址 |
| `to` | `string` | 接收方 TRON 地址（base58 格式） |
| `amount` | `string` | 人类可读单位的金额（如 `"1.5"` 表示 1.5 USDT），精度转换会自动处理 |
| `decimals` | `number` | 可选，代币精度。省略时通过合约的 `decimals()` 自动检测（推荐 — 可避免 USDD/SUN/JST 等非 6dp 代币出现 10^N 量级错误） |
| `network` | `TronNetwork` | 可选，网络覆盖参数 |
| `options` | `SignerOptions` | 可选，传入 `{ signal }` 可启用取消功能 |

### `signer.signMessage(message, network?, options?): Promise<{ signature: string }>`

对纯文本消息进行签名。

### `signer.signTypedData(typedData, network?, options?): Promise<{ signature: string }>`

对 EIP-712 结构化数据进行签名。

```ts
const { signature } = await signer.signTypedData({
  domain: { name: "MyDApp", version: "1", chainId: 728126428 },
  types: {
    Greeting: [{ name: "contents", type: "string" }],
  },
  primaryType: "Greeting",
  message: { contents: "Hello Tron!" },
});
```

### `signer.signTransaction(transaction, network?, broadcast?, options?): Promise<{ signedTransaction; txId?; status?; error? }>`

对原始交易进行签名。当 `broadcast` 为 `true` 时，签名后的交易会通过 TronLink 广播到链上，且 SDK 会自动轮询链上确认状态 — 可能的 `status` 取值参见[广播结果](#broadcast-result)。

| 参数 | 类型 | 说明 |
| ---- | ---- | ---- |
| `transaction` | `Record<string, unknown>` | 待签名的原始交易对象 |
| `network` | `TronNetwork` | 可选，网络覆盖参数 |
| `broadcast` | `boolean` | 签名后是否广播（默认：`false`） |
| `options` | `SignerOptions` | 可选 — 取消、确认控制、广播回调 |

```ts
// 仅签名
const { signedTransaction } = await signer.signTransaction(tx);

// 签名、广播并等待确认（默认行为）
const { signedTransaction, txId, status, error } = await signer.signTransaction(tx, "nile", true);
// status === "success" — 已在链上确认
// status === "pending" — 广播成功但在超时时间内未被确认
// status === "failed"  — 链上执行失败；`error` 包含失败原因

// 广播但不等待确认
const result = await signer.signTransaction(tx, "nile", true, { confirm: false });

// 在交易进入内存池时立即收到通知
const result = await signer.signTransaction(tx, "nile", true, {
  onBroadcasted: ({ txId }) => console.log("Broadcast:", txId),
});
```

### 广播结果 {#broadcast-result}

广播类方法（`sendTrx`、`sendTrc20`、以及 `broadcast: true` 时的 `signTransaction`）均返回 `BroadcastResult`：

```ts
interface BroadcastResult {
  txId: string;
  status: "success" | "pending" | "failed";
  error?: string; // 当 status === "failed" 时携带
}
```

`"failed"` 表示交易已上链但执行失败（如 `OUT_OF_ENERGY`、Solidity revert）。**它不会抛出异常** — 请检查 `status`。SDK 仅在广播本身没有发生时才会抛出（签名异常、用户拒绝、网络不可达等）。

### `signer.waitForTransaction(txId, network?, options?): Promise<{ status; error? }>`

轮询网络以确认交易状态。当交易在链上确认时返回 `{ status: "success" }`；达到超时时间则返回 `{ status: "pending" }`；如果交易 revert / 能量耗尽则返回 `{ status: "failed", error }`。

| 参数 | 类型 | 说明 |
| ---- | ---- | ---- |
| `txId` | `string` | 要监控的交易 ID |
| `network` | `TronNetwork` | 可选，网络覆盖参数 |
| `options` | `WaitForTransactionOptions` | 可选 — `timeoutMs`(默认：30000)、`signal` |

```ts
const { status, error } = await signer.waitForTransaction(txId, "nile");
if (status === "success") console.log("已在链上确认");
else if (status === "failed") console.warn("执行失败：", error);
```

> **提示：** 在使用 `signTransaction` 且 `broadcast: true` 时，确认轮询会自动执行 — 除非设置了 `confirm: false`，否则无需另行调用 `waitForTransaction`。

### `signer.getBalance(address, network?): Promise<{ balance: string; balanceSun: number }>`

查询指定地址的 TRX 余额，无需浏览器授权。

### `signer.onBrowserDisconnect`

用于设置授权页面被关闭或失去连接（心跳超时）时触发的回调。可用于资源清理或重新提示用户。

```ts
signer.onBrowserDisconnect = () => {
  console.log("浏览器授权页面已关闭");
};
```

### 取消与选项

所有签名方法均支持可选的 `SignerOptions`：

| 选项 | 类型 | 说明 |
| ---- | ---- | ---- |
| `signal` | `AbortSignal` | 用于取消待处理请求。若已被中止，则不会打开浏览器页面。 |
| `confirm` | `boolean` | 广播后是否等待链上确认（默认：`true`），仅在 `broadcast: true` 时生效。 |
| `confirmTimeoutMs` | `number` | 等待确认的最长时间（毫秒，默认：`30000`）。 |
| `onBroadcasted` | `(info) => void` | 在交易进入内存池后（确认前）触发，回调中的错误会被吞掉。 |

```ts
const controller = new AbortController();

// 30 秒后取消
setTimeout(() => controller.abort(), 30_000);

try {
  const { txId } = await signer.sendTrx("TXxx...", 1, undefined, {
    signal: controller.signal,
  });
} catch (e) {
  // e.message === "CANCELLED_BY_CALLER"
}
```

## 安全与副作用 {#safety-side-effects}

| 副作用 | 方法 |
| --- | --- |
| **读取**（无需审批，不改状态） | `getBalance`、`waitForTransaction`、`getConfig` |
| **仅签名**（产出签名，无链上影响） | `signMessage`、`signTypedData`、`broadcast: false` 的 `signTransaction` |
| **远程写**（签名 + 链上广播） | `sendTrx`、`sendTrc20`、`broadcast: true` 的 `signTransaction` |
| **连接**（本地会话） | `connectWallet`、`start`、`stop` |

- **人工确认（HITL）：** `connectWallet` 及每个签名/远程写调用都需要用户在 TronLink 审批页确认——被拒绝时 SDK 会抛错。私钥永不离开 TronLink。
- **重试策略：**
    - 读取与仅签名调用可安全重试（幂等，无链上影响）。
    - 远程写调用**不得**盲目重试。SDK 仅在广播从未发生时抛错（签名错误、用户拒绝、网络不可达）——这些可安全重试。但返回 `status: "pending"` 意味着广播可能已上链,重发有双花风险。重试前请先用 `waitForTransaction(txId)` 对账。
- **失败 ≠ 抛错：** 链上失败（`OUT_OF_ENERGY`、revert）以 `BroadcastResult` 的 `status: "failed"` 报告,不会抛出——请基于 `status` 分支,而非 try/catch。参见 [Broadcast Result](#broadcast-result)。

## 工作原理

1. 你的代码调用签名方法（如 `signMessage`）
2. 本地 HTTP 服务在端口 3386 启动，并打开**单个浏览器标签页**显示授权页面
3. 授权页面通过 **TIP-6963** 协议发现钱包（回退到 `window.tron`）
4. 自动解锁钱包，并在需要时切换网络
5. 对于 `connectWallet`，如果钱包已连接，会无需用户交互自动完成
6. 对于签名/发送操作，用户查看交易详情后点击 **批准** 或 **拒绝**
7. 授权页面会将交易类型（TRX 转账、TRC20、TRC721 NFT、质押、委托、投票等）解析为人类可读的展示
8. TronLink 在浏览器中完成签名
9. 结果返回给你的代码 — 页面保持打开状态并轮询下一个请求

后续所有操作都会复用同一个浏览器标签页。每个服务会话有唯一 ID — 来自旧会话的浏览器标签页会自动失效。页面会通过心跳检测服务断开并显示会话过期提示。本地服务仅绑定到 `127.0.0.1`。若端口 3386 已被占用，会自动递增。请求超时时间为 5 分钟。进程退出时（SIGINT/SIGTERM）服务会优雅关闭。

## 网络

所有签名方法均支持可选的 `network` 参数：

| 网络 | 完整节点地址 | 区块链浏览器 |
| ---- | ------------ | ------------ |
| `mainnet`（默认） | `https://api.trongrid.io` | `https://tronscan.org` |
| `nile` | `https://nile.trongrid.io` | `https://nile.tronscan.org` |
| `shasta` | `https://api.shasta.trongrid.io` | `https://shasta.tronscan.org` |

## 环境变量

| 变量名 | 说明 | 默认值 |
| ------ | ---- | ------ |
| `TRON_NETWORK` | 默认网络 | `mainnet` |
| `TRON_HTTP_PORT` | 本地 HTTP 服务端口 | `3386` |
| `TRON_API_KEY` | TronGrid API Key（可选） | - |

## 类型定义

```ts
type TronNetwork = "mainnet" | "nile" | "shasta";

interface AppConfig {
  network: TronNetwork;
  httpPort: number;
  apiKey?: string;
}

interface NetworkConfig {
  name: string;
  fullHost: string;
  explorerUrl: string;
}

interface SignerOptions {
  signal?: AbortSignal;
  confirm?: boolean;
  confirmTimeoutMs?: number;
  onBroadcasted?: (info: { txId: string; signedTransaction: Record<string, unknown> }) => void;
}

interface WaitForTransactionOptions {
  timeoutMs?: number;
  signal?: AbortSignal;
}

type BroadcastStatus = "success" | "pending" | "failed";

interface BroadcastResult {
  txId: string;
  status: BroadcastStatus;
  error?: string;
}
```

## 导出

```ts
// 类
export { TronSigner } from "./tron-signer.js";

// 配置
export { NETWORKS, DEFAULT_HTTP_PORT, REQUEST_TIMEOUT_MS, loadConfig } from "./config.js";

// 类型
export type {
  TronNetwork, NetworkConfig, AppConfig,
  PendingRequestType, PendingRequest,
  SendTrxData, SendTrc20Data,
  SignMessageData, SignTypedDataData, SignTransactionData,
  SignerOptions, WaitForTransactionOptions,
  BroadcastStatus, BroadcastResult,
} from "./types.js";
```

## 版本与许可证

- **包：** `tronlink-signer` v0.1.4
- **许可证：** MIT —— `SPDX-License-Identifier: MIT`
- **变更记录 / 发布：** [https://github.com/TronLink/mcp-tronlink-signer/releases](https://github.com/TronLink/mcp-tronlink-signer/releases) —— 与 `mcp-tronlink-signer` 共用版本线；已发布 GitHub release：**v0.1.1、v0.1.2**（2026-04-15）。v0.1.3 / v0.1.4 截至当前仅 npm —— MCP 可见变更详见 [`mcp-tronlink-signer` 的内联 changelog](mcp-tronlink-signer.md#inline-changelog)，SDK 层跟随同一波次。

### 兼容性与迁移策略

SDK 与 MCP 封装层共用版本线、共同发布。

- **语义化版本。** 1.0 之前：**minor**（0.x → 0.y）允许破坏性变更；**patch**（0.1.x → 0.1.y）不变更导出类型、函数签名或 `error.code`。1.0 之后：标准 semver，仅 major 允许破坏。
- **稳定契约**（patch 不会动）：
    - 导出函数名（`connect`、`sendTrx`、`sendTrc20`、`signMessage`、`signTypedData`、`signTransaction`）。
    - `BroadcastResult` 结构（`status: 'success' | 'pending'`、`txId`、`error?`）。
    - `error.code` 枚举值与 `error.retryable` 语义。
    - HITL（浏览器审批）强制要求——patch 永远不会引入程序化绕过。
- **不稳定契约**（随时可能变化）：
    - `./internal/*`、`./browser-bridge.ts` 等内部 helper 导出。
    - 审批页 UI 文案、签名提示、stderr 日志行。
    - `error.message` 的具体文本（分支用 `error.code`）。
- **类型层破坏。** SDK 是 TS-first，minor 升级可能 **新增** 内部 options 接口的必填字段而不改函数签名——在 TS 严格模式下表现为 `tsc` 报错但 runtime 行为不变。这种我们当作 **minor 变更** 处理，不算 major；TS-严格的消费方请把版本钉到 `~0.1`，或升级前先看 diff。
- **升级后校验。** 重新导入公开类型，确认 `BroadcastResult` 分支仍能通过编译；MCP 模式下再 `list_tools` 复核封装层工具名 + `inputSchema`。
