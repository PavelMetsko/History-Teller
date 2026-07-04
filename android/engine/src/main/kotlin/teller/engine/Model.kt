package teller.engine

import kotlinx.serialization.json.*

/** Направленное отношение между акторами. */
data class Relation(val rel: String, val from: String, val to: String)

/** Состояние мира: флаги персонажей + направленные отношения. Мутируемый — как в оригинале. */
class World {
    private val flags = HashMap<String, MutableSet<String>>()
    private val relations = HashSet<Relation>()

    fun hasFlag(charId: String, flag: String): Boolean = flags[charId]?.contains(flag) == true
    fun setFlag(charId: String, flag: String) { flags.getOrPut(charId) { HashSet() }.add(flag) }
    fun removeFlag(charId: String, flag: String) { flags[charId]?.remove(flag) }
    fun hasRelation(rel: String, from: String, to: String) = relations.contains(Relation(rel, from, to))
    fun addRelation(rel: String, from: String, to: String) { relations.add(Relation(rel, from, to)) }
    fun removeRelation(rel: String, from: String, to: String) { relations.remove(Relation(rel, from, to)) }
    fun isAlive(charId: String) = !hasFlag(charId, DEAD_FLAG)

    /** Глубокая копия (для снапшотов после каждой панели). */
    fun clone(): World {
        val w = World()
        for ((k, v) in flags) w.flags[k] = HashSet(v)
        w.relations.addAll(relations)
        return w
    }

    companion object { const val DEAD_FLAG = "dead" }
}

// ---- Определения контента (чистые данные) ----

data class CharacterDef(val id: String, val name: String, val tags: List<String>)
data class SceneDef(val id: String, val name: String, val tags: List<String>, val slots: Int,
                    val action: String?, val roles: List<String>?)
data class RelationCondition(val rel: String, val to: String)
data class ActorDef(val variable: String, val slot: Int, val tags: List<String>, val flags: List<String>,
                    val notFlags: List<String>, val relations: List<RelationCondition>)
data class TriggerDef(val sceneTags: List<String>, val actors: List<ActorDef>)
data class EffectDef(val type: String, val target: String?, val flag: String?,
                     val rel: String?, val from: String?, val to: String?)
data class RuleDef(val id: String, val priority: Int, val trigger: TriggerDef, val effects: List<EffectDef>)
data class FactCard(val accuracy: String, val text: String, val source: String)
data class InitialStateDef(val flags: Map<String, List<String>>, val relations: List<List<String>>)

/** Заполнение одной панели игроком. */
data class Panel(val sceneId: String?, val characters: MutableList<String>)

data class LevelDef(
    val id: String, val order: Int, val title: String, val epoch: String, val panels: Int,
    val scenes: List<String>, val characters: List<String>,
    val initialState: InitialStateDef?, val initialText: String?, val goalText: String?, val goalHint: String?,
    val goal: GoalNode, val factCard: FactCard?, val solution: List<Panel>?,
    val music: String?, val cover: String?, val act: String?
) {
    /** Свежий мир со стартовыми условиями. Вызывать для каждой симуляции. */
    fun createInitialWorld(): World {
        val w = World()
        initialState?.let { st ->
            for ((cid, fs) in st.flags) for (f in fs) w.setFlag(cid, f)
            for (r in st.relations) if (r.size >= 3) w.addRelation(r[0], r[1], r[2])
        }
        return w
    }
}

/** Дерево условий цели: all / any / not / flag / relation. */
sealed class GoalNode {
    data class All(val children: List<GoalNode>) : GoalNode()
    data class Any(val children: List<GoalNode>) : GoalNode()
    data class Not(val child: GoalNode) : GoalNode()
    data class Flag(val char: String, val flag: String) : GoalNode()
    data class Rel(val rel: String, val from: String, val to: String) : GoalNode()

    fun isMet(w: World): Boolean = when (this) {
        is All -> children.all { it.isMet(w) }
        is Any -> children.any { it.isMet(w) }
        is Not -> !child.isMet(w)
        is Flag -> w.hasFlag(char, flag)
        is Rel -> w.hasRelation(rel, from, to)
    }

    companion object {
        fun parse(el: JsonElement): GoalNode {
            val o = el.jsonObject
            return when {
                "all" in o -> All(o["all"]!!.jsonArray.map { parse(it) })
                "any" in o -> Any(o["any"]!!.jsonArray.map { parse(it) })
                "not" in o -> Not(parse(o["not"]!!))
                "flag" in o -> o["flag"]!!.jsonObject.let {
                    Flag(it["char"]!!.jsonPrimitive.content, it["is"]!!.jsonPrimitive.content)
                }
                "relation" in o -> o["relation"]!!.jsonObject.let {
                    Rel(it["rel"]!!.jsonPrimitive.content, it["from"]!!.jsonPrimitive.content, it["to"]!!.jsonPrimitive.content)
                }
                else -> throw IllegalArgumentException("Unknown goal node: $o")
            }
        }
    }
}
