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

    private fun read(code: String): Map<String, String> = try {
        val txt = assets!!.open("i18n/$code.json").bufferedReader().use { it.readText() }
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
        fun read(p: String) = assets.open(p).bufferedReader().use { it.readText() }
        L10n.load(assets, langOverride)
        db = ContentDb.fromJson(read("content/characters.json"), read("content/scenes.json"), read("content/rules.json"))
        val files = assets.list("content/levels")?.filter { it.endsWith(".json") } ?: emptyList()
        val loaded = files.map { ContentDb.loadLevel(read("content/levels/$it")) }.filter { it.id != "rivals" }
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

        val actKeys = listOf("act.rome.1", "act.rome.2", "act.rome.3", "act.tudor.1", "act.tudor.2", "act.tudor.3",
            "act.revolution.1", "act.revolution.2", "act.revolution.3",
            "act.empire.1", "act.empire.2", "act.empire.3",
            "act.borgia.1", "act.borgia.2", "act.borgia.3",
            "act.byzantium.1", "act.byzantium.2", "act.byzantium.3")
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
