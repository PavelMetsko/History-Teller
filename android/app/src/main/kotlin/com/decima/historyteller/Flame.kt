package com.decima.historyteller

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.graphics.drawscope.scale
import androidx.compose.ui.graphics.drawscope.translate
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlin.math.cos
import kotlin.math.sin

// ---- «Путь огня» (docs/f2p-patch-4.0.md §9) ----

object Flame {
    /** Цвета стадии: низ → верх пламени (как FlameBadge.colors на iOS). */
    fun colors(tier: Int): Pair<Color, Color> = when (tier) {
        0 -> Color.Gray.copy(0.5f) to Color.Gray.copy(0.3f)
        1 -> Color(1f, 0.62f, 0.20f) to Color(1f, 0.86f, 0.40f)
        2 -> Color(1f, 0.50f, 0.10f) to Color(1f, 0.80f, 0.30f)
        3 -> Color(0.95f, 0.30f, 0.08f) to Color(1f, 0.70f, 0.20f)
        4 -> Color(0.80f, 0.10f, 0.10f) to Color(1f, 0.55f, 0.15f)
        5 -> Color(0.10f, 0.40f, 0.95f) to Color(0.45f, 0.85f, 1f)
        else -> Color(0.55f, 0.15f, 0.85f) to Color(1f, 0.75f, 0.95f)
    }
}

/** Контур язычка пламени в квадрате w×w: острый верх, круглое основание, «хвостик» сбоку. */
private fun flamePath(w: Float): Path = Path().apply {
    moveTo(w * 0.50f, 0f)
    cubicTo(w * 0.62f, w * 0.20f, w * 0.90f, w * 0.38f, w * 0.88f, w * 0.66f)
    cubicTo(w * 0.86f, w * 0.88f, w * 0.68f, w, w * 0.50f, w)
    cubicTo(w * 0.30f, w, w * 0.12f, w * 0.88f, w * 0.12f, w * 0.66f)
    cubicTo(w * 0.12f, w * 0.48f, w * 0.24f, w * 0.38f, w * 0.30f, w * 0.26f)
    cubicTo(w * 0.34f, w * 0.38f, w * 0.38f, w * 0.44f, w * 0.44f, w * 0.46f)
    cubicTo(w * 0.40f, w * 0.30f, w * 0.44f, w * 0.14f, w * 0.50f, 0f)
    close()
}

/**
 * Пламя серии: растёт (70–100%) и меняет цвет со стадией (0 — погасло, 1 Искра … 6 Вечный огонь).
 * Живое — подрагивает; со Свечи — белая сердцевина, с Костра — ореол, с Маяка — искры по кругу.
 */
@Composable
fun FlameBadge(tier: Int, size: Dp = 28.dp, animated: Boolean = true) {
    val live = animated && tier > 0
    val tr = rememberInfiniteTransition(label = "flame")
    val flick by tr.animateFloat(0f, 1f, infiniteRepeatable(tween(550), RepeatMode.Reverse), label = "f")
    val spin by tr.animateFloat(0f, 360f, infiniteRepeatable(tween(8000, easing = LinearEasing)), label = "s")
    val f = if (live) flick else 0.5f
    val (bottom, top) = Flame.colors(tier)
    val scale = 0.7f + 0.3f * tier.coerceAtMost(6) / 6f
    Canvas(Modifier.size(size)) {
        val s = this.size.minDimension
        val c = Offset(s / 2, s / 2)
        if (tier >= 4) {
            val r = s * 0.7f * (0.94f + 0.14f * f)
            drawCircle(Brush.radialGradient(listOf(top.copy(0.55f), Color.Transparent), c, r), r, c)
        }
        val w = s * scale
        val left = (s - w) / 2
        val topY = s - w - (s - w) * 0.25f
        // Подрагивание — от основания.
        drawFlame(w, left, topY, 0.97f + 0.06f * (1 - f), 0.96f + 0.09f * f,
            Brush.verticalGradient(listOf(top, bottom), topY, topY + w))
        if (tier >= 2) {
            val iw = w * 0.42f
            drawFlame(iw, left + (w - iw) / 2, topY + w - iw, 1f, 0.9f + 0.2f * f,
                Brush.verticalGradient(listOf(Color.White.copy(0.85f), Color.White.copy(0.6f)), topY + w - iw, topY + w))
        }
        if (tier >= 5) {
            val sr = s * 0.08f
            for (i in 0 until 6) {
                val a = Math.toRadians((i * 60 + (if (live) spin else 0f)).toDouble())
                val p = Offset(c.x + (s * 0.62f * sin(a)).toFloat(), c.y - (s * 0.62f * cos(a)).toFloat())
                drawSparkle(p, sr, top)
            }
        }
    }
}

private fun DrawScope.drawFlame(w: Float, left: Float, topY: Float, sx: Float, sy: Float, brush: Brush) {
    translate(left, topY) {
        scale(sx, sy, pivot = Offset(w / 2, w)) { drawPath(flamePath(w), brush) }
    }
}

private fun DrawScope.drawSparkle(p: Offset, r: Float, color: Color) {
    val path = Path().apply {
        moveTo(p.x, p.y - r); quadraticBezierTo(p.x, p.y, p.x + r, p.y)
        quadraticBezierTo(p.x, p.y, p.x, p.y + r); quadraticBezierTo(p.x, p.y, p.x - r, p.y)
        quadraticBezierTo(p.x, p.y, p.x, p.y - r); close()
    }
    drawPath(path, color)
}

/** Станции дороги: начала стадий пламени и вехи с подсказками. */
private val roadStations: List<Int> =
    (Meta.flameTiers.map { it.first } + Meta.milestones.map { it.first }).toSortedSet().toList()

/**
 * Экран «Путь огня»: слева нынешнее пламя, стадия, серия, бонус, сколько до следующей стадии, рекорд,
 * статус дня или «Вернуть серию»; справа — горизонтальная дорога станций.
 */
@Composable
fun StreakRoadScreen(onRestore: () -> Unit, onBack: () -> Unit) {
    val streak = Meta.currentStreak
    val tier = Meta.flameTier(streak)
    Box(Modifier.fillMaxSize().padding(16.dp)) {
        BookPage(Modifier.fillMaxSize()) {
            Row(Modifier.fillMaxSize().padding(start = 26.dp, end = 22.dp, top = 16.dp, bottom = 14.dp),
                horizontalArrangement = Arrangement.spacedBy(18.dp)) {
                StreakHeader(streak, tier, onRestore, Modifier.width(210.dp).fillMaxHeight())
                StreakRoad(streak, tier, Modifier.weight(1f).fillMaxHeight())
            }
            BackButton(Modifier.align(Alignment.TopStart), onBack)
        }
    }
}

@Composable
private fun StreakHeader(streak: Int, tier: Int, onRestore: () -> Unit, modifier: Modifier) {
    Column(modifier, horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(5.dp)) {
        Text(L10n.s("ui.flame_road"), color = Palette.ink, fontSize = 20.sp, fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
        Box(Modifier.padding(vertical = 2.dp)) { FlameBadge(tier, 86.dp) }
        Text(if (tier > 0) L10n.s("ui.flame.$tier") else "—", color = Palette.ink, fontSize = 18.sp,
            fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
        Text(L10n.s("ui.streak_days", streak), color = Palette.ink, fontSize = 15.sp, fontFamily = Fonts.rounded)
        val bonus = Meta.flameBonus(streak)
        if (bonus > 0) {
            Box(Modifier.clip(RoundedCornerShape(50)).background(Flame.colors(tier).first)
                .padding(horizontal = 10.dp, vertical = 4.dp)) {
                Text(L10n.s("ui.flame_bonus", bonus), color = Palette.paper, fontSize = 12.sp,
                    fontWeight = FontWeight.Bold, fontFamily = Fonts.rounded)
            }
        }
        if (tier < Meta.flameTiers.size) {
            val days = Meta.flameTiers[tier].first - streak
            Text(L10n.s("ui.flame_next", L10n.s("ui.flame.${tier + 1}"), days), color = Palette.inkSoft,
                fontSize = 11.sp, fontFamily = Fonts.rounded, textAlign = TextAlign.Center)
        }
        Text(L10n.s("ui.flame_best", maxOf(Meta.bestStreak, streak)), color = Palette.inkSoft, fontSize = 11.sp,
            fontFamily = Fonts.rounded)
        Spacer(Modifier.weight(1f))
        val broken = Meta.brokenStreak
        if (broken != null) {
            val premium = Billing.subscribed
            Box(Modifier.clip(RoundedCornerShape(50)).background(Color(0xFFFF9500)).clickable { onRestore() }
                .padding(horizontal = 14.dp, vertical = 7.dp)) {
                Text((if (premium) "" else "▶ ") + L10n.s("ui.streak_restore"), color = Palette.paper, fontSize = 13.sp,
                    fontWeight = FontWeight.Bold, fontFamily = Fonts.rounded)
            }
            Text(L10n.s("ui.streak_lost", broken), color = Palette.inkSoft, fontSize = 10.sp, fontFamily = Fonts.rounded)
        } else {
            val done = Meta.solvedToday
            Text((if (done) "✓ " else "! ") + L10n.s(if (done) "ui.flame_today" else "ui.flame_todo"),
                color = if (done) Palette.success else Palette.maroon, fontSize = 11.sp, fontWeight = FontWeight.Bold,
                fontFamily = Fonts.rounded, textAlign = TextAlign.Center)
        }
    }
}

@Composable
private fun StreakRoad(streak: Int, tier: Int, modifier: Modifier) {
    val scroll = rememberScrollState()
    val density = LocalDensity.current
    val next = roadStations.firstOrNull { it > streak }
    LaunchedEffect(Unit) {
        // Автопрокрутка к следующей станции: станция 84 dp + отрезок 54 dp.
        val idx = next?.let { roadStations.indexOf(it) } ?: roadStations.lastIndex
        kotlinx.coroutines.delay(200)
        val px = with(density) { (10 + idx * (84 + 54) + 42).dp.toPx() }
        scroll.animateScrollTo((px - scroll.viewportSize / 2f).toInt().coerceAtLeast(0), tween(600))
    }
    val pulseT = rememberInfiniteTransition(label = "road")
    val pulse by pulseT.animateFloat(0f, 1f, infiniteRepeatable(tween(900), RepeatMode.Reverse), label = "p")
    Column(modifier) {
        Text(L10n.s("ui.flame_rule"), color = Palette.inkSoft, fontSize = 11.sp, fontFamily = Fonts.rounded, maxLines = 2)
        Box(Modifier.weight(1f).fillMaxWidth(), contentAlignment = Alignment.CenterStart) {
            Row(Modifier.horizontalScroll(scroll).padding(horizontal = 10.dp), verticalAlignment = Alignment.CenterVertically) {
                roadStations.forEachIndexed { i, day ->
                    Station(day, streak, isNext = day == next, pulse = pulse)
                    if (i + 1 < roadStations.size) Segment(day, roadStations[i + 1], streak, tier)
                }
            }
        }
    }
}

@Composable
private fun Station(day: Int, streak: Int, isNext: Boolean, pulse: Float) {
    val reached = streak >= day
    val tierHere = Meta.flameTiers.indexOfFirst { it.first == day }.takeIf { it >= 0 }?.plus(1)
    val hints = Meta.milestoneHints(day)
    Column(Modifier.width(84.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(5.dp)) {
        Box(Modifier.height(38.dp), contentAlignment = Alignment.Center) {
            if (tierHere != null) FlameBadge(if (reached || isNext) tierHere else 0, 34.dp, animated = reached)
        }
        Text(tierHere?.let { L10n.s("ui.flame.$it") } ?: " ", color = if (reached) Palette.ink else Palette.inkSoft,
            fontSize = 10.sp, fontFamily = Fonts.rounded, maxLines = 1, softWrap = false)
        val sc = if (isNext) 1f + 0.08f * pulse else 1f
        Box(Modifier.size(46.dp).graphicsLayer { scaleX = sc; scaleY = sc }
            .shadow(if (isNext) (2 + 8 * pulse).dp else 0.dp, CircleShape, ambientColor = Color(0xFFFF9500), spotColor = Color(0xFFFF9500))
            .clip(CircleShape).background(if (reached) Palette.gold else Palette.panel)
            .border(if (isNext) 3.dp else 2.dp, if (isNext) Color(0xFFFF9500) else Palette.ink.copy(if (reached) 0.6f else 0.3f), CircleShape),
            contentAlignment = Alignment.Center) {
            Text(if (reached) "✓" else "$day", color = Palette.ink, fontSize = if (reached) 18.sp else 15.sp,
                fontWeight = FontWeight.Bold, fontFamily = Fonts.rounded)
        }
        Text(L10n.s("ui.gift_day", day), color = Palette.inkSoft, fontSize = 10.sp, fontFamily = Fonts.rounded,
            maxLines = 1, softWrap = false)
        Column(Modifier.height(40.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(2.dp)) {
            if (hints > 0) RoadPill("+$hints 💡", reached)
            if (tierHere != null && Meta.flameTiers[tierHere - 1].second > 0)
                RoadPill(L10n.s("ui.flame_bonus", Meta.flameTiers[tierHere - 1].second), reached)
        }
    }
}

@Composable
private fun RoadPill(text: String, on: Boolean) {
    Box(Modifier.clip(RoundedCornerShape(50)).background(if (on) Palette.gold.copy(0.4f) else Palette.ink.copy(0.07f))
        .padding(horizontal = 7.dp, vertical = 2.dp)) {
        Text(text, color = if (on) Palette.ink else Palette.inkSoft, fontSize = 10.sp, fontFamily = Fonts.rounded,
            maxLines = 1, softWrap = false)
    }
}

/** Отрезок между станциями: залит на пройденную долю, на текущем — маркер-огонёк. */
@Composable
private fun Segment(a: Int, b: Int, streak: Int, tier: Int) {
    val frac = ((streak - a).toFloat() / (b - a)).coerceIn(0f, 1f)
    val width = 54.dp
    // Кружок станции стоит почти ровно по середине колонки — отрезок по центру ряда.
    Box(Modifier.width(width).height(60.dp), contentAlignment = Alignment.CenterStart) {
        Box(Modifier.width(width).height(6.dp).clip(RoundedCornerShape(3.dp)).background(Palette.ink.copy(0.12f)))
        Box(Modifier.width(width * frac).height(6.dp).clip(RoundedCornerShape(3.dp)).background(Palette.gold))
        if (streak in (a + 1) until b) {
            Box(Modifier.offset(x = width * frac - 11.dp, y = (-14).dp)) { FlameBadge(tier, 22.dp) }
        }
    }
}
