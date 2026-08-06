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
}

/** Расстановка с точностью до порядка внутри панели — так считается `distinct`. */
private fun signature(sol: List<Panel>): String =
    sol.joinToString("|") { "${it.sceneId ?: "-"}:${it.characters.sorted().joinToString(",")}" }
