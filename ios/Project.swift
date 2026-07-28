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
        framework("GameContent",
                  resourceList: [
                      // Установочный бандл: JSON, i18n, арт Рима + общий (prop/ui).
                      "Modules/GameContent/Resources/**",
                      // On-Demand Resources по главам — App Store хостит, качается при открытии.
                      .glob(pattern: "Modules/GameContent/ChapterResources/Tudor.xcassets",
                            tags: ["chapter_tudor"]),
                      .glob(pattern: "Modules/GameContent/ChapterResources/Revolution.xcassets",
                            tags: ["chapter_revolution"]),
                      .glob(pattern: "Modules/GameContent/ChapterResources/Empire.xcassets",
                            tags: ["chapter_empire"]),
                      .glob(pattern: "Modules/GameContent/ChapterResources/Borgia.xcassets",
                            tags: ["chapter_borgia"]),
                      .glob(pattern: "Modules/GameContent/ChapterResources/Byzantium.xcassets",
                            tags: ["chapter_byzantium"]),
                  ],
                  dependencies: [.target(name: "Simulation")]),
        framework("LevelFeature",
                  dependencies: [
                    .target(name: "DesignSystem"),
                    .target(name: "GameContent"),
                    .target(name: "Simulation"),
                  ]),
        framework("MenuFeature",
                  dependencies: [
                    .target(name: "DesignSystem"),
                    .target(name: "GameContent"),
                  ]),
        framework("EpochMapFeature",
                  dependencies: [
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
                // MARK: - Название / версия (версию правь здесь)
                "CFBundleName": "History Teller",
                "CFBundleDisplayName": "History Teller",
                "CFBundleShortVersionString": "1.0",    // маркетинговая версия (видна в App Store)
                "CFBundleVersion": "3",                 // номер сборки — уникален для каждой загрузки в TestFlight
                // MARK: - Категория / соответствие
                "LSApplicationCategoryType": "public.app-category.puzzle-games",
                "ITSAppUsesNonExemptEncryption": false, // своего шифрования нет → без вопроса об экспортном соответствии
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
            ]
        ),
        // Снапшот-тесты доски: рендерят LevelBoardView в PNG для каждого сценария каждого уровня.
        .target(
            name: "SnapshotTests",
            destinations: destinations,
            product: .unitTests,
            bundleId: "com.decima.historyteller.snapshottests",
            deploymentTargets: deployment,
            infoPlist: .default,
            sources: ["Tests/Snapshot/**"],
            dependencies: [
                .external(name: "SnapshotTesting"),
                .target(name: "LevelFeature"),
                .target(name: "GameContent"),
                .target(name: "Simulation"),
                .target(name: "DesignSystem"),
                .target(name: "GameProgress"),
            ]
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
        .scheme(
            name: "SnapshotTests",
            shared: true,
            buildAction: .buildAction(targets: ["SnapshotTests"]),
            testAction: .targets(["SnapshotTests"])
        ),
    ]
)
