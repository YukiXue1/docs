# iOS Core (Open Source)

**GitHub**: [https://github.com/TronLink/tronlink-iOS-core](https://github.com/TronLink/tronlink-iOS-core)

Use TronLink’s native iOS wallet module to create a TRON wallet, read its address, and sign transactions or messages.

## Installation

The pod targets iOS 15.1 or later and declares Swift 4.2. Add the dependency to your app target in the Podfile.

```ruby
pod 'tronlink-iOS-core', '2.0.1'
```

Run `pod install`, open the generated `.xcworkspace` in Xcode, and import the module in Swift.

```swift
import TLCore
```

## Run the example project

To explore the wallet APIs in the upstream Xcode project, install its pods from the example directory.

```bash
git clone --branch 2.0.1 https://github.com/TronLink/tronlink-iOS-core.git
cd tronlink-iOS-core/Example
pod install
```

Open the workspace in `Example/`. The Swift tests show wallet creation, transaction and message signing, and how to export a private key or mnemonic. [Swift wallet examples](https://github.com/TronLink/tronlink-iOS-core/blob/2.0.1/Example/Tests/Tests.swift)

## Privacy

Installing the pod or creating a wallet does not start a statistics upload. The host app must invoke the reporter and implement the upload callback in `TRXMetricsDataSource`. To enable uploads, the app must also identify its environment as production or pre-release. The same check applies to Debug and Release builds. In TronLink iOS, Basic Mode suppresses reporting, as do watch-only wallets and Shasta activity. [iOS privacy policy](https://github.com/TronLink/tronlink-iOS-core/blob/2.0.1/PRIVACY-POLICY.md)

## Version & License

Version `2.0.1`. [Podspec](https://github.com/TronLink/tronlink-iOS-core/blob/2.0.1/tronlink-iOS-core.podspec) · [Apache License 2.0](https://github.com/TronLink/tronlink-iOS-core/blob/2.0.1/LICENSE)
