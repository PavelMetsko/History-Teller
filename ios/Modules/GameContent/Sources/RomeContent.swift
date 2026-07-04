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

        // === Глава 3 · Французская революция (1789–1815) ===
        // Акт I · Революция
        "oath",
        "varennes",
        "king_trial",
        "antoinette",
        // Акт II · Террор
        "marat",
        "jacobins",
        "danton",
        "thermidor",
        // Акт III · Наполеон
        "toulon",
        "brumaire",
        "sacre",
        "empress",
        "waterloo",

        // === Глава 4 · Российская империя (1547–1775) ===
        // Акт I · Иван Грозный
        "coronation",
        "kazan",
        "oprichnina",
        "wrath",
        // Акт II · Пётр Великий
        "streltsy",
        "poltava",
        "alexei",
        "emperor",
        // Акт III · Екатерина Великая
        "coup",
        "potemkin",
        "reform",
        "pugachev",
        "execution",

        // === Глава 5 · Дом Борджиа (1492–1507) ===
        // Акт I · Восхождение
        "conclave",
        "nepotism",
        "giulia",
        "juan",
        // Акт II · Яд и власть
        "fratricide",
        "prince",
        "lucrezia",
        "poison",
        // Акт III · Государь
        "excommunicate",
        "bonfire",
        "poison_death",
        "julius",
        "downfall",

        // === Глава 6 · Византия (518–548) ===
        // Акт I · Восхождение
        "heir",
        "marriage",
        "coronation",
        "minister",
        // Акт II · Ника
        "nika",
        "flight",
        "massacre",
        "execution",
        "john_fall",
        // Акт III · Слава и закат
        "reconquest",
        "hagia",
        "disgrace",
        "theodora_death",
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
        localize(db, &levels)
        return Pack(db: db, levels: levels.sorted { $0.order < $1.order })
    }

    /// Наложить перевод на имена/сцены/уровни (движок сравнивает по id — на симуляцию не влияет).
    private static func localize(_ db: ContentDb, _ levels: inout [LevelDef]) {
        guard L10n.lang != "ru" else { return }
        var chNames: [String: String] = [:], scNames: [String: String] = [:], scActions: [String: String] = [:]
        for id in db.characters.keys { if let t = L10n.opt("char.\(id)") { chNames[id] = t } }
        for id in db.scenes.keys {
            if let t = L10n.opt("scene.\(id)") { scNames[id] = t }
            if let t = L10n.opt("scene.\(id).action") { scActions[id] = t }
        }
        db.localizeNames(characterNames: chNames, sceneNames: scNames, sceneActions: scActions)

        // заголовки актов: raw-русская строка `act` → локализованная (по обратному соответствию)
        let actKeys = ["act.rome.1", "act.rome.2", "act.rome.3", "act.tudor.1", "act.tudor.2", "act.tudor.3",
                       "act.revolution.1", "act.revolution.2", "act.revolution.3",
                       "act.empire.1", "act.empire.2", "act.empire.3",
                       "act.borgia.1", "act.borgia.2", "act.borgia.3",
                       "act.byzantium.1", "act.byzantium.2", "act.byzantium.3"]
        var actMap: [String: String] = [:]
        for k in actKeys { if let ru = L10n.ruBase(k), let loc = L10n.opt(k) { actMap[ru] = loc } }

        for i in levels.indices {
            let id = levels[i].id
            if let a = levels[i].act, let loc = actMap[a] { levels[i].act = loc }
            if let t = L10n.opt("level.\(id).title") { levels[i].title = t }
            if let t = L10n.opt("level.\(id).goal")  { levels[i].goalText = t }
            if let t = L10n.opt("level.\(id).hint")  { levels[i].goalHint = t }
            if let t = L10n.opt("level.\(id).intro") { levels[i].initialText = t }
            if levels[i].factCard != nil {
                if let t = L10n.opt("level.\(id).fact")   { levels[i].factCard!.text = t }
                if let t = L10n.opt("level.\(id).source") { levels[i].factCard!.source = t }
            }
        }
    }
}
