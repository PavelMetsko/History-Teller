// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "HistoryTeller",
    dependencies: [
        // Атрибуция установок и покупок (MMP) — нужна для закупки в AppLovin.
        .package(url: "https://github.com/tenjin/tenjin-ios-sdk.git", from: "1.20.1"),
    ]
)
