package teller.editor

import kotlinx.serialization.json.*
import teller.engine.*

/**
 * Мост между движком и редактором в браузере.
 *
 * Наружу отдаём JSON-строки, а не объекты: `@JsExport` не пропускает произвольные типы Kotlin,
 * а гонять руками ещё одну схему в обе стороны — лишний источник расхождений.
 */
@OptIn(ExperimentalJsExport::class)
@JsExport
object Engine {

    /**
     * Разбор уровня солвером — то же, что делает `gradle :engine:run` для всего контента.
     *
     * Возвращает:
     *   raw          сколько всего расстановок удовлетворяют цели
     *   distinct     сколько среди них принципиально разных (одинаковые с точностью до порядка — одна)
     *   solutionOk   решает ли эталонная расстановка из поля `solution` (null — поля нет)
     *   searchSpace  размер перебора; по нему видно, что уровень раздут
     *   solutions    первые несколько решений — показать автору, что именно проходит
     */
    fun analyze(
        charactersJson: String,
        scenesJson: String,
        rulesJson: String,
        levelJson: String,
    ): String = runCatching {
        val db = ContentDb.fromJson(charactersJson, scenesJson, rulesJson)
        val level = ContentDb.loadLevel(levelJson)
        val res = Solver.solve(level, db)

        val distinct = res.solutions.map(::signature).toSet()
        val solutionOk = level.solution?.let { sol ->
            val world = level.createInitialWorld()
            teller.engine.Engine.simulate(sol, db, world)
            level.goal.isMet(world)
        }

        buildJsonObject {
            put("ok", true)
            put("raw", res.solutions.size)
            put("distinct", distinct.size)
            put("searchSpace", res.searchSpace)
            put("solutionOk", solutionOk?.let { JsonPrimitive(it) } ?: JsonNull)
            putJsonArray("solutions") {
                for (sol in res.solutions.take(24)) {
                    addJsonArray {
                        for (panel in sol) addJsonObject {
                            put("scene", panel.sceneId ?: "")
                            putJsonArray("characters") { panel.characters.forEach { add(it) } }
                        }
                    }
                }
            }
        }.toString()
    }.getOrElse { e ->
        // Редактор всегда получает валидный JSON — половина правок в процессе заведомо сломана,
        // и падать на каждой букве нельзя.
        buildJsonObject {
            put("ok", false)
            put("error", e.message ?: e.toString())
        }.toString()
    }

    /** Все допустимые расстановки одной панели — для подсказок в редакторе. */
    fun panelOptions(
        charactersJson: String,
        scenesJson: String,
        rulesJson: String,
        levelJson: String,
    ): String = runCatching {
        val db = ContentDb.fromJson(charactersJson, scenesJson, rulesJson)
        val level = ContentDb.loadLevel(levelJson)
        buildJsonObject {
            put("ok", true)
            putJsonArray("options") {
                for (p in Solver.panelOptions(level, db)) addJsonObject {
                    put("scene", p.sceneId ?: "")
                    putJsonArray("characters") { p.characters.forEach { add(it) } }
                }
            }
        }.toString()
    }.getOrElse { e ->
        buildJsonObject { put("ok", false); put("error", e.message ?: e.toString()) }.toString()
    }

    /**
     * Прогон расстановки игрока, как на доске в игре (playable-реклама): порядок героев в кадрах
     * подбирается так, чтобы сработало больше правил (зеркало BoardModel.autoAssignSlots), затем
     * снапшот флагов после каждого кадра, сработавшие правила и выполнена ли цель.
     * `panelsJson` — [{"scene": "forum" | null, "characters": ["caesar", ...]}, ...].
     */
    fun run(
        charactersJson: String,
        scenesJson: String,
        rulesJson: String,
        levelJson: String,
        panelsJson: String,
    ): String = runCatching {
        val db = ContentDb.fromJson(charactersJson, scenesJson, rulesJson)
        val level = ContentDb.loadLevel(levelJson)
        val input = Json.parseToJsonElement(panelsJson).jsonArray.map { el ->
            val o = el.jsonObject
            Panel(o["scene"]?.jsonPrimitive?.contentOrNull?.ifEmpty { null },
                o["characters"]?.jsonArray?.map { it.jsonPrimitive.content }?.toMutableList() ?: mutableListOf())
        }
        val panels = autoAssign(input, level, db)
        val res = teller.engine.Engine.run(panels, db, level.createInitialWorld())
        buildJsonObject {
            put("ok", true)
            put("goalMet", level.goal.isMet(res.world))
            putJsonArray("panels") {
                panels.forEachIndexed { i, p -> addJsonObject {
                    put("scene", p.sceneId ?: "")
                    putJsonArray("characters") { p.characters.forEach { add(it) } }
                    putJsonObject("flags") {
                        for (c in level.characters) putJsonArray(c) { res.snapshots[i].flagsOf(c).sorted().forEach { add(it) } }
                    }
                } }
            }
            putJsonArray("events") {
                for (e in res.events) addJsonObject { put("panel", e.panelIndex); put("rule", e.ruleId) }
            }
        }.toString()
    }.getOrElse { e ->
        buildJsonObject { put("ok", false); put("error", e.message ?: e.toString()) }.toString()
    }
}

/** Порядок героев во всех кадрах, при котором срабатывает больше правил (≤ 6³ вариантов). */
private fun autoAssign(panels: List<Panel>, level: LevelDef, db: ContentDb): List<Panel> {
    val idxs = panels.indices.filter { panels[it].characters.size > 1 }
    if (idxs.isEmpty()) return panels
    val options = idxs.map { permutations(panels[it].characters) }
    var best = panels
    var bestScore = -1
    val pick = IntArray(idxs.size)
    while (true) {
        val trial = panels.toMutableList()
        idxs.forEachIndexed { k, i -> trial[i] = Panel(trial[i].sceneId, options[k][pick[k]].toMutableList()) }
        val score = teller.engine.Engine.run(trial, db, level.createInitialWorld()).events.size
        if (score > bestScore) { bestScore = score; best = trial }
        var carry = pick.size - 1
        while (carry >= 0) { pick[carry]++; if (pick[carry] < options[carry].size) break; pick[carry] = 0; carry-- }
        if (carry < 0) break
    }
    return best
}

private fun permutations(items: List<String>): List<List<String>> =
    if (items.size < 2) listOf(items)
    else items.flatMapIndexed { i, item -> permutations(items.filterIndexed { j, _ -> j != i }).map { listOf(item) + it } }

/** Расстановка с точностью до порядка внутри панели — так считается `distinct`. */
private fun signature(sol: List<Panel>): String =
    sol.joinToString("|") { "${it.sceneId ?: "-"}:${it.characters.sorted().joinToString(",")}" }
