# 被动接收TronLink插件的消息

TronLink 支持 TRON 主网及测试网（Shasta、Nile）。开发者可以在 DApp 中监听 TronLink 派发的事件消息，以判断当前选择的网络以及当前激活的账户。下面通过一个简单示例进行演示。

```html
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TronLink Events Demo</title>
</head>
<body>
<script>
    // 1. 通过 TIP-6963 发现 TronLink provider，并在该 provider 上注册事件监听
    let tron;
    window.addEventListener("TIP6963:announceProvider", (e) => {
        if (e.detail.info && e.detail.info.name === "TronLink") {
            tron = e.detail.provider; // === window.tron
            console.log("TronLink 检测成功！");

            tron.on("accountsChanged", (accounts) => {
                console.log("accountsChanged", accounts); // 钱包锁定时为 []
            });
            tron.on("chainChanged", ({ chainId }) => {
                console.log("chainChanged", chainId);
            });
            tron.on("connect", ({ chainId }) => {
                console.log("connect", chainId);
            });
        }
    });
    // 让已加载的钱包重新公告自己
    window.dispatchEvent(new Event("TIP6963:requestProvider"));

    // 2. 原始 window.postMessage 事件 — 涵盖旧版 3.x 事件与授权流程
    window.addEventListener("message", function (e) {
        if (!e.data || !e.data.message) return;
        const { action, data } = e.data.message;

        switch (action) {
            // --- 历史授权事件（兼容 3.x，未来版本将废弃） ---
            case "connectWeb":
                console.log("connectWeb", data);
                break;
            case "acceptWeb":
                console.log("acceptWeb", data);
                break;
            case "rejectWeb":
                console.log("rejectWeb", data);
                break;
            case "disconnectWeb":
                console.log("disconnectWeb", data);
                break;

            // --- 已废弃的 3.x 事件（主链 / 侧链检测） ---
            case "tabReply":
                if (data?.data?.node?.chain === "_") {
                    console.log("tronLink 当前选择主链");
                } else {
                    console.log("tronLink 当前选择侧链");
                }
                break;
            case "setAccount":
                console.log("setAccount，当前地址：", data.address);
                break;
            case "setNode":
                if (data?.node?.chain === "_") {
                    console.log("tronLink 当前选择主链");
                } else {
                    console.log("tronLink 当前选择侧链");
                }
                break;
        }
    });
</script>
</body>
</html>
```

下面分别对每个监听器进行详细说明，含返回值与截图。

---

## 检测 TronLink（TIP-6963）

事件标识：`TIP6963:announceProvider`

### 简介

TronLink 通过 TIP-6963 协议对外公告自己的 provider 对象。监听 `TIP6963:announceProvider` 并派发 `TIP6963:requestProvider`，即可安全地发现钱包，无需污染全局命名空间或轮询 `window.tron`。announce 事件返回的 provider 即为 `window.tron`。

完整的 TIP-6963 规范请参考 [主动请求 TronLink 插件功能](./active-requests.md#get-tronlink-provider-via-tip-6963)。

### 技术规范

#### 代码示例

```javascript
let tron;
window.addEventListener('TIP6963:announceProvider', (e) => {
  if (e.detail.info && e.detail.info.name === 'TronLink') {
    tron = e.detail.provider; // === window.tron
    console.log('TronLink 检测成功！');
  }
});
// 让已加载的钱包重新公告自己
window.dispatchEvent(new Event('TIP6963:requestProvider'));
```

如果派发请求后 `tron` 仍为 undefined，则说明用户未安装 TronLink，可提示用户进行安装。

## 账户改变消息

消息标识： `accountsChanged`
### 简介
以下情况会产生此消息

  1. 用户登录

  2. 用户切换账号

  3. 用户锁定钱包

  4. 钱包超时自动锁定

### 技术规范
#### 代码示例
```typescript
window.tron.on('accountsChanged', (accountArray) => {
  // handler logic
  console.log('got accountsChanged event', accountArray)
})
```
#### 返回值
```typescript
['your_current_account_address']
```
##### 返回值示例
1. 用户登录时，消息体内容为
```javascript
['TZ5XixnRyraxJJy996Q1sip85PHWuj4793'] // 当前的账号
```

2. 用户切换账号时，消息体内容为
```javascript
['TRKb2nAnCBfwxnLxgoKJro6VbyA6QmsuXq'] // 新选择的账号地址
```

3. 用户锁定和钱包超时自动锁定时，消息体内容为
```javascript
[]
```

> **旧版用法（不推荐）：** [setAccount（3.x）](#setaccount)


## 网络改变消息

消息标识： `chainChanged`
### 简介
开发者可以监听此消息来获取网络的改变
以下情况会产生此消息

1. 用户改变网络的时候
### 技术规范
#### 代码示例
```typescript
window.tron.on('chainChanged', ({chainId}) => {
  // handler logic
  console.log('got chainChanged event', chainId)
})
```

#### 返回值

```typescript
{
  chainId: string;
}
```
- 目前只支持如下chainId：
  - mainnet(主网): `0x2b6653dc`
  - shasta(shasta测试网): `0x94a9059e`
  - nile(nile测试网): `0xcd8690dc`
- chainId的值大小写敏感。

> **旧版用法（不推荐）：** [setNode（3.x）](#setnode) 或 [tabReply（3.x）](#tabreply)

## TronLink可以提供服务的消息

消息标识： `connect`
### 简介
如果 TronLink 及 `window.tron` 对象可用，此事件会在 provider 初始化完成后被派发一次（包含 `disconnect` 之后重新连接的场景）。

**时序注意**：该事件在插件 init 完成后约 100ms 派发。如果 DApp 的监听器在插件 init 之后才注册（例如页面加载较慢、通过 TIP-6963 `requestProvider` 才拿到 provider），则可能错过 `connect` 事件。此时直接把"provider 存在"视作已连接，并结合 `tron.tronWeb?.ready` 判断当前状态即可。

### 技术规范
#### 代码示例
```typescript
window.tron.on('connect', ({chainId}) => {
  // handler logic
  console.log('got connect event', chainId)
})
```

> **旧版用法（不推荐）：** [connectWeb（postMessage）](#connectweb) 或 [acceptWeb（postMessage）](#acceptweb)

## 断开连接网站消息
消息标识： `disconnect`
### 简介
TIP-1193 规范规定：当 provider 与所有链断开连接时，应派发 `disconnect` 事件并携带 `ProviderRpcError` 对象。

**当前 TronLink 行为**：TronLink 目前 **不会** 在 provider 上派发 `disconnect`。当用户断开网站（或钱包被锁定）时，会通过 `accountsChanged` 派发空数组 `[]` 来表示——在 TronLink 实现 `disconnect` 之前，请以此作为断连信号。

### 技术规范
#### 代码示例
```typescript
// 规范保留事件——注册监听器无害，但当前不会被触发。
window.tron.on('disconnect', (providerRpcError) => {
  console.error(providerRpcError); // { code: 4900, message: 'Disconnected' }
})
```

> **旧版用法（不推荐）：** [disconnectWeb（postMessage）](#disconnectweb) 或 [rejectWeb（postMessage）](#rejectweb)

## 历史遗留问题

以下消息通过 `window.postMessage` 派发，DApp 接收到的内容是一个 `MessageEvent`，事件结构可参考 [MessageEvent 的 MDN 文档](https://developer.mozilla.org/en-US/docs/Web/API/MessageEvent)。

以下四个消息为了兼容 3.x 保留，并在未来版本将会被废弃：

1. 用户拒绝连接消息`rejectWeb`

2. 用户断连网站消息`disconnectWeb`

3. 用户确定连接消息`acceptWeb`

4. 用户主动连接网站消息`connectWeb`

### 用户拒绝连接消息 rejectWeb
消息标识： `rejectWeb`

以下情况会产生此消息

1. dapp请求连接，用户在弹窗中拒绝连接后
 
![TronLink 连接弹窗，用户点击"拒绝"触发 rejectWeb 事件](../images/zh_plugin-wallet_rejectWeb.png)


开发者可以监听此消息来获取用户拒绝连接消息
```typescript
window.addEventListener('message', function (e) {
  if (e.data.message && e.data.message.action == "rejectWeb") {
      // handler logic
      console.log('got rejectWeb event', e.data)
  }
})
```

### 用户断连网站消息 disconnectWeb
消息标识： `disconnectWeb`

以下情况会产生此消息

1. 用户主动断开连接

![TronLink 已连接站点列表，用户对某 DApp 点击"断开"触发 disconnectWeb 事件](../images/zh_plugin-wallet_disconnectWeb.png)


开发者可以监听此消息来获取用户主动断连消息
```typescript
window.addEventListener('message', function (e) {
  if (e.data.message && e.data.message.action == "disconnectWeb") {
      // handler logic
      console.log('got disconnectWeb event', e.data)
  }
})
```

### 用户确定连接消息 acceptWeb
消息标识： `acceptWeb`

以下情况会产生此消息

1. 用户确定连接消息


![TronLink 连接弹窗，用户点击"接受"触发 acceptWeb 事件](../images/zh_plugin-wallet_acceptWeb.png)

开发者可以监听此消息来获取用户确定连接消息
```typescript
window.addEventListener('message', function (e) {
  if (e.data.message && e.data.message.action == "acceptWeb") {
      // handler logic
      console.log('got acceptWeb event', e.data)
  }
})
```

### 用户主动连接网站消息 connectWeb
消息标识： `connectWeb`

以下情况会产生此消息

1. 用户主动连接网站时


![TronLink 已连接站点列表，用户主动对某授权 DApp 点击"连接"触发 connectWeb 事件](../images/zh_plugin-wallet_connectWeb.png)


开发者可以监听此消息来获取用户主动连接网站消息
```typescript
window.addEventListener('message', function (e) {
  if (e.data.message && e.data.message.action == "connectWeb") {
      // handler logic
      console.log('got connectWeb event', e.data)
  }
})
```

---

## 已废弃的 3.x 事件（主链 / 侧链）

以下事件是 TronLink 3.x 通过原始 `window.postMessage` 用于检测当前网络与账户的方式。它们已被 `window.tron` 上的 `accountsChanged` / `chainChanged` 取代，仅供存量代码参考 — 新接入请勿使用。

### 网络初始化（`tabReply`）

页面加载后 TronLink 完成初始化时触发一次。检查 `e.data.message.data.data.node.chain`：值为 `'_'` 表示主链，其他值表示对应侧链标识。

```javascript
window.addEventListener('message', function (e) {
  if (e.data.message && e.data.message.action == "tabReply") {
    if (e.data.message.data.data.node.chain == '_') {
      console.log("tronLink 当前选择主链");
    } else {
      console.log("tronLink 当前选择侧链");
    }
  }
});
```

### 账户切换（`setAccount`）

用户切换当前账户时触发。

```javascript
window.addEventListener('message', function (e) {
  if (e.data.message && e.data.message.action == "setAccount") {
    console.log("当前地址：", e.data.message.data.address);
  }
});
```

### 网络切换（`setNode`）

用户切换网络时触发。`chain == '_'` 的判断方式与 `tabReply` 相同。

```javascript
window.addEventListener('message', function (e) {
  if (e.data.message && e.data.message.action == "setNode") {
    if (e.data.message.data.node.chain == '_') {
      console.log("tronLink 当前选择主链");
    } else {
      console.log("tronLink 当前选择侧链");
    }
  }
});
```