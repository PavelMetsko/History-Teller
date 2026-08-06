package com.decima.historyteller

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.spring
import androidx.compose.animation.core.tween
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.animateFloat
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import kotlin.random.Random

// ============================ Выбор языка (первый запуск) ============================

@Composable
fun LanguagePickerScreen(onSelect: (String) -> Unit) {
    val languages = listOf(
        "en" to "English", "ru" to "Русский", "es" to "Español",
        "de" to "Deutsch", "fr" to "Français", "it" to "Italiano",
        "pt" to "Português", "pl" to "Polski", "nl" to "Nederlands",
    )
    Box(Modifier.fillMaxSize().background(Palette.backdrop), contentAlignment = Alignment.Center) {
        Column(
            Modifier.widthIn(max = 660.dp).padding(horizontal = 54.dp, vertical = 26.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text("History Teller", color = Palette.paper, fontSize = 24.sp, fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
            Text("Language · Язык · Sprache", color = Palette.paper.copy(alpha = 0.5f), fontSize = 11.sp,
                letterSpacing = 1.sp, fontFamily = Fonts.rounded, modifier = Modifier.padding(top = 4.dp, bottom = 16.dp))
            for (row in languages.chunked(3)) {
                Row(Modifier.fillMaxWidth().padding(vertical = 7.dp),
                    horizontalArrangement = Arrangement.spacedBy(14.dp)) {
                    for ((code, name) in row) {
                        Box(
                            Modifier.weight(1f).clip(RoundedCornerShape(14.dp)).background(Palette.panel)
                                .border(3.dp, Palette.ink, RoundedCornerShape(14.dp))
                                .clickable { onSelect(code) }.padding(vertical = 14.dp),
                            contentAlignment = Alignment.Center
                        ) { Text(name, color = Palette.ink, fontSize = 17.sp, fontWeight = FontWeight.SemiBold, fontFamily = Fonts.rounded) }
                    }
                }
            }
        }
    }
}

// ============================ Пошаговый онбординг ============================

private data class OnbStep(val title: String, val body: String)

@Composable
fun OnboardingScreen(onFinish: () -> Unit) {
    val steps = (1..6).map { OnbStep(L10n.s("ui.onb.$it.title"), L10n.s("ui.onb.$it.body")) }
    var step by remember { mutableIntStateOf(0) }
    val isLast = step >= steps.size - 1

    Box(Modifier.fillMaxSize().background(Palette.backdrop), contentAlignment = Alignment.Center) {
        Column(
            Modifier.widthIn(max = 720.dp).fillMaxSize().padding(horizontal = 54.dp, vertical = 26.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(L10n.s("ui.how_to_play").uppercase(), color = Palette.gold, fontSize = 12.sp,
                fontWeight = FontWeight.Bold, letterSpacing = 2.sp, fontFamily = Fonts.rounded)

            Box(
                Modifier.fillMaxWidth().weight(1f).padding(vertical = 18.dp)
                    .clip(RoundedCornerShape(22.dp)).background(Palette.panel)
                    .border(4.dp, Palette.ink, RoundedCornerShape(22.dp)),
                contentAlignment = Alignment.Center
            ) {
                Row(Modifier.padding(horizontal = 34.dp), verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(30.dp)) {
                    Box(Modifier.size(140.dp).clip(CircleShape).background(Palette.gold.copy(alpha = 0.16f))
                        .border(3.dp, Palette.gold.copy(alpha = 0.5f), CircleShape),
                        contentAlignment = Alignment.Center) {
                        Text("${step + 1}", color = Palette.maroon, fontSize = 58.sp, fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
                    }
                    Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                        Text(steps[step].title, color = Palette.ink, fontSize = 25.sp, fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
                        Text(steps[step].body, color = Palette.inkSoft, fontSize = 17.sp, fontFamily = Fonts.rounded, lineHeight = 24.sp)
                    }
                }
            }

            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    for (i in steps.indices)
                        Box(Modifier.size(8.dp).clip(CircleShape)
                            .background(if (i == step) Palette.gold else Palette.paper.copy(alpha = 0.35f)))
                }
                Spacer(Modifier.weight(1f))
                Box(
                    Modifier.clip(RoundedCornerShape(24.dp)).background(Palette.maroon)
                        .border(3.dp, Palette.ink, RoundedCornerShape(24.dp))
                        .clickable { if (isLast) onFinish() else step++ }
                        .padding(horizontal = 26.dp, vertical = 11.dp)
                ) { Text(L10n.s(if (isLast) "ui.start" else "ui.next"), color = Palette.paper, fontSize = 16.sp,
                    fontWeight = FontWeight.Bold, fontFamily = Fonts.rounded) }
            }
        }
    }
}

// ============================ Экран загрузки главы ============================

@Composable
fun ChapterLoadingScreen(epoch: String, chapterTitle: String, onReady: () -> Unit) {
    val ctx = androidx.compose.ui.platform.LocalContext.current
    val demo = remember {
        GameContent.level("cleopatra_throne")
            ?: GameContent.levels("rome").firstOrNull { it.panels == 3 && it.solution != null }
            ?: GameContent.levels("rome").first()
    }
    val panels = remember(demo) { demo.solution?.filter { it.sceneId != null } ?: emptyList() }
    val tip = remember { L10n.s("ui.tip.${Random.nextInt(8) + 1}") }
    var retry by remember { mutableIntStateOf(0) }
    // Прогресс настоящий — искусственную задержку показа убрали вместе с Play Asset Delivery:
    // экран и так появляется только когда главы действительно нет на диске.
    val progress = (ContentSync.phase as? ContentSync.Phase.Syncing)?.progress ?: 0f
    val failure = (ContentSync.phase as? ContentSync.Phase.Failed)?.message

    LaunchedEffect(retry) {
        ContentSync.ensureChapter(ctx, epoch)
        if (ContentSync.phase is ContentSync.Phase.Ready) { delay(400); onReady() }
    }

    // глобальный индекс «прыжков» слева направо
    fun stagger(pi: Int, si: Int): Long {
        var idx = 0; for (p in 0 until pi) idx += panels[p].characters.size
        return ((idx + si) * 260).toLong()
    }

    Box(Modifier.fillMaxSize().background(Palette.backdrop)) {
        Column(Modifier.fillMaxSize().padding(horizontal = 46.dp, vertical = 24.dp),
            verticalArrangement = Arrangement.spacedBy(22.dp), horizontalAlignment = Alignment.CenterHorizontally) {

            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text(L10n.s("ui.downloading_chapter").uppercase(), color = Palette.gold, fontSize = 11.sp,
                    fontWeight = FontWeight.Bold, letterSpacing = 2.sp, fontFamily = Fonts.rounded)
                Text(chapterTitle, color = Palette.paper, fontSize = 20.sp, fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
            }

            Row(Modifier.fillMaxWidth().weight(1f), horizontalArrangement = Arrangement.spacedBy(20.dp)) {
                panels.forEachIndexed { pi, panel ->
                    Box(
                        Modifier.weight(1f).fillMaxHeight().clip(RoundedCornerShape(16.dp))
                            .border(4.dp, Palette.ink, RoundedCornerShape(16.dp)),
                        contentAlignment = Alignment.BottomCenter
                    ) {
                        ArtImage("scene_${panel.sceneId}", Modifier.fillMaxSize(), ContentScale.Crop)
                        Box(Modifier.fillMaxWidth().fillMaxHeight(0.5f).align(Alignment.BottomCenter)
                            .background(Brush.verticalGradient(listOf(Color.Transparent, Palette.ink.copy(alpha = 0.28f)))))
                        Row(Modifier.fillMaxHeight().padding(bottom = 6.dp), verticalAlignment = Alignment.Bottom) {
                            panel.characters.forEachIndexed { si, cid ->
                                HoppingSprite(cid, stagger(pi, si))
                            }
                        }
                    }
                }
            }

            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.Bottom, horizontalArrangement = Arrangement.spacedBy(22.dp)) {
                Column(Modifier.weight(1.4f)) {
                    Text(L10n.s("ui.how_to_play").uppercase(), color = Palette.gold, fontSize = 10.sp,
                        fontWeight = FontWeight.Bold, letterSpacing = 1.4.sp, fontFamily = Fonts.rounded)
                    Text(tip, color = Palette.paper, fontSize = 15.sp, fontWeight = FontWeight.SemiBold,
                        fontFamily = Fonts.rounded, lineHeight = 20.sp, modifier = Modifier.padding(top = 5.dp))
                }
                Column(Modifier.width(230.dp)) {
                    ProgressBar(progress)
                    Row(Modifier.fillMaxWidth().padding(top = 6.dp)) {
                        Text(if (progress >= 1f) L10n.s("ui.ready") else L10n.s("ui.downloading_chapter"),
                            color = Palette.paper.copy(alpha = 0.5f), fontSize = 10.sp, fontFamily = Fonts.rounded)
                        Spacer(Modifier.weight(1f))
                        Text("${(progress * 100).toInt()}%", color = Palette.gold, fontSize = 10.sp,
                            fontWeight = FontWeight.Bold, fontFamily = Fonts.rounded)
                    }
                }
            }
        }
        // Сеть отвалилась посреди докачки — не выкидываем в меню молча, даём повторить.
        if (failure != null) DownloadFailed(failure, onRetry = { retry++ }, onCancel = onReady)
    }
}

/** Загрузка не удалась: причина, «Повторить» и выход — вместо молчаливого возврата. */
@Composable
private fun DownloadFailed(message: String, onRetry: () -> Unit, onCancel: () -> Unit) {
    Box(Modifier.fillMaxSize().background(Palette.backdrop.copy(alpha = 0.94f)), contentAlignment = Alignment.Center) {
        Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(14.dp)) {
            Text(L10n.s("ui.load_fail"), color = Palette.paper, fontSize = 20.sp,
                fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
            Text(message, color = Palette.paper.copy(alpha = 0.7f), fontSize = 12.sp, fontFamily = Fonts.rounded)
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                Box(Modifier.clip(RoundedCornerShape(24.dp)).background(Palette.maroon)
                    .border(2.dp, Palette.gold, RoundedCornerShape(24.dp))
                    .clickable { onRetry() }.padding(horizontal = 22.dp, vertical = 10.dp)) {
                    Text(L10n.s("ui.retry"), color = Palette.paper, fontSize = 15.sp, fontFamily = Fonts.rounded)
                }
                Box(Modifier.clip(RoundedCornerShape(24.dp))
                    .clickable { onCancel() }.padding(horizontal = 22.dp, vertical = 10.dp)) {
                    Text(L10n.s("ui.cancel"), color = Palette.paper.copy(alpha = 0.7f),
                        fontSize = 15.sp, fontFamily = Fonts.rounded)
                }
            }
        }
    }
}

/** Первый запуск: пока едет core, показываем прогресс, а не пустой экран. */
@Composable
fun BootScreen(bootError: String? = null, onRetry: () -> Unit) {
    val progress = (ContentSync.phase as? ContentSync.Phase.Syncing)?.progress ?: 0f
    val failure = bootError ?: (ContentSync.phase as? ContentSync.Phase.Failed)?.message
    Box(Modifier.fillMaxSize().background(Palette.backdrop), contentAlignment = Alignment.Center) {
        if (failure != null) {
            DownloadFailed(failure, onRetry = onRetry, onCancel = onRetry)
        } else {
            Column(Modifier.width(230.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                ProgressBar(progress)
                Text(L10n.s("ui.downloading_content"), color = Palette.paper.copy(alpha = 0.5f),
                    fontSize = 10.sp, fontFamily = Fonts.rounded, modifier = Modifier.padding(top = 6.dp))
            }
        }
    }
}

@Composable
private fun HoppingSprite(cid: String, delayMs: Long) {
    val anim = remember { Animatable(0f) }
    LaunchedEffect(cid) { delay(delayMs); anim.animateTo(1f, spring(dampingRatio = 0.55f, stiffness = 260f)) }
    val bobT = rememberInfiniteTransition(label = "bob")
    val bob by bobT.animateFloat(0f, 1f, infiniteRepeatable(tween(1400), RepeatMode.Reverse), label = "b")
    val painter = artPainter("char_$cid")
    if (painter != null) Image(painter, null,
        Modifier.fillMaxHeight().graphicsLayer {
            val a = anim.value
            translationY = (1f - a) * 150.dp.toPx() - (if (a > 0.98f) bob * 4.dp.toPx() else 0f)
            val sc = 0.4f + 0.6f * a; scaleX = sc; scaleY = sc; alpha = a
        }, contentScale = ContentScale.Fit)
}

@Composable
private fun ProgressBar(progress: Float) {
    val shimmerT = rememberInfiniteTransition(label = "shimmer")
    val shimmer by shimmerT.animateFloat(0f, 1f, infiniteRepeatable(tween(1100), RepeatMode.Restart), label = "s")
    Box(Modifier.fillMaxWidth().height(12.dp).clip(RoundedCornerShape(8.dp))
        .background(Palette.paper.copy(alpha = 0.14f))
        .border(2.dp, Palette.ink, RoundedCornerShape(8.dp))) {
        Box(Modifier.fillMaxHeight().fillMaxWidth(progress.coerceIn(0f, 1f))
            .clip(RoundedCornerShape(6.dp)).background(Palette.gold)
            .background(Brush.horizontalGradient(
                0f to Color.Transparent,
                (shimmer * 1.2f - 0.2f).coerceIn(0f, 1f) to Palette.paper.copy(alpha = 0.6f),
                (shimmer * 1.2f).coerceIn(0f, 1f) to Color.Transparent
            )))
    }
}
