package com.decima.historyteller

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
import androidx.compose.material.icons.automirrored.filled.ArrowBack
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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ColorFilter
import androidx.compose.ui.graphics.ColorMatrix
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.layout.ContentScale
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
        flagTarget(setOf("at_war"))?.let { return mk(Kind.MARCH, b[it], null, "") }
        flagTarget(setOf("conqueror"))?.let { return mk(Kind.CONQUER, b[it], null, "⚔️") }
        flagTarget(setOf("crowned", "emperor", "empress", "reigns", "supreme_head", "first_consul"))
            ?.let { return mk(Kind.CROWN, b[it], null, "👑") }
        relationPair(setOf("loves"))?.let { (f, t) -> return mk(Kind.LOVE, b[f], b[t], "❤️") }
        relationPair(setOf("ally_of"))?.let { (f, t) -> return mk(Kind.ALLY, b[f], b[t], "🤝") }
        flagTarget(setOf("backed"))?.let { return mk(Kind.ALLY, b[it], other(it), "🛡") }
        flagTarget(setOf("honored", "flaunting", "triumphant", "rome_restored", "settled", "hero", "absolute", "supreme"))
            ?.let { return mk(Kind.TRIUMPH, b[it], null, "🎉") }
        flagTarget(setOf("exiled", "cast_off", "widowed", "grieving"))?.let { return mk(Kind.DOWNFALL, b[it], null, "💔") }
        flagTarget(setOf("plotting"))?.let { return mk(Kind.CONSPIRE, b[it], null, "🗡") }
        flagTarget(setOf("has_heir"))?.let { return mk(Kind.BIRTH, null, null, "👶") }
        return mk(Kind.SPARK, null, null, "✨")
    }

    private fun sfxFor(kind: Kind): String = when (kind) {
        Kind.KILL, Kind.BATTLE, Kind.CONQUER -> "kill"
        Kind.CONDEMN, Kind.CONSPIRE -> "conspire"
        Kind.CROWN, Kind.TRIUMPH, Kind.BIRTH, Kind.MARCH -> "crown"
        Kind.LOVE -> "love"
        Kind.ALLY -> "ally"
        Kind.DOWNFALL -> "error"
        Kind.SPARK -> "select"
    }

    private fun recompute() {
        result = Engine.run(panels, db, level.createInitialWorld())
        val fresh = result.events.filter { eventKey(it) !in seenEventKeys }
        lastBeats = fresh.map(::beat)
        seenEventKeys = result.events.map(::eventKey).toSet()
        lastBeats.map { it.kind }.distinct().forEach { onSfx?.invoke(sfxFor(it)) }
        changeToken++
    }
    private fun update(i: Int, transform: (Panel) -> Panel) {
        panels = panels.toMutableList().also { it[i] = transform(it[i]) }; recompute()
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
    fun applySelection(i: Int) {
        when (val s = selected) {
            is Sel.Scene -> setScene(i, s.id)
            is Sel.Char -> place(i, s.id)
            null -> {}
        }
        selected = null
    }

    enum class Diag { OK, WRONG_SCENE, WRONG_CHARS, INERT, WRONG_ORDER }
    fun diagnose(i: Int): Diag = computeDiagnoses().getOrElse(i) { Diag.OK }

    /** Диагноз ВСЕХ панелей разом и БЕЗ привязки к позиции: панель сверяется с эталоном как с
     *  мультимножеством (та же сцена + тот же состав → OK, где бы она ни стояла). Не «краснеем» на
     *  панели, которая сама по себе верна: та сцена/не те лица → WRONG_CHARS; те лица/не та сцена →
     *  WRONG_SCENE; мимо → INERT. Если ВСЕ панели совпали, но доска не решена — беда лишь в порядке
     *  → WRONG_ORDER. (Зеркало iOS LevelBoardModel.computeDiagnoses.) */
    private fun computeDiagnoses(): List<Diag> {
        val n = panels.size
        if (isSolved || !isBoardComplete) return List(n) { Diag.OK }
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
        // Все заполненные панели совпали по содержимому, но доска не решена → дело только в порядке.
        if (pending.isEmpty()) {
            for (i in 0 until n) if (filled(i) != null) diag[i] = Diag.WRONG_ORDER
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
        return diag
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

@Composable
fun BoardScreen(levelId: String, onSolved: () -> Unit, onExit: () -> Unit) {
    val level = GameContent.level(levelId) ?: return
    val model = remember(levelId) { BoardModel(level, GameContent.db) }
    model.onSfx = { Audio.sfx(it) }
    var showFact by remember { mutableStateOf(false) }
    var showHint by remember { mutableStateOf(false) }
    var celebrate by remember(levelId) { mutableStateOf(false) }
    val boardShake = remember(levelId) { Animatable(0f) }
    LaunchedEffect(levelId) { Audio.startMusic(level.music ?: "theme") }
    LaunchedEffect(model.isSolved) {
        if (model.isSolved) {
            Audio.sfx("win"); onSolved(); celebrate = true
            delay(2400); showFact = true
            delay(500); celebrate = false
        }
    }
    // неверный ход: доска заполнена, но цель не достигнута — тряска (+ звук, если панели «мертвы»)
    LaunchedEffect(model.changeToken) {
        if (!model.isSolved && model.isBoardComplete) {
            if (model.lastBeats.isEmpty()) Audio.sfx("error")
            boardShake.snapTo(0f); boardShake.animateTo(1f, tween(450, easing = LinearEasing))
        }
    }
    val exit = { Audio.sfx("select"); Audio.startMusic("theme"); onExit() }
    val shakeDx = (sin(boardShake.value * PI * 3) * 9.0 * (1f - boardShake.value)).toFloat()

    Box(Modifier.fillMaxSize().padding(14.dp)) {
        BookPage(Modifier.fillMaxSize().graphicsLayer { translationX = shakeDx.dp.toPx() }) {
            BoxWithConstraints(Modifier.fillMaxSize()) {
                val trayScale = min(1.6f, max(1f, maxWidth.value / 720f))
                Column(Modifier.fillMaxSize().padding(horizontal = 20.dp, vertical = 12.dp).statusBarsPadding()) {
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
                            Text(level.goalText ?: "", color = Palette.ink, fontSize = 18.sp, fontWeight = FontWeight.Bold,
                                fontFamily = Fonts.serif, textAlign = TextAlign.Center, maxLines = 2)
                        }
                        Row(Modifier.align(Alignment.CenterEnd), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            IconMini(Icons.Filled.Info) { showHint = true }
                            IconMini(Icons.Filled.Refresh) { model.reset() }
                        }
                    }
                    // panels
                    BoxWithConstraints(Modifier.fillMaxWidth().weight(1f)) {
                        val n = max(1, model.panels.size)
                        val gap = 14.dp
                        val cellH = min(maxHeight.value, 430f).dp
                        val cellW = min(((maxWidth - gap * (n - 1)).value / n), cellH.value * 1.2f).dp
                        Row(Modifier.fillMaxSize(), horizontalArrangement = Arrangement.spacedBy(gap, Alignment.CenterHorizontally),
                            verticalAlignment = Alignment.CenterVertically) {
                            for (i in model.panels.indices) {
                                val beats = model.lastBeats.filter { it.panelIndex == i }
                                PanelCell(model, i, cellW, cellH, beats, model.changeToken)
                            }
                        }
                    }
                    TokenTray(model, trayScale)
                }
            }
            BackRibbon(Modifier.align(Alignment.TopStart).statusBarsPadding()) { exit() }
        }
        if (celebrate) ConfettiOverlay()
        if (showHint) HintPopup(level.title, listOfNotNull(level.initialText, level.goalHint).joinToString("\n\n")) { showHint = false }
        if (showFact) FactPopup(level, onReplay = { Audio.sfx("select"); showFact = false; model.reset() }) { showFact = false; exit() }
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
                     beats: List<BoardModel.Beat>, changeToken: Int) {
    val panel = model.panels[i]
    val diag = model.diagnose(i)
    val highlighted = model.selected != null
    val isOrderHint = diag == BoardModel.Diag.WRONG_ORDER
    val border = when {
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
            .clip(RoundedCornerShape(10.dp))
            .background(Palette.panel)
            .border(if (highlighted || diag != BoardModel.Diag.OK) 3.dp else 2.dp, border, RoundedCornerShape(10.dp))
            .clickable(enabled = model.selected != null) { model.applySelection(i) }
    ) {
        val sid = panel.sceneId
        if (sid != null) {
            // сцена появляется с лёгким наплывом
            val sceneAppear = remember(sid) { Animatable(0f) }
            LaunchedEffect(sid) { sceneAppear.animateTo(1f, tween(280, easing = FastOutSlowInEasing)) }
            val id = drawableId("scene_$sid")
            if (id != 0) Image(painterResource(id), null,
                Modifier.fillMaxSize().graphicsLayer {
                    alpha = sceneAppear.value
                    val s = 0.9f + 0.1f * sceneAppear.value; scaleX = s; scaleY = s
                }, contentScale = ContentScale.Crop)
            model.sceneAction(sid)?.let { action ->
                Box(Modifier.padding(7.dp).clip(RoundedCornerShape(10.dp)).background(Palette.paper.copy(0.92f))
                    .padding(horizontal = 8.dp, vertical = 3.dp)) {
                    Text(action, color = Palette.ink, fontSize = 11.sp, fontWeight = FontWeight.Bold, fontFamily = Fonts.rounded)
                }
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
            Text(if (highlighted) L10n.s("ui.tap") else L10n.s("ui.scene"),
                color = Palette.inkSoft.copy(0.7f), fontSize = 11.sp, fontFamily = Fonts.rounded,
                modifier = Modifier.align(Alignment.Center))
        }
    }
}

/** Спрайт персонажа со всей «живостью»: появление-пружина, падение при гибели, дрожь заговорщика,
 *  выпад активной стороны к цели, реакция пострадавшего/триумфатора, опускающаяся корона. */
@Composable
private fun CharSprite(model: BoardModel, i: Int, cid: String, slot: Int, spriteH: androidx.compose.ui.unit.Dp,
                       beats: List<BoardModel.Beat>) {
    val snap = model.snapshot(i)
    val dead = snap.hasFlag(cid, "dead")
    // слой 3: отдельная поза «повержен». Есть → показываем её без ч/б и заваливания.
    val deadId = if (dead) drawableId("char_${cid}_dead") else 0
    val useDeadPose = dead && deadId != 0
    val topple = dead && !useDeadPose   // старый фолбэк
    // разгромлен, но жив → поза «повержен-живой»
    val defeated = !dead && listOf("fugitive", "defeated", "exiled", "cast_off", "widowed", "disgraced", "grieving")
        .any { snap.hasFlag(cid, it) }
    val defeatedId = if (defeated) drawableId("char_${cid}_defeated") else 0
    val useDefeatedPose = defeated && defeatedId != 0
    // победные состояния → поза «триумф» (если не разгромлен)
    val triumphant = !dead && !defeated && listOf("crowned", "reigns", "emperor", "empress", "victor", "conqueror",
        "triumphant", "honored", "first_consul", "supreme_head", "absolute", "at_war").any { snap.hasFlag(cid, it) }
    val triumphId = if (triumphant) drawableId("char_${cid}_triumph") else 0
    val useTriumphPose = triumphant && triumphId != 0
    val plotting = !dead && snap.hasFlag(cid, "plotting")
    val plotId = if (plotting && !defeated) drawableId("char_${cid}_plot") else 0
    val usePlotPose = plotting && !defeated && plotId != 0
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
    // падение при гибели (только если нет позы «повержен»)
    val fall by animateFloatAsState(if (topple) 80f else 0f, spring(dampingRatio = 0.55f), label = "fall")
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
        val cd = if (useDeadPose) deadId else if (useDefeatedPose) defeatedId
            else if (usePlotPose) plotId else if (useTriumphPose) triumphId else drawableId("char_$cid")
        if (cd != 0) Image(painterResource(cd), null,
            Modifier.height(spriteH).graphicsLayer {
                transformOrigin = androidx.compose.ui.graphics.TransformOrigin(0.5f, 1f)
                val s = appear.value * moScale; scaleX = s; scaleY = s
                rotationZ = fall + tremble + moRot
                translationY = (if (topple) spriteH.toPx() * 0.24f else 0f) + moDy.dp.toPx() +
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
    val id = drawableId(prop)
    if (id != 0) Image(painterResource(id), null, Modifier.size(size).graphicsLayer {
        scaleX = scale.value; scaleY = scale.value; translationY = ty.value.dp.toPx(); this.alpha = alpha.value
    }, contentScale = ContentScale.Fit)
}

/** Нож гильотины падает сверху вниз по центру панели. */
@Composable
private fun GuillotineBlade(panelH: androidx.compose.ui.unit.Dp) {
    val drop = remember { Animatable(0f) }
    LaunchedEffect(Unit) { drop.animateTo(1f, tween(260, easing = FastOutSlowInEasing)) }
    val id = drawableId("prop_blade")
    if (id != 0) Image(painterResource(id), null, Modifier.height(panelH * 0.52f).graphicsLayer {
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
    val id = drawableId("prop_crown")
    if (id != 0) Image(painterResource(id), null, Modifier.size(34.dp).graphicsLayer {
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
}

@Composable
private fun TokenTray(model: BoardModel, scale: Float) {
    Row(Modifier.fillMaxWidth().height((90 * scale).dp), horizontalArrangement = Arrangement.Center,
        verticalAlignment = Alignment.CenterVertically) {
        for (sid in model.level.scenes) SceneToken(model, sid, scale)
        Box(Modifier.padding(horizontal = 6.dp).width(1.5.dp).height((56 * scale).dp).background(Palette.ink.copy(0.3f)))
        for (cid in model.roster) CharTokenT(model, cid, scale)
    }
}

@Composable
private fun SceneToken(model: BoardModel, sid: String, scale: Float) {
    val sel = model.selected == BoardModel.Sel.Scene(sid)
    Column(Modifier.padding(horizontal = (6 * scale).dp).clickable { Audio.sfx("select"); model.selectItem(BoardModel.Sel.Scene(sid)) },
        horizontalAlignment = Alignment.CenterHorizontally) {
        val id = drawableId("scene_$sid")
        Box(Modifier.size((66 * scale).dp, (46 * scale).dp).clip(RoundedCornerShape(7.dp)).background(Palette.panel)
            .border(if (sel) 3.dp else 2.dp, if (sel) Palette.gold else Palette.ink.copy(0.55f), RoundedCornerShape(7.dp))) {
            if (id != 0) Image(painterResource(id), null, Modifier.fillMaxSize(), contentScale = ContentScale.Crop)
        }
        Text(model.sceneName(sid), color = Palette.inkSoft, fontSize = (9 * scale).sp, fontFamily = Fonts.rounded, maxLines = 1)
    }
}

@Composable
private fun CharTokenT(model: BoardModel, cid: String, scale: Float) {
    val sel = model.selected == BoardModel.Sel.Char(cid)
    val badges = stateBadges(cid, model.world)
    Column(Modifier.padding(horizontal = (6 * scale).dp).clickable { Audio.sfx("select"); model.selectItem(BoardModel.Sel.Char(cid)) },
        horizontalAlignment = Alignment.CenterHorizontally) {
        Box(Modifier.size((58 * scale).dp, (54 * scale).dp)
            .then(if (sel) Modifier.clip(RoundedCornerShape(9.dp)).background(Palette.gold.copy(0.28f))
                .border(3.dp, Palette.gold, RoundedCornerShape(9.dp)) else Modifier),
            contentAlignment = Alignment.TopEnd) {
            val id = drawableId("char_$cid")
            if (id != 0) Image(painterResource(id), null, Modifier.fillMaxSize(), contentScale = ContentScale.Fit)
            if (badges.isNotEmpty()) Text(badges.joinToString(""), fontSize = (10 * scale).sp)
        }
        Text(model.charName(cid), color = Palette.inkSoft, fontSize = (9 * scale).sp, fontFamily = Fonts.rounded, maxLines = 1)
    }
}

@Composable
private fun FactPopup(level: LevelDef, onReplay: () -> Unit, onClose: () -> Unit) {
    Box(Modifier.fillMaxSize().background(Color.Black.copy(0.5f)).clickable { onClose() }, contentAlignment = Alignment.Center) {
        BookPage(Modifier.widthIn(max = 520.dp).padding(20.dp)) {
            Column(Modifier.padding(22.dp).verticalScroll(rememberScrollState()),
                horizontalAlignment = Alignment.CenterHorizontally) {
                Pill(L10n.s("ui.solved"), Palette.success.copy(0.2f))
                Spacer(Modifier.height(10.dp))
                Text(level.title, color = Palette.ink, fontSize = 22.sp, fontWeight = FontWeight.Bold,
                    fontFamily = Fonts.serif, textAlign = TextAlign.Center)
                level.factCard?.let { fc ->
                    Spacer(Modifier.height(10.dp))
                    Pill(accuracyLabel(fc.accuracy), Palette.gold.copy(0.25f))
                    Spacer(Modifier.height(10.dp))
                    Text(fc.text, color = Palette.ink, fontSize = 14.sp, fontFamily = Fonts.rounded)
                    Spacer(Modifier.height(8.dp))
                    Text(fc.source, color = Palette.inkSoft, fontSize = 11.sp, fontStyle = FontStyle.Italic, fontFamily = Fonts.rounded)
                }
                Spacer(Modifier.height(16.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(12.dp), verticalAlignment = Alignment.CenterVertically) {
                    // «Ещё раз» — сыграть уровень заново
                    Box(Modifier.clip(RoundedCornerShape(30.dp)).background(Palette.paper)
                        .border(1.5.dp, Palette.maroon.copy(0.5f), RoundedCornerShape(30.dp))
                        .clickable { onReplay() }.padding(horizontal = 22.dp, vertical = 11.dp)) {
                        Text(L10n.s("ui.replay"), color = Palette.maroon, fontSize = 16.sp, fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
                    }
                    Box(Modifier.clip(RoundedCornerShape(30.dp)).background(Palette.maroon).clickable { onClose() }
                        .padding(horizontal = 30.dp, vertical = 11.dp)) {
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
    Box(Modifier.fillMaxSize().background(Color.Black.copy(0.5f)).clickable { onClose() }, contentAlignment = Alignment.Center) {
        BookPage(Modifier.widthIn(max = 520.dp).padding(20.dp)) {
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
    Box(modifier.offset(x = 42.dp, y = 0.dp).size(40.dp, 52.dp)
        .clip(RoundedCornerShape(bottomStart = 8.dp, bottomEnd = 8.dp)).background(Palette.ribbon)
        .clickable { onBack() }, contentAlignment = Alignment.Center) {
        Icon(Icons.AutoMirrored.Filled.ArrowBack, null, tint = Color.White, modifier = Modifier.size(18.dp))
    }
}
