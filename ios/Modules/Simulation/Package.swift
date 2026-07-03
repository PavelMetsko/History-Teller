// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "Simulation",
    products: [
        .library(name: "Simulation", targets: ["Simulation"]),
    ],
    targets: [
        .target(name: "Simulation"),
        .testTarget(
            name: "SimulationTests",
            dependencies: ["Simulation"]
        ),
    ]
)
