import Foundation
import Observation

/// Прогресс игрока: множество пройденных уровней в UserDefaults. Анлок — по порядку.
@Observable
public final class ProgressStore {
    private let defaults: UserDefaults
    private let key: String

    public private(set) var completed: Set<String>

    public init(defaults: UserDefaults = .standard, key: String = "ht.progress.completed.v1") {
        self.defaults = defaults
        self.key = key
        self.completed = Set(defaults.stringArray(forKey: key) ?? [])
    }

    /// ВРЕМЕННО (только Debug-сборки): всё открыто для плейтеста. В Release-сборке — false.
    public static var unlockAll: Bool {
        #if DEBUG
        return true
        #else
        return false
        #endif
    }

    public func isCompleted(_ id: String) -> Bool { completed.contains(id) }

    public func markCompleted(_ id: String) {
        guard !completed.contains(id) else { return }
        completed.insert(id)
        persist()
    }

    public func reset() {
        completed.removeAll()
        persist()
    }

    /// Уровень открыт, если он первый или предыдущий по порядку пройден.
    public func isUnlocked(levelId: String, orderedIds: [String]) -> Bool {
        if Self.unlockAll { return true }
        guard let idx = orderedIds.firstIndex(of: levelId) else { return false }
        if idx == 0 { return true }
        return isCompleted(orderedIds[idx - 1])
    }

    public var solvedCount: Int { completed.count }

    private func persist() {
        defaults.set(Array(completed), forKey: key)
    }
}
