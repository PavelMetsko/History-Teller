package com.decima.historyteller

import android.content.Context
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import java.io.File
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest
import java.util.UUID

/** Манифест облачного контента (собирается tools/publish_content.py). Порт iOS ContentManifest. */
@Serializable
data class ContentManifest(
    val version: Int,
    val minAppVersion: String,
    val chapters: List<Chapter>,
    val disabled: List<String>,
    /** Показательный уровень: на нём построены онбординг и экран загрузки главы. Лежит в core. */
    val demo: String? = null,
    val core: List<String>,
    /** Описания уровней главы — всё, что нужно, чтобы открыть её карту. Килобайты. */
    val chapterIndex: Map<String, List<String>> = emptyMap(),
    /** Обложки карточек в порядке прохождения — качаются фоном, уже на открытой карте. */
    val chapterCovers: Map<String, List<String>> = emptyMap(),
    /** Файлы одного уровня: гейт при входе в него и единица фоновой докачки. */
    val levelFiles: Map<String, List<String>> = emptyMap(),
    /** Глава целиком. Осталось ради манифестов, сохранённых до поуровневой загрузки. */
    val chapterFiles: Map<String, List<String>>,
    val files: Map<String, FileRef>,
    /** Реклама за уровень — выключатель без релиза. Нет блока — реклама включена, без кулдауна. */
    val ads: Ads? = null,
) {
    @Serializable data class Ads(val rewarded: Boolean? = null, val cooldownSec: Int? = null)
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
    var baseUrl: String = "https://cdn.historyteller.app"

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

    /**
     * Описания уровней главы: без них не собрать карту. Старый манифест поуровневых списков
     * не знает — там гейтом остаётся глава целиком.
     */
    private fun indexFiles(id: String): List<String>? {
        val m = manifest ?: return null
        return m.chapterIndex[id] ?: m.chapterFiles[id]
    }

    /** Файлы одного уровня. Пусто — манифест старый, значит глава уже скачана целиком. */
    private fun levelFiles(id: String): List<String> = manifest?.levelFiles?.get(id).orEmpty()

    /** Можно ли открывать карту главы. */
    fun isChapterIndexReady(id: String): Boolean =
        indexFiles(id)?.all { fileFor(it) != null } == true

    /** Можно ли входить в уровень, не показывая загрузку. */
    fun isLevelReady(id: String): Boolean = levelFiles(id).all { fileFor(it) != null }

    /**
     * Уровень для онбординга и экрана загрузки. Его файлы входят в core, поэтому он на диске
     * с первого запуска — до того, как скачана хоть одна глава.
     */
    fun demoLevelId(): String? = manifest?.demo

    /** Главы, доступные этой сборке: манифест может нести контент, требующий более новой версии. */
    fun availableChapters(): List<ContentManifest.Chapter> =
        manifest?.chapters.orEmpty().filter { supports(it.minAppVersion) }

    /** Можно ли открыть уровень платной главы за ролик (флаг в манифесте, по умолчанию да). */
    fun rewardedEnabled(): Boolean = manifest?.ads?.rewarded ?: true
    /** Минимальная пауза между роликами, секунды (по умолчанию нет). */
    fun rewardedCooldown(): Int = manifest?.ads?.cooldownSec ?: 0

    fun isLevelDisabled(id: String): Boolean = manifest?.disabled?.contains(id) == true

    // ---- Синхронизация ----

    /** Обновить манифест и докачать core — после этого работают меню, список глав и локализация. */
    suspend fun syncCore(ctx: Context) = withContext(Dispatchers.IO) {
        ensureDirs(ctx)
        cancelPrefetch()     // манифест меняется под ногами, а в конце ещё и чистятся сироты
        phase = Phase.Syncing(0f)
        try {
            val fresh = fetchManifest(ctx)
            if (fresh == null) {
                phase = Phase.Ready      // контент не менялся — всё нужное уже на диске
                return@withContext
            }
            if (!supports(fresh.minAppVersion)) {
                // Контент новее приложения целиком — работаем на том, что уже скачано.
                phase = if (manifest == null) Phase.Failed("Требуется обновление приложения") else Phase.Ready
                return@withContext
            }
            // Что уже лежало на диске — считаем по ПРЕЖНЕМУ манифесту, пока он ещё актуален.
            // По новому это не определить: правка, задевшая файл, меняет его хеш, и он
            // выглядел бы никогда не скачанным.
            val installed = downloadedPaths(manifest)
            manifest = fresh
            download(fresh.core, fresh)
            // Догружаем изменившееся среди уже скачанного: иначе правка уровня выкинула бы его
            // с карты — файл сменил хеш, а в кеше лежит прежний. Обновляем ровно то, что было,
            // а не главу целиком: с поуровневой загрузкой глава почти всегда скачана частично.
            download(installed.filter { fresh.files.containsKey(it) }, fresh)
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

    /**
     * Гейт перед картой главы: одни описания уровней, десятки килобайт. Всё остальное едет
     * потом — обложки фоном на уже открытой карте, файлы уровня при входе в него.
     */
    suspend fun ensureChapterIndex(ctx: Context, id: String) = withContext(Dispatchers.IO) {
        ensureDirs(ctx)
        cancelPrefetch()
        val m = manifest
        val files = indexFiles(id)
        if (m == null || files == null) { phase = Phase.Failed("Глава $id не найдена в манифесте"); return@withContext }
        if (isChapterIndexReady(id)) { phase = Phase.Ready; return@withContext }
        phase = Phase.Syncing(0f)
        try {
            download(files, m)
            generation++
            phase = Phase.Ready
        } catch (e: Exception) {
            phase = Phase.Failed(e.message ?: "Не удалось скачать главу")
        }
    }

    /**
     * Гейт перед уровнем: его сцены, персонажи и музыка, ~1 МБ. Обычно к этому моменту всё уже
     * принесла фоновая докачка, и экран загрузки не показывается вовсе.
     */
    suspend fun ensureLevel(ctx: Context, id: String) = withContext(Dispatchers.IO) {
        ensureDirs(ctx)
        cancelPrefetch()
        val m = manifest
        if (m == null) { phase = Phase.Failed("Манифест не загружен"); return@withContext }
        if (isLevelReady(id)) { phase = Phase.Ready; return@withContext }
        phase = Phase.Syncing(0f)
        try {
            download(levelFiles(id), m)
            generation++
            Audio.reloadSfx(ctx)
            phase = Phase.Ready
        } catch (e: Exception) {
            phase = Phase.Failed(e.message ?: "Не удалось скачать эпизод")
        }
    }

    /**
     * Фоновая докачка главы, с которой игрок сейчас работает: сперва обложки карточек в порядке
     * прохождения, потом уровни целиком — начиная с того, куда игрок пойдёт дальше. Ничего не
     * блокирует и не трогает [phase]: экраны на нём завязаны, а фон не должен ими двигать.
     */
    fun prefetchChapter(ctx: Context, id: String, startingAt: String? = null) {
        ensureDirs(ctx)
        cancelPrefetch()
        val m = manifest ?: return
        val ids = m.chapters.firstOrNull { it.id == id }?.levels.orEmpty()
        val start = ids.indexOf(startingAt).coerceAtLeast(0)
        // От текущего эпизода вперёд, потом по кругу к началу: чем ближе уровень к игроку,
        // тем раньше он приезжает. Сам текущий идёт первым, до обложек, — по нему кликнут
        // с наибольшей вероятностью, и кликнут скорее, чем долистают карту.
        val order = ids.drop(start) + ids.take(start)
        val queue = order.take(1).flatMap { levelFiles(it) } + m.chapterCovers[id].orEmpty() +
            order.flatMap { levelFiles(it) }

        prefetch = scope.launch {
            for (path in queue) {
                if (!isActive) return@launch
                val ref = m.files[path] ?: continue
                if (File(objects, ref.h).exists()) continue
                runCatching { fetchObject(ref, path) }.onSuccess { generation++ }
            }
        }
    }

    fun cancelPrefetch() {
        prefetch?.cancel()
        prefetch = null
    }

    // ---- Внутреннее ----

    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private var prefetch: Job? = null

    /**
     * Логические пути, файлы которых лежат на диске. Считается до подмены манифеста — по
     * прежним хешам, потому что только они описывают то, что реально скачано.
     */
    private fun downloadedPaths(m: ContentManifest?): List<String> {
        if (m == null) return emptyList()
        return m.files.filterValues { File(objects, it.h).exists() }.keys.toList()
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
            fetchObject(ref, path)
            done += ref.s
            phase = Phase.Syncing(done.toFloat() / total)
        }
    }

    /** Скачать один объект и положить его в кеш под именем-хешем. */
    private fun fetchObject(ref: ContentManifest.FileRef, path: String) {
        val bytes = get("f/${ref.h}")
        val actual = MessageDigest.getInstance("SHA-256").digest(bytes)
            .joinToString("") { "%02x".format(it) }
        if (actual != ref.h) throw IllegalStateException("Файл повреждён при загрузке: $path")
        // Пишем во временный файл и переименовываем: оборванная закачка не оставит битый объект,
        // который потом будет считаться готовым. Имя уникальное — фоновая докачка и загрузка
        // уровня могут одновременно тянуть один объект, и общий `.part` они бы затёрли друг другу.
        val tmp = File(objects, "${ref.h}.${UUID.randomUUID()}.part")
        tmp.writeBytes(bytes)
        val dst = File(objects, ref.h)
        dst.delete()
        if (!tmp.renameTo(dst)) {
            tmp.delete()
            throw IllegalStateException("Не удалось сохранить $path")
        }
    }

    /**
     * Манифест, если он изменился. `null` — сервер ответил 304, на диске уже актуальный.
     *
     * Манифест — единственное, что запрашивается на КАЖДОМ запуске: сам контент лежит в кеше
     * по хешу и второй раз не качается. Но весит он ~100 КБ, поэтому спрашиваем условно,
     * по ETag — когда контент не менялся, ответ пустой, пара сотен байт заголовков.
     */
    private fun fetchManifest(ctx: Context): ContentManifest? {
        val prefs = ctx.getSharedPreferences("ht.sync", Context.MODE_PRIVATE)
        val conn = (URL("${baseUrl.trimEnd('/')}/manifest.json").openConnection() as HttpURLConnection).apply {
            connectTimeout = 15_000
            readTimeout = 30_000
            if (manifest != null) prefs.getString(ETAG, null)?.let { setRequestProperty("If-None-Match", it) }
        }
        try {
            if (conn.responseCode == 304) return null
            if (conn.responseCode !in 200..299) {
                throw IllegalStateException("Сервер контента ответил ${conn.responseCode}")
            }
            val body = conn.inputStream.use { it.readBytes() }
            val fresh = json.decodeFromString<ContentManifest>(String(body))
            // ETag запоминаем ПОСЛЕ разбора: на битом ответе он бы навсегда заглушил обновления.
            conn.getHeaderField("ETag")?.let { prefs.edit().putString(ETAG, it).apply() }
            return fresh
        } finally {
            conn.disconnect()
        }
    }

    private const val ETAG = "manifest.etag"

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
