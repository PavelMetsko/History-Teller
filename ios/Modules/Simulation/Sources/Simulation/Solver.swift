import Foundation

/// Brute-force солвер: проверяет решаемость уровня перебором всех расстановок.
/// Для контент-пайплайна и подсказок; пространство поиска у таких пазлов маленькое.
public enum Solver {

    public struct Result {
        public var solutions: [[Panel]] = []
        public var searchSpace: Int = 0
        public var isSolvable: Bool { !solutions.isEmpty }
    }

    public static func solve(_ level: LevelDef, _ db: ContentDb, maxSolutions: Int = .max) -> Result {
        let options = panelOptions(level, db)
        var result = Result()
        result.searchSpace = pow(options.count, level.panels)
        if options.isEmpty { return result }

        let n = level.panels
        var indices = [Int](repeating: 0, count: n)
        // Одометр по индексам опций — ленивый декартов степенной перебор (без материализации всех расстановок).
        while true {
            let assignment = indices.map { options[$0] }
            let world = Engine.simulate(assignment, db, initial: level.createInitialWorld()).world
            if level.goal.isMet(world) {
                result.solutions.append(assignment)
                if result.solutions.count >= maxSolutions { break }
            }
            var pos = n - 1
            while pos >= 0 {
                indices[pos] += 1
                if indices[pos] == options.count { indices[pos] = 0; pos -= 1 }
                else { break }
            }
            if pos < 0 { break }
        }
        return result
    }

    /// Все варианты заполнения панели. Порядок персонажей = роли-слоты → размещения.
    static func panelOptions(_ level: LevelDef, _ db: ContentDb) -> [Panel] {
        var options: [Panel] = []
        for sceneId in level.scenes {
            let slots = db.scenes[sceneId]!.slots
            let maxK = min(slots, level.characters.count)
            for k in 0...maxK {
                for perm in Engine.permutations(level.characters, k) {
                    options.append(Panel(sceneId: sceneId, characters: perm))
                }
            }
        }
        return options
    }

    static func pow(_ base: Int, _ exp: Int) -> Int {
        var r = 1
        for _ in 0..<exp { r *= base }
        return r
    }
}
