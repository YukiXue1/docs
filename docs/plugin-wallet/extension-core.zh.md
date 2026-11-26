# 插件开源核心库

**GitHub**: [https://github.com/TronLink/tronlink-extension-core](https://github.com/TronLink/tronlink-extension-core)

`@tronlink/core` 是 TronLink 插件使用的 JavaScript / TypeScript 钱包库。钱包应用可以用它派生 TRON 和 EVM 账户，并在本地签名。DApp 如需连接用户已安装的 TronLink 插件并请求签名，请使用[插件提供的接口](active-requests.zh.md)。

## 安装

通过 npm 安装。该包提供 CommonJS、ES 模块入口以及 TypeScript 类型声明。

```bash
npm install @tronlink/core@1.1.4
```

项目指定 Node.js `24.22.1`，开发使用 pnpm `10.12.4`。TypeScript 项目需要 `4.9.5` 及以上版本。面向浏览器打包时，需要为 `buffer`、`crypto`、`stream` 等 Node 模块配置 polyfill。[上游 webpack 配置](https://github.com/TronLink/tronlink-extension-core/blob/1.1.4/webpack.config.js) · [1.1.4 环境要求](https://github.com/TronLink/tronlink-extension-core/blob/1.1.4/README.md#prerequisites)

## 派生 TRON 地址

生成助记词，获取第一个账户下第一个地址的派生路径，再用该路径派生私钥并计算地址。

```ts
import { BaseWallet, TronWallet } from '@tronlink/core';

const wallet = new TronWallet();
const mnemonic = BaseWallet.generateRandomMnemonic();
const path = wallet.derivePath({ accountIndex: 0, addressIndex: 0 });
const privateKey = wallet.derivePrivateKey({ mnemonic, path });
const address = wallet.getAddressBy({ privateKey });
```

派生 EVM 地址时，使用 `EvmWallet` 的 `derivePath` 获取对应路径，再派生私钥。[TRON 与 EVM 账户示例](https://github.com/TronLink/tronlink-extension-core/blob/1.1.4/demo/create_account.ts)

## 签名

两个钱包类都支持交易、消息和结构化数据签名。对 TRON 交易签名时，将已构建的交易传入 `wallet.signTransaction({ privateKey, data: rawTransaction })`。对 EVM 交易签名时，在 `data` 中提供链配置和未签名交易。签名结果在本地返回，广播需另行执行。[TRON 签名示例](https://github.com/TronLink/tronlink-extension-core/blob/1.1.4/demo/tron_signature.ts) · [EVM 签名示例](https://github.com/TronLink/tronlink-extension-core/blob/1.1.4/demo/evm_signature.ts)

## Ledger 与使用统计

Ledger 签名要求浏览器提供 `navigator.hid`。使用设备上的 TRX 应用时选择 `LedgerTrxSigner`，使用 ETH 应用时选择 `LedgerEvmSigner`。

导入包、派生地址或在本地签名都不会自动上传统计数据。启用上报需要宿主调用 `checkAndReportXY(deps)` 并提供上传回调。可选的 `userStatistics` 模块使用设备上为地址分配的 UUID，按日期和金额区间汇总主网活动。[隐私与上报说明](https://github.com/TronLink/tronlink-extension-core/blob/1.1.4/PRIVACY.md)

## 版本与许可证

包版本为 `1.1.4`。[包配置](https://github.com/TronLink/tronlink-extension-core/blob/1.1.4/package.json) · [Apache License 2.0](https://github.com/TronLink/tronlink-extension-core/blob/1.1.4/LICENSE)
