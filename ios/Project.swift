import ProjectDescription

let destinations: Destinations = [.iPhone, .iPad]
let deployment: DeploymentTargets = .iOS("17.0")

// Swift 5 language mode на старте миграции — избегаем строгой concurrency-возни в UI-слое,
// пока каркас не устоялся.
let baseSettings: SettingsDictionary = [
    "SWIFT_VERSION": "5.0",
    "CODE_SIGN_STYLE": "Automatic",
    "DEVELOPMENT_TEAM": "LG956X5CL5",
]

/// Откуда приложение берёт контент. Debug-сборка на устройстве ходит на локальный стенд
/// (`tools/publish_content.py --serve 8787`) по адресу Мака в той же Wi-Fi — иначе телефон
/// видит только то, что залито на боевой CDN, и новые уровни на нём не появляются.
/// Адрес переопределяется из командной строки: `xcodebuild HT_CONTENT_BASE_URL=http://…`.
let debugContentURL = "http://192.168.1.68:8787"
let releaseContentURL = "https://cdn.historyteller.app"

func framework(_ name: String,
               sources: SourceFilesList? = nil,
               resources: Bool = false,
               resourceList: ResourceFileElements? = nil,
               dependencies: [TargetDependency] = []) -> Target {
    .target(
        name: name,
        destinations: destinations,
        product: .framework,
        bundleId: "com.decima.historyteller.\(name.lowercased())",
        deploymentTargets: deployment,
        sources: sources ?? ["Modules/\(name)/Sources/**"],
        // resourceList (с ODR-тегами) имеет приоритет над bool-глобом Resources/**
        resources: resourceList ?? (resources ? ["Modules/\(name)/Resources/**"] : nil),
        dependencies: dependencies
    )
}

let project = Project(
    name: "HistoryTeller",
    settings: .settings(base: baseSettings),
    targets: [
        // Чистый движок. Sources совпадают с SPM-пакетом (Package.swift оставлен для `swift test`),
        // но в приложение он входит как обычный динамический фреймворк — линкуется один раз.
        framework("Simulation", sources: ["Modules/Simulation/Sources/Simulation/**"]),
        framework("DesignSystem"),
        framework("GameProgress"),
        // Согласие (Google UMP) + ATT, атрибуция (Tenjin), rewarded-реклама (Google AdMob).
        // Отдельно от фич: сторонние SDK тянутся только сюда.
        framework("Ads", dependencies: [
            .external(name: "TenjinSDK"),
            .external(name: "GoogleMobileAds"),
            .external(name: "GoogleUserMessagingPlatform"),
            .target(name: "GameContent"),   // покупки Store → Tenjin
        ]),
        // Арт — файлами WebP (Resources/Art), не каталогом ассетов: actool перекодирует каталог
        // без потерь и съедает весь выигрыш. ODR отсюда убран — Apple его в фреймворках не
        // поддерживает, теги проставлялись, но не работали; доставку глав берёт на себя ContentSync.
        framework("GameContent",
                  resources: true,
                  dependencies: [.target(name: "Simulation")]),
        framework("LevelFeature",
                  dependencies: [
                    .target(name: "DesignSystem"),
                    .target(name: "GameContent"),
                    .target(name: "Simulation"),
                  ]),
        framework("MenuFeature",
                  dependencies: [
                    .target(name: "Ads"),          // строка «Конфиденциальность» в настройках
                    .target(name: "DesignSystem"),
                    .target(name: "GameContent"),
                    .target(name: "Simulation"),   // онбординг разбирает реальный уровень
                  ]),
        framework("EpochMapFeature",
                  dependencies: [
                    .target(name: "Ads"),          // окно уровня: «открыть за ролик»
                    .target(name: "DesignSystem"),
                    .target(name: "GameContent"),
                    .target(name: "Simulation"),
                    .target(name: "GameProgress"),
                  ]),
        .target(
            name: "HistoryTeller",
            destinations: destinations,
            product: .app,
            productName: "HistoryTeller",
            bundleId: "com.decima.historyteller",
            deploymentTargets: deployment,
            infoPlist: .extendingDefault(with: [
                // MARK: - Источник контента (см. debugContentURL выше)
                "HTContentBaseURL": "$(HT_CONTENT_BASE_URL)",
                // Стенд раздаётся по http на серый адрес — для Debug это надо разрешить явно,
                // и iOS отдельно спросит разрешение на локальную сеть.
                "NSAppTransportSecurity": ["NSAllowsLocalNetworking": true],
                "NSLocalNetworkUsageDescription":
                    "Загрузка контента с локального стенда разработки.",
                // MARK: - Название / версия (версию правь здесь)
                "CFBundleName": "History Teller",
                "CFBundleDisplayName": "History Teller",
                "CFBundleShortVersionString": "3.0.1",  // маркетинговая версия (видна в App Store)
                "CFBundleVersion": "1",                 // номер сборки — уникален для каждой загрузки в TestFlight
                // MARK: - Категория / соответствие
                "LSApplicationCategoryType": "public.app-category.puzzle-games",
                "ITSAppUsesNonExemptEncryption": false, // своего шифрования нет → без вопроса об экспортном соответствии
                // MARK: - Реклама / согласие
                // Копии SKAdNetwork-постбэков уходят в Tenjin (атрибуция закупки на iOS).
                "NSAdvertisingAttributionReportEndpoint": "https://tenjin-skan.com",
                // App ID History Teller в AdMob — без него SDK Google падает на старте.
                "GADApplicationIdentifier": "ca-app-pub-6335946344432887~7440324473",
                // SKAdNetwork: Google (атрибуция показов рекламы на iOS 14+). Сети медиации — по мере подключения.
                "SKAdNetworkItems": [["SKAdNetworkIdentifier": "cstr6suwn9.skadnetwork"]],
                "NSUserTrackingUsageDescription":
                    "Your data will be used to show you more relevant ads and to measure where players come from.",
                "LSRequiresIPhoneOS": true,
                // MARK: - Устройства (iPhone + iPad)
                "UIDeviceFamily": [1, 2],
                // MARK: - Запуск / полноэкранность
                "UILaunchScreen": [:],
                "UIRequiresFullScreen": true,
                // MARK: - Ориентация (только ландшафт)
                "UISupportedInterfaceOrientations": [
                    "UIInterfaceOrientationLandscapeLeft",
                    "UIInterfaceOrientationLandscapeRight",
                ],
                "UISupportedInterfaceOrientations~ipad": [
                    "UIInterfaceOrientationLandscapeLeft",
                    "UIInterfaceOrientationLandscapeRight",
                ],
            ]),
            sources: ["App/Sources/**"],
            resources: ["App/Resources/**"],
            dependencies: [
                .target(name: "LevelFeature"),
                .target(name: "MenuFeature"),
                .target(name: "EpochMapFeature"),
                .target(name: "GameProgress"),
                .target(name: "DesignSystem"),
                .target(name: "GameContent"),
                .target(name: "Simulation"),
                .target(name: "Ads"),
            ],
            settings: .settings(configurations: [
                .debug(name: "Debug", settings: ["HT_CONTENT_BASE_URL": .string(debugContentURL)]),
                .release(name: "Release", settings: ["HT_CONTENT_BASE_URL": .string(releaseContentURL)]),
            ])
        ),
    ],
    schemes: [
        .scheme(
            name: "HistoryTeller",
            shared: true,
            buildAction: .buildAction(targets: ["HistoryTeller"]),
            runAction: .runAction(
                configuration: "Debug",
                // StoreKit-конфиг для локального теста покупок в Xcode
                options: .options(storeKitConfigurationPath: .relativeToManifest("App/Store.storekit"))
            )
        ),
    ]
)
