package teller.engine

import java.io.File

/** Прогон солвера по всем уровням (валидация Kotlin-порта против Swift). Запуск: gradle :engine:run */
fun main() {
    val content = findContent()
    fun read(p: String) = File(content, p).readText()
    val db = ContentDb.fromJson(read("rome/characters.json"), read("rome/scenes.json"), read("rome/rules.json"))

    val dirs = listOf(File(content, "rome/levels"), File(content, "tudor/levels"), File(content, "revolution/levels"), File(content, "empire/levels"), File(content, "borgia/levels"), File(content, "byzantium/levels"))
    val rows = ArrayList<Pair<Int, String>>()
    for (dir in dirs) {
        val files = dir.listFiles { f -> f.name.endsWith(".json") } ?: continue
        for (f in files) {
            val level = ContentDb.loadLevel(f.readText())
            if (level.id == "rivals") continue
            val res = Solver.solve(level, db)
            val distinct = res.solutions.map { sol ->
                sol.joinToString("|") { "${it.sceneId ?: "-"}:${it.characters.sorted().joinToString(",")}" }
            }.toSet().size
            // валидация solution-поля
            val solOk = level.solution?.let {
                val w = level.createInitialWorld(); Engine.simulate(it, db, w); level.goal.isMet(w)
            }
            val tag = when (solOk) { true -> "✓sol"; false -> "✗SOL!"; null -> "—" }
            val key = level.order + when (level.epoch) { "tudor" -> 1000; "revolution" -> 2000; "empire" -> 3000; else -> 0 }
            rows.add(key to "[${level.epoch}] ord=${level.order}\t${level.id}\traw=${res.solutions.size}\tdistinct=$distinct\t$tag")
        }
    }
    println("=== Kotlin-движок: солвер по всем уровням ===")
    rows.sortedBy { it.first }.forEach { println(it.second) }
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
