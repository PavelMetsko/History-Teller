package teller.engine

import kotlinx.serialization.json.*
import java.io.File

/**
 * Прогон солвера по всему контенту. Запуск: `gradle :engine:run`.
 *
 * Состав глав берётся из `Content/chapters.json`, выключенные уровни — из `Content/disabled.json`:
 * те же файлы, по которым собирается облачный манифест. Раньше и список эпох, и исключение
 * `rivals` были вписаны сюда руками, и валидатор незаметно расходился с тем, что видит игрок.
 *
 * Колонки:
 *   raw       сколько всего расстановок удовлетворяют цели
 *   distinct  сколько среди них принципиально разных (порядок внутри панели не считается)
 *   ✓sol      эталонная расстановка из поля `solution` действительно решает уровень
 */
fun main() {
    val content = findContent()
    fun read(p: String) = File(content, p).readText()
    val db = ContentDb.fromJson(read("rome/characters.json"), read("rome/scenes.json"), read("rome/rules.json"))

    val chapters = Json.parseToJsonElement(read("chapters.json")).jsonArray
        .map { it.jsonObject["id"]!!.jsonPrimitive.content to it.jsonObject["number"]!!.jsonPrimitive.int }
    val disabled = File(content, "disabled.json").takeIf { it.exists() }
        ?.let { f -> Json.parseToJsonElement(f.readText()).jsonArray.map { it.jsonPrimitive.content } }
        ?.toSet() ?: emptySet()

    var bad = 0
    val rows = ArrayList<Pair<Int, String>>()
    for ((epoch, number) in chapters) {
        val files = File(content, "$epoch/levels").listFiles { f -> f.name.endsWith(".json") } ?: continue
        for (f in files) {
            val level = ContentDb.loadLevel(f.readText())
            if (level.id in disabled) continue
            val res = Solver.solve(level, db)
            val distinct = res.solutions.map { sol ->
                sol.joinToString("|") { "${it.sceneId ?: "-"}:${it.characters.sorted().joinToString(",")}" }
            }.toSet().size
            val solOk = level.solution?.let {
                val w = level.createInitialWorld(); Engine.simulate(it, db, w); level.goal.isMet(w)
            }
            val tag = when (solOk) { true -> "✓sol"; false -> "✗SOL!"; null -> "—" }
            if (solOk == false || !res.isSolvable) bad++
            rows.add(number * 1000 + level.order to
                "[$epoch] ord=${level.order}\t${level.id}\traw=${res.solutions.size}\tdistinct=$distinct\t$tag")
        }
    }

    println("=== солвер по всему контенту: ${chapters.size} глав, ${rows.size} уровней ===")
    if (disabled.isNotEmpty()) println("выключено (пропущено): ${disabled.joinToString(", ")}")
    rows.sortedBy { it.first }.forEach { println(it.second) }
    if (bad > 0) {
        // Ненулевой код возврата — чтобы CI падал, а не «зеленел» с поломанным контентом.
        println("\nПРОБЛЕМНЫХ УРОВНЕЙ: $bad (нерешаемые или с неверным эталоном)")
        kotlin.system.exitProcess(1)
    }
}

/** Ищем каталог Content/ вверх от текущей директории. */
private fun findContent(): File {
    var d: File? = File(".").absoluteFile
    while (d != null) {
        val c = File(d, "Content/rome/characters.json")
        if (c.exists()) return File(d, "Content")
        d = d.parentFile
    }
    error("Content/ не найден (запускай из репозитория)")
}
