import Foundation

/// Направленное отношение между акторами. В C# это был кортеж (rel, from, to) в HashSet;
/// в Swift кортежи не Hashable — заворачиваем в структуру.
struct Relation: Hashable {
    let rel: String
    let from: String
    let to: String
}

/// Состояние мира: флаги персонажей + направленные отношения.
/// Чистый Swift, без UIKit/SwiftUI. Мутируемый — как в оригинальном движке.
public final class World {
    public static let deadFlag = "dead"

    private var flags: [String: Set<String>] = [:]
    private var relations: Set<Relation> = []

    public init() {}

    public func hasFlag(_ charId: String, _ flag: String) -> Bool {
        flags[charId]?.contains(flag) ?? false
    }

    public func setFlag(_ charId: String, _ flag: String) {
        flags[charId, default: []].insert(flag)
    }

    public func removeFlag(_ charId: String, _ flag: String) {
        flags[charId]?.remove(flag)
    }

    public func hasRelation(_ rel: String, _ from: String, _ to: String) -> Bool {
        relations.contains(Relation(rel: rel, from: from, to: to))
    }

    public func addRelation(_ rel: String, _ from: String, _ to: String) {
        relations.insert(Relation(rel: rel, from: from, to: to))
    }

    public func removeRelation(_ rel: String, _ from: String, _ to: String) {
        relations.remove(Relation(rel: rel, from: from, to: to))
    }

    public func isAlive(_ charId: String) -> Bool { !hasFlag(charId, World.deadFlag) }

    /// Глубокая копия (для снапшотов после каждой панели).
    /// Dictionary и Set в Swift — value-типы (copy-on-write), присваивание = глубокое копирование.
    public func clone() -> World {
        let w = World()
        w.flags = flags
        w.relations = relations
        return w
    }
}
