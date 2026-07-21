# 开始开发

本文档以端到端方式带你完成 DApp 与 TronLink 钱包的对接 — 从检测钱包、请求授权，到签名并广播一笔交易。

## 概述

TronLink 是一款面向 TRON 网络的浏览器扩展钱包。DApp 只要集成 TronLink，便能与 TRON 网络进行通信 — TronLink 会向每个页面注入 `window.tron` 对象，对外暴露 `tronWeb` 实例、`request` 方法以及 `on` / `removeListener` 等事件订阅能力。

## `window.tron` 对象

```typescript
interface TronProvider {
  isTronLink: true;
  request: (args: { method: string; params?: any }) => Promise<any>;       // 调用钱包能力（如 eth_requestAccounts）
  tronWeb: TronWeb | false;                                                // 用户授权后与当前账户/网络绑定；授权前为 `false`
  on(event: string, listener: (...args: any[]) => void): this;             // 订阅 provider 事件（accountsChanged / chainChanged / connect）
  removeListener(event: string, listener: (...args: any[]) => void): this;
}
```

用户完成授权后，`window.tron.tronWeb` 即可用于构建、签名与广播交易。

## 检测 TronLink（TIP-6963）

TIP-6963 是检测 TronLink（及其他 TRON 钱包）的推荐方式，避免污染全局命名空间。监听 `TIP6963:announceProvider` 事件，并派发 `TIP6963:requestProvider` 让已安装的钱包主动声明自己。

```javascript
let tronProvider;

window.addEventListener("TIP6963:announceProvider", (e) => {
  if (e.detail.info && e.detail.info.name === "TronLink") {
    tronProvider = e.detail.provider; // === window.tron
  }
});

window.dispatchEvent(new Event("TIP6963:requestProvider"));
```

如果派发请求后 `tronProvider` 仍为 undefined，则说明用户未安装 TronLink，可提示用户进行安装。

## 请求授权 {#request-authorization}

通过 `eth_requestAccounts` 请求用户授权连接钱包。用户同意时 Promise resolve 为一个仅含当前选中地址的数组；失败时 Promise reject，错误对象形如 `{ code, message }`。

```typescript
try {
  const accounts: string[] = await tronProvider.request({ method: "eth_requestAccounts" });
  console.log("已连接：", accounts[0]);
} catch (err) {
  // err 结构：{ code: number, message: string }
  console.warn("授权失败：", err);
}
```

| code   | 说明 |
| ------ | ---- |
| 4001   | 用户拒绝请求 —— 点击**拒绝**、关闭弹窗，或请求不是来自当前活跃标签页 |
| -32000 | 钱包处于锁定状态时，同一来源 20 秒内重复发起 `eth_requestAccounts`（频控） |
| 4200   | 不支持的方法 |

完整的 TIP-1102（`eth_requestAccounts`）规范请参考 [主动请求 TronLink 插件功能](../plugin-wallet/active-requests.md)；旧版 `tron_requestAccounts` 连接方式也在同一页内。

## 获取 `tronWeb` 实例

简化版 helper —— 如果用户已授权过当前 DApp，直接复用已有的 `tronWeb` 实例，否则发起授权请求。

```javascript
async function getTronWeb() {
  if (!tronProvider) throw new Error("未检测到 TronLink");
  if (tronProvider.tronWeb?.ready) {
    return tronProvider.tronWeb;
  }
  await tronProvider.request({ method: "eth_requestAccounts" });
  return tronProvider.tronWeb;
}
```

`tronProvider.tronWeb` 通常在 `eth_requestAccounts` resolve 后即可使用。后续用户切换账号、锁屏、切换网络等情况，请在 provider 上监听 `accountsChanged` / `chainChanged` 事件，完整事件清单见 [被动接收 TronLink 插件的消息](../plugin-wallet/passive-messages.md)。

获取 `tronWeb` 实例后，即可执行链上交互：TRX/TRC20 转账、多签交易、消息签名、合约调用等。完整的 `tronWeb` API 用法请参考 [TronWeb 文档](https://tronweb.network/docu/docs/intro)。

## 端到端示例：签名并广播一笔 TRX 转账

下面这个独立的 HTML 示例通过 TIP-6963 检测 TronLink、请求授权、构建一笔 TRX 转账、在 TronLink 弹窗中提示用户签名，然后将签名后的交易广播到链上。

```html
<!DOCTYPE html>
<html lang="zh">
  <head>
    <meta charset="UTF-8" />
    <title>TronLink Demo</title>
  </head>
  <body>
    <button onclick="connect()">连接 TronLink</button>
    <script>
      let tronProvider;

      window.addEventListener("TIP6963:announceProvider", (e) => {
        if (e.detail.info && e.detail.info.name === "TronLink") {
          tronProvider = e.detail.provider;
        }
      });
      window.dispatchEvent(new Event("TIP6963:requestProvider"));

      async function connect() {
        if (!tronProvider) return alert("未检测到 TronLink！");
        try {
          const accounts = await tronProvider.request({
            method: "eth_requestAccounts",
          });
          console.log("已连接：", accounts[0]);

          const tronweb = tronProvider.tronWeb;
          const from = tronweb.defaultAddress.base58;
          const to = "TN9RRaXkCFtTXRso2GdTZxSxxwufzxLQPP"; // 请替换为真实的收款地址

          // 构建一笔 10 SUN 的 TRX 转账（金额单位为 SUN：1 TRX = 1_000_000 SUN）
          const tx = await tronweb.transactionBuilder.sendTrx(to, 10, from);

          // 弹出 TronLink 确认窗口
          const signedTx = await tronweb.trx.sign(tx);

          // 广播到网络
          const broadcastTx = await tronweb.trx.sendRawTransaction(signedTx);
          console.log(broadcastTx);
        } catch (error) {
          // 用户拒绝时为 { code: 4001, message: "User rejected the request." }
          console.error(error);
        }
      }
    </script>
  </body>
</html>
```

## 相关文档

- [主动请求 TronLink 插件功能](../plugin-wallet/active-requests.md) — 完整的请求/响应说明
- [被动接收 TronLink 插件的消息](../plugin-wallet/passive-messages.md) — 账户 / 网络变化事件
- [普通转账](transfer.md)、[多签转账](multi-sign-transfer.md)、[消息签名](message-signing.md)、[Stake 2.0](stake2.md)
- [TronWeb 文档](https://tronweb.network/docu/docs/intro)
