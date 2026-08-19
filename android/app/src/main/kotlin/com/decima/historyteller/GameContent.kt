package com.decima.historyteller

import android.content.res.AssetManager
import kotlinx.serialization.json.*
import teller.engine.*
import java.util.Locale

/** Локализация: каталог i18n/<lang>.json в assets. Порт iOS L10n. */
object L10n {
    val available = listOf("ru", "en", "es", "de", "fr", "it", "pt", "pl", "nl")
    private var base: Map<String, String> = emptyMap()
    /** Английский слой между выбранным языком и русской базой: непереведённый ключ читается
     *  по-английски, а не кириллицей (каталог перевода может отставать от контента). */
    private var fallback: Map<String, String> = emptyMap()
    private var table: Map<String, String> = emptyMap()
    var lang: String = "ru"; private set
    private var assets: AssetManager? = null

    fun load(assets: AssetManager, override: String?) {
        this.assets = assets
        base = read("ru")
        lang = resolve(override)
        table = if (lang == "ru") base else read(lang)
        fallback = if (lang == "en" || lang == "ru") emptyMap() else read("en")
    }

    private fun resolve(override: String?): String {
        if (!override.isNullOrEmpty() && override in available) return override
        val dev = Locale.getDefault().language.lowercase()
        return if (dev in available) dev else "en"
    }

    /**
     * Строки, которые нужны ДО того, как каталог скачан (первый запуск), И новые UI-ключи,
     * добавленные вместе с кодом: облачный каталог публикуется отдельно, и до публикации такой
     * ключ показывался игроку голым. Правило: добавил ключ в код — продублируй его здесь.
     */
    private val builtin: Map<String, Map<String, String>> = mapOf(
        "ui.terms" to mapOf(
            "ru" to "Условия использования",
            "en" to "Terms of Use",
            "es" to "Términos de uso",
            "de" to "Nutzungsbedingungen",
            "fr" to "Conditions d'utilisation",
            "it" to "Termini d'uso",
            "pt" to "Termos de uso",
            "pl" to "Warunki korzystania",
            "nl" to "Gebruiksvoorwaarden",
        ),
        "ui.privacy" to mapOf(
            "ru" to "Политика конфиденциальности",
            "en" to "Privacy Policy",
            "es" to "Política de privacidad",
            "de" to "Datenschutzerklärung",
            "fr" to "Politique de confidentialité",
            "it" to "Informativa sulla privacy",
            "pt" to "Política de Privacidade",
            "pl" to "Polityka prywatności",
            "nl" to "Privacybeleid",
        ),
        "ui.swap_hint" to mapOf(
            "ru" to "Зажми кадр и перетащи на другой — кадры можно менять местами",
            "en" to "Press and hold a panel, then drag it onto another — panels swap places",
            "es" to "Mantén pulsado un panel y arrástralo sobre otro: los paneles se intercambian",
            "de" to "Halte ein Panel gedrückt und zieh es auf ein anderes – Panels tauschen die Plätze",
            "fr" to "Maintiens un cadre appuyé et fais-le glisser sur un autre — les cadres s'échangent",
            "it" to "Tieni premuto un riquadro e trascinalo su un altro: i riquadri si scambiano",
            "pt" to "Segure um quadro e arraste-o sobre outro — os quadros trocam de lugar",
            "pl" to "Przytrzymaj kadr i przeciągnij go na inny — kadry zamienią się miejscami",
            "nl" to "Houd een kader ingedrukt en sleep het op een ander — kaders wisselen van plaats",
        ),
        "ui.wrong_unused" to mapOf(
            "ru" to "Такой сцены в этой истории нет",
            "en" to "This scene isn't part of the story",
            "es" to "Esta escena no forma parte de la historia",
            "de" to "Diese Szene gehört nicht zur Geschichte",
            "fr" to "Cette scène ne fait pas partie de l'histoire",
            "it" to "Questa scena non fa parte della storia",
            "pt" to "Esta cena não faz parte da história",
            "pl" to "Tej sceny nie ma w tej historii",
            "nl" to "Deze scène hoort niet bij het verhaal",
        ),
        "ui.downloading_content" to mapOf(
            "ru" to "Загрузка контента…", "en" to "Downloading content…", "es" to "Descargando contenido…",
            "de" to "Inhalte werden geladen…", "fr" to "Téléchargement du contenu…",
            "it" to "Download dei contenuti…", "pt" to "Baixando conteúdo…",
            "pl" to "Pobieranie zawartości…", "nl" to "Inhoud downloaden…",
        ),
        "ui.load_fail" to mapOf(
            "ru" to "Не удалось загрузить контент", "en" to "Failed to load content",
            "es" to "No se pudo cargar el contenido", "de" to "Inhalte konnten nicht geladen werden",
            "fr" to "Échec du chargement du contenu", "it" to "Impossibile caricare i contenuti",
            "pt" to "Falha ao carregar o conteúdo", "pl" to "Nie udało się pobrać zawartości",
            "nl" to "Laden van inhoud mislukt",
        ),
        "ui.retry" to mapOf(
            "ru" to "Повторить", "en" to "Retry", "es" to "Reintentar", "de" to "Erneut versuchen",
            "fr" to "Réessayer", "it" to "Riprova", "pt" to "Tentar novamente",
            "pl" to "Ponów", "nl" to "Opnieuw",
        ),
    )

    fun s(key: String): String =
        table[key] ?: fallback[key] ?: base[key] ?: builtin[key]?.get(lang) ?: builtin[key]?.get("en") ?: key
    fun s(key: String, vararg args: Any): String = String.format(s(key), *args)
    /** Тот же английский слой, что и в s(): непереведённый уровень читается по-английски. */
    fun opt(key: String): String? = table[key] ?: fallback[key]
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

    /**
     * Накладывает тексты из каталога. Тексты уровней вынесены из их JSON целиком, поэтому
     * накладывать надо всегда — включая русский, иначе уровень останется без названия и цели.
     */
    private fun localize(levels: List<LevelDef>): List<LevelDef> {
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
