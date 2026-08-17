import Foundation

/// Все определения — чистые данные, загружаются из JSON. Движок не знает конкретных персонажей.

public struct CharacterDef: Decodable {
    public let id: String
    public var name: String
    public var tags: [String] = []

    enum CodingKeys: String, CodingKey { case id, name, tags }

    public init(id: String, name: String, tags: [String] = []) {
        self.id = id; self.name = name; self.tags = tags
    }

    public init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        id = try c.decode(String.self, forKey: .id)
        name = try c.decodeIfPresent(String.self, forKey: .name) ?? ""
        tags = try c.decodeIfPresent([String].self, forKey: .tags) ?? []
    }
}

public struct SceneDef: Decodable {
    public let id: String
    public var name: String
    public var tags: [String] = []
    public var slots: Int = 2
    public var action: String?        // глагол карты действия («заговор», «соблазнение»)
    public var actionIcon: String?    // иконка действия для UI
    public var roles: [String]?       // подписи ролей-слотов; nil = порядок не важен

    enum CodingKeys: String, CodingKey { case id, name, tags, slots, action, actionIcon, roles }

    public init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        id = try c.decode(String.self, forKey: .id)
        name = try c.decodeIfPresent(String.self, forKey: .name) ?? ""
        tags = try c.decodeIfPresent([String].self, forKey: .tags) ?? []
        slots = try c.decodeIfPresent(Int.self, forKey: .slots) ?? 2
        action = try c.decodeIfPresent(String.self, forKey: .action)
        actionIcon = try c.decodeIfPresent(String.self, forKey: .actionIcon)
        roles = try c.decodeIfPresent([String].self, forKey: .roles)
    }
}

public struct RelationCondition: Decodable {
    public let rel: String
    public let to: String   // имя переменной другого актора
}

public struct ActorDef: Decodable {
    public var variable: String                    // "var" в JSON (ключевое слово в Swift)
    public var slot: Int = -1                       // ≥0 — жёсткая привязка к позиции в кадре (роль)
    public var tags: [String] = []                  // требуемые теги CharacterDef
    public var flags: [String] = []                 // требуемые флаги состояния
    public var notFlags: [String] = []              // запрещённые флаги
    public var relations: [RelationCondition] = []

    enum CodingKeys: String, CodingKey {
        case variable = "var", slot, tags, flags, notFlags, relations
    }

    public init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        variable = try c.decode(String.self, forKey: .variable)
        slot = try c.decodeIfPresent(Int.self, forKey: .slot) ?? -1
        tags = try c.decodeIfPresent([String].self, forKey: .tags) ?? []
        flags = try c.decodeIfPresent([String].self, forKey: .flags) ?? []
        notFlags = try c.decodeIfPresent([String].self, forKey: .notFlags) ?? []
        relations = try c.decodeIfPresent([RelationCondition].self, forKey: .relations) ?? []
    }
}

public struct TriggerDef: Decodable {
    public var sceneTags: [String] = []
    public var actors: [ActorDef] = []

    enum CodingKeys: String, CodingKey { case sceneTags, actors }

    public init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        sceneTags = try c.decodeIfPresent([String].self, forKey: .sceneTags) ?? []
        actors = try c.decodeIfPresent([ActorDef].self, forKey: .actors) ?? []
    }
}

public struct EffectDef: Decodable {
    public let type: String   // setFlag | removeFlag | addRelation | removeRelation
    public var target: String?
    public var flag: String?
    public var rel: String?
    public var from: String?
    public var to: String?
}

public struct RuleDef: Decodable {
    public let id: String
    public var priority: Int = 0
    public var trigger: TriggerDef
    public var effects: [EffectDef] = []

    enum CodingKeys: String, CodingKey { case id, priority, trigger, effects }

    public init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        id = try c.decode(String.self, forKey: .id)
        priority = try c.decodeIfPresent(Int.self, forKey: .priority) ?? 0
        trigger = try c.decode(TriggerDef.self, forKey: .trigger)
        effects = try c.decodeIfPresent([EffectDef].self, forKey: .effects) ?? []
    }
}

/// Достоверность эпизода — метаданные, задаются в файле уровня.
/// Сам текст и источник живут в каталогах i18n и накладываются на загрузке.
public struct FactCard: Decodable {
    public let accuracy: String   // fact | simplification | legend
    public var text: String = ""
    public var source: String = ""

    enum CodingKeys: String, CodingKey { case accuracy, text, source }

    public init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        accuracy = try c.decode(String.self, forKey: .accuracy)
        text = try c.decodeIfPresent(String.self, forKey: .text) ?? ""
        source = try c.decodeIfPresent(String.self, forKey: .source) ?? ""
    }
}

/// Стартовые условия уровня (например, «Брут — союзник Цезаря»).
public struct InitialStateDef: Decodable {
    public var flags: [String: [String]] = [:]
    public var relations: [[String]] = []   // [rel, from, to]

    enum CodingKeys: String, CodingKey { case flags, relations }

    public init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        flags = try c.decodeIfPresent([String: [String]].self, forKey: .flags) ?? [:]
        relations = try c.decodeIfPresent([[String]].self, forKey: .relations) ?? []
    }
}

/// Заполнение одной панели игроком.
public struct Panel: Decodable, Equatable {
    public var sceneId: String?                 // nil = пустая панель
    public var characters: [String]

    public init(sceneId: String?, characters: [String] = []) {
        self.sceneId = sceneId
        self.characters = characters
    }

    enum CodingKeys: String, CodingKey { case scene, characters }

    public init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        sceneId = try c.decodeIfPresent(String.self, forKey: .scene)
        characters = try c.decodeIfPresent([String].self, forKey: .characters) ?? []
    }
}

/// Шаг гида-помощника: реплика, которая висит на доске, пока не выполнено `until`.
///
/// Нужен на первых уровнях: игра нигде не объясняет, что правила срабатывают сами, что сцен
/// больше, чем кадров, и что порядок кадров значим. Онбординг говорит это на демо-уровне
/// абстрактно, а здесь игрок доходит до того же руками — и получает историю как награду.
/// Условие описано тем же деревом, что и цель уровня, поэтому гид не требует своей логики.
public struct CoachStep: Decodable {
    public var text: String            // суффикс ключа `level.<id>.coach.<text>`
    public var until: GoalNode?        // шаг закрыт, когда предикат выполнен
    public var untilScene: String?     // …или когда эта сцена выставлена в любой кадр
    // Списки, а не одиночные значения: на шаге «положи в кадр Ромула и Герсилию» звать надо
    // обоих, и подсветка должна переходить на оставшегося, когда первого уже поставили.
    public var highlightScenes: [String] = []
    public var highlightChars: [String] = []

    enum CodingKeys: String, CodingKey { case text, until, untilScene, highlightScenes, highlightChars }

    public init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        text = try c.decode(String.self, forKey: .text)
        until = try c.decodeIfPresent(GoalNode.self, forKey: .until)
        untilScene = try c.decodeIfPresent(String.self, forKey: .untilScene)
        highlightScenes = try c.decodeIfPresent([String].self, forKey: .highlightScenes) ?? []
        highlightChars = try c.decodeIfPresent([String].self, forKey: .highlightChars) ?? []
    }
}

public struct LevelDef: Decodable {
    public let id: String
    public var order: Int = 0
    public var title: String
    public let epoch: String
    public let panels: Int
    public var scenes: [String] = []
    public var characters: [String] = []
    public var initialState: InitialStateDef?
    public var initialText: String?
    public var goalText: String?   // цель-предложение для чекбокса
    public var goalHint: String?   // подсказка про запрещающие условия
    public let goal: GoalNode
    public var factCard: FactCard?
    public var solution: [Panel]?  // эталонное решение (для подсказок и валидации)
    public var music: String?      // тема настроения (напр. "battle"); nil → тема главы
    public var cover: String?      // сцена-обложка для карты; nil → первая из scenes
    public var act: String?        // подглава-акт для группировки на карте («Акт I · Восхождение»)
    public var coach: [CoachStep] = []   // гид-помощник (обычно только на первом уровне главы)

    enum CodingKeys: String, CodingKey {
        case id, order, title, epoch, panels, scenes, characters,
             initialState, initialText, goalText, goalHint, goal, factCard, solution, music, cover,
             act, coach
    }

    public init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        id = try c.decode(String.self, forKey: .id)
        order = try c.decodeIfPresent(Int.self, forKey: .order) ?? 0
        title = try c.decodeIfPresent(String.self, forKey: .title) ?? ""   // текст приходит из i18n
        epoch = try c.decode(String.self, forKey: .epoch)
        panels = try c.decode(Int.self, forKey: .panels)
        scenes = try c.decodeIfPresent([String].self, forKey: .scenes) ?? []
        characters = try c.decodeIfPresent([String].self, forKey: .characters) ?? []
        initialState = try c.decodeIfPresent(InitialStateDef.self, forKey: .initialState)
        initialText = try c.decodeIfPresent(String.self, forKey: .initialText)
        goalText = try c.decodeIfPresent(String.self, forKey: .goalText)
        goalHint = try c.decodeIfPresent(String.self, forKey: .goalHint)
        goal = try c.decode(GoalNode.self, forKey: .goal)
        coach = try c.decodeIfPresent([CoachStep].self, forKey: .coach) ?? []
        factCard = try c.decodeIfPresent(FactCard.self, forKey: .factCard)
        solution = try c.decodeIfPresent([Panel].self, forKey: .solution)
        music = try c.decodeIfPresent(String.self, forKey: .music)
        cover = try c.decodeIfPresent(String.self, forKey: .cover)
        act = try c.decodeIfPresent(String.self, forKey: .act)
    }

    /// Свежий мир со стартовыми условиями. Вызывать для каждой симуляции (мир мутируется).
    public func createInitialWorld() -> World {
        let w = World()
        guard let initialState else { return w }
        for (charId, fs) in initialState.flags {
            for f in fs { w.setFlag(charId, f) }
        }
        for r in initialState.relations where r.count >= 3 {
            w.addRelation(r[0], r[1], r[2])
        }
        return w
    }
}
