package com.decima.historyteller

import android.app.Activity
import android.content.Context
import com.google.android.play.core.review.ReviewManagerFactory

/**
 * Когда просить оценку в Google Play. Порт iOS `ReviewPrompt`, правила те же и нарочно строгие:
 * просим только у того, кто втянулся (несколько уровней и не одна глава), не чаще раза в сутки
 * и не больше трёх раз за всё время. Момент — выход с пройденного уровня, сразу после награды.
 *
 * Диалог Play показывается только у сборок, установленных из магазина, и сам решает, показывать
 * ли его вообще; вне Play вызов молча ничего не делает — это нормально и ошибкой не считается.
 */
object ReviewPrompt {
    private const val PREFS = "ht.review"
    private const val LAST = "lastAsked"
    private const val COUNT = "askCount"
    const val MIN_SOLVED = 10
    const val MIN_CHAPTERS = 2
    const val MAX_ASKS = 3
    private const val COOLDOWN_MS = 24L * 60 * 60 * 1000

    fun shouldAsk(ctx: Context, solvedCount: Int, chaptersTouched: Int, now: Long = System.currentTimeMillis()): Boolean {
        if (solvedCount < MIN_SOLVED || chaptersTouched < MIN_CHAPTERS) return false
        val p = ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        if (p.getInt(COUNT, 0) >= MAX_ASKS) return false
        val last = p.getLong(LAST, 0L)
        return last == 0L || now - last >= COOLDOWN_MS
    }

    /** Показать окно оценки и отметить попытку (даже если Play решит окно не рисовать). */
    fun ask(activity: Activity) {
        val p = activity.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        p.edit().putLong(LAST, System.currentTimeMillis()).putInt(COUNT, p.getInt(COUNT, 0) + 1).apply()
        val manager = ReviewManagerFactory.create(activity)
        manager.requestReviewFlow().addOnCompleteListener { task ->
            if (task.isSuccessful) manager.launchReviewFlow(activity, task.result)
        }
    }
}
