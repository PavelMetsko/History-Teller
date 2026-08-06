package com.decima.historyteller

import android.content.Context
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import java.io.File
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest

/** Манифест облачного контента (собирается tools/publish_content.py). Порт iOS ContentManifest. */
@Serializable
data class ContentManifest(
    val version: Int,
    val minAppVersion: String,
    val chapters: List<Chapter>,
    val disabled: List<String>,
    val core: List<String>,
    val chapterFiles: Map<String, List<String>>,
    val files: Map<String, FileRef>,
) {
    @Serializable data class FileRef(val h: String, val s: Int)
    @Serializable data class Chapter(
        val id: String,
        val number: Int,
        val cover: String,
        val icon: String,
        val free: Boolean,
        val minAppVersion: String,
        val levels: List<String>,
    )
}

/**
 * Доставка контента из облака. Порт iOS ContentSync.
 *
 * Файлы лежат в кеше **по хешу** (`objects/<sha256>`), а не по имени: при смене версии контента
 * не бывает устаревших файлов, одинаковый арт разных глав хранится один раз, а прерванная
 * докачка не оставляет главу в полуготовом виде — готовность считается по наличию всех объектов.
 *
 * Кеш — в filesDir, а не в cacheDir: систему никто не просил вычищать арт посреди сессии.
 */
object ContentSync {
    sealed interface Phase {
        object Idle : Phase
        data class Syncing(val progress: Float) : Phase
        object Ready : Phase
        data class Failed(val message: String) : Phase
    }

    var phase by mutableStateOf<Phase>(Phase.Idle); private set
    var manifest by mutableStateOf<ContentManifest?>(null); private set

    /**
     * Растёт после каждой удачной докачки. Служит ключом для `remember` в Compose: версия
     * манифеста при докачке главы не меняется, а новые файлы появляются — без этого счётчика
     * кадр так и держал бы промах кеша.
     */
    var generation by mutableStateOf(0); private set

    /**
     * Базовый URL раздачи — публичный dev-адрес бакета R2. Cloudflare его троттлит и не
     * рекомендует для продакшена: перед релизом сюда должен встать свой домен.
     *
     * Для локального стенда (`tools/publish_content.py --serve`) ставится в `http://10.0.2.2:8787`
     * — это адрес хоста изнутри эмулятора; открытый HTTP с API 28 требует networkSecurityConfig.
     */
    var baseUrl: String = "https://pub-6903ffa4531e43d19ab534800387df28.r2.dev"

    private val json = Json { ignoreUnknownKeys = true }
    private lateinit var root: File
    private lateinit var objects: File

    private fun ensureDirs(ctx: Context) {
        if (::objects.isInitialized) return
        root = File(ctx.filesDir, "content")
        objects = File(root, "objects").apply { mkdirs() }
        manifest = runCatching { json.decodeFromString<ContentManifest>(File(root, "manifest.json").readText()) }
            .getOrNull()
    }

    // ---- Доступ к файлам ----

    /** Логический путь (`art/char_caesar.webp`) → файл на диске, если он скачан. */
    fun fileFor(logical: String): File? {
        val ref = manifest?.files?.get(logical) ?: return null
        return File(objects, ref.h).takeIf { it.exists() }
    }

    /** Содержимое скачанного текстового файла (JSON контента), если он есть. */
    fun text(logical: String): String? = fileFor(logical)?.readText()

    /**
     * Порядок уровней по всем доступным главам, с учётом [disabled].
     * `null` — манифеста ещё нет, вызывающий откатывается на вшитый набор.
     */
    fun levelIds(): List<String>? {
        if (manifest == null) return null
        return availableChapters().flatMap { it.levels }.filterNot { isLevelDisabled(it) }
    }

    fun isChapterReady(id: String): Boolean {
        val files = manifest?.chapterFiles?.get(id) ?: return false
        return files.all { fileFor(it) != null }
    }

    /** Главы, доступные этой сборке: манифест может нести контент, требующий более новой версии. */
    fun availableChapters(): List<ContentManifest.Chapter> =
        manifest?.chapters.orEmpty().filter { supports(it.minAppVersion) }

    fun isLevelDisabled(id: String): Boolean = manifest?.disabled?.contains(id) == true

    // ---- Синхронизация ----

    /** Обновить манифест и докачать core — после этого работают меню, список глав и локализация. */
    suspend fun syncCore(ctx: Context) = withContext(Dispatchers.IO) {
        ensureDirs(ctx)
        phase = Phase.Syncing(0f)
        try {
            val fresh = json.decodeFromString<ContentManifest>(String(get("manifest.json")))
            if (!supports(fresh.minAppVersion)) {
                // Контент новее приложения целиком — работаем на том, что уже скачано.
                phase = if (manifest == null) Phase.Failed("Требуется обновление приложения") else Phase.Ready
                return@withContext
            }
            // Какие главы были собраны — считаем по ПРЕЖНЕМУ манифесту, пока он ещё актуален.
            // По новому это не определить: правка, задевшая все файлы главы разом, обнулила бы
            // все хеши, и глава выглядела бы никогда не скачанной.
            val installed = chaptersReady(manifest)
            manifest = fresh
            download(fresh.core, fresh)
            // Догружаем изменившееся в собранных главах: иначе правка уровня выкинула бы его
            // с карты — файл сменил хеш, а в кеше лежит прежний.
            for (id in installed) fresh.chapterFiles[id]?.let { download(it, fresh) }
            // Манифест фиксируем только когда всё реально на диске.
            File(root, "manifest.json").writeText(json.encodeToString(ContentManifest.serializer(), fresh))
            pruneOrphans(fresh)
            generation++
            Audio.reloadSfx(ctx)
            phase = Phase.Ready
        } catch (e: Exception) {
            // Офлайн — не беда, если прошлый манифест и его файлы уже лежат.
            phase = if (manifest != null) Phase.Ready else Phase.Failed(e.message ?: "Нет связи с сервером контента")
        }
    }

    /** Докачать главу. Если всё на месте — возвращается сразу. */
    suspend fun ensureChapter(ctx: Context, id: String) = withContext(Dispatchers.IO) {
        ensureDirs(ctx)
        val m = manifest
        val files = m?.chapterFiles?.get(id)
        if (m == null || files == null) { phase = Phase.Failed("Глава $id не найдена в манифесте"); return@withContext }
        if (isChapterReady(id)) { phase = Phase.Ready; return@withContext }
        phase = Phase.Syncing(0f)
        try {
            download(files, m)
            generation++
            Audio.reloadSfx(ctx)
            phase = Phase.Ready
        } catch (e: Exception) {
            phase = Phase.Failed(e.message ?: "Не удалось скачать главу")
        }
    }

    // ---- Внутреннее ----

    /**
     * Главы, полностью собранные по данному манифесту. Вызывается до подмены манифеста —
     * по прежним хешам, потому что только они описывают то, что реально лежит на диске.
     */
    private fun chaptersReady(m: ContentManifest?): List<String> {
        if (m == null) return emptyList()
        return m.chapterFiles.filterValues { files ->
            files.all { path -> m.files[path]?.let { File(objects, it.h).exists() } == true }
        }.keys.toList()
    }

    /**
     * Выкидывает объекты, на которые новый манифест больше не ссылается: после правки контента
     * прежняя версия файла осталась бы на диске навсегда.
     */
    private fun pruneOrphans(m: ContentManifest) {
        val alive = m.files.values.map { it.h }.toHashSet()
        objects.listFiles()?.forEach { if (it.name !in alive) it.delete() }
    }

    /** Качает недостающие объекты. Прогресс — по байтам, чтобы полоска не скакала на мелких JSON. */
    private fun download(logical: List<String>, m: ContentManifest) {
        val missing = logical.mapNotNull { path ->
            val ref = m.files[path] ?: return@mapNotNull null
            if (File(objects, ref.h).exists()) null else path to ref
        }
        if (missing.isEmpty()) return

        val total = missing.sumOf { it.second.s }.coerceAtLeast(1)
        var done = 0
        // Последовательно: контент мелкий, а так прогресс честный и мы не забиваем канал.
        for ((path, ref) in missing) {
            val bytes = get("f/${ref.h}")
            val actual = MessageDigest.getInstance("SHA-256").digest(bytes)
                .joinToString("") { "%02x".format(it) }
            if (actual != ref.h) throw IllegalStateException("Файл повреждён при загрузке: $path")
            // Пишем во временный файл и переименовываем: оборванная закачка не оставит битый
            // объект, который потом будет считаться готовым.
            val tmp = File(objects, "${ref.h}.part")
            tmp.writeBytes(bytes)
            val dst = File(objects, ref.h)
            dst.delete()
            if (!tmp.renameTo(dst)) throw IllegalStateException("Не удалось сохранить $path")
            done += ref.s
            phase = Phase.Syncing(done.toFloat() / total)
        }
    }

    private fun get(path: String): ByteArray {
        val conn = (URL("${baseUrl.trimEnd('/')}/$path").openConnection() as HttpURLConnection).apply {
            connectTimeout = 15_000
            readTimeout = 30_000
        }
        try {
            if (conn.responseCode !in 200..299) {
                throw IllegalStateException("Сервер контента ответил ${conn.responseCode}")
            }
            return conn.inputStream.use { it.readBytes() }
        } finally {
            conn.disconnect()
        }
    }

    /**
     * Потянет ли эта сборка контент, требующий версии [required].
     * Сравниваем по числовым компонентам: строковое сравнение считает "1.10" старше "1.9".
     */
    private fun supports(required: String): Boolean {
        val a = BuildConfig.VERSION_NAME.split(".").map { it.toIntOrNull() ?: 0 }
        val b = required.split(".").map { it.toIntOrNull() ?: 0 }
        for (i in 0 until maxOf(a.size, b.size)) {
            val x = a.getOrElse(i) { 0 }
            val y = b.getOrElse(i) { 0 }
            if (x != y) return x > y
        }
        return true
    }
}
