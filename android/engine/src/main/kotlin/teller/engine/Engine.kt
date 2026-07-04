package teller.engine

/**
 * Движок симуляции: прогоняет панели слева направо, применяя правила по убыванию приоритета.
 * Семантика 1:1 со Swift-движком (порт).
 */
object Engine {

    /** Результат прогона с трассой: финальный мир + снапшот после каждой панели (для UI-бейджей). */
    data class SimResult(val world: World, val snapshots: List<World>)

    /** Прогон со снапшотами (для доски). Солвер использует лёгкий [simulate] без трассы. */
    fun run(panels: List<Panel>, db: ContentDb, initial: World? = null): SimResult {
        val world = initial ?: World()
        val snaps = ArrayList<World>(panels.size)
        for (panel in panels) {
            val sceneId = panel.sceneId
            if (sceneId != null) {
                val sceneTags = db.scenes[sceneId]!!.tags
                for (rule in db.rulesByPriorityDesc) {
                    if (!rule.trigger.sceneTags.all { sceneTags.contains(it) }) continue
                    for (binding in findBindings(rule.trigger.actors, panel.characters, world, db)) {
                        val stillValid = rule.trigger.actors.all { a ->
                            world.isAlive(binding[a.variable]!!) && actorMatches(a, binding[a.variable]!!, binding, world, db)
                        }
                        if (stillValid) applyEffects(rule.effects, binding, world)
                    }
                }
            }
            snaps.add(world.clone())
        }
        return SimResult(world, snaps)
    }

    fun simulate(panels: List<Panel>, db: ContentDb, initial: World? = null): World {
        val world = initial ?: World()
        for (panel in panels) {
            val sceneId = panel.sceneId ?: continue
            val sceneTags = db.scenes[sceneId]!!.tags
            for (rule in db.rulesByPriorityDesc) {
                if (!rule.trigger.sceneTags.all { sceneTags.contains(it) }) continue
                for (binding in findBindings(rule.trigger.actors, panel.characters, world, db)) {
                    // Биндинг мог быть инвалидирован эффектом в этой же панели — перепроверяем.
                    val stillValid = rule.trigger.actors.all { a ->
                        world.isAlive(binding[a.variable]!!) &&
                            actorMatches(a, binding[a.variable]!!, binding, world, db)
                    }
                    if (!stillValid) continue
                    applyEffects(rule.effects, binding, world)
                }
            }
        }
        return world
    }

    fun actorMatches(actor: ActorDef, charId: String, binding: Map<String, String>,
                     world: World, db: ContentDb): Boolean {
        val def = db.characters[charId]!!
        if (!actor.tags.all { def.tags.contains(it) }) return false
        if (!actor.flags.all { world.hasFlag(charId, it) }) return false
        if (actor.notFlags.any { world.hasFlag(charId, it) }) return false
        for (rc in actor.relations) {
            val other = binding[rc.to] ?: return false
            if (!world.hasRelation(rc.rel, charId, other)) return false
        }
        return true
    }

    /** Назначения живых персонажей на переменные. slot ≥ 0 — жёсткая привязка к позиции. */
    fun findBindings(actors: List<ActorDef>, present: List<String>,
                     world: World, db: ContentDb): List<Map<String, String>> {
        val alive = present.filter { world.isAlive(it) }
        val result = ArrayList<Map<String, String>>()

        if (actors.any { it.slot >= 0 }) {
            val binding = HashMap<String, String>()
            val used = HashSet<String>()
            for (a in actors.filter { it.slot >= 0 }) {
                if (a.slot >= present.size) return result
                val c = present[a.slot]
                if (!world.isAlive(c) || !used.add(c)) return result
                binding[a.variable] = c
            }
            val rest = actors.filter { it.slot < 0 }
            val free = alive.filter { !used.contains(it) }
            for (perm in permutations(free, rest.size)) {
                val b = HashMap(binding)
                for (i in rest.indices) b[rest[i].variable] = perm[i]
                if (actors.all { actorMatches(it, b[it.variable]!!, b, world, db) }) result.add(b)
            }
            return result
        }

        for (perm in permutations(alive, actors.size)) {
            val binding = HashMap<String, String>()
            for (i in actors.indices) binding[actors[i].variable] = perm[i]
            if (actors.all { actorMatches(it, binding[it.variable]!!, binding, world, db) }) result.add(binding)
        }
        return result
    }

    fun applyEffects(effects: List<EffectDef>, binding: Map<String, String>, world: World) {
        for (e in effects) when (e.type) {
            "setFlag" -> world.setFlag(binding[e.target]!!, e.flag!!)
            "removeFlag" -> world.removeFlag(binding[e.target]!!, e.flag!!)
            "addRelation" -> world.addRelation(e.rel!!, binding[e.from]!!, binding[e.to]!!)
            "removeRelation" -> world.removeRelation(e.rel!!, binding[e.from]!!, binding[e.to]!!)
            else -> throw IllegalStateException("Unknown effect type: ${e.type}")
        }
    }

    /** Упорядоченные выборки длины k без повторений (порядок стабилен, как в Swift). */
    fun permutations(items: List<String>, k: Int): List<List<String>> {
        if (k == 0) return listOf(emptyList())
        if (k > items.size) return emptyList()
        val result = ArrayList<List<String>>()
        for (i in items.indices) {
            val rest = items.toMutableList().apply { removeAt(i) }
            for (tail in permutations(rest, k - 1)) result.add(listOf(items[i]) + tail)
        }
        return result
    }
}

/** Brute-force солвер: перебор всех расстановок (для контент-пайплайна и подсказок). */
object Solver {
    class Result {
        val solutions = ArrayList<List<Panel>>()
        var searchSpace = 0
        val isSolvable get() = solutions.isNotEmpty()
    }

    fun solve(level: LevelDef, db: ContentDb, maxSolutions: Int = Int.MAX_VALUE): Result {
        val options = panelOptions(level, db)
        val result = Result()
        result.searchSpace = pow(options.size, level.panels)
        if (options.isEmpty()) return result

        val n = level.panels
        val indices = IntArray(n)
        while (true) {
            val assignment = indices.map { options[it] }
            val world = Engine.simulate(assignment, db, level.createInitialWorld())
            if (level.goal.isMet(world)) {
                result.solutions.add(assignment)
                if (result.solutions.size >= maxSolutions) break
            }
            var pos = n - 1
            while (pos >= 0) {
                indices[pos]++
                if (indices[pos] == options.size) { indices[pos] = 0; pos-- } else break
            }
            if (pos < 0) break
        }
        return result
    }

    fun panelOptions(level: LevelDef, db: ContentDb): List<Panel> {
        val options = ArrayList<Panel>()
        for (sceneId in level.scenes) {
            val slots = db.scenes[sceneId]!!.slots
            val maxK = minOf(slots, level.characters.size)
            for (k in 0..maxK)
                for (perm in Engine.permutations(level.characters, k))
                    options.add(Panel(sceneId, perm.toMutableList()))
        }
        return options
    }

    private fun pow(base: Int, exp: Int): Int { var r = 1; repeat(exp) { r *= base }; return r }
}
