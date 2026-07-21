# 错误码对照表

TronLink 智能体在一次用户请求里跨 DApp provider → DeepLink → MCP → Signer MCP → CLI 时，最多会碰到五套错误码方言。本页是以**业务含义**为主轴的横向对照，用来把任一方言里的错误码翻译到其他方言，并判断重试是否安全。

> 各列表头链接的"每个 surface 自己的错误表"仍然是 SSOT,本页只是导航工具——遇到歧义时，以**你实际调用的那个 surface 的结构化字段**为准(MCP 与 Signer MCP 看 `error.code`;provider 看 JS Error 的 `code`;DeepLink 看回调里的 `code`;CLI 看退出状态 + stderr 错误行的 `error` 消息前缀)。

| 业务含义 | DApp provider([EIP-1474][provider]) | DeepLink([5 位码][deeplink]) | MCP([`TL_*`][mcp]) | Signer MCP([码表][signer]) | CLI([exit + stderr 分类][cli]) | 可重试? |
| --- | :---: | :---: | :---: | :---: | :---: | :---: |
| **用户拒绝 / 取消**签名或连接弹窗 | `4001` | `300`(交易取消) | —(HITL——只能在新的 tool 调用里再次唤起) | `USER_REJECTED`、`CANCELLED_BY_CALLER` | `1` · `Transaction cancelled by user in TronLink` | **否** |
| **参数非法** / payload 错 | `tronWeb` 构造器抛错 | `10001`–`10020`、`10024`、`10025` | `TL_INVALID_INPUT` | `INVALID_INPUT` | `1` · 校验错误(发生在任何钱包交互之前) | **否**——修参数 |
| **方法 / capability 不支持** | `4200` | `10003`、`10008`、`10009`、`10011`、`10023` | `TL_CAPABILITY_NOT_AVAILABLE` | — | — | **否** |
| **钱包授权不匹配**(发起地址 ≠ 当前钱包) | provider 返回空 `accounts[]` | `10021`、`10022` | — | — | — | **否**——重新授权 |
| **没有钱包 / 无会话 / 签名器断连** | provider 未注入(`window.tron` 不存在) | `10016` | `TL_NO_ACTIVE_SESSION` | `BROWSER_DISCONNECTED`(审批页关闭——写操作先链上对账) | `1` · `Signer disconnected (browser closed?)` | **否**——先重新初始化；写操作对账后再重发 |
| **限流 / 钱包锁定** | `-32000`(20 秒内重复 `eth_requestAccounts` 且钱包锁定) | — | `TL_CHAIN_QUERY_FAILED`(TronGrid HTTP 429) | — | — | **是**——等一会儿再试 |
| **网络 / RPC 抖动**(TronGrid、RPC 错) | `tronWeb` 调用里的 TronGrid HTTP 错 | — | `TL_CHAIN_QUERY_FAILED`、`TL_GASFREE_QUERY_FAILED`、`TL_MULTISIG_QUERY_FAILED` | `NETWORK_ERROR` | `1` · `Network connection failed` | **是** |
| **链上执行失败**(广播后:`REVERT`、`OUT_OF_ENERGY`、`FAILED`) | `sendRawTransaction` 抛错或经 `getTransactionInfo` 暴露 | — | `TL_CHAIN_SEND_FAILED`、`TL_CHAIN_SWAP_FAILED`、`TL_GASFREE_SEND_FAILED`、`TL_MULTISIG_SUBMIT_FAILED` | `BROADCAST_FAILED`、`ON_CHAIN_FAILED` | `1` · 原始节点消息(`OUT_OF_ENERGY` / `REVERT`)或 `Transaction broadcast failed:` | **否**——交易已 final;查根因;**永远不要**自动重试写操作 |
| **超时**(用户没及时签 / 元素找不到) | 调用解析慢，无规范化的码 | — | `TL_WAIT_TIMEOUT`、`TL_NAVIGATION_FAILED` | `TIMEOUT`(仅审批窗口——尚未签名) | `1` · `TronLink approval timed out` | **视情况**——读操作可以;**可能已被广播的写操作**先用 `tronWeb.trx.getTransactionInfo` / `tl_chain_get_tx` 对账后再决定。(Signer 的 `TIMEOUT` 恒为审批前超时，重发是安全的) |
| **内部 / 未知** | `-32603`(Internal error) | — | `TL_INTERNAL_ERROR`、`TL_LAUNCH_FAILED` | — | `1` · 未分类的原始消息 | **可重试一次**——再失败带 log 上报 |

[provider]: ../dapp/getting-started.md#request-authorization
[deeplink]: ../mobile/deeplink.md#result-code
[mcp]: ../ai-support/tronlink-mcp-core.md#error-codes
[signer]: ../ai-support/mcp-tronlink-signer.md#errors
[cli]: ../ai-support/tronlink-cli.md#errors

## 使用方式

1. 在任一 surface 收到错误后，在表里找到对应的业务含义行，横向读出其他 surface 的对应码(或空白)。
2. **可重试?** 列是给智能体的安全提示:
    - **否**——自动重试会失败甚至有害。最危险的是"链上执行失败",此时交易已上链，无法撤回。
    - **是**——临时性问题，退避(指数，最多 3 次)后重试原调用。
    - **视情况**——读操作可以重试;**写操作不要在没对账的情况下自动重试**。
3. **Signer MCP** 列是 signer 文档的条件分类法——v0.1.x 中只有 `USER_REJECTED` 与 `CANCELLED_BY_CALLER` 逐字出现在线上文本里,其余请结合 `status` 与消息判断(见 [Signer 错误][signer])。
4. DeepLink 和 CLI 两列有很多空白，是因为这两个 surface 只覆盖了生命周期的一段——DeepLink 仅限移动端且跨信任边界;CLI(v1.0.x)只以 `0`/`1` 退出，失败类别在上表所示的 stderr `error` 消息前缀里(见 [CLI 错误][cli])。**用得到哪个 surface 就以哪个 surface 为准**。

## 给下游 MCP 服务的约束

下游 MCP 服务对框架级状况应复用 `TL_*` 码。Signer 的服务专属码(`USER_REJECTED`、`TIMEOUT`、`BROWSER_DISCONNECTED` 等)早于此规则，构成其**已文档化的方言**,已在上表 Signer MCP 列完成 join。如出现**新的**业务含义，先在本页加行 + 在 `tronlink-mcp-core`(SSOT)加 `TL_*` 常量，再在消费端引用——**不要在消费端继续临时造码**。
