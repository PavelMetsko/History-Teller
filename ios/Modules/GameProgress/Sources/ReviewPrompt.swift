import Foundation

/// Когда просить оценку в магазине.
///
/// Правила простые и нарочно строгие: просим только у того, кто уже втянулся (прошёл несколько
/// уровней и заглянул не в одну главу), не чаще раза в сутки и не больше трёх раз за всё время —
/// система всё равно показывает окно не чаще трёх раз в год, а лишние вызовы просто пропадают
/// впустую. Момент выбран после факт-карточки: игрок только что выиграл и прочитал награду.
public enum ReviewPrompt {
    private static let lastKey = "ht.review.lastAsked"
    private static let countKey = "ht.review.askCount"

    /// Сколько уровней и глав должно быть за плечами, прежде чем мы вообще заикнёмся об оценке.
    public static let minSolved = 10
    public static let minChapters = 2
    public static let maxAsks = 3
    private static let cooldown: TimeInterval = 24 * 60 * 60

    public static func shouldAsk(solvedCount: Int, chaptersTouched: Int,
                                 defaults: UserDefaults = .standard,
                                 now: Date = Date()) -> Bool {
        guard solvedCount >= minSolved, chaptersTouched >= minChapters else { return false }
        guard defaults.integer(forKey: countKey) < maxAsks else { return false }
        let last = defaults.double(forKey: lastKey)
        guard last == 0 || now.timeIntervalSince1970 - last >= cooldown else { return false }
        return true
    }

    /// Отметить, что окно показано. Вызывать сразу после запроса: система может окно и не
    /// показать, но повторять попытку в тот же день всё равно незачем.
    public static func recordAsked(defaults: UserDefaults = .standard, now: Date = Date()) {
        defaults.set(now.timeIntervalSince1970, forKey: lastKey)
        defaults.set(defaults.integer(forKey: countKey) + 1, forKey: countKey)
    }
}
