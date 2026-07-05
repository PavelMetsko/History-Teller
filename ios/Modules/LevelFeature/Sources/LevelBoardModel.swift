import Foundation
import Observation
import Simulation

/// Состояние экрана уровня: расстановка панелей + живой прогон движка после каждого изменения.
@Observable
public final class LevelBoardModel {
    public let level: LevelDef
    public let db: ContentDb

    public private(set) var panels: [Panel]
    public private(set) var result: SimulationResult
    public var showFact: Bool = false

    /// Правила, сработавшие в результате последнего действия (для анимаций/звука).
    public private(set) var lastFiredEvents: [RuleEvent] = []
    /// Семантические «биты» последнего действия — что именно произошло и с кем
    /// (кого убили + кто убийца, кого короновали, кто кого полюбил). Выводятся из
    /// эффектов правила, поэтому работают для любой эпохи без хардкода под ruleId.
    public private(set) var lastBeats: [Beat] = []
    /// Бампается на каждый пересчёт — вью подписывается, чтобы проигрывать «сок».
    public private(set) var changeToken: Int = 0
    private var seenEventKeys: Set<String> = []
    @ObservationIgnored private lazy var ruleById: [String: RuleDef] =
        Dictionary(db.rulesByPriorityDesc.map { ($0.id, $0) }, uniquingKeysWith: { a, _ in a })

    /// Диагноз панели: почему заполненная панель «мертва» (ни одно правило не сработало).
    public enum PanelDiagnosis: Equatable { case ok, wrongScene, wrongCharacters, inert }
    public private(set) var panelDiagnoses: [PanelDiagnosis] = []

    public init(level: LevelDef, db: ContentDb) {
        self.level = level
        self.db = db
        let empty = Array(repeating: Panel(sceneId: nil), count: max(1, level.panels))
        self.panels = empty
        self.result = Engine.simulate(empty, db, initial: level.createInitialWorld(), collectTrace: true)
        seenEventKeys = Set(result.events.map(Self.key))
        panelDiagnoses = Array(repeating: .ok, count: empty.count)
    }

    public var world: World { result.world }
    public var isSolved: Bool { level.goal.isMet(result.world) }
    public var roster: [String] { level.characters }

    /// Доска полностью заполнена (в каждой панели сцена и все слоты заняты) —
    /// момент «завершённой попытки»: если при этом не решено, значит ход неверный.
    public var isBoardComplete: Bool {
        panels.allSatisfy { p in
            guard let sid = p.sceneId, let sc = db.scenes[sid] else { return false }
            return p.characters.count == sc.slots
        }
    }

    /// Выбранный сбоку элемент — применяется тапом по панели.
    public enum Selection: Equatable { case scene(String); case character(String) }
    public var selected: Selection?

    public func selectItem(_ s: Selection) {
        selected = (selected == s) ? nil : s
    }

    /// Применить выбранное к панели (тап-плейсмент). Возвращает, что применили.
    @discardableResult
    public func applySelection(at index: Int) -> Selection? {
        guard let sel = selected else { return nil }
        switch sel {
        case .scene(let sid):
            setScene(sid, at: index)
        case .character(let cid):
            guard panels[index].sceneId != nil,
                  panels[index].characters.count < slots(at: index),
                  !panels[index].characters.contains(cid) else { selected = nil; return nil }
            place(cid, at: index)
        }
        selected = nil
        return sel
    }

    public func characterName(_ id: String) -> String { db.characters[id]?.name ?? id }
    public func sceneName(_ id: String) -> String { db.scenes[id]?.name ?? id }
    public func sceneAction(_ id: String) -> String? { db.scenes[id]?.action }

    public func slots(at index: Int) -> Int {
        guard let sid = panels[index].sceneId, let scene = db.scenes[sid] else { return 0 }
        return scene.slots
    }

    /// Персонажи, которых ещё можно поставить в панель (не дубли внутри одной панели).
    public func availableCharacters(at index: Int) -> [String] {
        roster.filter { !panels[index].characters.contains($0) }
    }

    public func setScene(_ sceneId: String?, at index: Int) {
        panels[index].sceneId = sceneId
        if let sid = sceneId, let max = db.scenes[sid]?.slots {
            if panels[index].characters.count > max {
                panels[index].characters.removeLast(panels[index].characters.count - max)
            }
        } else {
            panels[index].characters.removeAll()
        }
        recompute()
    }

    public func place(_ charId: String, at index: Int) {
        guard panels[index].sceneId != nil,
              panels[index].characters.count < slots(at: index),
              !panels[index].characters.contains(charId) else { return }
        panels[index].characters.append(charId)
        recompute()
    }

    public func removeCharacter(_ charId: String, at index: Int) {
        panels[index].characters.removeAll { $0 == charId }
        recompute()
    }

    public func reset() {
        panels = Array(repeating: Panel(sceneId: nil), count: max(1, level.panels))
        selected = nil
        seenEventKeys = []
        recompute()
    }

    /// Разложить эталонное решение уровня (dev-хук для превью/скриншотов).
    public func applySolution() {
        guard let solution = level.solution else { return }
        var next = Array(repeating: Panel(sceneId: nil), count: max(1, level.panels))
        for (i, panel) in solution.enumerated() where i < next.count { next[i] = panel }
        panels = next
        recompute()
    }

    /// Dev-хук: заполнить все панели заведомо неверно (первая сцена + первые герои).
    public func fillDebugWrong() {
        for i in panels.indices {
            guard let sid = level.scenes.first, let sc = db.scenes[sid] else { continue }
            setScene(sid, at: i)
            for c in roster.prefix(sc.slots) { place(c, at: i) }
        }
    }

    /// Состояние мира после указанной панели (для бейджей внутри панели).
    public func snapshot(after index: Int) -> World {
        guard index >= 0, index < result.snapshots.count else { return result.world }
        return result.snapshots[index]
    }

    private func recompute() {
        result = Engine.simulate(panels, db, initial: level.createInitialWorld(), collectTrace: true)
        // Новые (ещё не показанные) сработавшие правила — для анимаций/звука.
        lastFiredEvents = result.events.filter { !seenEventKeys.contains(Self.key($0)) }
        lastBeats = lastFiredEvents.map { beat(from: $0) }
        seenEventKeys = Set(result.events.map(Self.key))
        // Ошибки показываем только когда весь раунд заполнен (и не решён) — иначе не придираемся.
        panelDiagnoses = (isSolved || !isBoardComplete)
            ? Array(repeating: .ok, count: panels.count)
            : panels.indices.map { diagnose($0) }
        changeToken &+= 1
    }

    /// Сверка панели с эталонным решением (позиция за позицией):
    /// та сцена, но не те лица → wrongCharacters; та расстановка, но не та сцена → wrongScene;
    /// и то и другое мимо → inert. Пустые/неполные панели и уровни без эталона не трогаем.
    private func diagnose(_ index: Int) -> PanelDiagnosis {
        let p = panels[index]
        guard let sid = p.sceneId, let sc = db.scenes[sid], p.characters.count == sc.slots else { return .ok }
        guard let solution = level.solution, index < solution.count else { return .ok }
        let sol = solution[index]
        let sameChars = Set(sol.characters) == Set(p.characters)
        if sol.sceneId == sid {
            return sameChars ? .ok : .wrongCharacters
        }
        return sameChars ? .wrongScene : .inert
    }

    /// Что «читаемо» произошло в сработавшем правиле — для анимации-взаимодействия.
    public struct Beat: Identifiable {
        public let id = UUID()
        public let panelIndex: Int
        public enum Kind { case kill, battle, condemn, conquer, march, crown,
                                love, ally, triumph, downfall, conspire, birth, spark }
        public let kind: Kind
        public let primary: String?     // тот, «над кем» действие: жертва / коронованный / проигравший / осуждённый
        public let secondary: String?   // действующий: убийца / победитель / обвинитель / второй влюблённый
        public let symbol: String
    }

    /// Выводим смысл из эффектов правила (не из его id), поэтому одна логика
    /// покрывает все эпохи: любое правило со `setFlag dead` — это убийство и т.д.
    /// Соглашение: `primary` — тот, кто «страдает/возвышается» (жертва, осуждённый,
    /// проигравший, коронованный), `secondary` — активный (убийца, обвинитель, победитель).
    private func beat(from e: RuleEvent) -> Beat {
        let effs = ruleById[e.ruleId]?.effects ?? []
        let b = e.binding
        func flagTarget(_ flags: Set<String>) -> String? {
            effs.first { $0.type == "setFlag" && ($0.flag.map(flags.contains) ?? false) }?.target
        }
        func relationPair(_ rels: Set<String>) -> (String, String)? {
            for ef in effs where ef.type == "addRelation" && (ef.rel.map(rels.contains) ?? false) {
                if let f = ef.from, let t = ef.to { return (f, t) }
            }
            return nil
        }
        // «другой» связанный актор — активная сторона напротив пострадавшего
        func other(than v: String?) -> String? {
            let target = v.flatMap { b[$0] }
            return b.first { $0.key != v && $0.value != target }?.value
        }
        func mk(_ kind: Beat.Kind, _ p: String?, _ s: String?, _ sym: String) -> Beat {
            Beat(panelIndex: e.panelIndex, kind: kind, primary: p, secondary: s, symbol: sym)
        }

        // Убийство: кто-то получает флаг смерти. Убийца — другой связанный актор.
        if let v = flagTarget(["dead"]) {
            return mk(.kill, b[v], other(than: v), "☠️")
        }
        // Битва с проигравшим: беглец/разбитый + победитель напротив.
        if let loser = flagTarget(["fugitive", "defeated"]) {
            return mk(.battle, b[loser], other(than: loser), "⚔️")
        }
        // Суд/обвинение: осуждён/обвинён + обвинитель напротив.
        if let accused = flagTarget(["condemned", "accused"]) {
            return mk(.condemn, b[accused], other(than: accused), "⚖️")
        }
        // Переход/поход — объявление войны, но пока НЕ бой (никого не рубит) → без меча.
        if let m = flagTarget(["at_war"]) {
            return mk(.march, b[m], nil, "")
        }
        // Единоличное завоевание.
        if let c = flagTarget(["conqueror"]) {
            return mk(.conquer, b[c], nil, "⚔️")
        }
        // Коронация/воцарение/возвышение.
        if let c = flagTarget(["crowned", "emperor", "empress", "reigns", "supreme_head", "first_consul"]) {
            return mk(.crown, b[c], nil, "👑")
        }
        // Любовь.
        if let (f, t) = relationPair(["loves"]) {
            return mk(.love, b[f], b[t], "❤️")
        }
        // Союз / поддержка.
        if let (f, t) = relationPair(["ally_of"]) {
            return mk(.ally, b[f], b[t], "🤝")
        }
        if let backed = flagTarget(["backed"]) {
            return mk(.ally, b[backed], other(than: backed), "🛡")
        }
        // Триумф/слава.
        if let t = flagTarget(["honored", "flaunting", "triumphant", "rome_restored",
                               "settled", "hero", "absolute", "supreme"]) {
            return mk(.triumph, b[t], nil, "🎉")
        }
        // Низложение/изгнание/утрата.
        if let d = flagTarget(["exiled", "cast_off", "widowed"]) {
            return mk(.downfall, b[d], nil, "💔")
        }
        // Заговор.
        if let plot = flagTarget(["plotting"]) {
            return mk(.conspire, b[plot], nil, "🗡")
        }
        // Рождение наследника.
        if flagTarget(["has_heir"]) != nil {
            return mk(.birth, nil, nil, "👶")
        }
        return mk(.spark, nil, nil, "✨")
    }

    private static func key(_ e: RuleEvent) -> String {
        let b = e.binding.sorted { $0.key < $1.key }.map { "\($0.key)=\($0.value)" }.joined(separator: ",")
        return "\(e.panelIndex)|\(e.ruleId)|\(b)"
    }
}

/// Флаги состояния → эмодзи-бейджи (v1, без отдельного арта иконок).
public enum StateBadges {
    public static func emojis(for charId: String, in world: World) -> [String] {
        var out: [String] = []
        if world.hasFlag(charId, "dead")       { out.append("☠️") }
        if world.hasFlag(charId, "plotting")   { out.append("🗡") }
        if world.hasFlag(charId, "traitor")    { out.append("🎭") }
        if world.hasFlag(charId, "crowned")    { out.append("👑") }
        if world.hasFlag(charId, "backed")     { out.append("🛡") }
        if world.hasFlag(charId, "conqueror")  { out.append("⚔️") }
        if world.hasFlag(charId, "locked_out") { out.append("🔒") }
        if world.hasFlag(charId, "inside")     { out.append("🚪") }
        if world.hasFlag(charId, "in_rome")    { out.append("🏛") }
        if world.hasFlag(charId, "has_heir")   { out.append("👶") }
        return out
    }
}
