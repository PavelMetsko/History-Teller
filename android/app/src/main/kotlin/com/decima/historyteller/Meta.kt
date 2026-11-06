package com.decima.historyteller

import android.content.Context
import android.content.SharedPreferences
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import java.util.TimeZone
import kotlin.math.floor

/**
 * Мета-прогресс поверх пройденных уровней: опыт и звания, подсказки, серия дней, подарок дня,
 * эпизод дня и счётчики интерстишела. Правила — `docs/f2p-patch-4.0.md`, порт iOS `Meta` 1:1.
 * «День» — локальный календарный, чтобы серия и подарок сменялись в полночь игрока, а не по UTC.
 *
 * Хранение — SharedPreferences `ht` с ключами `ht.meta.*` (те же имена, что в UserDefaults на iOS).
 * Поля — Compose-состояние: меню, доска и экран награды перерисовываются сами.
 */
object Meta {
    const val BASE_XP = 100
    const val NO_HINT_BONUS = 50
    const val START_HINTS = 3
    const val RANK_UP_HINTS = 2
    /** Подарок дня по шагу календаря 1…7. */
    val GIFTS = listOf(1, 1, 2, 1, 2, 2, 3)
    /** Сколько первых уровней каждой главы идут в эпизоды дня — поздние слишком сложны для «зашёл на минуту». */
    const val DAILY_POOL_PER_CHAPTER = 10
    const val RANK_NAMES = 15

    var xp by mutableIntStateOf(0); private set
    var hints by mutableIntStateOf(0); private set
    var streak by mutableIntStateOf(0); private set
    var streakDay by mutableIntStateOf(0); private set
    var bestStreak by mutableIntStateOf(0); private set
    var giftDay by mutableIntStateOf(0); private set
    var giftStep by mutableIntStateOf(0); private set
    var dailyDone by mutableIntStateOf(0); private set
    var restoredFor by mutableIntStateOf(0); private set
    private var hinted by mutableStateOf<Set<String>>(emptySet())

    private lateinit var d: SharedPreferences

    /** Раз за процесс, из MainActivity — до первого обращения к полям. */
    fun init(ctx: Context) {
        if (::d.isInitialized) return
        d = ctx.applicationContext.getSharedPreferences("ht", Context.MODE_PRIVATE)
        xp = d.getInt(K.XP, 0)
        hints = d.getInt(K.HINTS, 0)
        streak = d.getInt(K.STREAK, 0)
        streakDay = d.getInt(K.STREAK_DAY, 0)
        bestStreak = d.getInt(K.BEST_STREAK, 0)
        giftDay = d.getInt(K.GIFT_DAY, 0)
        giftStep = d.getInt(K.GIFT_STEP, 0)
        dailyDone = d.getInt(K.DAILY_DONE, 0)
        restoredFor = d.getInt(K.RESTORED_FOR, 0)
        hinted = d.getStringSet(K.HINTED, emptySet())?.toSet() ?: emptySet()
    }

    /** Один раз при первом запуске 4.0: стартовые подсказки и опыт за уже пройденное. */
    fun bootstrap(solvedCount: Int) {
        if (d.getBoolean(K.INIT_DONE, false)) return
        d.edit().putBoolean(K.INIT_DONE, true).apply()
        hints = put(K.HINTS, START_HINTS)
        xp = put(K.XP, solvedCount * BASE_XP)
    }

    // ---- День ----

    fun day(millis: Long = System.currentTimeMillis()): Int {
        val s = millis / 1000.0 + TimeZone.getDefault().getOffset(millis) / 1000.0
        return floor(s / 86_400).toInt()
    }

    val today: Int get() = day()

    // ---- Звания ----

    /** Опыт, с которого начинается уровень `n` (n ≥ 1): 0, 200, 450, 750, 1100, … */
    fun threshold(n: Int): Int {
        if (n <= 1) return 0
        return (1 until n).fold(0) { acc, k -> acc + 150 + 50 * k }
    }

    fun levelForXP(xp: Int): Int {
        var n = 1
        while (threshold(n + 1) <= xp) n++
        return n
    }

    val level: Int get() = levelForXP(xp)

    /** Ключ имени звания (`ui.rank.N`): после пятнадцатого имя больше не меняется. */
    fun rankKey(level: Int): String = "ui.rank.${level.coerceIn(1, RANK_NAMES)}"

    /** Доля пути к следующему уровню, 0…1. */
    fun levelProgress(xp: Int): Float {
        val n = levelForXP(xp)
        val lo = threshold(n); val hi = threshold(n + 1)
        return (xp - lo).toFloat() / maxOf(1, hi - lo)
    }

    // ---- Подсказки ----

    fun wasHinted(levelId: String) = levelId in hinted

    /** Списать подсказку. Premium не тратит. Уровень помечается — без бонуса «без подсказок». */
    fun spendHint(levelId: String, premium: Boolean): Boolean {
        if (!premium && hints <= 0) return false
        if (!premium) hints = put(K.HINTS, hints - 1)
        markHinted(levelId)
        return true
    }

    /** Подсказка за ролик: сразу применяется, в запас не идёт. */
    fun markHinted(levelId: String) {
        hinted = hinted + levelId
        d.edit().putStringSet(K.HINTED, hinted).apply()
    }

    fun addHints(n: Int) { hints = put(K.HINTS, hints + n) }

    // ---- Серия ----

    /** Серия, которую показываем: живая, пока вчера или сегодня что-то решено. */
    val currentStreak: Int get() = if (streakDay >= today - 1) streak else 0
    val solvedToday: Boolean get() = streakDay == today

    /** Прервалась ровно вчера (позавчера решал, вчера нет) — её ещё можно вернуть. */
    val brokenStreak: Int?
        get() = if (streakDay == today - 2 && streak >= 2 && restoredFor != today) streak else null

    fun restoreStreak() {
        if (brokenStreak == null) return
        streakDay = put(K.STREAK_DAY, today - 1)
        restoredFor = put(K.RESTORED_FOR, today)
    }

    /** Вехи «Пути огня»: день серии → подсказки. После года — +10 каждые 30 дней. */
    val milestones: List<Pair<Int, Int>> = listOf(
        3 to 1, 7 to 3, 14 to 5, 30 to 10, 60 to 10, 100 to 15, 150 to 10, 200 to 10, 365 to 30,
    )

    fun milestoneHints(streak: Int): Int {
        milestones.firstOrNull { it.first == streak }?.let { return it.second }
        return if (streak > 365 && (streak - 365) % 30 == 0) 10 else 0
    }

    /** Стадии пламени: с какого дня серии и бонус к опыту (%). Стадия 0 — серии нет.
     *  Имена — `ui.flame.N`: Искра, Свеча, Факел, Костёр, Маяк, Вечный огонь. */
    val flameTiers: List<Pair<Int, Int>> = listOf(1 to 0, 3 to 10, 7 to 20, 14 to 30, 30 to 40, 60 to 50)

    fun flameTier(streak: Int): Int = flameTiers.indexOfLast { streak >= it.first } + 1

    fun flameBonus(streak: Int): Int { val t = flameTier(streak); return if (t > 0) flameTiers[t - 1].second else 0 }

    val currentFlameTier: Int get() = flameTier(currentStreak)

    // ---- Подарок дня ----

    val giftAvailable: Boolean get() = giftDay != today
    /** Шаг, который выдаст «Забрать» сегодня. */
    val nextGiftStep: Int get() = if (giftDay == today - 1) giftStep % 7 + 1 else 1

    fun claimGift(): Int {
        if (!giftAvailable) return 0
        val step = nextGiftStep
        val n = GIFTS[step - 1]
        giftStep = put(K.GIFT_STEP, step)
        giftDay = put(K.GIFT_DAY, today)
        addHints(n)
        return n
    }

    // ---- Эпизод дня ----

    val dailyDoneToday: Boolean get() = dailyDone == today

    /** Эпизод дня: детерминированно по дню из первых уровней каждой главы, пройденные — мимо. */
    fun dailyLevel(day: Int, chapters: List<Pair<String, List<String>>>,
                   isCompleted: (String) -> Boolean, isDisabled: (String) -> Boolean): Pair<String, String>? {
        val pool = chapters.flatMap { (ch, levels) ->
            levels.take(DAILY_POOL_PER_CHAPTER).filterNot(isDisabled).map { ch to it }
        }
        val fresh = pool.filterNot { isCompleted(it.second) }
        val list = fresh.ifEmpty { pool }
        if (list.isEmpty()) return null
        // (UInt32(day) × 2654435761) mod 2^32: в Long умножение переполняется по модулю 2^64,
        // младшие 32 бита от этого не меняются — ровно то же, что `&*` в Swift.
        val h = (day.toLong() * 2_654_435_761L) and 0xFFFF_FFFFL
        return list[(h % list.size).toInt()]
    }

    // ---- Решение уровня ----

    data class SolveReward(
        var xpGained: Int = 0,
        var xpBefore: Int = 0,
        var xpAfter: Int = 0,
        var levelBefore: Int = 1,
        var levelAfter: Int = 1,
        var rankHints: Int = 0,
        var streakBefore: Int = 0,
        var streakAfter: Int = 0,
        var streakGrew: Boolean = false,
        var milestoneHints: Int = 0,
        var isDaily: Boolean = false,
        var dailyHints: Int = 0,
        var noHint: Boolean = false,
        var flameBonus: Int = 0,
        var tierBefore: Int = 0,
        var tierAfter: Int = 0,
    ) {
        val flameGrew: Boolean get() = tierAfter > tierBefore
        val rankedUp: Boolean get() = levelAfter > levelBefore
        val totalHints: Int get() = rankHints + milestoneHints + dailyHints
    }

    /** Первое решение уровня: опыт, звание, серия, эпизод дня. Повторное — только серия дня. */
    fun recordSolve(levelId: String, firstSolve: Boolean, isDaily: Boolean): SolveReward {
        val r = SolveReward()
        r.streakBefore = currentStreak
        r.tierBefore = flameTier(r.streakBefore)
        val t = today
        if (streakDay != t) {
            streak = put(K.STREAK, if (streakDay == t - 1) streak + 1 else 1)
            streakDay = put(K.STREAK_DAY, t)
            r.streakGrew = true
            bestStreak = put(K.BEST_STREAK, maxOf(bestStreak, streak))
            r.milestoneHints = milestoneHints(streak)
        }
        r.streakAfter = streak
        r.tierAfter = flameTier(streak)

        r.xpBefore = xp
        r.levelBefore = level
        if (firstSolve) {
            r.noHint = !wasHinted(levelId)
            var gain = BASE_XP + if (r.noHint) NO_HINT_BONUS else 0
            if (isDaily && !dailyDoneToday) {
                gain *= 2
                r.isDaily = true
                r.dailyHints = 1
                dailyDone = put(K.DAILY_DONE, t)
            }
            r.flameBonus = flameBonus(streak)
            gain += gain * r.flameBonus / 100
            r.xpGained = gain
            xp = put(K.XP, xp + gain)
        }
        r.xpAfter = xp
        r.levelAfter = level
        r.rankHints = (r.levelAfter - r.levelBefore) * RANK_UP_HINTS
        if (r.totalHints > 0) addHints(r.totalHints)
        return r
    }

    // ---- Интерстишел ----

    val sinceInterstitial: Int get() = d.getInt(K.SINCE_INTER, 0)
    /** Unix-секунды последней полноэкранной рекламы. Double, как на iOS: храним битами в Long. */
    val lastFullscreen: Double
        get() = java.lang.Double.longBitsToDouble(d.getLong(K.LAST_FULLSCREEN, java.lang.Double.doubleToRawLongBits(0.0)))

    fun noteLevelFinished() { d.edit().putInt(K.SINCE_INTER, sinceInterstitial + 1).apply() }

    fun noteInterstitialShown() {
        d.edit().putInt(K.SINCE_INTER, 0).apply()
        noteFullscreenShown()
    }

    fun noteFullscreenShown() {
        d.edit().putLong(K.LAST_FULLSCREEN,
            java.lang.Double.doubleToRawLongBits(System.currentTimeMillis() / 1000.0)).apply()
    }

    // ---- Прочее ----

    var lastLevel: String?
        get() = d.getString(K.LAST_LEVEL, null)
        set(v) = d.edit().putString(K.LAST_LEVEL, v).apply()

    var pushAsked: Boolean
        get() = d.getBoolean(K.PUSH_ASKED, false)
        set(v) = d.edit().putBoolean(K.PUSH_ASKED, v).apply()

    /** Сброс прогресса из меню: мета обнуляется вместе с пройденными уровнями, подсказки остаются. */
    fun reset() {
        xp = put(K.XP, 0)
        streak = put(K.STREAK, 0)
        streakDay = put(K.STREAK_DAY, 0)
        dailyDone = put(K.DAILY_DONE, 0)
        hinted = emptySet()
        d.edit().putStringSet(K.HINTED, emptySet()).apply()
    }

    internal fun prefString(key: String): String? = d.getString(key, null)
    internal fun putPrefString(key: String, value: String?) { d.edit().putString(key, value).apply() }

    private fun put(key: String, value: Int): Int {
        d.edit().putInt(key, value).apply()
        return value
    }

    private object K {
        const val INIT_DONE = "ht.meta.init"
        const val XP = "ht.meta.xp"
        const val HINTS = "ht.meta.hints"
        const val HINTED = "ht.meta.hinted"
        const val STREAK = "ht.meta.streak"
        const val STREAK_DAY = "ht.meta.streakDay"
        const val BEST_STREAK = "ht.meta.bestStreak"
        const val GIFT_DAY = "ht.meta.giftDay"
        const val GIFT_STEP = "ht.meta.giftStep"
        const val DAILY_DONE = "ht.meta.dailyDone"
        const val SINCE_INTER = "ht.meta.sinceInter"
        const val LAST_FULLSCREEN = "ht.meta.lastFullscreen"
        const val RESTORED_FOR = "ht.meta.restoredFor"
        const val PUSH_ASKED = "ht.meta.pushAsked"
        const val LAST_LEVEL = "ht.meta.lastLevel"
    }
}

/**
 * «Без рекламы» — поглавно. Играются все главы (с рекламой), а купленная глава даёт в ней
 * самой: нет интерстишелов и безлимитные подсказки. Подписчики (3.x) сохраняют всё везде.
 */
object Premium {
    fun adsFree(epoch: String?): Boolean =
        Billing.subscribed || (epoch != null && epoch in Billing.unlockedEpochs)
}

/**
 * Эпизод дня поверх манифеста. Сегодняшний выбор запоминается в `ht.meta.dailyPick` =
 * «day|chapter|level» (как на iOS): пул исключает пройденные, и без этого карточка в меню
 * «перескакивала» бы на другой эпизод после любого решённого уровня из первых десяти.
 */
object Daily {
    private const val KEY = "ht.meta.dailyPick"

    fun chapters(): List<Pair<String, List<String>>> =
        ContentSync.availableChapters().map { it.id to it.levels }

    /** (глава, уровень) на день `day`. Сегодняшний сохраняется, остальные считаются как есть. */
    fun pick(progress: Progress, day: Int = Meta.today): Pair<String, String>? {
        val today = Meta.today
        if (day == today) {
            Meta.prefString(KEY)?.split("|")?.takeIf { it.size == 3 && it[0] == "$today" }?.let { return it[1] to it[2] }
        }
        val p = Meta.dailyLevel(day, chapters(), progress::isCompleted, ContentSync::isLevelDisabled) ?: return null
        if (day == today) Meta.putPrefString(KEY, "$today|${p.first}|${p.second}")
        return p
    }

    fun isDaily(progress: Progress, levelId: String): Boolean = pick(progress)?.second == levelId

    /** После сброса прогресса пул снова полный — сегодняшний выбор пересчитываем. */
    fun invalidate() { Meta.putPrefString(KEY, null) }
}
