package teller.engine

import kotlinx.serialization.json.*

/** Загруженный контент: персонажи/сцены/правила по id. */
class ContentDb(
    val characters: MutableMap<String, CharacterDef>,
    val scenes: MutableMap<String, SceneDef>,
    val rulesByPriorityDesc: List<RuleDef>
) {
    /** Локализовать отображаемые имена/действия (перевод по id — на симуляцию не влияет). */
    fun localizeNames(characterNames: Map<String, String>, sceneNames: Map<String, String>,
                      sceneActions: Map<String, String>) {
        for ((id, name) in characterNames) characters[id]?.let { characters[id] = it.copy(name = name) }
        for ((id, name) in sceneNames) scenes[id]?.let { scenes[id] = it.copy(name = name) }
        for ((id, act) in sceneActions) scenes[id]?.let { scenes[id] = it.copy(action = act) }
    }

    companion object {
        private val json = Json { ignoreUnknownKeys = true }

        fun fromJson(charactersJson: String, scenesJson: String, rulesJson: String): ContentDb {
            val chars = json.parseToJsonElement(charactersJson).jsonArray.map { Parse.character(it.jsonObject) }
            val scenes = json.parseToJsonElement(scenesJson).jsonArray.map { Parse.scene(it.jsonObject) }
            val rules = json.parseToJsonElement(rulesJson).jsonArray.map { Parse.rule(it.jsonObject) }
            return ContentDb(
                chars.associateBy { it.id }.toMutableMap(),
                scenes.associateBy { it.id }.toMutableMap(),
                rules.sortedByDescending { it.priority }   // Kotlin sortedBy* стабилен, как в Swift
            )
        }

        fun loadLevel(levelJson: String): LevelDef =
            Parse.level(json.parseToJsonElement(levelJson).jsonObject)
    }
}

/** Ручной разбор JSON — 1:1 с кастомными Decodable-инитами Swift. */
object Parse {
    private fun JsonObject.str(k: String): String? = this[k]?.jsonPrimitive?.contentOrNull
    private fun JsonObject.strList(k: String): List<String> =
        this[k]?.jsonArray?.map { it.jsonPrimitive.content } ?: emptyList()
    private fun JsonObject.intOr(k: String, d: Int): Int = this[k]?.jsonPrimitive?.intOrNull ?: d

    fun character(o: JsonObject) = CharacterDef(o.str("id")!!, o.str("name") ?: "", o.strList("tags"))

    fun scene(o: JsonObject) = SceneDef(
        o.str("id")!!, o.str("name") ?: "", o.strList("tags"), o.intOr("slots", 2),
        o.str("action"), o["roles"]?.jsonArray?.map { it.jsonPrimitive.content })

    fun actor(o: JsonObject) = ActorDef(
        o.str("var")!!, o.intOr("slot", -1), o.strList("tags"), o.strList("flags"), o.strList("notFlags"),
        o["relations"]?.jsonArray?.map { val r = it.jsonObject; RelationCondition(r.str("rel")!!, r.str("to")!!) }
            ?: emptyList())

    fun trigger(o: JsonObject) = TriggerDef(
        o.strList("sceneTags"), o["actors"]?.jsonArray?.map { actor(it.jsonObject) } ?: emptyList())

    fun effect(o: JsonObject) = EffectDef(
        o.str("type")!!, o.str("target"), o.str("flag"), o.str("rel"), o.str("from"), o.str("to"))

    fun rule(o: JsonObject) = RuleDef(
        o.str("id")!!, o.intOr("priority", 0), trigger(o["trigger"]!!.jsonObject),
        o["effects"]?.jsonArray?.map { effect(it.jsonObject) } ?: emptyList())

    fun panel(o: JsonObject) = Panel(
        o.str("scene"), (o["characters"]?.jsonArray?.map { it.jsonPrimitive.content } ?: emptyList()).toMutableList())

    fun factCard(o: JsonObject) = FactCard(o.str("accuracy")!!, o.str("text") ?: "", o.str("source") ?: "")

    fun initialState(o: JsonObject) = InitialStateDef(
        o["flags"]?.jsonObject?.mapValues { it.value.jsonArray.map { v -> v.jsonPrimitive.content } } ?: emptyMap(),
        o["relations"]?.jsonArray?.map { it.jsonArray.map { v -> v.jsonPrimitive.content } } ?: emptyList())

    fun level(o: JsonObject) = LevelDef(
        o.str("id")!!, o.intOr("order", 0), o.str("title") ?: "", o.str("epoch")!!, o["panels"]!!.jsonPrimitive.int,
        o.strList("scenes"), o.strList("characters"),
        o["initialState"]?.let { initialState(it.jsonObject) },
        o.str("initialText"), o.str("goalText"), o.str("goalHint"),
        GoalNode.parse(o["goal"]!!), o["factCard"]?.let { factCard(it.jsonObject) },
        o["solution"]?.jsonArray?.map { panel(it.jsonObject) },
        o.str("music"), o.str("cover"), o.str("act"))
}
