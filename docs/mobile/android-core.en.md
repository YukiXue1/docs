# Android Core (Open Source)

**GitHub**: [https://github.com/TronLink/tronlink-android-core](https://github.com/TronLink/tronlink-android-core)

Integrate the wallet functions used by TronLink Android to create a TRON wallet, read its address, and sign transactions or messages.

## Installation

The library requires Android API level 21 or later and Java 8 or later. Add JitPack to the repositories Gradle uses to resolve dependencies (Groovy DSL).

```groovy
repositories {
    maven { url "https://jitpack.io" }
}
```

Add the AAR to the app module’s dependencies.

```groovy
dependencies {
    implementation 'com.github.TronLink:tronlink-android-core:1.0.2@aar'
}
```

## Create a wallet

Create a wallet in your app and read its TRON address.

```java
import org.tron.walletserver.Wallet;

// Inside an application method
Wallet wallet = new Wallet(true);
String address = wallet.getAddress();
```

The wallet tests also show how to restore an address from a mnemonic or private key. For transaction and message signing, see the signing tests. [Wallet examples](https://github.com/TronLink/tronlink-android-core/blob/1.0.2/core/src/test/java/org/tron/WalletCoreUnitTest.java) · [Signing examples](https://github.com/TronLink/tronlink-android-core/blob/1.0.2/core/src/test/java/org/tron/TransactionCoreUnitTest.java)

## Verify the AAR

Verification requires the exact AAR signed by TronLink and its matching detached `.asc` signature. JitPack supplies the AAR alone, and the [1.0.2 release](https://github.com/TronLink/tronlink-android-core/releases/tag/1.0.2) lists no signature attachment. If you need to verify this version, request the signed AAR and matching signature from the maintainers. The [upstream verification instructions](https://github.com/TronLink/tronlink-android-core/blob/1.0.3/README.md#integrity-check) were added in 1.0.3.

Download the [public key](https://keys.openpgp.org/vks/v1/by-fingerprint/7B910EA80207596075E6D7BA5D34F7A6550473BA) as `tronlink-build.asc`. Check the signing subkey fingerprint against the one in the upstream instructions, `7B910EA80207596075E6D7BA5D34F7A6550473BA`. Once it matches, import the key and verify the two files supplied by the maintainers, substituting their filenames below.

```bash
gpg --show-keys --with-subkey-fingerprint tronlink-build.asc
gpg --import tronlink-build.asc
gpg --verify release.aar.asc release.aar
```

## Privacy

Embedding Android Core 1.0.2 does not start usage reporting. This tag predates the `UserStatistics` module, which was introduced in [1.0.8](https://github.com/TronLink/tronlink-android-core/releases/tag/1.0.8).

## Version & License

The upstream installation example uses `1.0.2`. [Apache License 2.0](https://github.com/TronLink/tronlink-android-core/blob/1.0.2/LICENSE)
