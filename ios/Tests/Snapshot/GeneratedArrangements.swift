enum GeneratedArrangements {
    typealias Case = (level: String, name: String, panels: [(scene: String?, chars: [String])])
    static let all: [Case] = [
    (level: "caesar_crown", name: "SOLVED__palace-caesar.cleopatra__forum-caesar.antony__lupercalia-antony.caesar", panels: [(scene: "palace", chars: ["caesar", "cleopatra"]), (scene: "forum", chars: ["caesar", "antony"]), (scene: "lupercalia", chars: ["antony", "caesar"])]),
    (level: "triumvirate", name: "SOLVED__forum-antony.octavian__back_room-antony.octavian__proscription-antony.octavian.brutus", panels: [(scene: "forum", chars: ["antony", "octavian"]), (scene: "back_room", chars: ["antony", "octavian"]), (scene: "proscription", chars: ["antony", "octavian", "brutus"])]),
    (level: "tarsus", name: "SOLVED__barge-apollodorus.cleopatra__palace-antony.cleopatra", panels: [(scene: "barge", chars: ["apollodorus", "cleopatra"]), (scene: "palace", chars: ["antony", "cleopatra"])]),
    ]
}
