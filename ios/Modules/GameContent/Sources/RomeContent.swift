import Foundation
import Simulation

/// Загрузка контент-пака эпохи «Рим» из бандла (JSON лежит рядом с движком-агностиком).
public enum RomeContent {

    public struct Pack {
        public let db: ContentDb
        public let levels: [LevelDef]
    }

    /// Порядок попыток загрузки уровней. Отсутствующие тихо пропускаются.
    private static let levelIds = [
        "cleopatra_charm",
        "caesar_crown",
        "cleopatra_throne",
        "cleopatra_heir",
        "rivals",
        "caesar_assassination",
        "philippi",
    ]

    public static func load() throws -> Pack {
        let bundle = Bundle.gameContent
        func json(_ name: String) throws -> String {
            guard let url = bundle.url(forResource: name, withExtension: "json") else {
                throw NSError(domain: "GameContent", code: 1,
                              userInfo: [NSLocalizedDescriptionKey: "Не найден ресурс \(name).json"])
            }
            return try String(contentsOf: url, encoding: .utf8)
        }

        let db = try ContentDb.fromJson(
            charactersJson: try json("characters"),
            scenesJson: try json("scenes"),
            rulesJson: try json("rules"))

        var levels: [LevelDef] = []
        for id in levelIds {
            guard let raw = try? json(id) else { continue }
            levels.append(try ContentDb.loadLevel(raw))
        }
        return Pack(db: db, levels: levels.sorted { $0.order < $1.order })
    }
}
