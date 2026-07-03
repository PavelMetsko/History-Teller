import Foundation

private final class BundleToken {}

public extension Bundle {
    /// Бандл с контентом эпохи (JSON + Assets.xcassets). Устойчиво находим его независимо
    /// от того, куда Tuist положил ресурсы: в сам фреймворк, во вложенный .bundle или в app.
    static let gameContent: Bundle = {
        let frameworkResources = Bundle(for: BundleToken.self).resourceURL
        let candidates: [URL?] = [
            frameworkResources,
            frameworkResources?.appendingPathComponent("GameContent_GameContent.bundle"),
            frameworkResources?.appendingPathComponent("GameContent.bundle"),
            Bundle.main.resourceURL,
            Bundle.main.resourceURL?.appendingPathComponent("GameContent_GameContent.bundle"),
        ]
        for case let url? in candidates {
            if let bundle = Bundle(url: url),
               bundle.url(forResource: "characters", withExtension: "json") != nil {
                return bundle
            }
        }
        return Bundle(for: BundleToken.self)
    }()
}
