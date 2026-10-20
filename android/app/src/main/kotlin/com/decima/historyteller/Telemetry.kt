package com.decima.historyteller

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.util.UUID
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit

/**
 * Анонимная статистика игры для скрытого админ-экрана в iOS (сервер `server/stats`, Cloudflare).
 * Порт iOS Telemetry. Игрок — случайный ID установки; имени, почты, рекламного ID и
 * местоположения нет (страну определяет Cloudflare). События копятся и уходят пачкой; без сети
 * очередь ждёт следующей попытки.
 */
object Telemetry {
    private const val ENDPOINT = "https://stats.historyteller.app/e"
    private const val PREFS = "ht.telemetry"
    private const val MAX_QUEUE = 200

    private val io = Executors.newSingleThreadScheduledExecutor()
    private lateinit var appContext: Context
    private lateinit var iid: String
    private val queue = ArrayList<JSONObject>()
    private var flushScheduled = false

    fun init(context: Context) {
        if (::appContext.isInitialized) return
        appContext = context.applicationContext
        val p = appContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        iid = p.getString("iid", null) ?: UUID.randomUUID().toString().also { p.edit().putString("iid", it).apply() }
        runCatching { JSONArray(p.getString("queue", "[]")) }.getOrNull()?.let { arr ->
            for (i in 0 until arr.length()) queue += arr.getJSONObject(i)
        }
    }

    /** `session` | `level_start` | `level_complete` | `ad_unlock`. */
    fun track(type: String, level: String? = null, chapter: String? = null) {
        if (!::appContext.isInitialized) return
        val ev = JSONObject().put("type", type)
        level?.let { ev.put("level", it) }
        chapter?.let { ev.put("chapter", it) }
        io.execute {
            queue += ev
            while (queue.size > MAX_QUEUE) queue.removeAt(0)
            persist()
            // Небольшая пауза — события одного действия уходят вместе.
            if (!flushScheduled) { flushScheduled = true; io.schedule({ flush() }, 2, TimeUnit.SECONDS) }
        }
    }

    private fun flush() {
        flushScheduled = false
        while (queue.isNotEmpty()) {
            val batch = queue.take(50)
            val body = JSONObject()
                .put("iid", iid).put("platform", "android")
                .put("ver", BuildConfig.VERSION_NAME).put("lang", L10n.lang)
                .put("events", JSONArray(batch))
            val ok = runCatching {
                val c = URL(ENDPOINT).openConnection() as HttpURLConnection
                c.requestMethod = "POST"; c.doOutput = true
                c.connectTimeout = 15000; c.readTimeout = 15000
                c.setRequestProperty("Content-Type", "application/json")
                c.outputStream.use { it.write(body.toString().toByteArray()) }
                val code = c.responseCode
                c.disconnect()
                code in 200..299
            }.getOrDefault(false)
            if (!ok) return
            repeat(batch.size) { if (queue.isNotEmpty()) queue.removeAt(0) }
            persist()
        }
    }

    private fun persist() {
        appContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit()
            .putString("queue", JSONArray(queue).toString()).apply()
    }
}
