import Foundation

/// Сработавшее правило — для анимаций/звука в UI.
public struct RuleEvent {
    public let panelIndex: Int
    public let ruleId: String
    public let binding: [String: String]
}

/// Результат прогона: финальный мир + трасса (снапшоты/события/лог) для UI.
public struct SimulationResult {
    public let world: World
    public let snapshots: [World]   // состояние после каждой панели (для бейджей)
    public let events: [RuleEvent]  // сработавшие правила (для анимаций/звука)
    public let log: [String]
}

/// Движок симуляции: прогоняет панели слева направо, применяя правила по убыванию приоритета.
/// Семантика 1:1 с эталонным C#-движком (и tools/simulate.py).
public enum Engine {

    /// - Parameters:
    ///   - initial: стартовый мир (мутируется!). Передавайте level.createInitialWorld().
    ///   - collectTrace: собирать ли снапшоты/события/лог (для UI). Solver вызывает без трассы.
    @discardableResult
    public static func simulate(_ panels: [Panel], _ db: ContentDb,
                                initial: World? = nil,
                                collectTrace: Bool = false) -> SimulationResult {
        let world = initial ?? World()
        var snapshots: [World] = []
        var events: [RuleEvent] = []
        var log: [String] = []

        for i in 0..<panels.count {
            let panel = panels[i]
            guard let sceneId = panel.sceneId else {
                if collectTrace { snapshots.append(world.clone()) }
                continue
            }

            let sceneTags = db.scenes[sceneId]!.tags
            for rule in db.rulesByPriorityDesc {
                if !rule.trigger.sceneTags.allSatisfy({ sceneTags.contains($0) }) { continue }

                for binding in findBindings(rule.trigger.actors, panel.characters, world, db) {
                    // Биндинг мог быть инвалидирован эффектом в этой же панели
                    // (например, персонаж погиб) — перепроверяем живость и условия.
                    let stillValid = rule.trigger.actors.allSatisfy { a in
                        world.isAlive(binding[a.variable]!) &&
                        actorMatches(a, binding[a.variable]!, binding, world, db)
                    }
                    if !stillValid { continue }

                    applyEffects(rule.effects, binding, world)
                    if collectTrace {
                        log.append("panel \(i + 1): rule '\(rule.id)' " +
                            binding.map { "\($0.key)=\($0.value)" }.joined(separator: ", "))
                        events.append(RuleEvent(panelIndex: i, ruleId: rule.id, binding: binding))
                    }
                }
            }
            if collectTrace { snapshots.append(world.clone()) }
        }
        return SimulationResult(world: world, snapshots: snapshots, events: events, log: log)
    }

    static func actorMatches(_ actor: ActorDef, _ charId: String,
                             _ binding: [String: String], _ world: World, _ db: ContentDb) -> Bool {
        let def = db.characters[charId]!
        if !actor.tags.allSatisfy({ def.tags.contains($0) }) { return false }
        if !actor.flags.allSatisfy({ world.hasFlag(charId, $0) }) { return false }
        if actor.notFlags.contains(where: { world.hasFlag(charId, $0) }) { return false }
        for rc in actor.relations {
            guard let other = binding[rc.to] else { return false }
            if !world.hasRelation(rc.rel, charId, other) { return false }
        }
        return true
    }

    /// Назначения живых персонажей на переменные. Актор со slot ≥ 0 жёстко привязан
    /// к позиции в кадре (роль сцены), остальные перебираются.
    static func findBindings(_ actors: [ActorDef], _ present: [String],
                             _ world: World, _ db: ContentDb) -> [[String: String]] {
        let alive = present.filter { world.isAlive($0) }
        var result: [[String: String]] = []

        if actors.contains(where: { $0.slot >= 0 }) {
            var binding: [String: String] = [:]
            var used: Set<String> = []
            for a in actors where a.slot >= 0 {
                if a.slot >= present.count { return result }
                let c = present[a.slot]
                if !world.isAlive(c) || !used.insert(c).inserted { return result }
                binding[a.variable] = c
            }
            let rest = actors.filter { $0.slot < 0 }
            let free = alive.filter { !used.contains($0) }
            for perm in permutations(free, rest.count) {
                var b = binding
                for i in 0..<rest.count { b[rest[i].variable] = perm[i] }
                if actors.allSatisfy({ actorMatches($0, b[$0.variable]!, b, world, db) }) {
                    result.append(b)
                }
            }
            return result
        }

        for perm in permutations(alive, actors.count) {
            var binding: [String: String] = [:]
            for i in 0..<actors.count { binding[actors[i].variable] = perm[i] }
            // Условия отношений ссылаются на другие переменные — проверяем после полного назначения.
            if actors.allSatisfy({ actorMatches($0, binding[$0.variable]!, binding, world, db) }) {
                result.append(binding)
            }
        }
        return result
    }

    static func applyEffects(_ effects: [EffectDef],
                             _ binding: [String: String], _ world: World) {
        for e in effects {
            switch e.type {
            case "setFlag":        world.setFlag(binding[e.target!]!, e.flag!)
            case "removeFlag":     world.removeFlag(binding[e.target!]!, e.flag!)
            case "addRelation":    world.addRelation(e.rel!, binding[e.from!]!, binding[e.to!]!)
            case "removeRelation": world.removeRelation(e.rel!, binding[e.from!]!, binding[e.to!]!)
            default: fatalError("Unknown effect type: \(e.type)")
            }
        }
    }

    /// Упорядоченные выборки длины k без повторений (порядок генерации стабилен, как в C#).
    static func permutations(_ items: [String], _ k: Int) -> [[String]] {
        if k == 0 { return [[]] }
        if k > items.count { return [] }
        var result: [[String]] = []
        for i in 0..<items.count {
            var rest = items
            rest.remove(at: i)
            for tail in permutations(rest, k - 1) {
                result.append([items[i]] + tail)
            }
        }
        return result
    }
}
