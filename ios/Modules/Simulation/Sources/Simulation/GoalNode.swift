import Foundation

/// Дерево условий цели уровня: all / any / not / flag / relation.
public indirect enum GoalNode {
    case all([GoalNode])
    case any([GoalNode])
    case not(GoalNode)
    case flag(char: String, flag: String)
    case relation(rel: String, from: String, to: String)

    public func isMet(_ world: World) -> Bool {
        switch self {
        case .all(let children):  return children.allSatisfy { $0.isMet(world) }
        case .any(let children):  return children.contains { $0.isMet(world) }
        case .not(let child):     return !child.isMet(world)
        case .flag(let char, let flag):
            return world.hasFlag(char, flag)
        case .relation(let rel, let from, let to):
            return world.hasRelation(rel, from, to)
        }
    }
}

extension GoalNode: Decodable {
    private enum CodingKeys: String, CodingKey { case all, any, not, flag, relation }
    private struct FlagObj: Decodable { let char: String; let `is`: String }
    private struct RelObj: Decodable { let rel: String; let from: String; let to: String }

    public init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        if c.contains(.all) {
            self = .all(try c.decode([GoalNode].self, forKey: .all))
        } else if c.contains(.any) {
            self = .any(try c.decode([GoalNode].self, forKey: .any))
        } else if c.contains(.not) {
            self = .not(try c.decode(GoalNode.self, forKey: .not))
        } else if c.contains(.flag) {
            let f = try c.decode(FlagObj.self, forKey: .flag)
            self = .flag(char: f.char, flag: f.is)
        } else if c.contains(.relation) {
            let r = try c.decode(RelObj.self, forKey: .relation)
            self = .relation(rel: r.rel, from: r.from, to: r.to)
        } else {
            throw DecodingError.dataCorrupted(.init(
                codingPath: decoder.codingPath,
                debugDescription: "Unknown goal node"))
        }
    }
}
