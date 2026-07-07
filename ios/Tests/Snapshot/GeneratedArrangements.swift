enum GeneratedArrangements {
    typealias Case = (level: String, name: String, panels: [(scene: String?, chars: [String])])
    static let all: [Case] = [
    (level: "union", name: "SOLVED__chapel-henry7.eliz_york__chamber-henry7.eliz_york__tower-henry7.warbeck", panels: [(scene: "chapel", chars: ["henry7", "eliz_york"]), (scene: "chamber", chars: ["henry7", "eliz_york"]), (scene: "tower", chars: ["henry7", "warbeck"])]),
    (level: "jane_seymour", name: "SOLVED__tower-henry.boleyn__chapel-henry.seymour__chamber-henry.seymour", panels: [(scene: "tower", chars: ["henry", "boleyn"]), (scene: "chapel", chars: ["henry", "seymour"]), (scene: "chamber", chars: ["henry", "seymour"])]),
    (level: "jane_grey", name: "SOLVED__council-northumberland.jane_grey__court-mary1.jane_grey__tower-mary1.jane_grey", panels: [(scene: "council", chars: ["northumberland", "jane_grey"]), (scene: "court", chars: ["mary1", "jane_grey"]), (scene: "tower", chars: ["mary1", "jane_grey"])]),
    (level: "bloody_mary", name: "SOLVED__abbey-mary1__chapel-philip.mary1__court-mary1__stake-mary1.cranmer", panels: [(scene: "abbey", chars: ["mary1"]), (scene: "chapel", chars: ["philip", "mary1"]), (scene: "court", chars: ["mary1"]), (scene: "stake", chars: ["mary1", "cranmer"])]),
    (level: "elizabeth", name: "SOLVED__abbey-elizabeth__court-elizabeth.dudley", panels: [(scene: "abbey", chars: ["elizabeth"]), (scene: "court", chars: ["elizabeth", "dudley"])]),
    (level: "mary_stuart", name: "SOLVED__spy_room-walsingham.mary_stuart__tower-elizabeth.mary_stuart", panels: [(scene: "spy_room", chars: ["walsingham", "mary_stuart"]), (scene: "tower", chars: ["elizabeth", "mary_stuart"])]),
    (level: "armada", name: "SOLVED__fireships-drake.philip__sea_battle-elizabeth.philip", panels: [(scene: "fireships", chars: ["drake", "philip"]), (scene: "sea_battle", chars: ["elizabeth", "philip"])]),
    ]
}
