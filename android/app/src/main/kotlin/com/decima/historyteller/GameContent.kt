package com.decima.historyteller

import android.content.res.AssetManager
import kotlinx.serialization.json.*
import teller.engine.*
import java.util.Locale

/** Локализация: каталог i18n/<lang>.json в assets. Порт iOS L10n. */
object L10n {
    val available = listOf("ru", "en", "es", "de", "fr", "it", "pt", "pl", "nl")
    private var base: Map<String, String> = emptyMap()
    private var table: Map<String, String> = emptyMap()
    var lang: String = "ru"; private set
    private var assets: AssetManager? = null

    fun load(assets: AssetManager, override: String?) {
        this.assets = assets
        base = read("ru")
        lang = resolve(override)
        table = if (lang == "ru") base else read(lang)
    }

    private fun resolve(override: String?): String {
        if (!override.isNullOrEmpty() && override in available) return override
        val dev = Locale.getDefault().language.lowercase()
        return if (dev in available) dev else "en"
    }

    fun s(key: String): String = table[key] ?: base[key] ?: key
    fun s(key: String, vararg args: Any): String = String.format(s(key), *args)
    fun opt(key: String): String? = table[key]
    fun ruBase(key: String): String? = base[key]

    /**
     * Все ключи базы с данным префиксом. Нужно, чтобы не держать списки ключей в коде:
     * новая глава приносит свои `act.<epoch>.N` вместе с каталогом и подхватывается сама.
     */
    fun keys(prefix: String): List<String> = base.keys.filter { it.startsWith(prefix) }.sorted()

    private fun read(code: String): Map<String, String> = try {
        // Скачанный каталог перекрывает вшитый — правки переводов приезжают без релиза.
        val txt = ContentSync.text("content/i18n/$code.json")
            ?: assets!!.open("i18n/$code.json").bufferedReader().use { it.readText() }
        // Каталоги общие с iOS: `%@` (ObjC) → `%s` для Java String.format.
        Json.parseToJsonElement(txt).jsonObject.mapValues { it.value.jsonPrimitive.content.replace("%@", "%s") }
    } catch (e: Exception) { emptyMap() }
}

/** Загрузка контента из assets + локализация на загрузке (порт RomeContent). */
object GameContent {
    lateinit var db: ContentDb
        private set
    var levels: List<LevelDef> = emptyList()
        private set

    fun load(assets: AssetManager, langOverride: String?) {
        // Скачанное перекрывает вшитое: в бандле лишь стартовый набор, актуальный контент — из облака.
        fun read(logical: String, bundled: String = logical) =
            ContentSync.text(logical) ?: assets.open(bundled).bufferedReader().use { it.readText() }

        L10n.load(assets, langOverride)
        db = ContentDb.fromJson(read("content/characters.json"), read("content/scenes.json"), read("content/rules.json"))

        // Состав уровней задаёт манифест — иначе добавленный в облаке уровень не появился бы,
        // а выключенный продолжал бы показываться. Без манифеста работаем на вшитом наборе.
        val ids = ContentSync.levelIds()
        val loaded = if (ids != null) {
            ids.mapNotNull { id -> runCatching { ContentDb.loadLevel(read("content/levels/$id.json")) }.getOrNull() }
        } else {
            val files = assets.list("content/levels")?.filter { it.endsWith(".json") } ?: emptyList()
            files.map { ContentDb.loadLevel(read("content/levels/$it")) }.filter { it.id != "rivals" }
        }
        levels = localize(loaded).sortedBy { it.order }
    }

    fun levels(epoch: String): List<LevelDef> = levels.filter { it.epoch == epoch }.sortedBy { it.order }
    fun level(id: String): LevelDef? = levels.firstOrNull { it.id == id }

    private fun localize(levels: List<LevelDef>): List<LevelDef> {
        if (L10n.lang == "ru") return levels
        val chN = db.characters.keys.mapNotNull { id -> L10n.opt("char.$id")?.let { id to it } }.toMap()
        val scN = db.scenes.keys.mapNotNull { id -> L10n.opt("scene.$id")?.let { id to it } }.toMap()
        val scA = db.scenes.keys.mapNotNull { id -> L10n.opt("scene.$id.action")?.let { id to it } }.toMap()
        db.localizeNames(chN, scN, scA)

        // Ключи актов берём из самого каталога — так глава, приехавшая из облака, приносит свои акты с собой.
        val actKeys = L10n.keys("act.")
        val actMap = actKeys.mapNotNull { k ->
            val ru = L10n.ruBase(k); val loc = L10n.opt(k); if (ru != null && loc != null) ru to loc else null
        }.toMap()

        return levels.map { lv ->
            lv.copy(
                title = L10n.opt("level.${lv.id}.title") ?: lv.title,
                goalText = L10n.opt("level.${lv.id}.goal") ?: lv.goalText,
                goalHint = L10n.opt("level.${lv.id}.hint") ?: lv.goalHint,
                initialText = L10n.opt("level.${lv.id}.intro") ?: lv.initialText,
                act = lv.act?.let { actMap[it] } ?: lv.act,
                factCard = lv.factCard?.let { fc ->
                    fc.copy(
                        text = L10n.opt("level.${lv.id}.fact") ?: fc.text,
                        source = L10n.opt("level.${lv.id}.source") ?: fc.source
                    )
                }
            )
        }
    }
}

/** Имя drawable-ресурса для сцены/персонажа (совпадает с iOS: scene_<id>, char_<id>). */
fun sceneDrawable(id: String) = "scene_$id"
fun charDrawable(id: String) = "char_$id"
