package com.decima.historyteller

import android.Manifest
import android.app.Activity
import android.app.AlarmManager
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import java.util.Calendar

/**
 * Локальные напоминания (`docs/f2p-patch-4.0.md` §3). Перепланируются при уходе в фон и после
 * каждого решения: снимаем все наши и ставим заново — серия, эпизод дня, подарок, неделя.
 *
 * AlarmManager с неточным `setAndAllowWhileIdle`: точное время не нужно, а точные будильники
 * требуют отдельного разрешения. Текст считаем при планировании — в момент срабатывания
 * процесс может быть холодным, и каталога переводов в памяти нет.
 */
object Notifications {
    const val CHANNEL = "ht.reminders"
    private const val REQUEST_PERMISSION = 4001
    private val KINDS = listOf("streak", "daily", "comeback", "week")

    /** Канал — на старте приложения (без него Android 8+ уведомление не покажет). */
    fun createChannel(ctx: Context) {
        val nm = ctx.getSystemService(NotificationManager::class.java) ?: return
        if (nm.getNotificationChannel(CHANNEL) != null) return
        nm.createNotificationChannel(NotificationChannel(CHANNEL, "History Teller", NotificationManager.IMPORTANCE_DEFAULT))
    }

    /** Системное разрешение — один раз, после закрытия первого экрана награды. */
    fun askOnce(activity: Activity?) {
        if (Meta.pushAsked) return
        Meta.pushAsked = true
        if (activity != null && Build.VERSION.SDK_INT >= 33 &&
            activity.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            activity.requestPermissions(arrayOf(Manifest.permission.POST_NOTIFICATIONS), REQUEST_PERMISSION)
        }
        reschedule(activity ?: return)
    }

    /**
     * Снять наши и поставить заново. До вопроса о разрешении не планируем ничего — как на iOS,
     * где без разрешения напоминаний нет. Без загруженного контента (холодный старт) — тоже.
     */
    fun reschedule(ctx: Context) {
        if (!Meta.pushAsked || GameContent.levels.isEmpty() && ContentSync.availableChapters().isEmpty()) return
        val am = ctx.getSystemService(AlarmManager::class.java) ?: return
        KINDS.forEachIndexed { i, k -> am.cancel(pending(ctx, i, k, null)) }

        val progress = Progress(ctx)
        val now = System.currentTimeMillis()
        fun at(daysAhead: Int, hour: Int): Long = Calendar.getInstance().apply {
            add(Calendar.DAY_OF_YEAR, daysAhead)
            set(Calendar.HOUR_OF_DAY, hour); set(Calendar.MINUTE, 0)
            set(Calendar.SECOND, 0); set(Calendar.MILLISECOND, 0)
        }.timeInMillis
        fun schedule(kind: String, time: Long, body: String) {
            if (time <= now) return
            val pi = pending(ctx, KINDS.indexOf(kind), kind, body)
            runCatching { am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, time, pi) }
        }
        fun title(id: String) = L10n.opt("level.$id.title") ?: GameContent.level(id)?.title

        // Серия сгорает сегодня в полночь — напоминаем вечером, если сегодня ещё не решал.
        val streak = Meta.currentStreak
        if (streak >= 1 && !Meta.solvedToday) schedule("streak", at(0, 20), L10n.s("ui.push.streak", streak))
        // Эпизод дня — завтрашний.
        Daily.pick(progress, Meta.today + 1)?.let { (_, id) ->
            title(id)?.let { schedule("daily", at(1, 19), L10n.s("ui.push.daily", it)) }
        }
        schedule("comeback", at(3, 18), L10n.s("ui.push.gift"))
        // Неделя: последний открытый эпизод, а если он пройден — следующий за ним в главе.
        weekLevel(progress)?.let { id -> title(id)?.let { schedule("week", at(7, 18), L10n.s("ui.push.week", it)) } }
    }

    private fun weekLevel(progress: Progress): String? {
        val last = Meta.lastLevel ?: return GameContent.levels.firstOrNull { !progress.isCompleted(it.id) }?.id
        if (!progress.isCompleted(last)) return last
        val epoch = GameContent.level(last)?.epoch
        val ids = ContentSync.availableChapters().firstOrNull { it.id == epoch }?.levels
            ?: GameContent.levels(epoch ?: "").map { it.id }
        val i = ids.indexOf(last)
        return ids.getOrNull(i + 1)?.takeUnless { ContentSync.isLevelDisabled(it) } ?: last
    }

    private fun pending(ctx: Context, code: Int, kind: String, body: String?): PendingIntent {
        val intent = Intent(ctx, ReminderReceiver::class.java).setAction("ht.reminder.$kind")
        if (body != null) intent.putExtra("body", body).putExtra("id", code)
        return PendingIntent.getBroadcast(ctx, code, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
    }
}

/** Будильник сработал — показываем уведомление; тап открывает игру. */
class ReminderReceiver : BroadcastReceiver() {
    override fun onReceive(ctx: Context, intent: Intent) {
        val body = intent.getStringExtra("body") ?: return
        if (Build.VERSION.SDK_INT >= 33 &&
            ctx.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) return
        Notifications.createChannel(ctx)
        val open = PendingIntent.getActivity(ctx, 0,
            Intent(ctx, MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
        val n = Notification.Builder(ctx, Notifications.CHANNEL)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle("History Teller")
            .setContentText(body)
            .setStyle(Notification.BigTextStyle().bigText(body))
            .setContentIntent(open)
            .setAutoCancel(true)
            .build()
        runCatching { ctx.getSystemService(NotificationManager::class.java)?.notify(intent.getIntExtra("id", 0), n) }
    }
}
