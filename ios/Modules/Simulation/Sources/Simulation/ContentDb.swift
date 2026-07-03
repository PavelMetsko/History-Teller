import Foundation

/// Загруженный контент эпохи. Принимает JSON-строки — источник (бандл, файл, CDN)
/// решается на уровне приложения, движок об этом не знает.
public final class ContentDb {
    public private(set) var characters: [String: CharacterDef]
    public private(set) var scenes: [String: SceneDef]
    public let rulesByPriorityDesc: [RuleDef]

    init(characters: [String: CharacterDef], scenes: [String: SceneDef], rules: [RuleDef]) {
        self.characters = characters
        self.scenes = scenes
        self.rulesByPriorityDesc = rules
    }

    /// Локализовать отображаемые имена/действия (загрузчик передаёт словари id→перевод).
    /// Движок сравнивает по id/тегам, так что перевод имён на симуляцию не влияет.
    public func localizeNames(characterNames: [String: String],
                              sceneNames: [String: String],
                              sceneActions: [String: String]) {
        for (id, name) in characterNames where characters[id] != nil { characters[id]!.name = name }
        for (id, name) in sceneNames where scenes[id] != nil { scenes[id]!.name = name }
        for (id, act) in sceneActions where scenes[id] != nil { scenes[id]!.action = act }
    }

    public static func fromJson(charactersJson: String, scenesJson: String, rulesJson: String) throws -> ContentDb {
        let decoder = JSONDecoder()
        let chars = try decoder.decode([CharacterDef].self, from: Data(charactersJson.utf8))
        let scenes = try decoder.decode([SceneDef].self, from: Data(scenesJson.utf8))
        let rules = try decoder.decode([RuleDef].self, from: Data(rulesJson.utf8))
        return ContentDb(
            characters: Dictionary(chars.map { ($0.id, $0) }, uniquingKeysWith: { a, _ in a }),
            scenes: Dictionary(scenes.map { ($0.id, $0) }, uniquingKeysWith: { a, _ in a }),
            // sorted(by:) в Swift стабилен → порядок равных приоритетов сохраняется, как в LINQ OrderByDescending.
            rules: rules.sorted { $0.priority > $1.priority }
        )
    }

    public static func loadLevel(_ levelJson: String) throws -> LevelDef {
        try JSONDecoder().decode(LevelDef.self, from: Data(levelJson.utf8))
    }
}
