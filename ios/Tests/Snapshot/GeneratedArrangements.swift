enum GeneratedArrangements {
    typealias Case = (level: String, name: String, panels: [(scene: String?, chars: [String])])
    static let all: [Case] = [
    (level: "pompey_death", name: "wrong_order_test", panels: [(scene: "harbor", chars: ["pompey", "ptolemy"]), (scene: "egypt_court", chars: ["caesar", "ptolemy"])]),
    (level: "bosworth", name: "test", panels: [(scene: "bosworth_turn", chars: ["stanley", "henry7"]), (scene: "bosworth_field", chars: ["richard3", "henry7"]), (scene: "bosworth_crown", chars: ["henry7", "stanley"])]),
    ]
}
