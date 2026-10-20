// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "HistoryTeller",
    dependencies: [
        // Атрибуция установок и покупок (MMP) — нужна для закупки в AppLovin.
        .package(url: "https://github.com/tenjin/tenjin-ios-sdk.git", from: "1.20.1"),
        // Rewarded-реклама (Google AdMob) и согласие GDPR (Google UMP — сертифицированный CMP,
        // без него AdMob в ЕЭЗ рекламу не показывает). Форма согласия — в AdMob → Privacy & messaging.
        .package(url: "https://github.com/googleads/swift-package-manager-google-mobile-ads.git", from: "13.11.0"),
        .package(url: "https://github.com/googleads/swift-package-manager-google-user-messaging-platform.git", from: "3.1.0"),
    ]
)
