package com.decima.historyteller

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
import teller.engine.*
import kotlin.math.max
import kotlin.math.min

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
    private var prevEvents: Set<String> = emptySet()
    init { prevEvents = reactions() }

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

    /** Активные события мира (для звуков-реакций) — пробинг по ростеру, без доступа к внутренностям World. */
    private fun reactions(): Set<String> {
        val w = result.world
        val ev = HashSet<String>()
        for (c in level.characters) {
            if (w.hasFlag(c, "dead")) ev.add("kill:$c")
            if (w.hasFlag(c, "crowned")) ev.add("crown:$c")
            if (w.hasFlag(c, "plotting")) ev.add("conspire:$c")
        }
        for (a in level.characters) for (b in level.characters) if (a != b) {
            if (w.hasRelation("loves", a, b)) ev.add("love:$a:$b")
            if (w.hasRelation("ally_of", a, b)) ev.add("ally:$a:$b")
        }
        return ev
    }

    private fun recompute() {
        result = Engine.run(panels, db, level.createInitialWorld())
        val now = reactions()
        (now - prevEvents).map { it.substringBefore(':') }.distinct().forEach { onSfx?.invoke(it) }
        prevEvents = now
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

    enum class Diag { OK, WRONG_SCENE, WRONG_CHARS, INERT }
    fun diagnose(i: Int): Diag {
        if (isSolved || !isBoardComplete) return Diag.OK
        val p = panels[i]; val sid = p.sceneId ?: return Diag.OK
        val sc = db.scenes[sid] ?: return Diag.OK
        if (p.characters.size != sc.slots) return Diag.OK
        val sol = level.solution?.getOrNull(i) ?: return Diag.OK
        val same = sol.characters.toSet() == p.characters.toSet()
        return if (sol.sceneId == sid) (if (same) Diag.OK else Diag.WRONG_CHARS)
        else (if (same) Diag.WRONG_SCENE else Diag.INERT)
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
    LaunchedEffect(levelId) { Audio.startMusic(level.music ?: "theme") }
    LaunchedEffect(model.isSolved) { if (model.isSolved) { Audio.sfx("win"); onSolved(); showFact = true } }
    val exit = { Audio.sfx("select"); Audio.startMusic("theme"); onExit() }

    Box(Modifier.fillMaxSize().padding(14.dp)) {
        BookPage(Modifier.fillMaxSize()) {
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
                            for (i in model.panels.indices) PanelCell(model, i, cellW, cellH)
                        }
                    }
                    TokenTray(model, trayScale)
                }
            }
            BackRibbon(Modifier.align(Alignment.TopStart).statusBarsPadding()) { exit() }
        }
        if (showHint) HintPopup(level.goalHint ?: "") { showHint = false }
        if (showFact) FactPopup(level) { showFact = false; exit() }
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
private fun PanelCell(model: BoardModel, i: Int, cellW: androidx.compose.ui.unit.Dp, cellH: androidx.compose.ui.unit.Dp) {
    val panel = model.panels[i]
    val diag = model.diagnose(i)
    val highlighted = model.selected != null
    val border = when {
        highlighted -> Palette.gold
        diag != BoardModel.Diag.OK -> Palette.maroon
        else -> Palette.ink.copy(0.55f)
    }
    Box(
        Modifier.size(cellW, cellH).clip(RoundedCornerShape(10.dp))
            .background(Palette.panel)
            .border(if (highlighted || diag != BoardModel.Diag.OK) 3.dp else 2.dp, border, RoundedCornerShape(10.dp))
            .clickable(enabled = model.selected != null) { model.applySelection(i) }
    ) {
        val sid = panel.sceneId
        if (sid != null) {
            val id = drawableId("scene_$sid")
            if (id != 0) Image(painterResource(id), null, Modifier.fillMaxSize(), contentScale = ContentScale.Crop)
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
                        val cid = panel.characters[slot]
                        val snap = model.snapshot(i)
                        val dead = snap.hasFlag(cid, "dead")
                        val micro = model.microState(cid, i)
                        Box(contentAlignment = Alignment.TopCenter) {
                            val cd = drawableId("char_$cid")
                            if (cd != 0) Image(painterResource(cd), null,
                                Modifier.height(spriteH).graphicsLayer {
                                    if (dead) { rotationZ = 80f; translationY = spriteH.toPx() * 0.24f }
                                }.clickable { if (model.selected != null) model.applySelection(i) else model.removeChar(i, cid) },
                                contentScale = ContentScale.Fit, colorFilter = if (dead) grayscale else null)
                            if (micro != null && !dead) Text(micro, fontSize = 20.sp, modifier = Modifier.offset(y = (-6).dp))
                        }
                    }
                }
            }
            // подсказка об ошибке
            wrongHint(diag)?.let { hint ->
                Box(Modifier.align(Alignment.BottomCenter).padding(bottom = 8.dp).clip(RoundedCornerShape(20.dp))
                    .background(Palette.maroon.copy(0.94f)).padding(horizontal = 10.dp, vertical = 5.dp)) {
                    Text(hint, color = Color.White, fontSize = 10.sp, fontFamily = Fonts.rounded)
                }
            }
        } else {
            Text(if (highlighted) L10n.s("ui.tap") else L10n.s("ui.scene"),
                color = Palette.inkSoft.copy(0.7f), fontSize = 11.sp, fontFamily = Fonts.rounded,
                modifier = Modifier.align(Alignment.Center))
        }
    }
}

private fun wrongHint(d: BoardModel.Diag): String? = when (d) {
    BoardModel.Diag.OK -> null
    BoardModel.Diag.WRONG_CHARS -> L10n.s("ui.wrong_chars")
    BoardModel.Diag.WRONG_SCENE -> L10n.s("ui.wrong_scene")
    BoardModel.Diag.INERT -> L10n.s("ui.wrong_inert")
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
private fun FactPopup(level: LevelDef, onClose: () -> Unit) {
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
                Box(Modifier.clip(RoundedCornerShape(30.dp)).background(Palette.maroon).clickable { onClose() }
                    .padding(horizontal = 30.dp, vertical = 11.dp)) {
                    Text(L10n.s("ui.next"), color = Palette.paper, fontSize = 16.sp, fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
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
@Composable private fun HintPopup(hint: String, onClose: () -> Unit) {
    Box(Modifier.fillMaxSize().background(Color.Black.copy(0.5f)).clickable { onClose() }, contentAlignment = Alignment.Center) {
        BookPage(Modifier.widthIn(max = 460.dp).padding(20.dp)) {
            Column(Modifier.padding(26.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                Text(hint, color = Palette.ink, fontSize = 16.sp, fontFamily = Fonts.rounded, textAlign = TextAlign.Center)
                Spacer(Modifier.height(18.dp))
                Box(Modifier.clip(RoundedCornerShape(28.dp)).background(Palette.maroon).clickable { onClose() }
                    .padding(horizontal = 40.dp, vertical = 10.dp)) {
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
