package com.decima.historyteller

import android.content.Context
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.net.HttpURLConnection
import java.net.URL

/**
 * Счётчики прохождения глав — «играет ли в это кто-нибудь и докуда доходит». Порт iOS Stats.
 *
 * Наружу уходит только строка-ключ (`done:rome:sabines`). Ни идентификатора установки, ни
 * времени, ни чего-либо ещё о человеке: на сервере копится «сколько раз ключ приходил»,
 * и связать два ключа одного игрока нельзя даже теоретически. Это осознанное ограничение —
 * оно позволяет не менять обещание политики приватности.
 *
 * Каждый ключ отправляется максимум один раз за установку, поэтому счётчик читается как
 * «столько установок сюда дошло», а не «столько раз запускали».
 */
object Stats {
    private const val ENDPOINT = "https://stats.historyteller.app/c"
    private const val SENT = "sent"
    private const val PENDING = "pending"
    private const val BATCH = 16      // столько же принимает Worker за раз

    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    fun chapterOpened(ctx: Context, chapter: String) = send(ctx, "open:$chapter")

    fun levelSolved(ctx: Context, chapter: String, level: String) = send(ctx, "done:$chapter:$level")

    /** Досылает то, что не ушло раньше. Зовётся на старте: эпизод могли пройти в самолёте. */
    fun flushPending(ctx: Context) = send(ctx, null)

    /**
     * Кладёт ключ в очередь и пытается отправить очередь целиком.
     *
     * Ключ переезжает в «отправленные» только после успеха — иначе пройденный офлайн эпизод
     * пропал бы навсегда, а один запрос на пару десятков байт того не стоит.
     */
    private fun send(ctx: Context, key: String?) {
        // Debug-сборки в счётчики не пишут: иначе своя же отладка выглядит как игроки.
        if (BuildConfig.DEBUG) return
        val prefs = ctx.applicationContext.getSharedPreferences("ht.stats", Context.MODE_PRIVATE)
        val sent = prefs.getStringSet(SENT, emptySet()).orEmpty()
        val pending = prefs.getStringSet(PENDING, emptySet()).orEmpty().toMutableSet()

        if (key != null) {
            if (key in sent) return
            if (!pending.add(key)) return       // уже в очереди — отправку и так вот-вот попробуем
            prefs.edit().putStringSet(PENDING, pending).apply()
        }
        if (pending.isEmpty()) return

        val batch = pending.take(BATCH)
        scope.launch {
            if (!post(batch)) return@launch
            prefs.edit()
                .putStringSet(SENT, sent + batch)
                .putStringSet(PENDING, pending - batch.toSet())
                .apply()
        }
    }

    private fun post(keys: List<String>): Boolean = try {
        val conn = (URL(ENDPOINT).openConnection() as HttpURLConnection).apply {
            requestMethod = "POST"
            connectTimeout = 10_000
            readTimeout = 10_000
            doOutput = true
            setRequestProperty("Content-Type", "application/json")
        }
        try {
            val body = JSONObject().put("e", JSONArray(keys)).toString()
            conn.outputStream.use { it.write(body.toByteArray()) }
            conn.responseCode in 200..299
        } finally {
            conn.disconnect()
        }
    } catch (e: Exception) {
        false      // счётчики — побочная штука, сломать игру они не должны
    }
}

/**
 * Доли прохождения эпизодов: «этот прошли 68% из тех, кто до него добрался». Порт iOS SolveRates.
 *
 * Считает их сервер, сюда приезжают только проценты — абсолютных чисел клиент не видит и
 * показать не может. Эпизоды, по которым выборки мало, сервер просто не присылает, поэтому
 * на пустой статистике карточки молчат сами, без порогов в UI.
 */
object SolveRates {
    private const val ENDPOINT = "https://stats.historyteller.app/p"
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private var table by mutableStateOf<Map<String, Map<String, Int>>>(emptyMap())
    private var cache: File? = null

    /** Процент для карточки. `null` — сервер по этому эпизоду промолчал, показывать нечего. */
    fun percent(chapter: String, level: String): Int? = table[chapter]?.get(level)

    /**
     * Обновить в фоне. Зовём просто на старте: ответ едет с `max-age=600` и его придерживает
     * край, так что частые запуски в базу не бьют.
     */
    fun refresh(ctx: Context) {
        val file = cache ?: File(ctx.applicationContext.filesDir, "solve-rates.json").also { cache = it }
        scope.launch {
            // Сперва с диска: карта не должна «доливать» проценты через секунду после открытия,
            // и офлайн они тоже нужны.
            if (table.isEmpty() && file.exists()) parse(file.readText())?.let { table = it }
            val body = runCatching {
                val conn = (URL(ENDPOINT).openConnection() as HttpURLConnection).apply {
                    connectTimeout = 10_000; readTimeout = 10_000
                }
                try {
                    if (conn.responseCode !in 200..299) null
                    else conn.inputStream.use { it.readBytes().decodeToString() }
                } finally { conn.disconnect() }
            }.getOrNull() ?: return@launch
            parse(body)?.let { table = it; runCatching { file.writeText(body) } }
        }
    }

    private fun parse(text: String): Map<String, Map<String, Int>>? = runCatching {
        val p = JSONObject(text).getJSONObject("p")
        p.keys().asSequence().associateWith { chapter ->
            val levels = p.getJSONObject(chapter)
            levels.keys().asSequence().associateWith { levels.getInt(it) }
        }
    }.getOrNull()
}
