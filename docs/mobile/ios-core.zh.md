# iOS 开源核心库

**GitHub**: [https://github.com/TronLink/tronlink-iOS-core](https://github.com/TronLink/tronlink-iOS-core)

在 iOS 应用中使用 TronLink 的原生钱包模块，可以创建 TRON 钱包、读取地址，并对交易或消息签名。

## 安装

该 Pod 支持 iOS 15.1 及以上，声明的 Swift 版本为 4.2。在 Podfile 中为应用 target 添加依赖。

```ruby
pod 'tronlink-iOS-core', '2.0.1'
```

运行 `pod install`，用 Xcode 打开生成的 `.xcworkspace`，然后在 Swift 文件中导入模块。

```swift
import TLCore
```

## 运行示例工程

要在上游 Xcode 示例工程中查看钱包 API 的用法，请先进入示例目录安装依赖。

```bash
git clone --branch 2.0.1 https://github.com/TronLink/tronlink-iOS-core.git
cd tronlink-iOS-core/Example
pod install
```

在 Xcode 中打开 `Example/` 下的工作区。Swift 测试展示了创建钱包、签署交易和消息，以及导出私钥或助记词的用法。[Swift 钱包示例](https://github.com/TronLink/tronlink-iOS-core/blob/2.0.1/Example/Tests/Tests.swift)

## 隐私

安装 Pod 或创建钱包不会自动上传统计数据。要启用上传，集成方需要主动调用上报方法，实现 `TRXMetricsDataSource` 的上传回调，并将应用当前连接的环境标记为生产或预发布。Debug 和 Release 构建都遵循这项检查。TronLink iOS 还会在基础模式、观察钱包和 Shasta 测试网下停用上报。[iOS 隐私说明](https://github.com/TronLink/tronlink-iOS-core/blob/2.0.1/PRIVACY-POLICY.md)

## 版本与许可证

版本为 `2.0.1`。[Podspec](https://github.com/TronLink/tronlink-iOS-core/blob/2.0.1/tronlink-iOS-core.podspec) · [Apache License 2.0](https://github.com/TronLink/tronlink-iOS-core/blob/2.0.1/LICENSE)
