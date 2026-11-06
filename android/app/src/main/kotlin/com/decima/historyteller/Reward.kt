package com.decima.historyteller

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.spring
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import teller.engine.LevelDef

/**
 * Экран награды после ПЕРВОГО решения уровня (`docs/f2p-patch-4.0.md` §2): опыт со счётчиком,
 * полоса звания (с переходом через порог), вспышка нового звания, карточка эпизода, которая
 * переворачивается в альбом, кольцо главы, серия, бонус эпизода дня и печать «Знаток» за главу.
 *
 * Всё идёт по таймлайну [phase]: каждая ступень вступает со своим звуком и вибрацией, кнопки
 * появляются, когда главное уже показано — чтобы «К карте» не нажимали вслепую.
 */
@Composable
fun RewardScreen(level: LevelDef, reward: Meta.SolveReward, hasNext: Boolean,
                 onNext: () -> Unit, onMap: () -> Unit) {
    val ctx = LocalContext.current
    val haptics = remember { Settings(ctx).haptics }
    val progress = remember { Progress(ctx) }
    // Глава: состав из манифеста (выключенные — мимо), иначе из загруженного контента.
    val chapterIds = remember(level.id) {
        (ContentSync.availableChapters().firstOrNull { it.id == level.epoch }?.levels
            ?: GameContent.levels(level.epoch).map { it.id }).filterNot { ContentSync.isLevelDisabled(it) }
    }
    val total = chapterIds.size
    val done = remember(level.id) { chapterIds.count { progress.isCompleted(it) } }
    val chapterComplete = total > 0 && done >= total

    /** 0 — счёт опыта, 1 — карточка, 2 — кольцо, 3 — серия, 4 — эпизод дня, 5 — печать главы, 6 — кнопки. */
    var phase by remember { mutableIntStateOf(0) }
    val shownXp = remember { Animatable(reward.xpBefore.toFloat()) }
    val gained = remember { Animatable(0f) }
    var rankBurst by remember { mutableStateOf(false) }
    val flip = remember { Animatable(180f) }
    val ring = remember { Animatable(if (total > 0) (done - 1).coerceAtLeast(0) / total.toFloat() else 0f) }

    LaunchedEffect(Unit) {
        Audio.sfx("accent")
        launch { gained.animateTo(reward.xpGained.toFloat(), tween(1000, easing = FastOutSlowInEasing)) }
        shownXp.animateTo(reward.xpAfter.toFloat(), tween(if (reward.rankedUp) 1500 else 1000, easing = FastOutSlowInEasing))
        delay(150)
        phase = 1; Audio.sfx("place"); Haptics.light(ctx, haptics)
        launch { flip.animateTo(0f, spring(dampingRatio = 0.55f, stiffness = Spring.StiffnessLow)) }
        delay(500)
        phase = 2
        if (total > 0) launch { ring.animateTo(done / total.toFloat(), tween(700, easing = FastOutSlowInEasing)) }
        delay(550)
        phase = 3
        if (reward.streakGrew) { Audio.sfx("accent"); Haptics.light(ctx, haptics) }
        delay(if (reward.milestoneHints > 0) 550 else 300)
        phase = 4
        if (reward.isDaily) { Audio.sfx("accent"); delay(400) }
        phase = 5
        if (chapterComplete) { Audio.sfx("win"); Haptics.success(ctx, haptics); delay(700) }
        phase = 6
    }
    // Порог звания пересечён прямо на счётчике — вспышка ровно в этот момент, а не в конце.
    val shownLevel = Meta.levelForXP(shownXp.value.toInt())
    LaunchedEffect(shownLevel > reward.levelBefore) {
        if (shownLevel > reward.levelBefore && !rankBurst) {
            rankBurst = true; Audio.sfx("win"); Haptics.success(ctx, haptics)
        }
    }

    val swallow = remember { MutableInteractionSource() }
    Box(Modifier.fillMaxSize().background(Color.Black.copy(0.55f))
        .clickable(interactionSource = swallow, indication = null) { },
        contentAlignment = Alignment.Center) {
        BookPage(Modifier.fillMaxWidth(0.94f).fillMaxHeight(0.94f).widthIn(max = 760.dp)) {
            Column(Modifier.fillMaxSize().padding(horizontal = 26.dp, vertical = 16.dp),
                horizontalAlignment = Alignment.CenterHorizontally) {
                Row(Modifier.fillMaxWidth().weight(1f), verticalAlignment = Alignment.CenterVertically) {
                    // ---- слева: опыт, звание, серия, бонусы ----
                    Column(Modifier.weight(1.15f).padding(end = 14.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                        XpCounter(gained.value.toInt())
                        RankBar(shownXp.value)
                        if (rankBurst) RankUpBurst(reward.levelAfter, reward.rankHints)
                        if (phase >= 3) StreakLine(reward)
                        if (phase >= 4 && reward.isDaily) PopIn {
                            RewardPill("☀️ " + L10n.s("ui.daily_bonus") + "  +${reward.dailyHints} 💡", Palette.gold.copy(0.3f))
                        }
                    }
                    // ---- справа: карточка эпизода и кольцо главы ----
                    Column(Modifier.weight(1f), horizontalAlignment = Alignment.CenterHorizontally) {
                        Box(contentAlignment = Alignment.Center) {
                            EpisodeCard(level, flip.value, 150.dp)
                            if (phase >= 5 && chapterComplete) MasterSeal(Modifier.align(Alignment.BottomEnd).offset(x = 34.dp, y = 22.dp))
                        }
                        Spacer(Modifier.height(8.dp))
                        if (phase >= 1) PopIn {
                            Text("📖 " + L10n.s("ui.card_added"), color = Palette.ink, fontSize = 13.sp,
                                fontWeight = FontWeight.Bold, fontFamily = Fonts.rounded)
                        }
                        Spacer(Modifier.height(6.dp))
                        if (phase >= 2 && total > 0) ChapterRing(ring.value, done, total)
                        if (phase >= 5 && chapterComplete) PopIn {
                            Text(L10n.s("ui.chapter_master", L10n.s("chapter.${level.epoch}.title")),
                                color = Palette.maroon, fontSize = 14.sp, fontWeight = FontWeight.Bold,
                                fontFamily = Fonts.serif, textAlign = TextAlign.Center,
                                modifier = Modifier.padding(top = 4.dp))
                        }
                    }
                }
                // ---- кнопки ----
                val btnAlpha by animateFloatAsStateCompat(if (phase >= 2) 1f else 0f)
                Row(Modifier.graphicsLayer { alpha = btnAlpha }.padding(top = 6.dp),
                    horizontalArrangement = Arrangement.spacedBy(12.dp), verticalAlignment = Alignment.CenterVertically) {
                    val enabled = phase >= 2
                    Box(Modifier.clip(RoundedCornerShape(30.dp)).background(Palette.paper)
                        .border(1.5.dp, Palette.maroon.copy(0.5f), RoundedCornerShape(30.dp))
                        .clickable(enabled = enabled) { Audio.sfx("select"); onMap() }
                        .padding(horizontal = 22.dp, vertical = 10.dp)) {
                        Text(L10n.s("ui.to_map"), color = Palette.maroon, fontSize = 16.sp,
                            fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
                    }
                    if (hasNext) NextEpisodeButton(enabled) { Audio.sfx("select"); onNext() }
                }
            }
        }
        if (phase in 1..2 || rankBurst && phase < 3 || phase == 5 && chapterComplete) ConfettiOverlay()
    }
}

/** Плавное значение без `label`-шума: обёртка над animateFloatAsState. */
@Composable
private fun animateFloatAsStateCompat(target: Float): State<Float> =
    androidx.compose.animation.core.animateFloatAsState(target, tween(350), label = "reward")

/** Пружинное появление: от 0.4 к 1 с перелётом — «выпрыгивает» на страницу. */
@Composable
private fun PopIn(content: @Composable () -> Unit) {
    val s = remember { Animatable(0.4f) }
    val a = remember { Animatable(0f) }
    LaunchedEffect(Unit) {
        launch { a.animateTo(1f, tween(180)) }
        s.animateTo(1f, spring(dampingRatio = 0.45f, stiffness = Spring.StiffnessMedium))
    }
    Box(Modifier.graphicsLayer { scaleX = s.value; scaleY = s.value; alpha = a.value }) { content() }
}

@Composable
private fun XpCounter(value: Int) {
    Row(verticalAlignment = Alignment.Bottom) {
        Text("+$value", color = Palette.maroon, fontSize = 46.sp, fontWeight = FontWeight.Bold,
            fontFamily = Fonts.serif, lineHeight = 48.sp)
        Text(" XP", color = Palette.gold, fontSize = 24.sp, fontWeight = FontWeight.Bold,
            fontFamily = Fonts.serif, modifier = Modifier.padding(bottom = 6.dp))
    }
}

/** Эмблема звания + «Ур. N · Звание» + полоса. Значение опыта — живое, с анимации счётчика. */
@Composable
private fun RankBar(xp: Float) {
    val lvl = Meta.levelForXP(xp.toInt())
    val lo = Meta.threshold(lvl); val hi = Meta.threshold(lvl + 1)
    val frac = ((xp - lo) / (hi - lo).coerceAtLeast(1)).coerceIn(0f, 1f)
    Row(verticalAlignment = Alignment.CenterVertically) {
        RankEmblem(lvl, 42.dp)
        Spacer(Modifier.width(10.dp))
        Column(Modifier.weight(1f)) {
            Text(L10n.s("ui.lvl_short", lvl) + " · " + L10n.s(Meta.rankKey(lvl)), color = Palette.ink,
                fontSize = 15.sp, fontWeight = FontWeight.Bold, fontFamily = Fonts.serif, maxLines = 1,
                overflow = TextOverflow.Ellipsis)
            Spacer(Modifier.height(5.dp))
            XpBar(frac, Modifier.fillMaxWidth().height(12.dp))
            Text("${xp.toInt() - lo} / ${hi - lo}", color = Palette.inkSoft, fontSize = 10.sp, fontFamily = Fonts.rounded)
        }
    }
}

/** Полоса опыта: пергаментная канавка с золотой заливкой и бликом. */
@Composable
fun XpBar(fraction: Float, modifier: Modifier) {
    Box(modifier.clip(RoundedCornerShape(50)).background(Palette.ink.copy(0.12f))
        .border(1.dp, Palette.ink.copy(0.25f), RoundedCornerShape(50))) {
        Box(Modifier.fillMaxHeight().fillMaxWidth(fraction.coerceIn(0f, 1f)).clip(RoundedCornerShape(50))
            .background(Palette.gold)) {
            Box(Modifier.fillMaxWidth().fillMaxHeight(0.4f).background(Color.White.copy(0.3f)))
        }
    }
}

/** Медаль с номером уровня игрока. */
@Composable
fun RankEmblem(level: Int, size: Dp) {
    Box(Modifier.size(size).shadow(3.dp, CircleShape).clip(CircleShape).background(Palette.maroon)
        .border(2.5.dp, Palette.gold, CircleShape), contentAlignment = Alignment.Center) {
        Text("$level", color = Palette.gold, fontSize = (size.value * 0.42f).sp, fontWeight = FontWeight.Bold,
            fontFamily = Fonts.serif)
    }
}

/** Вспышка нового звания: лучи крутятся, плашка «выпрыгивает». */
@Composable
private fun RankUpBurst(level: Int, hints: Int) {
    val spin = rememberInfiniteTransition(label = "rays")
    val rot by spin.animateFloat(0f, 360f, infiniteRepeatable(tween(6000)), label = "rot")
    PopIn {
        Box(contentAlignment = Alignment.CenterStart) {
            Canvas(Modifier.size(64.dp).graphicsLayer { rotationZ = rot }) {
                val c = Offset(size.width / 2, size.height / 2)
                for (k in 0 until 12) {
                    val ang = Math.toRadians(k * 30.0)
                    drawLine(Palette.gold.copy(0.7f), c,
                        Offset(c.x + (size.width / 2) * Math.cos(ang).toFloat(), c.y + (size.height / 2) * Math.sin(ang).toFloat()),
                        strokeWidth = 4f, cap = StrokeCap.Round)
                }
            }
            Row(Modifier.padding(start = 10.dp).clip(RoundedCornerShape(14.dp)).background(Palette.maroon)
                .border(2.dp, Palette.gold, RoundedCornerShape(14.dp)).padding(horizontal = 14.dp, vertical = 7.dp),
                verticalAlignment = Alignment.CenterVertically) {
                Column {
                    Text(L10n.s("ui.new_rank"), color = Palette.gold, fontSize = 11.sp, fontWeight = FontWeight.Bold,
                        fontFamily = Fonts.rounded, letterSpacing = 1.sp)
                    Text(L10n.s(Meta.rankKey(level)), color = Palette.paper, fontSize = 18.sp,
                        fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
                }
                if (hints > 0) {
                    Spacer(Modifier.width(12.dp))
                    Text("+$hints 💡", color = Palette.paper, fontSize = 16.sp, fontWeight = FontWeight.Bold, fontFamily = Fonts.rounded)
                }
            }
        }
    }
}

/** 🔥 серия: подпрыгивает, если выросла сегодня; веха — отдельной плашкой с подсказками. */
@Composable
private fun StreakLine(reward: Meta.SolveReward) {
    val bump = remember { Animatable(if (reward.streakGrew) 0.5f else 1f) }
    LaunchedEffect(Unit) { if (reward.streakGrew) bump.animateTo(1f, spring(dampingRatio = 0.35f, stiffness = Spring.StiffnessMediumLow)) }
    Row(verticalAlignment = Alignment.CenterVertically) {
        val tier = Meta.flameTier(reward.streakAfter)
        Box(Modifier.graphicsLayer {
            scaleX = 1.6f - 0.6f * bump.value; scaleY = 1.6f - 0.6f * bump.value
            translationY = -(1f - bump.value) * 30f
        }) { FlameBadge(tier, 30.dp) }
        Spacer(Modifier.width(6.dp))
        Text(L10n.s("ui.streak_days", reward.streakAfter), color = Palette.ink, fontSize = 16.sp,
            fontWeight = FontWeight.Bold, fontFamily = Fonts.rounded)
        if (reward.flameBonus > 0) {
            Spacer(Modifier.width(6.dp))
            Text(L10n.s("ui.flame_bonus", reward.flameBonus), color = Flame.colors(tier).first, fontSize = 12.sp,
                fontWeight = FontWeight.Bold, fontFamily = Fonts.rounded)
        }
        if (reward.flameGrew && reward.tierAfter > 1) {
            Spacer(Modifier.width(10.dp))
            PopIn { RewardPill(L10n.s("ui.flame_new") + " " + L10n.s("ui.flame.${reward.tierAfter}"), Palette.gold.copy(0.35f)) }
        }
        if (reward.milestoneHints > 0) {
            Spacer(Modifier.width(10.dp))
            PopIn { RewardPill(L10n.s("ui.streak_milestone") + "  +${reward.milestoneHints} 💡", Palette.love.copy(0.2f)) }
        }
    }
}

@Composable
private fun RewardPill(text: String, bg: Color) {
    Box(Modifier.clip(RoundedCornerShape(20.dp)).background(bg)
        .border(1.dp, Palette.gold.copy(0.6f), RoundedCornerShape(20.dp)).padding(horizontal = 12.dp, vertical = 5.dp)) {
        Text(text, color = Palette.ink, fontSize = 13.sp, fontWeight = FontWeight.Bold, fontFamily = Fonts.rounded)
    }
}

/**
 * Карточка эпизода (обложка как на карте главы). [rotation] 180 → 0: сначала видна рубашка,
 * на 90° карточка «переворачивается» лицом.
 */
@Composable
fun EpisodeCard(level: LevelDef, rotation: Float, width: Dp) {
    val density = androidx.compose.ui.platform.LocalDensity.current.density
    val cover = level.cover ?: level.scenes.firstOrNull()
    Box(Modifier.width(width).aspectRatio(0.72f)
        .graphicsLayer { rotationY = rotation; cameraDistance = 14f * density }
        .shadow(8.dp, RoundedCornerShape(12.dp)).clip(RoundedCornerShape(12.dp))) {
        if (rotation > 90f) {
            // Рубашка: бордовая с золотой рамкой и вопросом.
            Box(Modifier.fillMaxSize().background(Palette.maroon).border(3.dp, Palette.gold, RoundedCornerShape(12.dp)),
                contentAlignment = Alignment.Center) {
                Text("?", color = Palette.gold, fontSize = 48.sp, fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
            }
        } else {
            Column(Modifier.fillMaxSize().background(Palette.panel).border(3.dp, Palette.gold, RoundedCornerShape(12.dp))
                .padding(6.dp)) {
                Box(Modifier.fillMaxWidth().weight(1f).clip(RoundedCornerShape(8.dp)).background(Palette.paper)) {
                    val painter = cover?.let { artPainter("scene_$it") }
                    if (painter != null) Image(painter, null, Modifier.fillMaxSize(), contentScale = ContentScale.Crop)
                }
                Text(level.title, color = Palette.ink, fontSize = 12.sp, fontWeight = FontWeight.Bold,
                    fontFamily = Fonts.serif, textAlign = TextAlign.Center, maxLines = 2, lineHeight = 14.sp,
                    overflow = TextOverflow.Ellipsis, modifier = Modifier.fillMaxWidth().padding(top = 5.dp))
            }
        }
    }
}

/** Кольцо главы «done / total». */
@Composable
private fun ChapterRing(fraction: Float, done: Int, total: Int) {
    Box(Modifier.size(64.dp), contentAlignment = Alignment.Center) {
        Canvas(Modifier.fillMaxSize()) {
            val sw = 6.dp.toPx()
            val inset = sw / 2
            drawArc(Palette.ink.copy(0.15f), 0f, 360f, false, Offset(inset, inset),
                Size(size.width - sw, size.height - sw), style = Stroke(sw))
            drawArc(Palette.success, -90f, 360f * fraction.coerceIn(0f, 1f), false, Offset(inset, inset),
                Size(size.width - sw, size.height - sw), style = Stroke(sw, cap = StrokeCap.Round))
        }
        Text("$done / $total", color = Palette.ink, fontSize = 12.sp, fontWeight = FontWeight.Bold, fontFamily = Fonts.rounded)
    }
}

/** Золотая печать «Знаток»: падает на карточку с большого размера, как штамп. */
@Composable
fun MasterSeal(modifier: Modifier = Modifier, size: Dp = 70.dp, animate: Boolean = true) {
    val s = remember { Animatable(if (animate) 2.6f else 1f) }
    LaunchedEffect(Unit) { if (animate) s.animateTo(1f, spring(dampingRatio = 0.5f, stiffness = Spring.StiffnessMedium)) }
    Box(modifier.size(size).graphicsLayer { scaleX = s.value; scaleY = s.value; rotationZ = -14f }
        .shadow(6.dp, CircleShape).clip(CircleShape).background(Palette.gold)
        .border(3.dp, Color(0xFF9C7A2E), CircleShape), contentAlignment = Alignment.Center) {
        Box(Modifier.fillMaxSize(0.78f).border(1.5.dp, Palette.paper.copy(0.8f), CircleShape), contentAlignment = Alignment.Center) {
            Text("★", color = Palette.paper, fontSize = (size.value * 0.4f).sp, fontWeight = FontWeight.Bold)
        }
    }
}

/** «Следующий эпизод ▶» — главная кнопка, мягко пульсирует, зовёт дальше. */
@Composable
private fun NextEpisodeButton(enabled: Boolean, onClick: () -> Unit) {
    val t = rememberInfiniteTransition(label = "next")
    val pulse by t.animateFloat(1f, 1.05f, infiniteRepeatable(tween(800), RepeatMode.Reverse), label = "pulse")
    Box(Modifier.graphicsLayer { scaleX = pulse; scaleY = pulse }
        .shadow(8.dp, RoundedCornerShape(30.dp), ambientColor = Palette.gold, spotColor = Palette.gold)
        .clip(RoundedCornerShape(30.dp)).background(Palette.maroon)
        .border(2.dp, Palette.gold.copy(0.8f), RoundedCornerShape(30.dp))
        .clickable(enabled = enabled) { onClick() }.padding(horizontal = 28.dp, vertical = 10.dp)) {
        Text(L10n.s("ui.next_episode") + "  ▶", color = Palette.paper, fontSize = 16.sp,
            fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
    }
}
