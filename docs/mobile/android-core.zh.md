# Android 开源核心库

**GitHub**: [https://github.com/TronLink/tronlink-android-core](https://github.com/TronLink/tronlink-android-core)

在 Android 应用中集成 TronLink 的钱包功能，可以创建 TRON 钱包、读取地址，并对交易或消息签名。

## 安装

环境要求为 Android API 21 及以上、Java 8 及以上。在 Gradle 解析依赖的仓库列表中加入 JitPack。以下示例使用 Groovy DSL。

```groovy
repositories {
    maven { url "https://jitpack.io" }
}
```

在应用模块中声明 AAR 依赖。

```groovy
dependencies {
    implementation 'com.github.TronLink:tronlink-android-core:1.0.2@aar'
}
```

## 创建钱包

在应用中创建钱包并读取 TRON 地址。

```java
import org.tron.walletserver.Wallet;

// 在应用的方法中执行
Wallet wallet = new Wallet(true);
String address = wallet.getAddress();
```

钱包测试还演示了如何通过助记词或私钥恢复地址。交易签名和消息签名的用法见签名测试。[钱包示例](https://github.com/TronLink/tronlink-android-core/blob/1.0.2/core/src/test/java/org/tron/WalletCoreUnitTest.java) · [签名示例](https://github.com/TronLink/tronlink-android-core/blob/1.0.2/core/src/test/java/org/tron/TransactionCoreUnitTest.java)

## 验证 AAR 签名

验签需要 TronLink 签署的 AAR 原件及其配套的独立签名文件 `.asc`。JitPack 只提供 AAR，[1.0.2 发布页](https://github.com/TronLink/tronlink-android-core/releases/tag/1.0.2) 也没有签名附件。如需验证此版本，请向维护者索取签署的 AAR 和配套签名。[上游验签说明](https://github.com/TronLink/tronlink-android-core/blob/1.0.3/README.md#integrity-check) 自 1.0.3 起提供。

下载[发布公钥](https://keys.openpgp.org/vks/v1/by-fingerprint/7B910EA80207596075E6D7BA5D34F7A6550473BA)，保存为 `tronlink-build.asc`。先查看签名子密钥的指纹，与上游公布的 `7B910EA80207596075E6D7BA5D34F7A6550473BA` 核对。一致后导入公钥，再用维护者提供的两个文件验签；请替换下例中的文件名。

```bash
gpg --show-keys --with-subkey-fingerprint tronlink-build.asc
gpg --import tronlink-build.asc
gpg --verify release.aar.asc release.aar
```

## 隐私

集成 Android Core 1.0.2 不会启动使用统计上报。此版本还没有 `UserStatistics` 模块；该模块在 [1.0.8](https://github.com/TronLink/tronlink-android-core/releases/tag/1.0.8) 中引入。

## 版本与许可证

上游安装示例使用 `1.0.2`。[Apache License 2.0](https://github.com/TronLink/tronlink-android-core/blob/1.0.2/LICENSE)
