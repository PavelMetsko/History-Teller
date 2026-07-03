import Foundation
import Simulation

/// Загрузка контент-пака эпохи «Рим» из бандла (JSON лежит рядом с движком-агностиком).
public enum RomeContent {

    public struct Pack {
        public let db: ContentDb
        public let levels: [LevelDef]

        /// Уровни одной главы-эпохи, отсортированные по хронологии.
        public func levels(epoch: String) -> [LevelDef] {
            levels.filter { $0.epoch == epoch }.sorted { $0.order < $1.order }
        }
    }

    /// Порядок попыток загрузки уровней. Отсутствующие тихо пропускаются.
    private static let levelIds = [
        // === Глава 1 · Древний Рим (Падение Республики) ===
        // Акт I · Восхождение (49–48 до н.э.)
        "rubicon",
        "pharsalus",
        "pompey_death",
        // Акт II · Царица и диктатор (48–44 до н.э.)
        "cleopatra_charm",
        "cleopatra_throne",
        "cleopatra_heir",
        "caesar_crown",
        "caesar_assassination",
        // Акт III · Наследники (43–30 до н.э.)
        "triumvirate",
        "philippi",
        "tarsus",
        "discord",
        "actium",
        "alexandria",
        // "rivals" — вне основной линии (легенда/что-если). Файл сохранён.

        // === Глава 2 · Тюдоры (Династия, 1485–1603) ===
        // Акт I · Восхождение
        "bosworth",
        "union",
        // Акт II · Шесть жён
        "aragon_divorce",
        "anne_boleyn",
        "jane_seymour",
        "anne_cleves",
        "howard",
        "parr",
        // Акт III · Наследники
        "jane_grey",
        "bloody_mary",
        "elizabeth",
        "mary_stuart",
        "armada",
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
