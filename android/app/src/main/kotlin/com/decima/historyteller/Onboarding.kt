package com.decima.historyteller

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.LinearEasing
import androidx.compose.foundation.Canvas
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
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
import androidx.compose.ui.graphics.lerp
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import kotlin.random.Random
import teller.engine.LevelDef
import teller.engine.Panel

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

/**
 * Шаг онбординга: что написано внизу и сколько кадров доски к этому моменту собрано.
 * Порт iOS OnboardingView.
 */
private data class OnbStep(
    val key: Int,
    val filled: Int,             // сколько панелей заполнено героями
    val goal: Boolean = false,   // показывать баннер цели
    val cast: Boolean = false,   // показывать трей персонажей
    val fact: Boolean = false,   // показывать факт-карточку
)

private val ONB_STEPS = listOf(
    OnbStep(1, 0),
    OnbStep(2, 0, goal = true),
    OnbStep(3, 0, goal = true, cast = true),
    OnbStep(4, 1, goal = true, cast = true),
    OnbStep(5, 3, goal = true, cast = true),
    OnbStep(6, 3, fact = true),
)

/**
 * Онбординг: не абстрактные правила, а разбор одного настоящего уровня — пустые кадры
 * получают цель, каст и по эталонному решению героев, затем открывается факт-карточка.
 *
 * Уровень задан в `Content/demo.json` и лежит в core, поэтому доступен на первом запуске.
 * Без него (старый манифест) экран откатывается на текстовые шаги без доски.
 */
@Composable
fun OnboardingScreen(onFinish: () -> Unit) {
    val demo = remember { demoLevel() }
    val panels = remember(demo) { demo?.solution?.filter { it.sceneId != null } ?: emptyList() }
    var step by remember { mutableIntStateOf(0) }
    val cur = ONB_STEPS[step]
    val isLast = step == ONB_STEPS.size - 1

    Box(Modifier.fillMaxSize().background(Palette.backdrop), contentAlignment = Alignment.Center) {
        Column(
            Modifier.widthIn(max = 860.dp).fillMaxSize().padding(horizontal = 40.dp, vertical = 8.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                Text(L10n.s("ui.how_to_play").uppercase(), color = Palette.gold, fontSize = 11.sp,
                    fontWeight = FontWeight.Bold, letterSpacing = 2.sp, fontFamily = Fonts.rounded)
                Spacer(Modifier.weight(1f))
                if (!isLast) Text(L10n.s("ui.skip"), color = Palette.paper.copy(alpha = 0.5f),
                    fontSize = 12.sp, fontFamily = Fonts.rounded,
                    modifier = Modifier.clickable { onFinish() })
            }

            if (panels.isNotEmpty()) {
                // Цель разбираемого уровня. Скрытые блоки не держат за собой место: пока цель
                // и каст не показаны, их полосы читались как пустой провал между доской и
                // подписью, а на последних шагах сумма высот уже не влезала в landscape.
                if (cur.goal) Text(demo?.goalText ?: "", color = Palette.gold, fontSize = 14.sp,
                    fontFamily = Fonts.rounded)

                Box(Modifier.fillMaxWidth().weight(1f)) {
                    Row(Modifier.fillMaxSize(), horizontalArrangement = Arrangement.spacedBy(14.dp,
                        Alignment.CenterHorizontally)) {
                        panels.forEachIndexed { i, panel ->
                            // Пропорция вместо растяжения по ширине: на низком экране доске
                            // достаётся мало высоты, и кадры во всю ширину вырождались в полоски.
                            OnbPanel(panel, landed = i < cur.filled,
                                modifier = Modifier.fillMaxHeight().aspectRatio(1.3f))
                        }
                    }
                    // Награда ложится поверх собранной доски — как в игре. Затемнение ограничено
                    // доской: во весь экран оно гасило и подпись, и кнопку «Начать», будто они
                    // недоступны.
                    if (cur.fact && demo?.factCard != null) OnbFactCard(demo)
                }

                // Трей персонажей.
                if (cur.cast) {
                    Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                        for (cid in demo?.characters.orEmpty()) {
                            Row(
                                Modifier.clip(RoundedCornerShape(10.dp))
                                    .background(Palette.panel.copy(alpha = 0.5f))
                                    .border(2.dp, Palette.ink.copy(alpha = 0.7f), RoundedCornerShape(10.dp))
                                    .padding(horizontal = 9.dp, vertical = 3.dp),
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(5.dp),
                            ) {
                                artPainter("char_$cid")?.let {
                                    Image(it, null, Modifier.height(32.dp), contentScale = ContentScale.Fit)
                                }
                                Text(GameContent.db.characters[cid]?.name ?: cid, color = Palette.paper,
                                    fontSize = 11.sp, fontFamily = Fonts.rounded)
                            }
                        }
                    }
                }
            } else {
                Spacer(Modifier.weight(1f))
            }

            Column(horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(3.dp)) {
                Text(L10n.s("ui.onb.${cur.key}.title"), color = Palette.paper, fontSize = 17.sp,
                    fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
                Text(L10n.s("ui.onb.${cur.key}.body"), color = Palette.paper.copy(alpha = 0.72f),
                    fontSize = 13.sp, fontFamily = Fonts.rounded, textAlign = TextAlign.Center,
                    lineHeight = 17.sp, maxLines = 3)
            }

            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                Row(horizontalArrangement = Arrangement.spacedBy(7.dp)) {
                    for (i in ONB_STEPS.indices)
                        Box(Modifier.size(7.dp).clip(CircleShape)
                            .background(if (i == step) Palette.gold else Palette.paper.copy(alpha = 0.3f)))
                }
                Spacer(Modifier.weight(1f))
                Box(
                    Modifier.clip(RoundedCornerShape(24.dp)).background(Palette.maroon)
                        .border(3.dp, Palette.ink, RoundedCornerShape(24.dp))
                        .clickable { if (isLast) onFinish() else step++ }
                        .padding(horizontal = 24.dp, vertical = 9.dp)
                ) { Text(L10n.s(if (isLast) "ui.start" else "ui.next"), color = Palette.paper, fontSize = 15.sp,
                    fontWeight = FontWeight.Bold, fontFamily = Fonts.rounded) }
            }
        }

    }
}

/** Кадр доски: сцена, а поверх — герои, когда до кадра дошёл разбор. */
@Composable
private fun OnbPanel(panel: Panel, landed: Boolean, modifier: Modifier = Modifier) {
    val enter by animateFloatAsState(if (landed) 1f else 0f,
        spring(dampingRatio = 0.68f, stiffness = 420f), label = "onb-enter")
    Column(modifier.fillMaxHeight(), horizontalAlignment = Alignment.CenterHorizontally) {
        Box(
            Modifier.fillMaxWidth().weight(1f).clip(RoundedCornerShape(14.dp))
                .border(4.dp, Palette.ink, RoundedCornerShape(14.dp)),
            contentAlignment = Alignment.BottomCenter
        ) {
            panel.sceneId?.let { sid ->
                artPainter("scene_$sid")?.let {
                    Image(it, null, Modifier.fillMaxSize(), contentScale = ContentScale.Crop)
                }
            }
            Box(Modifier.fillMaxSize().background(
                Brush.verticalGradient(listOf(Color.Transparent, Palette.ink.copy(alpha = 0.32f)))))

            Row(Modifier.fillMaxHeight().padding(bottom = 4.dp),
                verticalAlignment = Alignment.Bottom,
                horizontalArrangement = Arrangement.spacedBy(2.dp)) {
                for (cid in panel.characters) {
                    artPainter("char_$cid")?.let {
                        Image(it, null,
                            Modifier.fillMaxHeight().graphicsLayer {
                                alpha = enter
                                scaleX = 0.4f + 0.6f * enter; scaleY = scaleX
                                translationY = (1f - enter) * 120f
                            },
                            contentScale = ContentScale.Fit)
                    }
                }
            }
            if (landed) Box(Modifier.fillMaxSize()
                .border(3.dp, Palette.gold.copy(alpha = 0.9f * enter), RoundedCornerShape(14.dp)))
        }
        // Подпись кадра — только у собранных: до этого подсказывать порядок нечестно,
        // новичок как раз учится его выводить.
        Text(if (landed) GameContent.db.scenes[panel.sceneId]?.name.orEmpty() else " ",
            color = Palette.paper.copy(alpha = 0.65f), fontSize = 10.sp, fontFamily = Fonts.rounded,
            maxLines = 1, modifier = Modifier.padding(top = 5.dp))
    }
}

/** Факт-карточка последнего шага — та же награда, что ждёт за решённый уровень. */
@Composable
private fun OnbFactCard(level: LevelDef) {
    Box(Modifier.fillMaxSize().background(Palette.backdrop.copy(alpha = 0.88f)),
        contentAlignment = Alignment.Center) {
        Column(
            Modifier.widthIn(max = 560.dp).padding(10.dp)
                .clip(RoundedCornerShape(18.dp)).background(Palette.paper)
                .border(4.dp, Palette.ink, RoundedCornerShape(18.dp)).padding(18.dp),
            verticalArrangement = Arrangement.spacedBy(9.dp)
        ) {
            Text(L10n.s("ui.acc_${level.factCard?.accuracy ?: "fact"}").uppercase(),
                color = Palette.gold, fontSize = 10.sp, fontWeight = FontWeight.Bold,
                letterSpacing = 1.6.sp, fontFamily = Fonts.rounded)
            Text(level.factCard?.text.orEmpty(), color = Palette.ink, fontSize = 15.sp,
                fontFamily = Fonts.rounded, lineHeight = 21.sp)
            Text(level.factCard?.source.orEmpty(), color = Palette.inkSoft, fontSize = 11.sp,
                fontFamily = Fonts.rounded)
        }
    }
}

/**
 * Показательный уровень из `Content/demo.json`. Раньше здесь стоял `levels("rome").first()`,
 * который на первом запуске падал: уровни Рима приезжают только вместе с главой.
 */
private fun demoLevel(): LevelDef? {
    ContentSync.demoLevelId()?.let { id -> GameContent.level(id)?.let { return it } }
    return GameContent.levels("rome").firstOrNull { it.panels == 3 && it.solution != null }
        ?: GameContent.levels("rome").firstOrNull()
}

// ============================ Экран загрузки главы ============================

@Composable
fun ChapterLoadingScreen(epoch: String, chapterTitle: String, onReady: () -> Unit) {
    val ctx = androidx.compose.ui.platform.LocalContext.current
    val demo = remember { demoLevel() }
    val panels = remember(demo) { demo?.solution?.filter { it.sceneId != null } ?: emptyList() }
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
            BootLoader(progress)
        }
    }
}

/**
 * Лоадер первого запуска: страница книги с сургучной печатью, вокруг которой золотое кольцо
 * наливается по мере загрузки. Тот же словарь, что и на остальных экранах — пергамент,
 * чернильный контур, золотые уголки. Порт iOS BootLoader.
 *
 * Единственная надпись — название игры: оно одинаково на всех языках. Каталог переводов в этот
 * момент ещё едет, а L10n до его появления сидит на русском, поэтому любая переводимая строка
 * здесь оказалась бы не на языке игрока.
 */
@Composable
private fun BootLoader(progress: Float) {
    val t = rememberInfiniteTransition(label = "boot")
    val spin by t.animateFloat(0f, 360f, infiniteRepeatable(tween(2200, easing = LinearEasing)), label = "spin")
    val pulse by t.animateFloat(0.97f, 1.05f,
        infiniteRepeatable(tween(1100), RepeatMode.Reverse), label = "pulse")
    val shown by animateFloatAsState(progress.coerceAtLeast(0.02f), tween(400), label = "ring")

    BookPage {
        Column(
            Modifier.padding(horizontal = 34.dp, vertical = 26.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            Box(Modifier.size(96.dp), contentAlignment = Alignment.Center) {
                Canvas(Modifier.fillMaxSize()) {
                    val stroke = 7.dp.toPx()
                    val pad = stroke / 2
                    val arc = Size(size.width - stroke, size.height - stroke)
                    drawArc(Palette.ink.copy(alpha = 0.14f), 0f, 360f, false,
                        topLeft = Offset(pad, pad), size = arc, style = Stroke(stroke))
                    drawArc(Palette.gold, -90f, 360f * shown, false,
                        topLeft = Offset(pad, pad), size = arc,
                        style = Stroke(stroke, cap = StrokeCap.Round))
                    // Бегущая искра: прогресс может стоять на месте, а экран должен жить.
                    drawArc(Palette.gold.copy(alpha = 0.55f), spin, 43f, false,
                        topLeft = Offset(pad, pad), size = arc,
                        style = Stroke(3.dp.toPx(), cap = StrokeCap.Round))
                }
                // Сургучная печать.
                Box(
                    Modifier.size(64.dp).graphicsLayer { scaleX = pulse; scaleY = pulse }
                        .clip(CircleShape).background(Palette.maroon)
                        .border(2.dp, Palette.ink.copy(alpha = 0.4f), CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    Text("HT", color = Palette.paper.copy(alpha = 0.9f), fontSize = 20.sp,
                        fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
                }
            }

            Text("History Teller", color = Palette.ink, fontSize = 19.sp,
                fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
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
