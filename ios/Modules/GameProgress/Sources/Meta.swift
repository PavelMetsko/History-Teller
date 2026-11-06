import Foundation
import Observation

/// Мета-прогресс поверх пройденных уровней: опыт и звания, подсказки, серия дней, подарок дня,
/// эпизод дня и счётчики интерстишела. Правила — `docs/f2p-patch-4.0.md`, Android повторяет их 1:1.
/// «День» — локальный календарный, чтобы серия и подарок сменялись в полночь игрока, а не по UTC.
@Observable
public final class Meta {
    public static let shared = Meta()

    public static let baseXP = 100
    public static let noHintBonus = 50
    public static let startHints = 3
    public static let rankUpHints = 2
    /// Подарок дня по шагу календаря 1…7.
    public static let gifts = [1, 1, 2, 1, 2, 2, 3]
    /// Сколько первых уровней каждой главы идут в эпизоды дня — поздние слишком сложны для «зашёл на минуту».
    public static let dailyPoolPerChapter = 10
    public static let rankNames = 15

    public private(set) var xp: Int
    public private(set) var hints: Int
    public private(set) var streak: Int
    public private(set) var streakDay: Int
    public private(set) var bestStreak: Int
    public private(set) var giftDay: Int
    public private(set) var giftStep: Int
    public private(set) var dailyDone: Int
    public private(set) var restoredFor: Int
    private var hinted: Set<String>

    @ObservationIgnored private let d: UserDefaults

    public init(defaults: UserDefaults = .standard) {
        d = defaults
        xp = d.integer(forKey: K.xp)
        hints = d.integer(forKey: K.hints)
        streak = d.integer(forKey: K.streak)
        streakDay = d.integer(forKey: K.streakDay)
        bestStreak = d.integer(forKey: K.bestStreak)
        giftDay = d.integer(forKey: K.giftDay)
        giftStep = d.integer(forKey: K.giftStep)
        dailyDone = d.integer(forKey: K.dailyDone)
        restoredFor = d.integer(forKey: K.restoredFor)
        hinted = Set(d.stringArray(forKey: K.hinted) ?? [])
    }

    /// Один раз при первом запуске 4.0: стартовые подсказки и опыт за уже пройденное.
    public func bootstrap(solvedCount: Int) {
        guard !d.bool(forKey: K.initDone) else { return }
        d.set(true, forKey: K.initDone)
        set(&hints, Self.startHints, K.hints)
        set(&xp, solvedCount * Self.baseXP, K.xp)
    }

    // MARK: День

    public static func day(_ date: Date = Date()) -> Int {
        let s = date.timeIntervalSince1970 + Double(TimeZone.current.secondsFromGMT(for: date))
        return Int(floor(s / 86_400))
    }

    public var today: Int { Self.day() }

    // MARK: Звания

    /// Опыт, с которого начинается уровень `n` (n ≥ 1): 0, 200, 450, 750, 1100, …
    public static func threshold(_ n: Int) -> Int {
        guard n > 1 else { return 0 }
        return (1..<n).reduce(0) { $0 + 150 + 50 * $1 }
    }

    public static func level(forXP xp: Int) -> Int {
        var n = 1
        while threshold(n + 1) <= xp { n += 1 }
        return n
    }

    public var level: Int { Self.level(forXP: xp) }

    /// Ключ имени звания (`ui.rank.N`): после пятнадцатого имя больше не меняется.
    public static func rankKey(_ level: Int) -> String { "ui.rank.\(min(max(level, 1), rankNames))" }

    /// Доля пути к следующему уровню, 0…1.
    public static func levelProgress(_ xp: Int) -> Double {
        let n = level(forXP: xp)
        let lo = threshold(n), hi = threshold(n + 1)
        return Double(xp - lo) / Double(max(1, hi - lo))
    }

    // MARK: Подсказки

    public func wasHinted(_ levelId: String) -> Bool { hinted.contains(levelId) }

    /// Списать подсказку. Premium не тратит. Уровень помечается — без бонуса «без подсказок».
    @discardableResult
    public func spendHint(levelId: String, premium: Bool) -> Bool {
        guard premium || hints > 0 else { return false }
        if !premium { set(&hints, hints - 1, K.hints) }
        markHinted(levelId)
        return true
    }

    /// Подсказка за ролик: сразу применяется, в запас не идёт.
    public func markHinted(_ levelId: String) {
        hinted.insert(levelId)
        d.set(Array(hinted), forKey: K.hinted)
    }

    public func addHints(_ n: Int) { set(&hints, hints + n, K.hints) }

    // MARK: Серия

    /// Серия, которую показываем: живая, пока вчера или сегодня что-то решено.
    public var currentStreak: Int { streakDay >= today - 1 ? streak : 0 }
    public var solvedToday: Bool { streakDay == today }

    /// Прервалась ровно вчера (позавчера решал, вчера нет) — её ещё можно вернуть.
    public var brokenStreak: Int? {
        streakDay == today - 2 && streak >= 2 && restoredFor != today ? streak : nil
    }

    public func restoreStreak() {
        guard brokenStreak != nil else { return }
        set(&streakDay, today - 1, K.streakDay)
        set(&restoredFor, today, K.restoredFor)
    }

    /// Вехи «Пути огня»: день серии → подсказки. После года — +10 каждые 30 дней.
    public static let milestones: [(day: Int, hints: Int)] = [
        (3, 1), (7, 3), (14, 5), (30, 10), (60, 10), (100, 15), (150, 10), (200, 10), (365, 30),
    ]

    public static func milestoneHints(_ streak: Int) -> Int {
        if let m = milestones.first(where: { $0.day == streak }) { return m.hints }
        return streak > 365 && (streak - 365) % 30 == 0 ? 10 : 0
    }

    /// Стадии пламени: с какого дня серии и какой бонус к опыту. Стадия 0 — серии нет.
    /// Имена — `ui.flame.N`: Искра, Свеча, Факел, Костёр, Маяк, Вечный огонь.
    public static let flameTiers: [(from: Int, bonus: Int)] = [
        (1, 0), (3, 10), (7, 20), (14, 30), (30, 40), (60, 50),
    ]

    public static func flameTier(_ streak: Int) -> Int {
        flameTiers.lastIndex { streak >= $0.from }.map { $0 + 1 } ?? 0
    }

    /// Бонус к опыту за серию, проценты.
    public static func flameBonus(_ streak: Int) -> Int {
        let t = flameTier(streak)
        return t > 0 ? flameTiers[t - 1].bonus : 0
    }

    public var flameTier: Int { Self.flameTier(currentStreak) }

    // MARK: Подарок дня

    public var giftAvailable: Bool { giftDay != today }
    /// Шаг, который выдаст «Забрать» сегодня.
    public var nextGiftStep: Int { giftDay == today - 1 ? giftStep % 7 + 1 : 1 }

    @discardableResult
    public func claimGift() -> Int {
        guard giftAvailable else { return 0 }
        let step = nextGiftStep
        let n = Self.gifts[step - 1]
        set(&giftStep, step, K.giftStep)
        set(&giftDay, today, K.giftDay)
        addHints(n)
        return n
    }

    // MARK: Эпизод дня

    public var dailyDoneToday: Bool { dailyDone == today }

    /// Эпизод дня: детерминированно по дню из первых уровней каждой главы, пройденные — мимо.
    public static func dailyLevel(day: Int, chapters: [(id: String, levels: [String])],
                                  isCompleted: (String) -> Bool,
                                  isDisabled: (String) -> Bool) -> (chapter: String, level: String)? {
        let pool = chapters.flatMap { ch in
            ch.levels.prefix(dailyPoolPerChapter).filter { !isDisabled($0) }.map { (ch.id, $0) }
        }
        let fresh = pool.filter { !isCompleted($0.1) }
        let list = fresh.isEmpty ? pool : fresh
        guard !list.isEmpty else { return nil }
        let h = (UInt64(UInt32(truncatingIfNeeded: day)) &* 2_654_435_761) % 4_294_967_296
        let pick = list[Int(h % UInt64(list.count))]
        return (pick.0, pick.1)
    }

    // MARK: Решение уровня

    public struct SolveReward: Equatable {
        public var xpGained = 0
        public var xpBefore = 0
        public var xpAfter = 0
        public var levelBefore = 1
        public var levelAfter = 1
        public var rankHints = 0
        public var streakBefore = 0
        public var streakAfter = 0
        public var streakGrew = false
        public var milestoneHints = 0
        public var isDaily = false
        public var dailyHints = 0
        public var noHint = false
        /// Бонус пламени к опыту этого решения (проценты) и стадии до/после.
        public var flameBonus = 0
        public var tierBefore = 0
        public var tierAfter = 0
        public var rankedUp: Bool { levelAfter > levelBefore }
        public var flameGrew: Bool { tierAfter > tierBefore }
        public var totalHints: Int { rankHints + milestoneHints + dailyHints }
    }

    /// Первое решение уровня: опыт, звание, серия, эпизод дня. Повторное — только серия дня.
    public func recordSolve(levelId: String, firstSolve: Bool, isDaily: Bool) -> SolveReward {
        var r = SolveReward()
        r.streakBefore = currentStreak
        r.tierBefore = Self.flameTier(r.streakBefore)
        let t = today
        if streakDay != t {
            set(&streak, streakDay == t - 1 ? streak + 1 : 1, K.streak)
            set(&streakDay, t, K.streakDay)
            r.streakGrew = true
            set(&bestStreak, max(bestStreak, streak), K.bestStreak)
            r.milestoneHints = Self.milestoneHints(streak)
        }
        r.streakAfter = streak
        r.tierAfter = Self.flameTier(streak)

        r.xpBefore = xp
        r.levelBefore = level
        if firstSolve {
            r.noHint = !wasHinted(levelId)
            var gain = Self.baseXP + (r.noHint ? Self.noHintBonus : 0)
            if isDaily && !dailyDoneToday {
                gain *= 2
                r.isDaily = true
                r.dailyHints = 1
                set(&dailyDone, t, K.dailyDone)
            }
            r.flameBonus = Self.flameBonus(streak)
            gain += gain * r.flameBonus / 100
            r.xpGained = gain
            set(&xp, xp + gain, K.xp)
        }
        r.xpAfter = xp
        r.levelAfter = level
        r.rankHints = (r.levelAfter - r.levelBefore) * Self.rankUpHints
        if r.totalHints > 0 { addHints(r.totalHints) }
        return r
    }

    // MARK: Интерстишел

    public var sinceInterstitial: Int { d.integer(forKey: K.sinceInter) }
    public var lastFullscreen: Double { d.double(forKey: K.lastFullscreen) }

    public func noteLevelFinished() { d.set(sinceInterstitial + 1, forKey: K.sinceInter) }

    public func noteInterstitialShown() {
        d.set(0, forKey: K.sinceInter)
        noteFullscreenShown()
    }

    public func noteFullscreenShown() { d.set(Date().timeIntervalSince1970, forKey: K.lastFullscreen) }

    // MARK: Прочее

    public var lastLevel: String? {
        get { d.string(forKey: K.lastLevel) }
        set { d.set(newValue, forKey: K.lastLevel) }
    }

    public var pushAsked: Bool {
        get { d.bool(forKey: K.pushAsked) }
        set { d.set(newValue, forKey: K.pushAsked) }
    }

    /// Сброс прогресса из меню: мета обнуляется вместе с пройденными уровнями, подсказки остаются.
    public func reset() {
        set(&xp, 0, K.xp)
        set(&streak, 0, K.streak)
        set(&streakDay, 0, K.streakDay)
        set(&dailyDone, 0, K.dailyDone)
        hinted = []
        d.set([String](), forKey: K.hinted)
    }

    private func set(_ field: inout Int, _ value: Int, _ key: String) {
        field = value
        d.set(value, forKey: key)
    }

    private enum K {
        static let initDone = "ht.meta.init"
        static let xp = "ht.meta.xp"
        static let hints = "ht.meta.hints"
        static let hinted = "ht.meta.hinted"
        static let streak = "ht.meta.streak"
        static let streakDay = "ht.meta.streakDay"
        static let bestStreak = "ht.meta.bestStreak"
        static let giftDay = "ht.meta.giftDay"
        static let giftStep = "ht.meta.giftStep"
        static let dailyDone = "ht.meta.dailyDone"
        static let sinceInter = "ht.meta.sinceInter"
        static let lastFullscreen = "ht.meta.lastFullscreen"
        static let restoredFor = "ht.meta.restoredFor"
        static let pushAsked = "ht.meta.pushAsked"
        static let lastLevel = "ht.meta.lastLevel"
    }
}
