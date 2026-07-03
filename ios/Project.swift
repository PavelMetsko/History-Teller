import ProjectDescription

let destinations: Destinations = [.iPhone, .iPad]
let deployment: DeploymentTargets = .iOS("17.0")

// Swift 5 language mode на старте миграции — избегаем строгой concurrency-возни в UI-слое,
// пока каркас не устоялся.
let baseSettings: SettingsDictionary = [
    "SWIFT_VERSION": "5.0",
    "CODE_SIGN_STYLE": "Automatic",
]

func framework(_ name: String,
               sources: SourceFilesList? = nil,
               resources: Bool = false,
               dependencies: [TargetDependency] = []) -> Target {
    .target(
        name: name,
        destinations: destinations,
        product: .framework,
        bundleId: "com.decima.historyteller.\(name.lowercased())",
        deploymentTargets: deployment,
        sources: sources ?? ["Modules/\(name)/Sources/**"],
        resources: resources ? ["Modules/\(name)/Resources/**"] : nil,
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
            bundleId: "com.decima.historyteller",
            deploymentTargets: deployment,
            infoPlist: .extendingDefault(with: [
                "UILaunchScreen": [:],
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
    ]
)
