package com.decima.historyteller

import androidx.compose.ui.platform.LocalDensity
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.spring
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.ui.draw.scale
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.ui.draw.alpha
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.KeyboardArrowLeft
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ColorFilter
import androidx.compose.ui.graphics.ColorMatrix
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.zIndex
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.gestures.detectDragGesturesAfterLongPress
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Rect
import androidx.compose.ui.layout.onGloballyPositioned
import androidx.compose.ui.layout.LayoutCoordinates
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.unit.IntOffset
import kotlin.math.roundToInt
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import teller.engine.*
import kotlin.math.PI
import kotlin.math.cos
import kotlin.math.max
import kotlin.math.min
import kotlin.math.roundToInt
import kotlin.math.sin
import kotlin.random.Random

// ---- Модель состояния доски (порт LevelBoardModel) ----
class BoardModel(val level: LevelDef, val db: ContentDb) {
    sealed class Sel { data class Scene(val id: String) : Sel(); data class Char(val id: String) : Sel() }

    var panels by mutableStateOf(List(max(1, level.panels)) { Panel(null, mutableListOf()) })
        private set
    var selected by mutableStateOf<Sel?>(null)
    var result by mutableStateOf(Engine.run(List(max(1, level.panels)) { Panel(null, mutableListOf()) }, db, level.createInitialWorld()))
        private set

    /** Колбэк звука (устанавливает BoardScreen → Audio.sfx). */
    var onSfx: ((String) -> Unit)? = null

    /** Семантические «биты» последнего действия (кого убили + кто убийца, кого короновали, …).
     *  Выводятся из эффектов правила, поэтому работают для любой эпохи. Зеркало iOS. */
    var lastBeats by mutableStateOf<List<Beat>>(emptyList())
        private set
    /** Бампается на каждый пересчёт — доска подписывается, чтобы проигрывать «сок». */
    var changeToken by mutableStateOf(0)
        private set
    private var seenEventKeys: Set<String> = emptySet()
    private val ruleById: Map<String, RuleDef> = db.rulesByPriorityDesc.associateBy { it.id }
    init { seenEventKeys = result.events.map(::eventKey).toSet() }

    val world get() = result.world
    val isSolved get() = level.goal.isMet(world)
    val roster get() = level.characters
    val isBoardComplete
        get() = panels.all { p -> p.sceneId != null && db.scenes[p.sceneId]?.let { p.characters.size == it.slots } == true }

    /**
     * Текущий шаг гида: первый невыполненный. Шаги закрываются состоянием доски, а не
     * нажатиями — пролистать гид, не сделав ход, нельзя.
     *
     * На решённом уровне гид молчит: без этой проверки он оживал на финальном ходу там, где
     * правило снимает флаг (в сабинянках `intercede` убирает `at_arms`), и условие шага
     * снова становилось невыполненным. Порт iOS `LevelBoardModel.coachStep`.
     */
    val coachStep: CoachStep?
        get() {
            if (isSolved) return null
            return level.coach.firstOrNull { st ->
                val until = st.until
                when {
                    st.untilScene != null -> panels.none { it.sceneId == st.untilScene }
                    until != null -> !until.isMet(world)
                    else -> true
                }
            }
        }

    /** Что подсветить в нижнем ряду. Уже поставленное не подсвечиваем: шаг гида закрывается
     *  позже, по срабатыванию правила, а кольцо должно показывать, что взять следующим. */
    val coachHighlightScenes: Set<String>
        get() = coachStep?.highlightScenes.orEmpty()
            .filter { sid -> panels.none { it.sceneId == sid } }.toSet()
    val coachHighlightChars: Set<String>
        get() = coachStep?.highlightChars.orEmpty()
            .filter { cid -> panels.none { cid in it.characters } }.toSet()

    fun snapshot(i: Int): World = result.snapshots.getOrElse(i) { world }
    fun slots(i: Int): Int = panels[i].sceneId?.let { db.scenes[it]?.slots } ?: 0
    fun sceneName(id: String) = db.scenes[id]?.name ?: id
    fun charName(id: String) = db.characters[id]?.name ?: id
    fun sceneAction(id: String) = db.scenes[id]?.action

    private fun eventKey(e: Engine.RuleEvent): String {
        val b = e.binding.entries.sortedBy { it.key }.joinToString(",") { "${it.key}=${it.value}" }
        return "${e.panelIndex}|${e.ruleId}|$b"
    }

    /** Что «читаемо» произошло в правиле — для анимации-взаимодействия.
     *  primary — тот, «над кем» действие (жертва/осуждённый/проигравший/коронованный),
     *  secondary — активный (убийца/обвинитель/победитель/второй влюблённый). */
    data class Beat(val panelIndex: Int, val kind: Kind, val primary: String?, val secondary: String?, val symbol: String)
    enum class Kind { KILL, BATTLE, CONDEMN, CONQUER, MARCH, CROWN, LOVE, ALLY, TRIUMPH, DOWNFALL, CONSPIRE, BIRTH, SPARK }

    /** Смысл выводим из эффектов правила (не из id), поэтому одна логика покрывает все эпохи. */
    private fun beat(e: Engine.RuleEvent): Beat {
        val effs = ruleById[e.ruleId]?.effects ?: emptyList()
        val b = e.binding
        fun flagTarget(flags: Set<String>): String? =
            effs.firstOrNull { it.type == "setFlag" && it.flag in flags }?.target
        fun relationPair(rels: Set<String>): Pair<String, String>? =
            effs.firstOrNull { it.type == "addRelation" && it.rel in rels }?.let { it.from!! to it.to!! }
        fun other(v: String?): String? {
            val target = v?.let { b[it] }
            return b.entries.firstOrNull { it.key != v && it.value != target }?.value
        }
        fun mk(kind: Kind, p: String?, s: String?, sym: String) = Beat(e.panelIndex, kind, p, s, sym)

        flagTarget(setOf("dead"))?.let { return mk(Kind.KILL, b[it], other(it), "☠️") }
        flagTarget(setOf("fugitive", "defeated"))?.let { return mk(Kind.BATTLE, b[it], other(it), "⚔️") }
        flagTarget(setOf("condemned", "accused"))?.let { return mk(Kind.CONDEMN, b[it], other(it), "⚖️") }
        flagTarget(setOf("at_war"))?.let { return mk(Kind.BATTLE, b[it], other(it), "⚔️") }
        flagTarget(setOf("conqueror"))?.let { return mk(Kind.CONQUER, b[it], null, "⚔️") }
        flagTarget(setOf("crowned", "emperor", "empress", "reigns", "supreme_head", "first_consul"))
            ?.let { return mk(Kind.CROWN, b[it], null, "👑") }
        relationPair(setOf("loves"))?.let { (f, t) -> return mk(Kind.LOVE, b[f], b[t], "❤️") }
        relationPair(setOf("wed"))?.let { (f, t) -> return mk(Kind.LOVE, b[f], b[t], "💍") }
        relationPair(setOf("ally_of"))?.let { (f, t) -> return mk(Kind.ALLY, b[f], b[t], "🤝") }
        flagTarget(setOf("backed"))?.let { return mk(Kind.ALLY, b[it], other(it), "🛡") }
        flagTarget(setOf("honored", "beloved", "flaunting", "triumphant", "rome_restored", "settled", "hero", "absolute", "supreme"))
            ?.let { return mk(Kind.TRIUMPH, b[it], null, "🎉") }
        flagTarget(setOf("exiled", "cast_off", "widowed", "grieving"))?.let { return mk(Kind.DOWNFALL, b[it], null, "💔") }
        flagTarget(setOf("plotting"))?.let { return mk(Kind.CONSPIRE, b[it], null, "🗡") }
        flagTarget(setOf("has_heir"))?.let { return mk(Kind.BIRTH, null, null, "👶") }
        // Прочие «глаголы» грамматики — у каждого свой значок, чтобы кадр никогда не молчал.
        flagTarget(setOf("bought"))?.let { return mk(Kind.ALLY, b[it], other(it), "💰") }
        flagTarget(setOf("conceded"))?.let { return mk(Kind.ALLY, b[it], other(it), "🤝") }
        flagTarget(setOf("starved"))?.let { return mk(Kind.DOWNFALL, b[it], other(it), "🍞") }
        flagTarget(setOf("away"))?.let { return mk(Kind.SPARK, b[it], null, "🏃") }
        flagTarget(setOf("strong"))?.let { return mk(Kind.SPARK, b[it], null, "💪") }
        flagTarget(setOf("rallied"))?.let { return mk(Kind.SPARK, b[it], null, "🚩") }
        flagTarget(setOf("standing"))?.let { return mk(Kind.SPARK, b[it], null, "⭐️") }
        return mk(Kind.SPARK, null, null, "✨")
    }

    private fun sfxFor(b: Beat): String = when (b.kind) {
        Kind.KILL -> "kill"
        Kind.BATTLE, Kind.CONQUER -> "clash"
        Kind.CONDEMN -> "gavel"
        Kind.CONSPIRE -> "conspire"
        Kind.CROWN, Kind.TRIUMPH, Kind.BIRTH -> "crown"
        Kind.MARCH -> "drum"
        Kind.LOVE -> "love"
        Kind.ALLY -> if (b.symbol == "💰") "coin" else "ally"
        Kind.DOWNFALL -> "error"
        Kind.SPARK -> when (b.symbol) { "💪", "🚩" -> "drum"; "🏃" -> "flee"; else -> "select" }
    }

    private fun recompute() {
        autoAssignSlots()   // до симуляции: порядок внутри панели подбираем за игрока
        result = Engine.run(panels, db, level.createInitialWorld())
        autoArrange()   // «пострадавший» бита — правее активного (косметика, только сцены без ролей)
        val fresh = result.events.filter { eventKey(it) !in seenEventKeys }
        lastBeats = fresh.map(::beat)
        seenEventKeys = result.events.map(::eventKey).toSet()
        lastBeats.map { sfxFor(it) }.distinct().forEach { onSfx?.invoke(it) }
        panelSymbols = computePanelSymbols()
        val diag = computeDiagnoses()
        if (diag.indices.any { i -> diag[i] != Diag.OK && (i >= lastDiag.size || lastDiag[i] == Diag.OK) }) wrongToken++
        lastDiag = diag
        changeToken++
    }
    private fun update(i: Int, transform: (Panel) -> Panel) {
        panels = panels.toMutableList().also { it[i] = transform(it[i]) }; recompute()
    }

    /**
     * Подобрать порядок персонажей внутри панели за игрока.
     *
     * Правила со `slot` привязывают актора к позиции в кадре (сцена с `roles`: слот 0 — убийца,
     * слот 1 — жертва), и движок это учитывает. Но пазл — в том, КОГО и в КАКУЮ сцену поставить,
     * а не в угадывании слота, поэтому если из тех же персонажей есть перестановка, при которой
     * в панели срабатывает больше правил, применяем её молча. Порт iOS `autoAssignSlots`.
     */
    /** Совместный перебор порядков во всех кадрах (≤ 6³): подкуп срабатывает в обе стороны и
     *  порядки внутри кадра равны по счёту, а от направления зависит всё дальше. При равном
     *  счёте сохраняем расстановку игрока. (Зеркало iOS autoAssignSlots.) */
    private fun autoAssignSlots() {
        val idxs = panels.indices.filter { panels[it].characters.size > 1 }
        if (idxs.isEmpty()) return
        val options = idxs.map { permutations(panels[it].characters.toList()) }
        var best = panels.map { it.characters.toList() }
        var bestScore = -1
        val pick = IntArray(idxs.size)
        while (true) {
            val trial = panels.toMutableList()
            idxs.forEachIndexed { k, i -> trial[i] = Panel(trial[i].sceneId, options[k][pick[k]].toMutableList()) }
            val sc = Engine.run(trial, db, level.createInitialWorld()).events.size
            if (sc > bestScore) { bestScore = sc; best = trial.map { it.characters.toList() } }
            var carry = pick.size - 1
            while (carry >= 0) { pick[carry]++; if (pick[carry] < options[carry].size) break; pick[carry] = 0; carry-- }
            if (carry < 0) break
        }
        panels = panels.mapIndexed { i, p -> Panel(p.sceneId, best[i].toMutableList()) }
    }
    private fun permutations(items: List<String>): List<List<String>> =
        if (items.size < 2) listOf(items)
        else items.flatMapIndexed { i, item ->
            permutations(items.filterIndexed { j, _ -> j != i }).map { listOf(item) + it }
        }

    /** Внутри панели ставим «пострадавшего» (primary бита) правее — косметика, единая
     *  грамматика «жертва справа». На сценах с ролями порядок значим и уже подобран
     *  в [autoAssignSlots], поэтому их не трогаем. */
    private fun autoArrange() {
        val prim = Array(panels.size) { mutableSetOf<String>() }
        for (e in result.events) if (e.panelIndex < panels.size) beat(e).primary?.let { prim[e.panelIndex].add(it) }
        var changed = false
        val np = panels.toMutableList()
        for (i in panels.indices) {
            val p = prim[i]; if (p.isEmpty()) continue
            if (np[i].sceneId?.let { db.scenes[it]?.roles?.isNotEmpty() } == true) continue
            val chars = np[i].characters
            val re = (chars.filter { it !in p } + chars.filter { it in p })
            if (re != chars) { np[i] = Panel(np[i].sceneId, re.toMutableList()); changed = true }
        }
        if (changed) panels = np
    }

    /** Drag-reorder сцен: вынуть панель из from и вставить на to. Порядок панелей значим — пересчёт. */
    fun movePanel(from: Int, to: Int) {
        if (from == to || from !in panels.indices || to !in panels.indices) return
        val np = panels.toMutableList(); val p = np.removeAt(from); np.add(to, p)
        panels = np; selected = null; recompute()
    }

    fun setScene(i: Int, sceneId: String?) {
        onSfx?.invoke(if (sceneId == null) "remove" else "select")
        update(i) { p ->
            val chars = if (sceneId == null) mutableListOf()
            else p.characters.take(db.scenes[sceneId]?.slots ?: 0).toMutableList()
            Panel(sceneId, chars)
        }
    }
    fun place(i: Int, charId: String) {
        val p = panels[i]
        if (p.sceneId == null || p.characters.size >= slots(i) || charId in p.characters) return
        onSfx?.invoke("place")
        update(i) { Panel(it.sceneId, (it.characters + charId).toMutableList()) }
    }
    fun removeChar(i: Int, charId: String) {
        onSfx?.invoke("remove")
        update(i) { Panel(it.sceneId, it.characters.filter { c -> c != charId }.toMutableList()) }
    }
    fun reset() {
        onSfx?.invoke("remove")
        panels = List(max(1, level.panels)) { Panel(null, mutableListOf()) }
        selected = null; recompute()
    }
    fun selectItem(s: Sel) { selected = if (selected == s) null else s }
    fun clearSelection() { selected = null }
    fun applySelection(i: Int) {
        when (val s = selected) {
            is Sel.Scene -> setScene(i, s.id)
            is Sel.Char -> place(i, s.id)
            null -> {}
        }
        selected = null
    }

    enum class Diag { OK, WRONG_SCENE, WRONG_CHARS, INERT, WRONG_ORDER, WRONG_SLOTS, SCENE_UNUSED }
    fun diagnose(i: Int): Diag = computeDiagnoses().getOrElse(i) { Diag.OK }

    /** Диагноз ВСЕХ панелей разом и БЕЗ привязки к позиции: панель сверяется с эталоном как с
     *  мультимножеством (та же сцена + тот же состав → OK, где бы она ни стояла). Не «краснеем» на
     *  панели, которая сама по себе верна: та сцена/не те лица → WRONG_CHARS; те лица/не та сцена →
     *  WRONG_SCENE; мимо → INERT. Если ВСЕ панели совпали, но доска не решена — беда лишь в порядке
     *  → WRONG_ORDER. (Зеркало iOS LevelBoardModel.computeDiagnoses.) */
    private fun computeDiagnoses(): List<Diag> {
        val n = panels.size
        if (isSolved) return List(n) { Diag.OK }
        val solution = level.solution ?: return List(n) { Diag.OK }
        val remaining = solution.map { it.sceneId to it.characters.toSet() }.toMutableList()

        fun filled(i: Int): Pair<String, Set<String>>? {
            val p = panels[i]; val sid = p.sceneId ?: return null
            val sc = db.scenes[sid] ?: return null
            if (p.characters.size != sc.slots) return null
            return sid to p.characters.toSet()
        }

        val diag = MutableList(n) { Diag.OK }
        val pending = mutableListOf<Int>()
        // Проход 1: точные совпадения (сцена + состав) → OK, вычёркиваем из остатка эталона.
        for (i in 0 until n) {
            val f = filled(i) ?: continue
            val m = remaining.indexOfFirst { it.first == f.first && it.second == f.second }
            if (m >= 0) remaining.removeAt(m) else pending.add(i)
        }
        // Валидация мгновенная: заполненные панели судим сразу (проход 2), а порядок кадров — только
        // по полной доске. Все панели совпали по содержимому, но доска не решена → дело в порядке.
        if (isBoardComplete && pending.isEmpty()) {
            // Те же люди, но не по ролям в кадре (подкуп в обратную сторону) — отдельный вердикт,
            // иначе игрок читает «не в том порядке» как порядок кадров и зря двигает кадры.
            val refPanels = solution.mapNotNull { p -> p.sceneId?.let { it to p.characters } }
            for (i in 0 until n) {
                filled(i) ?: continue
                val exact = refPanels.any { it.first == panels[i].sceneId && it.second == panels[i].characters }
                diag[i] = if (exact) Diag.WRONG_ORDER else Diag.WRONG_SLOTS
            }
            return diag
        }
        // Проход 2: неточные — по остатку. Та же сцена → не те лица; тот же состав → не то место; иначе мимо.
        for (i in pending) {
            val f = filled(i)!!
            val ms = remaining.indexOfFirst { it.first == f.first }
            val mc = remaining.indexOfFirst { it.second == f.second }
            when {
                ms >= 0 -> { diag[i] = Diag.WRONG_CHARS; remaining.removeAt(ms) }
                mc >= 0 -> { diag[i] = Diag.WRONG_SCENE; remaining.removeAt(mc) }
                else -> diag[i] = Diag.INERT
            }
        }
        // Доска не собрана, но все сцены уже стоят: сцена, которой в остатке решения нет, —
        // не та сцена, ещё до расстановки людей.
        if (!isBoardComplete && panels.all { it.sceneId != null }) {
            // Порядок кадров без людей не судим: пока роли пусты, «не тот порядок» недоказуем —
            // ранняя проверка этого давала ложную ошибку на верно выставленных сценах.
            val restScenes = remaining.map { it.first }.toMutableList()
            for (i in 0 until n) {
                if (filled(i) != null) continue
                val sid = panels[i].sceneId ?: continue
                val m = restScenes.indexOf(sid)
                if (m >= 0) restScenes.removeAt(m) else diag[i] = Diag.SCENE_UNUSED
            }
        }
        return diag
    }


    /** Бампается, когда у какой-то панели ПОЯВИЛСЯ диагноз-ошибка (экран играет звук/тряску). */
    var wrongToken by mutableStateOf(0)
        private set
    private var lastDiag: List<Diag> = emptyList()

    /** Постоянный символ «что происходит в кадре» — по самому сильному сработавшему правилу панели. */
    var panelSymbols by mutableStateOf<List<String?>>(emptyList())
        private set
    private fun computePanelSymbols(): List<String?> {
        fun rank(k: Kind) = when (k) {
            Kind.KILL -> 12; Kind.BATTLE -> 11; Kind.CONQUER -> 10; Kind.CROWN -> 9; Kind.CONDEMN -> 8
            Kind.LOVE -> 7; Kind.DOWNFALL -> 6; Kind.CONSPIRE -> 5; Kind.ALLY -> 4; Kind.TRIUMPH -> 3
            Kind.BIRTH -> 2; Kind.MARCH -> 1; Kind.SPARK -> 0
        }
        val out = MutableList<String?>(panels.size) { null }
        val best = MutableList(panels.size) { -1 }
        for (e in result.events) {
            if (e.panelIndex >= panels.size) continue
            val b = beat(e); if (b.symbol.isEmpty()) continue
            val r = rank(b.kind)
            if (r > best[e.panelIndex]) { best[e.panelIndex] = r; out[e.panelIndex] = b.symbol }
        }
        return out
    }
    fun microState(charId: String, i: Int): String? {
        val snap = snapshot(i)
        if (snap.hasFlag(charId, "crowned")) return "👑"
        if (panels[i].characters.any { it != charId && snap.hasRelation("loves", charId, it) }) return "💕"
        if (snap.hasFlag(charId, "plotting")) return "🗡"
        return null
    }
}

private val grayscale = ColorFilter.colorMatrix(ColorMatrix().apply { setToSaturation(0f) })

/** Состояние drag-and-drop: тянем токен из лотка → бросаем на панель под пальцем (порт iOS dragGesture). */
private class DragState {
    var item by mutableStateOf<BoardModel.Sel?>(null)
    var pos by mutableStateOf(Offset.Zero)       // палец в координатах корневого Box
    var ghost by mutableStateOf<String?>(null)   // имя арта для плавающего превью
    var isChar by mutableStateOf(false)
    var root: LayoutCoordinates? = null
    val panelRects = mutableStateMapOf<Int, Rect>()
    var hover by mutableStateOf(-1)
    fun panelAt(p: Offset): Int? = panelRects.entries.firstOrNull { it.value.contains(p) }?.key
}

/** Драг токена из лотка: тянем палец и бросаем на панель под ним. origin — позиция токена в корне. */
@Composable
private fun Modifier.tokenDrag(drag: DragState, item: BoardModel.Sel, art: String, isChar: Boolean, model: BoardModel): Modifier {
    var coords by remember { mutableStateOf<LayoutCoordinates?>(null) }
    return this
        .onGloballyPositioned { coords = it }
        .pointerInput(item, drag.root) {
            detectDragGestures(
                onDragStart = { off ->
                    val origin = drag.root?.let { r -> coords?.let { r.localBoundingBoxOf(it).topLeft } } ?: Offset.Zero
                    drag.item = item; drag.ghost = art; drag.isChar = isChar
                    drag.pos = origin + off
                    drag.hover = drag.panelAt(drag.pos) ?: -1
                    model.clearSelection()
                },
                onDrag = { ch, d -> ch.consume(); drag.pos += d; drag.hover = drag.panelAt(drag.pos) ?: -1 },
                onDragEnd = {
                    drag.panelAt(drag.pos)?.let { idx ->
                        when (item) {
                            is BoardModel.Sel.Scene -> model.setScene(idx, item.id)
                            is BoardModel.Sel.Char -> model.place(idx, item.id)
                        }
                    }
                    drag.item = null; drag.ghost = null; drag.hover = -1
                },
                onDragCancel = { drag.item = null; drag.ghost = null; drag.hover = -1 }
            )
        }
}

@Composable
fun BoardScreen(levelId: String, onSolved: () -> Unit, onExit: () -> Unit) {
    val level = GameContent.level(levelId) ?: return
    val model = remember(levelId) { BoardModel(level, GameContent.db) }
    model.onSfx = { Audio.sfx(it) }
    var showFact by remember { mutableStateOf(false) }
    /** Уровень решён, история ещё не открыта: на доске висит зов «Дальше». */
    var awaitingReveal by remember(levelId) { mutableStateOf(false) }
    var showHint by remember { mutableStateOf(false) }
    var celebrate by remember(levelId) { mutableStateOf(false) }
    val boardShake = remember(levelId) { Animatable(0f) }
    LaunchedEffect(levelId) { Audio.startMusic(level.music ?: "theme") }
    LaunchedEffect(model.isSolved) {
        if (model.isSolved) {
            // Историю не выкидываем сама собой: игрок только что собрал сцену и хочет
            // разглядеть, что получилось. Вместо этого зовём кнопкой — открыть её можно
            // когда захочется, а из карточки вернуться назад на доску.
            Audio.sfx("win"); onSolved(); celebrate = true
            delay(1000); awaitingReveal = true
            delay(1900); celebrate = false
        } else {
            // Доска разобрана («заново» или снятый токен) — звать к истории больше нечем.
            awaitingReveal = false; celebrate = false
        }
    }
    // неверный ход: доска заполнена, но цель не достигнута — тряска (+ звук, если панели «мертвы»)
    LaunchedEffect(model.changeToken) {
        // Полная, но нерешённая доска без единого диагноза (уровень без эталона) — общая тряска.
        if (!model.isSolved && model.isBoardComplete && (0 until model.panels.size).all { model.diagnose(it) == BoardModel.Diag.OK }) {
            if (model.lastBeats.isEmpty()) Audio.sfx("error")
            boardShake.snapTo(0f); boardShake.animateTo(1f, tween(450, easing = LinearEasing))
        }
    }
    // Валидация мгновенная: как только у панели появился диагноз — звук и тряска.
    LaunchedEffect(model.wrongToken) {
        if (model.wrongToken > 0) {
            Audio.sfx("error")
            boardShake.snapTo(0f); boardShake.animateTo(1f, tween(450, easing = LinearEasing))
        }
    }
    val exit = { Audio.sfx("select"); Audio.startMusic("theme"); onExit() }
    val shakeDx = (sin(boardShake.value * PI * 3) * 9.0 * (1f - boardShake.value)).toFloat()

    val drag = remember(levelId) { DragState() }
    // По вертикали полей меньше, чем по горизонтали: экран в ландшафте низкий,
    // и каждая точка высоты уходит кадрам, а не полям страницы.
    Box(Modifier.fillMaxSize().padding(horizontal = 14.dp, vertical = 6.dp)
        .onGloballyPositioned { drag.root = it }) {
        BookPage(Modifier.fillMaxSize().graphicsLayer { translationX = shakeDx.dp.toPx() }) {
            BoxWithConstraints(Modifier.fillMaxSize()) {
                // Считать по одной ширине нельзя: телефон в ландшафте широкий и низкий, и ряд
                // токенов переставал помещаться по высоте, съедая место у кадров.
                val trayScale = min(1.6f, max(0.78f, min(maxWidth.value / 720f, maxHeight.value / 440f)))
                Column(Modifier.fillMaxSize().padding(horizontal = 20.dp, vertical = 8.dp)) {
                    // titleBar — чекбокс+заголовок по центру (как iOS); лента слева и кнопки справа не наезжают
                    Box(Modifier.fillMaxWidth().padding(bottom = 6.dp)) {
                        Row(Modifier.align(Alignment.Center).padding(horizontal = 72.dp),
                            verticalAlignment = Alignment.CenterVertically) {
                            Box(Modifier.size(22.dp).clip(RoundedCornerShape(5.dp))
                                .background(if (model.isSolved) Palette.success else Color.Transparent)
                                .border(2.dp, if (model.isSolved) Palette.success else Palette.ink.copy(0.5f), RoundedCornerShape(5.dp)),
                                contentAlignment = Alignment.Center) {
                                if (model.isSolved) Icon(Icons.Filled.Check, null, tint = Color.White, modifier = Modifier.size(15.dp))
                            }
                            Spacer(Modifier.width(10.dp))
                            // Цель — условие задачи, её нельзя обрезать многоточием: три строки и
                            // шрифт по длине текста.
                            val goal = level.goalText ?: ""
                            Text(goal, color = Palette.ink, fontSize = (if (goal.length > 110) 13 else if (goal.length > 75) 15 else 18).sp,
                                fontWeight = FontWeight.Bold, lineHeight = (if (goal.length > 110) 15 else if (goal.length > 75) 17 else 20).sp,
                                fontFamily = Fonts.serif, textAlign = TextAlign.Center, maxLines = 3)
                        }
                        Row(Modifier.align(Alignment.CenterEnd), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            IconMini(Icons.Filled.Info) { showHint = true }
                            IconMini(Icons.Filled.Refresh) { model.reset() }
                        }
                    }
                    // panels
                    // Реплику гида рисуем поверх доски, а место под неё освобождаем отступом:
                    // если положить её отдельным ребёнком колонки, weight(1f) у кадров обнуляется
                    // и они исчезают совсем (проверено подсветкой областей на устройстве).
                    // 34dp — высота реплики, +12dp зазор, иначе она упирается в нижнюю кромку кадров
                    val coachPad = if (model.coachStep != null && !showFact && !awaitingReveal) 46.dp else 0.dp
                    BoxWithConstraints(Modifier.fillMaxWidth().weight(1f).padding(bottom = coachPad)) {
                        // Подсказка «кадры можно менять местами»: стоят ≥2 сцен, первые три раза, на 6 с.
                        var showSwapHint by remember { mutableStateOf(false) }
                        val ctx = LocalContext.current
                        LaunchedEffect(model.changeToken) {
                            val prefs = ctx.getSharedPreferences("ht", android.content.Context.MODE_PRIVATE)
                            val shown = prefs.getInt("swap_hint_shown", 0)
                            // На туториальных уровнях плашку не показываем: там про перетаскивание
                            // говорит гид, и две подсказки разом только загромождают доску.
                            if (shown < 3 && !showSwapHint && !model.isSolved && model.level.coach.isEmpty() &&
                                model.panels.count { it.sceneId != null } >= 2) {
                                prefs.edit().putInt("swap_hint_shown", shown + 1).apply()
                                showSwapHint = true; delay(6000); showSwapHint = false
                            }
                        }
                        // Формат плашки — как на iOS: золотая «пилюля» с тенью, стрелка отдельным
                        // знаком слева от текста, мягкий выезд сверху. Иконка и подпись разнесены,
                        // иначе ⇄ прилипает к первому слову и читается как часть фразы.
                        val hintAlpha by animateFloatAsState(if (showSwapHint) 1f else 0f,
                            tween(220), label = "swapHintAlpha")
                        val hintShift by animateFloatAsState(if (showSwapHint) 0f else -24f,
                            tween(220), label = "swapHintShift")
                        if (hintAlpha > 0.01f) Row(
                            Modifier.align(Alignment.TopCenter).zIndex(20f)
                                .graphicsLayer { alpha = hintAlpha; translationY = hintShift }
                                .padding(top = 6.dp)
                                .shadow(3.dp, RoundedCornerShape(50), clip = false)
                                .clip(RoundedCornerShape(50))
                                .background(Palette.gold.copy(0.95f))
                                .padding(horizontal = 12.dp, vertical = 6.dp),
                            horizontalArrangement = Arrangement.spacedBy(6.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text("⇄", color = Palette.ink, fontSize = 12.sp,
                                 fontWeight = FontWeight.Bold, fontFamily = Fonts.rounded)
                            Text(L10n.s("ui.swap_hint"), color = Palette.ink,
                                 fontSize = 12.sp, fontFamily = Fonts.rounded)
                        }
                        val n = max(1, model.panels.size)
                        val gap = 14.dp
                        val cellH = min(maxHeight.value, 430f).dp
                        val cellW = min(((maxWidth - gap * (n - 1)).value / n), cellH.value * 1.2f).dp
                        var draggingPanel by remember { mutableStateOf(-1) }
                        var dragDX by remember { mutableStateOf(0f) }
                        val stepPx = with(LocalDensity.current) { (cellW + gap).toPx() }
                        // Кадр, на который сейчас нацелен палец: его подсвечиваем, как на iOS,
                        // чтобы обмен местами был виден до того, как игрок отпустит палец.
                        val hoverPanel = if (draggingPanel >= 0)
                            (draggingPanel + Math.round(dragDX / stepPx))
                                .coerceIn(0, model.panels.size - 1)
                                .takeIf { it != draggingPanel }
                        else null
                        Row(Modifier.fillMaxSize(), horizontalArrangement = Arrangement.spacedBy(gap, Alignment.CenterHorizontally),
                            verticalAlignment = Alignment.CenterVertically) {
                            for (i in model.panels.indices) {
                                val beats = model.lastBeats.filter { it.panelIndex == i }
                                val placed = model.panels[i].sceneId != null
                                Box(Modifier
                                    .zIndex(if (draggingPanel == i) 10f else 0f)
                                    .graphicsLayer {
                                        if (draggingPanel == i) {
                                            translationX = dragDX; scaleX = 1.05f; scaleY = 1.05f
                                            shadowElevation = 18f; shape = RoundedCornerShape(10.dp); clip = false
                                        }
                                    }
                                    // Долгое нажатие, а не сразу тяга: короткий свайп по доске должен
                                    // оставаться прокруткой, да и подсказка обещает именно «зажми».
                                    .then(if (placed) Modifier.pointerInput(i, model.panels.size) {
                                        detectDragGesturesAfterLongPress(
                                            onDragStart = { draggingPanel = i; dragDX = 0f },
                                            onDrag = { ch, d -> ch.consume(); dragDX += d.x },
                                            onDragEnd = {
                                                val to = (i + Math.round(dragDX / stepPx)).coerceIn(0, model.panels.size - 1)
                                                if (to != i) model.movePanel(i, to)
                                                draggingPanel = -1; dragDX = 0f
                                            },
                                            onDragCancel = { draggingPanel = -1; dragDX = 0f })
                                    } else Modifier)
                                ) {
                                    PanelCell(model, i, cellW, cellH, beats, model.changeToken, drag)
                                    if (hoverPanel == i) Box(
                                        Modifier.matchParentSize().clip(RoundedCornerShape(10.dp))
                                            .background(Palette.gold.copy(0.22f)),
                                        contentAlignment = Alignment.Center) {
                                        Text("⇄", color = Palette.gold, fontSize = 26.sp,
                                             fontWeight = FontWeight.Bold, fontFamily = Fonts.rounded)
                                    }
                                }
                            }
                        }
                    }
                    TokenTray(model, trayScale, drag)
                }
            }
        }
        // Реплика гида — поверх доски, в зазоре, который освобождает coachPad выше.
        model.coachStep?.let { st ->
            if (!showFact && !awaitingReveal) CoachBubble(model.level.id, st,
                Modifier.align(Alignment.BottomCenter).padding(bottom = 82.dp))
        }
        // Лента висит на верхней кромке страницы, а не внутри неё (как закладка в книге).
        BackRibbon(Modifier.align(Alignment.TopStart)) { exit() }
        // Плавающее превью перетаскиваемого токена — следует за пальцем
        val ghost = drag.ghost
        if (drag.item != null && ghost != null) {
            val gp = artPainter(ghost)
            if (gp != null) {
                if (drag.isChar) {
                    Image(gp, null,
                        Modifier.offset { IntOffset((drag.pos.x - 38.dp.toPx()).roundToInt(), (drag.pos.y - 48.dp.toPx()).roundToInt()) }
                            .height(96.dp).alpha(0.92f).graphicsLayer { scaleX = 1.1f; scaleY = 1.1f },
                        contentScale = ContentScale.Fit)
                } else {
                    Image(gp, null,
                        Modifier.offset { IntOffset((drag.pos.x - 54.dp.toPx()).roundToInt(), (drag.pos.y - 38.dp.toPx()).roundToInt()) }
                            .size(108.dp, 76.dp).clip(RoundedCornerShape(8.dp)).alpha(0.92f),
                        contentScale = ContentScale.Crop)
                }
            }
        }
        if (celebrate) ConfettiOverlay()
        if (showHint) HintPopup(level.title, listOfNotNull(level.initialText, level.goalHint).joinToString("\n\n")) { showHint = false }
        if (awaitingReveal && !showFact) RevealButton { Audio.sfx("select"); showFact = true }
        if (showFact) FactPopup(level,
            onReplay = { Audio.sfx("select"); showFact = false; model.reset() },
            onBack = { showFact = false }) { showFact = false; exit() }
    }
}

/** Зов к истории: появляется на решённой доске и ждёт столько, сколько нужно игроку. */
@Composable
private fun BoxScope.RevealButton(onTap: () -> Unit) {
    val t = rememberInfiniteTransition(label = "reveal")
    val glow by t.animateFloat(0.15f, 0.55f,
        infiniteRepeatable(tween(1200), RepeatMode.Reverse), label = "glow")
    Row(
        Modifier.align(Alignment.BottomEnd).padding(end = 34.dp, bottom = 26.dp)
            .shadow(if (glow > 0.35f) 12.dp else 4.dp, RoundedCornerShape(30.dp),
                ambientColor = Palette.gold, spotColor = Palette.gold)
            .clip(RoundedCornerShape(30.dp)).background(Palette.maroon)
            .border(2.dp, Palette.gold.copy(alpha = 0.7f), RoundedCornerShape(30.dp))
            .clickable { onTap() }
            .padding(horizontal = 24.dp, vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Text("\uD83D\uDCDC", fontSize = 14.sp)
        Text(L10n.s("ui.next"), color = Palette.paper, fontSize = 15.sp,
            fontWeight = FontWeight.Bold, fontFamily = Fonts.rounded)
    }
}

/** Флаги состояния → эмодзи-бейджи (порт StateBadges из iOS). */
private fun stateBadges(charId: String, w: World): List<String> = buildList {
    if (w.hasFlag(charId, "dead")) add("☠️")
    if (w.hasFlag(charId, "plotting")) add("🗡")
    if (w.hasFlag(charId, "traitor")) add("🎭")
    if (w.hasFlag(charId, "crowned")) add("👑")
    if (w.hasFlag(charId, "backed")) add("🛡")
    if (w.hasFlag(charId, "conqueror")) add("⚔️")
    if (w.hasFlag(charId, "in_rome")) add("🏛")
    if (w.hasFlag(charId, "has_heir")) add("👶")
}

@Composable
private fun PanelCell(model: BoardModel, i: Int, cellW: androidx.compose.ui.unit.Dp, cellH: androidx.compose.ui.unit.Dp,
                     beats: List<BoardModel.Beat>, changeToken: Int, drag: DragState) {
    val panel = model.panels[i]
    val diag = model.diagnose(i)
    val highlighted = model.selected != null
    val hovered = drag.hover == i          // панель под перетаскиваемым токеном
    val isOrderHint = diag == BoardModel.Diag.WRONG_ORDER || diag == BoardModel.Diag.WRONG_SLOTS
    val border = when {
        hovered -> Palette.gold
        highlighted -> Palette.gold
        isOrderHint -> Palette.gold
        diag != BoardModel.Diag.OK -> Palette.maroon
        else -> Palette.ink.copy(0.55f)
    }
    // удар при «жёстких» событиях (гибель/битва/поход) — панель вздрагивает
    val impactBeats = beats.filter {
        it.kind == BoardModel.Kind.KILL || it.kind == BoardModel.Kind.BATTLE || it.kind == BoardModel.Kind.CONQUER
    }
    val panelShake = remember(i) { Animatable(0f) }
    LaunchedEffect(changeToken) {
        if (impactBeats.isNotEmpty()) { panelShake.snapTo(0f); panelShake.animateTo(1f, tween(380, easing = LinearEasing)) }
    }
    val pDx = (sin(panelShake.value * PI * 3) * 5.0 * (1f - panelShake.value)).toFloat()
    Box(
        Modifier.size(cellW, cellH).graphicsLayer { translationX = pDx.dp.toPx() }
            .onGloballyPositioned { c -> drag.root?.let { drag.panelRects[i] = it.localBoundingBoxOf(c) } }
            .clip(RoundedCornerShape(10.dp))
            .background(Palette.panel)
            .border(if (highlighted || hovered || diag != BoardModel.Diag.OK) 3.dp else 2.dp, border, RoundedCornerShape(10.dp))
            .clickable(enabled = model.selected != null) { model.applySelection(i) }
    ) {
        val sid = panel.sceneId
        if (sid != null) {
            // сцена появляется с лёгким наплывом
            val sceneAppear = remember(sid) { Animatable(0f) }
            LaunchedEffect(sid) { sceneAppear.animateTo(1f, tween(280, easing = FastOutSlowInEasing)) }
            val scenePainter = artPainter("scene_$sid")
            if (scenePainter != null) Image(scenePainter, null,
                Modifier.fillMaxSize().graphicsLayer {
                    alpha = sceneAppear.value
                    val s = 0.9f + 0.1f * sceneAppear.value; scaleX = s; scaleY = s
                }, contentScale = ContentScale.Crop)
            model.sceneAction(sid)?.let { action ->
                // Отступ справа — под крестик «убрать сцену»: длинные подписи вроде
                // «заступничество» иначе уезжали ему под кнопку.
                Box(Modifier.padding(7.dp).padding(end = 28.dp).clip(RoundedCornerShape(10.dp))
                    .background(Palette.paper.copy(0.92f))
                    .padding(horizontal = 7.dp, vertical = 3.dp)) {
                    // Одна строка: узкая плашка переносила длинные подписи по слогам
                    // («похище/ние»), а крестик рядом не оставляет ширины на два ряда.
                    Text(action, color = Palette.ink, fontSize = 9.sp, fontWeight = FontWeight.Bold,
                        fontFamily = Fonts.rounded, maxLines = 1, softWrap = false)
                }
            }
            // Постоянный значок «что тут происходит» — сердце, мечи, корона… (см. panelSymbols).
            model.panelSymbols.getOrNull(i)?.let { sym ->
                Box(Modifier.align(Alignment.TopCenter).padding(top = 34.dp).clip(CircleShape)
                    .background(Palette.paper.copy(0.9f)).border(1.dp, Palette.ink.copy(0.35f), CircleShape)
                    .padding(5.dp), contentAlignment = Alignment.Center) {
                    Text(sym, fontSize = 18.sp)
                }
            }
            // Постоянная «ручка»: кадр со сценой берётся долгим нажатием и меняется местами.
            // Иконка без текста — не зависит от каталога переводов.
            if (model.panels.size > 1) Box(Modifier.align(Alignment.BottomStart).padding(6.dp)
                .clip(CircleShape).background(Palette.paper.copy(0.8f)).padding(5.dp),
                contentAlignment = Alignment.Center) {
                Text("⇄", color = Palette.ink.copy(0.75f), fontSize = 11.sp, fontWeight = FontWeight.Bold)
            }
            // X убрать сцену
            Box(Modifier.align(Alignment.TopEnd).padding(6.dp).size(24.dp).clip(CircleShape)
                .background(Palette.paper.copy(0.95f)).border(1.5.dp, Palette.ink.copy(0.4f), CircleShape)
                .clickable { model.setScene(i, null) }, contentAlignment = Alignment.Center) {
                Icon(Icons.Filled.Close, null, tint = Palette.maroon, modifier = Modifier.size(13.dp))
            }
            // персонажи снизу
            val slots = model.slots(i)
            val spriteH = cellH * 0.6f
            Row(Modifier.align(Alignment.BottomCenter).fillMaxWidth().padding(bottom = 4.dp),
                horizontalArrangement = Arrangement.Center, verticalAlignment = Alignment.Bottom) {
                for (slot in 0 until slots) {
                    if (slot < panel.characters.size) {
                        CharSprite(model, i, panel.characters[slot], slot, spriteH, beats)
                    } else {
                        EmptySlot(spriteH)   // явный намёк: сюда нужен ещё персонаж
                    }
                }
            }
            // удар: цветная вспышка (красная — гибель, золотая — битва)
            impactBeats.forEach { b ->
                key(changeToken, b) {
                    ImpactFlash(if (b.kind == BoardModel.Kind.KILL) Palette.maroon else Palette.gold,
                        Modifier.matchParentSize())
                }
            }
            // битва/поход — скрещённые мечи в центре
            if (beats.any { it.kind == BoardModel.Kind.BATTLE || it.kind == BoardModel.Kind.CONQUER }) {
                key(changeToken) {
                    Box(Modifier.align(Alignment.Center)) { PropBurst("prop_swords", minOf(cellW, cellH) * 0.5f, 4f, 500) }
                }
            }
            // гильотина — нож падает сверху (в сцене-гильотине при казни)
            val isGuillotine = model.db.scenes[sid]?.tags?.contains("guillotine") == true
            if (isGuillotine && beats.any { it.kind == BoardModel.Kind.KILL }) {
                key(changeToken) { Box(Modifier.align(Alignment.TopCenter)) { GuillotineBlade(cellH) } }
            }
            // сердца между влюблёнными
            if (beats.any { it.kind == BoardModel.Kind.LOVE }) {
                key(changeToken) { HeartsRise(Modifier.align(Alignment.BottomCenter).padding(bottom = cellH * 0.28f)) }
            }
            // всплывающий символ события (у короны/любви/убийства/битвы — свой пропс/анимация)
            Box(Modifier.align(Alignment.TopCenter).padding(top = cellH * 0.14f)) {
                beats.filter {
                    it.kind != BoardModel.Kind.CROWN && it.kind != BoardModel.Kind.LOVE &&
                        it.kind != BoardModel.Kind.KILL && it.kind != BoardModel.Kind.BATTLE &&
                        it.kind != BoardModel.Kind.CONQUER && it.kind != BoardModel.Kind.MARCH
                }.forEach { b -> key(changeToken, b) { FlyingBadge(b.symbol) } }
            }
            // подсказка об ошибке
            wrongHint(diag)?.let { hint ->
                Box(Modifier.align(Alignment.BottomCenter).padding(bottom = 8.dp).clip(RoundedCornerShape(20.dp))
                    .background((if (isOrderHint) Palette.gold else Palette.maroon).copy(0.94f))
                    .padding(horizontal = 10.dp, vertical = 5.dp)) {
                    Text(hint, color = if (isOrderHint) Palette.ink else Color.White, fontSize = 10.sp, fontFamily = Fonts.rounded)
                }
            }
        } else {
            // как на iOS: значок над подписью — пустой кадр читается как «сюда нужна сцена»
            Column(Modifier.align(Alignment.Center), horizontalAlignment = Alignment.CenterHorizontally) {
                // Только базовый набор иконок: расширенного (TouchApp/Image) в проекте нет.
                Icon(Icons.Filled.Add, null,
                    tint = if (highlighted) Palette.maroon else Palette.inkSoft.copy(0.6f),
                    modifier = Modifier.size(20.dp))
                Spacer(Modifier.height(4.dp))
                Text(if (highlighted) L10n.s("ui.tap") else L10n.s("ui.scene"),
                    color = Palette.inkSoft.copy(0.7f), fontSize = 11.sp, fontFamily = Fonts.rounded)
            }
        }
    }
}

/** Пустой слот персонажа: пунктирная рамка + «+». Показывает, сколько ещё героев нужно в сцену. */
@Composable
private fun EmptySlot(spriteH: androidx.compose.ui.unit.Dp) {
    val hint = Palette.ink.copy(alpha = 0.32f)
    Box(
        Modifier.height(spriteH * 0.9f).width(spriteH * 0.6f).padding(horizontal = 4.dp, vertical = 6.dp)
            .drawBehind {
                drawRoundRect(color = hint,
                    style = Stroke(width = 2.dp.toPx(), pathEffect = PathEffect.dashPathEffect(floatArrayOf(9f, 8f), 0f)),
                    cornerRadius = androidx.compose.ui.geometry.CornerRadius(10.dp.toPx()))
            },
        contentAlignment = Alignment.Center
    ) {
        Text("+", color = hint, fontSize = (spriteH.value * 0.26f).sp, fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
    }
}

/** Спрайт персонажа со всей «живостью»: появление-пружина, падение при гибели, дрожь заговорщика,
 *  выпад активной стороны к цели, реакция пострадавшего/триумфатора, опускающаяся корона. */
@Composable
private fun CharSprite(model: BoardModel, i: Int, cid: String, slot: Int, spriteH: androidx.compose.ui.unit.Dp,
                       beats: List<BoardModel.Beat>) {
    val ctx = androidx.compose.ui.platform.LocalContext.current
    val snap = model.snapshot(i)
    val dead = snap.hasFlag(cid, "dead")
    // слой 3: отдельная поза «повержен». Есть (в res или паке) → показываем её без ч/б и заваливания.
    val useDeadPose = dead && artExists(ctx, "char_${cid}_dead")
    val topple = dead && !useDeadPose   // старый фолбэк
    // разгромлен, но жив → поза «повержен-живой»
    val defeated = !dead && listOf("fugitive", "defeated", "exiled", "cast_off", "widowed", "disgraced", "grieving")
        .any { snap.hasFlag(cid, it) }
    val useDefeatedPose = defeated && artExists(ctx, "char_${cid}_defeated")
    // победные состояния → поза «триумф» (если не разгромлен)
    val triumphant = !dead && !defeated && listOf("crowned", "reigns", "emperor", "empress", "victor", "conqueror",
        "triumphant", "honored", "beloved", "first_consul", "supreme_head", "absolute", "at_war").any { snap.hasFlag(cid, it) }
    val useTriumphPose = triumphant && artExists(ctx, "char_${cid}_triumph")
    val plotting = !dead && snap.hasFlag(cid, "plotting")
    val usePlotPose = plotting && !defeated && artExists(ctx, "char_${cid}_plot")
    val crowned = !dead && snap.hasFlag(cid, "crowned")
    val micro = model.microState(cid, i)
    val panelChars = model.panels[i].characters

    // роли в свежих битах
    val aggro = beats.firstOrNull {
        (it.kind == BoardModel.Kind.KILL || it.kind == BoardModel.Kind.BATTLE || it.kind == BoardModel.Kind.CONDEMN) &&
            it.secondary == cid
    }
    val lungeDX: Float = aggro?.primary?.let { vp ->
        panelChars.indexOf(vp).takeIf { it >= 0 }?.let { vs -> if (vs > slot) 20f else -20f }
    } ?: 0f
    val motion = when {
        beats.any { it.kind == BoardModel.Kind.CONDEMN && it.primary == cid } -> "recoil"
        !useDefeatedPose && beats.any { (it.kind == BoardModel.Kind.BATTLE || it.kind == BoardModel.Kind.DOWNFALL) && it.primary == cid } -> "slump"
        beats.any { (it.kind == BoardModel.Kind.TRIUMPH || it.kind == BoardModel.Kind.CONQUER || it.kind == BoardModel.Kind.MARCH) && it.primary == cid } -> "hop"
        else -> "none"
    }
    val crownDrop = beats.any { it.kind == BoardModel.Kind.CROWN && it.primary == cid }
    val killVictim = beats.any { it.kind == BoardModel.Kind.KILL && it.primary == cid }

    // появление — пружиной из уменьшенного
    val appear = remember(cid) { Animatable(0.4f) }
    LaunchedEffect(cid) { appear.animateTo(1f, spring(dampingRatio = 0.55f, stiffness = Spring.StiffnessMediumLow)) }
    // Падение при гибели (только если нет позы «повержен»). Валимся внутрь кадра: поворот
    // на 80° вокруг ступней уводит голову на целый рост вбок, и у крайнего справа персонажа
    // она оказывалась за кромкой кадра.
    val fallsLeft = slot * 2 >= panelChars.size
    val fall by animateFloatAsState(if (topple) (if (fallsLeft) -80f else 80f) else 0f,
        spring(dampingRatio = 0.55f), label = "fall")
    // короткое оседание, когда есть поза
    val settle by animateFloatAsState(if (useDeadPose) 1f else 0f, spring(dampingRatio = 0.5f), label = "settle")
    // дрожь заговорщика — фолбэк, если нет позы «заговорщик»
    val tremble = if (plotting && !usePlotPose) {
        val t = rememberInfiniteTransition(label = "tr")
        t.animateFloat(-2.5f, 2.5f, infiniteRepeatable(tween(110), RepeatMode.Reverse), label = "trv").value
    } else 0f
    // выпад к цели
    val lunge = remember(cid) { Animatable(0f) }
    LaunchedEffect(aggro, cid) {
        if (aggro != null && lungeDX != 0f) { lunge.animateTo(lungeDX, tween(100)); lunge.animateTo(0f, spring(dampingRatio = 0.5f)) }
    }
    // союз: мягкий наклон друг к другу
    val allyBeat = beats.firstOrNull { it.kind == BoardModel.Kind.ALLY && (it.primary == cid || it.secondary == cid) }
    val allyLeanDX: Float = allyBeat?.let { ab ->
        val partner = if (ab.primary == cid) ab.secondary else ab.primary
        partner?.let { p -> panelChars.indexOf(p).takeIf { it >= 0 }?.let { ps -> if (ps > slot) 12f else -12f } }
    } ?: 0f
    val lean = remember(cid) { Animatable(0f) }
    LaunchedEffect(allyBeat, cid) {
        if (allyBeat != null && allyLeanDX != 0f) { lean.animateTo(allyLeanDX, tween(220)); lean.animateTo(0f, spring(dampingRatio = 0.6f)) }
    }
    // реакция «над кем действие»: 0..1 прогресс
    val mo = remember(cid) { Animatable(0f) }
    LaunchedEffect(motion, cid) {
        if (motion != "none") {
            mo.snapTo(0f); mo.animateTo(1f, spring(dampingRatio = 0.45f, stiffness = Spring.StiffnessLow))
            delay(if (motion == "hop") 120 else 550); mo.animateTo(0f, spring(dampingRatio = 0.7f))
        }
    }
    val moDy = when (motion) { "hop" -> -20f * mo.value; "slump" -> 8f * mo.value; else -> 0f }
    val moRot = when (motion) { "slump" -> 10f * mo.value; "recoil" -> -12f * mo.value; else -> 0f }
    val moScale = when (motion) { "recoil" -> 1f - 0.1f * mo.value; "hop" -> 1f + 0.06f * mo.value; else -> 1f }

    Box(contentAlignment = Alignment.TopCenter) {
        val poseName = if (useDeadPose) "char_${cid}_dead" else if (useDefeatedPose) "char_${cid}_defeated"
            else if (usePlotPose) "char_${cid}_plot" else if (useTriumphPose) "char_${cid}_triumph" else "char_$cid"
        val cdPainter = artPainter(poseName)
        if (cdPainter != null) Image(cdPainter, null,
            Modifier.height(spriteH).graphicsLayer {
                transformOrigin = androidx.compose.ui.graphics.TransformOrigin(0.5f, 1f)
                val s = appear.value * moScale; scaleX = s; scaleY = s
                rotationZ = fall + tremble + moRot
                // Сдвига вниз у завала нет: вращаем вокруг ступней (transformOrigin выше),
                // поэтому тело и так ложится на пол. С ним оно уезжало под нижнюю кромку кадра
                // и обрезалось — выглядело как «падает за сцену».
                translationY = moDy.dp.toPx() +
                    (if (useDeadPose) ((1f - settle) * -6f).dp.toPx() else 0f)
                translationX = (lunge.value + lean.value).dp.toPx()
            }.clickable { if (model.selected != null) model.applySelection(i) else model.removeChar(i, cid) },
            contentScale = ContentScale.Fit, colorFilter = if (topple) grayscale else null)
        if (micro != null && !dead) Text(micro, fontSize = 20.sp, modifier = Modifier.offset(y = (-6).dp))
        if (crowned) CrownFlash()
        if (crownDrop) DescendingCrown()
        if (killVictim) PropBurst("prop_blood", spriteH * 0.72f, 6f, 750)
        if (dead) DustPuff(Modifier.align(Alignment.BottomCenter))
    }
}

// ---- Эффекты «сока» (порт из iOS LevelBoardView) ----

/** Всплывающий символ события: выпрыгивает с пружиной и уплывает вверх, тая. */
@Composable
private fun FlyingBadge(symbol: String) {
    val scale = remember { Animatable(0.2f) }
    val ty = remember { Animatable(0f) }
    val alpha = remember { Animatable(1f) }
    LaunchedEffect(Unit) {
        launch { scale.animateTo(1f, spring(dampingRatio = 0.45f, stiffness = Spring.StiffnessMedium)) }
        launch { delay(200); alpha.animateTo(0f, tween(900)) }
        delay(200); ty.animateTo(-70f, tween(1000, easing = FastOutSlowInEasing))
    }
    Text(symbol, fontSize = 30.sp, modifier = Modifier.graphicsLayer {
        scaleX = scale.value; scaleY = scale.value
        translationY = ty.value.dp.toPx()
        this.alpha = alpha.value
    })
}

/** Удар: цветная вспышка на всю панель (поверх идёт пропс — кровь/мечи). Красная — гибель, золотая — битва. */
@Composable
private fun ImpactFlash(color: Color, modifier: Modifier) {
    val p = remember { Animatable(0f) }
    LaunchedEffect(Unit) { p.animateTo(1f, tween(450, easing = FastOutSlowInEasing)) }
    Box(modifier.clip(RoundedCornerShape(10.dp)).background(color.copy(alpha = 0.42f * (1f - p.value))))
}

/** Пропс-объект, вылетающий на событии: выпрыгивает пружиной, держится и тает вверх. */
@Composable
private fun PropBurst(prop: String, size: androidx.compose.ui.unit.Dp, rise: Float = 8f, holdMs: Long = 550) {
    val scale = remember { Animatable(0.2f) }
    val ty = remember { Animatable(0f) }
    val alpha = remember { Animatable(1f) }
    LaunchedEffect(Unit) {
        launch { scale.animateTo(1f, spring(dampingRatio = 0.5f, stiffness = Spring.StiffnessMedium)) }
        launch { delay(holdMs); launch { ty.animateTo(-rise, tween(550)) }; alpha.animateTo(0f, tween(550)) }
    }
    val painter = artPainter(prop)
    if (painter != null) Image(painter, null, Modifier.size(size).graphicsLayer {
        scaleX = scale.value; scaleY = scale.value; translationY = ty.value.dp.toPx(); this.alpha = alpha.value
    }, contentScale = ContentScale.Fit)
}

/** Нож гильотины падает сверху вниз по центру панели. */
@Composable
private fun GuillotineBlade(panelH: androidx.compose.ui.unit.Dp) {
    val drop = remember { Animatable(0f) }
    LaunchedEffect(Unit) { drop.animateTo(1f, tween(260, easing = FastOutSlowInEasing)) }
    val painter = artPainter("prop_blade")
    if (painter != null) Image(painter, null, Modifier.height(panelH * 0.52f).graphicsLayer {
        translationY = (panelH.toPx() * (-0.78f + 0.68f * drop.value))
    }, contentScale = ContentScale.Fit)
}

/** Сердечки между влюблёнными — стайка поднимается вверх и тает. */
@Composable
private fun HeartsRise(modifier: Modifier) {
    val count = 5
    val p = remember { Animatable(0f) }
    LaunchedEffect(Unit) { p.animateTo(1f, tween(1000, easing = FastOutSlowInEasing)) }
    Box(modifier) {
        for (idx in 0 until count) {
            val dx = (idx - count / 2) * 16f
            Text("❤️", fontSize = 18.sp, modifier = Modifier.graphicsLayer {
                val local = p.value
                translationX = (dx * (0.5f + local)).dp.toPx()
                translationY = (-(64f + idx * 6f) * local).dp.toPx()
                alpha = 1f - local
            })
        }
    }
}

/** Корона (пропс-объект) падает сверху на голову и оседает с лёгким отскоком. */
@Composable
private fun DescendingCrown() {
    val land = remember { Animatable(0f) }
    LaunchedEffect(Unit) { land.animateTo(1f, spring(dampingRatio = 0.5f, stiffness = Spring.StiffnessLow)) }
    val painter = artPainter("prop_crown")
    if (painter != null) Image(painter, null, Modifier.size(34.dp).graphicsLayer {
        val s = 1.6f - 0.6f * land.value; scaleX = s; scaleY = s
        translationY = (-74f + 44f * land.value).dp.toPx()
        alpha = land.value
    }, contentScale = ContentScale.Fit)
}

/** Золотая вспышка-лучи при короновании. */
@Composable
private fun CrownFlash() {
    val count = 9
    val p = remember { Animatable(0f) }
    LaunchedEffect(Unit) { p.animateTo(1f, tween(500, easing = FastOutSlowInEasing)) }
    Box {
        for (idx in 0 until count) {
            val ang = idx.toFloat() / count * 360f
            val rad = (ang * PI / 180.0).toFloat()
            Box(Modifier.size(3.dp, 12.dp).graphicsLayer {
                val dist = 16f + 18f * p.value
                translationX = (sin(rad) * dist).dp.toPx()
                translationY = (-cos(rad) * dist).dp.toPx() - 8.dp.toPx()
                rotationZ = ang
                val s = 0.4f + 0.8f * p.value; scaleX = s; scaleY = s
                alpha = 0.9f * (1f - p.value)
            }.background(Palette.gold))
        }
    }
}

/** Пыль при падении — облачко разлетается веером и тает. */
@Composable
private fun DustPuff(modifier: Modifier) {
    val count = 7
    val p = remember { Animatable(0f) }
    LaunchedEffect(Unit) { p.animateTo(1f, tween(550, easing = FastOutSlowInEasing)) }
    Box(modifier) {
        for (idx in 0 until count) {
            val a = idx.toFloat() / (count - 1) * PI.toFloat()
            Box(Modifier.size(9.dp).clip(CircleShape).background(Palette.paperEdge.copy(alpha = 0.9f)).graphicsLayer {
                translationX = (cos(a) * 28f * p.value).dp.toPx()
                translationY = (-sin(a) * 14f * p.value).dp.toPx()
                val s = 0.4f + 1.1f * p.value; scaleX = s; scaleY = s
                alpha = 0.7f * (1f - p.value)
            })
        }
    }
}

/** Конфетти на победе — эмодзи сыплются сверху вниз. */
@Composable
private fun ConfettiOverlay() {
    val syms = listOf("🎉", "✨", "🎊", "⭐️", "👑", "❤️")
    data class Piece(val x: Float, val sym: String, val size: Float, val delay: Float, val dur: Float, val rot: Float)
    val pieces = remember {
        List(26) {
            Piece(Random.nextFloat(), syms[it % syms.size], (20..38).random().toFloat(),
                Random.nextFloat() * 0.35f, 1.3f + Random.nextFloat() * 0.8f, (-260..260).random().toFloat())
        }
    }
    val p = remember { Animatable(0f) }
    LaunchedEffect(Unit) { p.animateTo(1f, tween(2400, easing = LinearEasing)) }
    BoxWithConstraints(Modifier.fillMaxSize()) {
        val wPx = constraints.maxWidth.toFloat()
        val hPx = constraints.maxHeight.toFloat()
        pieces.forEach { pc ->
            Text(pc.sym, fontSize = pc.size.sp, modifier = Modifier.graphicsLayer {
                val local = ((p.value - pc.delay) / (pc.dur / 2.4f)).coerceIn(0f, 1f)
                translationX = pc.x * wPx
                translationY = -40f + local * (hPx + 80f)
                rotationZ = local * pc.rot
                alpha = 1f - local
            })
        }
    }
}

private fun wrongHint(d: BoardModel.Diag): String? = when (d) {
    BoardModel.Diag.OK -> null
    BoardModel.Diag.WRONG_CHARS -> L10n.s("ui.wrong_chars")
    BoardModel.Diag.WRONG_SCENE -> L10n.s("ui.wrong_scene")
    BoardModel.Diag.INERT -> L10n.s("ui.wrong_inert")
    BoardModel.Diag.WRONG_ORDER -> L10n.s("ui.wrong_order")
    BoardModel.Diag.WRONG_SLOTS -> L10n.s("ui.wrong_slots")
    BoardModel.Diag.SCENE_UNUSED -> L10n.s("ui.wrong_unused")
}

@Composable
private fun TokenTray(model: BoardModel, scale: Float, drag: DragState) {
    Row(Modifier.fillMaxWidth().height((90 * scale).dp), horizontalArrangement = Arrangement.Center,
        verticalAlignment = Alignment.CenterVertically) {
        for (sid in model.level.scenes) SceneToken(model, sid, scale, drag)
        Box(Modifier.padding(horizontal = 6.dp).width(1.5.dp).height((56 * scale).dp).background(Palette.ink.copy(0.3f)))
        for (cid in model.roster) CharTokenT(model, cid, scale, drag)
    }
}

@Composable
private fun SceneToken(model: BoardModel, sid: String, scale: Float, drag: DragState) {
    val sel = model.selected == BoardModel.Sel.Scene(sid)
    Column(Modifier.padding(horizontal = (6 * scale).dp)
        .coachPulse(sid in model.coachHighlightScenes)
        .tokenDrag(drag, BoardModel.Sel.Scene(sid), "scene_$sid", false, model)
        .clickable { Audio.sfx("select"); model.selectItem(BoardModel.Sel.Scene(sid)) },
        horizontalAlignment = Alignment.CenterHorizontally) {
        val stPainter = artPainter("scene_$sid")
        Box(Modifier.size((66 * scale).dp, (46 * scale).dp).clip(RoundedCornerShape(7.dp)).background(Palette.panel)
            .border(if (sel) 3.dp else 2.dp, if (sel) Palette.gold else Palette.ink.copy(0.55f), RoundedCornerShape(7.dp))
            .coachRing(sid in model.coachHighlightScenes, 7.dp)) {
            if (stPainter != null) Image(stPainter, null, Modifier.fillMaxSize(), contentScale = ContentScale.Crop)
        }
        Text(model.sceneName(sid), color = Palette.inkSoft, fontSize = (9 * scale).sp, fontFamily = Fonts.rounded, maxLines = 1)
    }
}

@Composable
private fun CharTokenT(model: BoardModel, cid: String, scale: Float, drag: DragState) {
    val sel = model.selected == BoardModel.Sel.Char(cid)
    val badges = stateBadges(cid, model.world)
    Column(Modifier.padding(horizontal = (6 * scale).dp)
        .coachPulse(cid in model.coachHighlightChars)
        .tokenDrag(drag, BoardModel.Sel.Char(cid), "char_$cid", true, model)
        .clickable { Audio.sfx("select"); model.selectItem(BoardModel.Sel.Char(cid)) },
        horizontalAlignment = Alignment.CenterHorizontally) {
        Box(Modifier.size((58 * scale).dp, (54 * scale).dp)
            .then(if (sel) Modifier.clip(RoundedCornerShape(9.dp)).background(Palette.gold.copy(0.28f))
                .border(3.dp, Palette.gold, RoundedCornerShape(9.dp)) else Modifier)
            .coachRing(cid in model.coachHighlightChars, 9.dp),
            contentAlignment = Alignment.TopEnd) {
            val ctPainter = artPainter("char_$cid")
            if (ctPainter != null) Image(ctPainter, null, Modifier.fillMaxSize(), contentScale = ContentScale.Fit)
            if (badges.isNotEmpty()) Text(badges.joinToString(""), fontSize = (10 * scale).sp)
        }
        Text(model.charName(cid), color = Palette.inkSoft, fontSize = (9 * scale).sp, fontFamily = Fonts.rounded, maxLines = 1)
    }
}

@Composable
private fun FactPopup(level: LevelDef, onReplay: () -> Unit, onBack: () -> Unit, onClose: () -> Unit) {
    // Тап по фону возвращает на доску, а не уводит с уровня: карточку теперь зовут вручную,
    // и закрыть её должно значить «хочу ещё посмотреть на сцену».
    //
    // indication = null у обеих зон обязательно: с обычным ripple подложка во весь экран
    // вспыхивала на каждое касание, в том числе на каждый жест прокрутки текста — читалось
    // как мигание экрана.
    val dismiss = remember { MutableInteractionSource() }
    val swallow = remember { MutableInteractionSource() }
    Box(Modifier.fillMaxSize().background(Color.Black.copy(0.5f))
        .clickable(interactionSource = dismiss, indication = null) { onBack() },
        contentAlignment = Alignment.Center) {
        BookPage(Modifier.fillMaxWidth(0.94f).fillMaxHeight(0.94f).widthIn(max = 720.dp)
            // Карточка съедает касания: иначе прокрутка текста била по фоновому «закрыть».
            .clickable(interactionSource = swallow, indication = null) { }) {
            Box(Modifier.align(Alignment.TopEnd).padding(10.dp).size(32.dp).clip(CircleShape)
                .background(Palette.paper).border(1.5.dp, Palette.ink.copy(0.25f), CircleShape)
                .clickable { onBack() }, contentAlignment = Alignment.Center) {
                Icon(Icons.Filled.Close, null, tint = Palette.inkSoft, modifier = Modifier.size(15.dp))
            }
            Column(Modifier.fillMaxSize().padding(start = 22.dp, end = 22.dp, top = 18.dp, bottom = 14.dp),
                horizontalAlignment = Alignment.CenterHorizontally) {
                // Прокручивается только текст. Кнопки закреплены снизу: раньше они ехали
                // вместе с текстом, и «Дальше» пряталась за нижней кромкой — на телефоне
                // в ландшафте догадаться, что надо доскроллить, было невозможно.
                Column(Modifier.weight(1f).verticalScroll(rememberScrollState()),
                    horizontalAlignment = Alignment.CenterHorizontally) {
                    Pill(L10n.s("ui.solved"), Palette.success.copy(0.2f))
                    Spacer(Modifier.height(8.dp))
                    Text(level.title, color = Palette.ink, fontSize = 22.sp, fontWeight = FontWeight.Bold,
                        fontFamily = Fonts.serif, textAlign = TextAlign.Center)
                    level.factCard?.let { fc ->
                        Spacer(Modifier.height(8.dp))
                        Pill(accuracyLabel(fc.accuracy), Palette.gold.copy(0.25f))
                        Spacer(Modifier.height(8.dp))
                        Text(fc.text, color = Palette.ink, fontSize = 14.sp, fontFamily = Fonts.rounded)
                        Spacer(Modifier.height(8.dp))
                        Text(fc.source, color = Palette.inkSoft, fontSize = 11.sp, fontStyle = FontStyle.Italic,
                            fontFamily = Fonts.rounded)
                    }
                }
                Spacer(Modifier.height(10.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(12.dp), verticalAlignment = Alignment.CenterVertically) {
                    Box(Modifier.clip(RoundedCornerShape(30.dp)).background(Palette.paper)
                        .border(1.5.dp, Palette.maroon.copy(0.5f), RoundedCornerShape(30.dp))
                        .clickable { onReplay() }.padding(horizontal = 22.dp, vertical = 10.dp)) {
                        Text(L10n.s("ui.replay"), color = Palette.maroon, fontSize = 16.sp, fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
                    }
                    Box(Modifier.clip(RoundedCornerShape(30.dp)).background(Palette.maroon).clickable { onClose() }
                        .padding(horizontal = 30.dp, vertical = 10.dp)) {
                        Text(L10n.s("ui.next"), color = Palette.paper, fontSize = 16.sp, fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
                    }
                }
            }
        }
    }
}

private fun accuracyLabel(acc: String) = when (acc) {
    "fact" -> L10n.s("ui.acc_fact"); "simplification" -> L10n.s("ui.acc_simplification")
    "legend" -> L10n.s("ui.acc_legend"); else -> L10n.s("ui.acc_fact")
}

@Composable private fun Pill(text: String, bg: Color) {
    Box(Modifier.clip(RoundedCornerShape(20.dp)).background(bg).padding(horizontal = 12.dp, vertical = 5.dp)) {
        Text(text, color = Palette.ink, fontSize = 13.sp, fontWeight = FontWeight.Bold, fontFamily = Fonts.rounded)
    }
}

@Composable private fun IconMini(icon: androidx.compose.ui.graphics.vector.ImageVector, modifier: Modifier = Modifier, onClick: () -> Unit) {
    Box(modifier.size(36.dp).clip(CircleShape).background(Palette.paper)
        .border(1.5.dp, Palette.ink.copy(0.3f), CircleShape).clickable { onClick() }, contentAlignment = Alignment.Center) {
        Icon(icon, null, tint = Palette.ink.copy(0.7f), modifier = Modifier.size(17.dp))
    }
}

/** Подсказка к уровню — затемнение + книжная карточка (по кнопке ⓘ, как на iOS). */
/** Подсказка в стиле финального окна: пергамент-карточка с плашкой «Подсказка», заголовком и текстом. */
@Composable private fun HintPopup(title: String, text: String, onClose: () -> Unit) {
    // indication = null у обеих зон — та же история, что и в FactPopup: с обычным ripple
    // подложка во весь экран вспыхивала на каждый жест прокрутки текста, и это читалось
    // как мигание экрана. Карточка вдобавок съедает касания, иначе скролл длинной подсказки
    // попутно жмёт «закрыть» на фоне.
    val dismiss = remember { MutableInteractionSource() }
    val swallow = remember { MutableInteractionSource() }
    Box(Modifier.fillMaxSize().background(Color.Black.copy(0.5f))
        .clickable(interactionSource = dismiss, indication = null) { onClose() },
        contentAlignment = Alignment.Center) {
        BookPage(Modifier.widthIn(max = 520.dp).padding(20.dp)
            .clickable(interactionSource = swallow, indication = null) { }) {
            Column(Modifier.padding(22.dp).verticalScroll(rememberScrollState()),
                horizontalAlignment = Alignment.CenterHorizontally) {
                Pill(L10n.s("ui.hint"), Palette.gold.copy(0.25f))
                Spacer(Modifier.height(10.dp))
                Text(title, color = Palette.ink, fontSize = 22.sp, fontWeight = FontWeight.Bold,
                    fontFamily = Fonts.serif, textAlign = TextAlign.Center)
                if (text.isNotEmpty()) {
                    Spacer(Modifier.height(10.dp))
                    Text(text, color = Palette.ink, fontSize = 14.sp, fontFamily = Fonts.rounded, textAlign = TextAlign.Center)
                }
                Spacer(Modifier.height(16.dp))
                Box(Modifier.clip(RoundedCornerShape(30.dp)).background(Palette.maroon).clickable { onClose() }
                    .padding(horizontal = 30.dp, vertical = 11.dp)) {
                    Text(L10n.s("ui.ok"), color = Palette.paper, fontSize = 16.sp, fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
                }
            }
        }
    }
}

@Composable private fun BackRibbon(modifier: Modifier, onBack: () -> Unit) {
    Box(modifier.offset(x = 42.dp, y = (-4).dp).size(40.dp, 52.dp)
        .shadow(3.dp, RibbonShape).clip(RibbonShape).background(Palette.ribbon)
        .border(1.5.dp, Palette.ink.copy(alpha = 0.35f), RibbonShape)
        .clickable { onBack() }, contentAlignment = Alignment.Center) {
        Icon(Icons.Filled.KeyboardArrowLeft, null, tint = Color.White,
            modifier = Modifier.size(22.dp).offset(y = (-4).dp))
    }
}


/**
 * Пульсация всей карточки токена: больше — обычный — меньше, по кругу.
 *
 * Пульсировать кольцом внутри токена оказалось плохо: собственная тёмная рамка карточки
 * его перекрывает, и мигание читается «внутрь», а не как указание.
 */
@Composable
private fun Modifier.coachPulse(active: Boolean): Modifier {
    if (!active) return this
    val pulse = rememberInfiniteTransition(label = "coach")
    val s by pulse.animateFloat(
        initialValue = 1.12f, targetValue = 0.94f,
        animationSpec = infiniteRepeatable(tween(750), RepeatMode.Reverse), label = "pulse")
    return this.scale(s)
}

/** Статичная золотая обводка на самой картинке — чтобы было видно, какой именно токен зовут. */
@Composable
private fun Modifier.coachRing(active: Boolean, radius: androidx.compose.ui.unit.Dp): Modifier =
    if (active) this.border(3.dp, Palette.gold, RoundedCornerShape(radius)) else this

/** Реплика гида: пергаментное окошко над рядом токенов. Не перехватывает касания —
 *  игрок должен продолжать играть, а не закрывать подсказки. */
@Composable
private fun CoachBubble(levelId: String, step: CoachStep, modifier: Modifier = Modifier) {
    Row(
        modifier                       // позицию задаёт вызывающий: внутренний отступ складывался
            .widthIn(max = 560.dp)     // с внешним и выбрасывал реплику под заголовок
            .clip(RoundedCornerShape(12.dp))
            .background(Palette.paper)
            .border(2.dp, Palette.gold, RoundedCornerShape(12.dp))
            .padding(horizontal = 14.dp, vertical = 9.dp),
        verticalAlignment = Alignment.Top) {
        // Кегль тот же, что у текста: более крупная стрелка садилась на свою базовую линию
        // ниже первой строки и выглядела съехавшей вниз.
        Text("→", color = Palette.maroon, fontSize = 13.sp, fontFamily = Fonts.rounded,
             modifier = Modifier.padding(end = 8.dp).alignByBaseline())
        Text(L10n.s("level.$levelId.coach.${step.text}"),
             color = Palette.ink, fontSize = 13.sp, fontFamily = Fonts.rounded,
             modifier = Modifier.alignByBaseline())
    }
}
