package com.decima.historyteller

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.spring
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.itemsIndexed
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.launch

// ---- Меню 4.0: полоса звания, серия, подсказки, эпизод дня ----

/**
 * Главное меню (`docs/f2p-patch-4.0.md` §2 «Меню»): сверху эмблема + «Ур. N · Звание» + опыт,
 * 🔥 серия, 💡 подсказки. Слева «Играть» и «Альбом», справа — карточка
 * эпизода дня вместо героев. Прервавшуюся вчера серию предлагаем вернуть плашкой.
 */
@Composable
fun MenuScreen(progress: Progress, onPlay: () -> Unit, onAlbum: () -> Unit, onSettings: () -> Unit,
               onReset: () -> Unit, onDaily: (chapter: String, level: String) -> Unit,
               onRestoreStreak: () -> Unit, onStreak: () -> Unit) {
    Box(Modifier.fillMaxSize().padding(16.dp)) {
        BookPage(Modifier.fillMaxSize()) {
            Column(Modifier.fillMaxSize().padding(horizontal = 30.dp, vertical = 14.dp)) {
                MenuTopBar(onSettings, onStreak)
                Meta.brokenStreak?.let { n -> StreakLostBanner(n, onRestoreStreak) }
                Row(Modifier.fillMaxWidth().weight(1f).widthIn(max = 760.dp).align(Alignment.CenterHorizontally),
                    verticalAlignment = Alignment.CenterVertically) {
                    Column(Modifier.weight(1f).padding(start = 10.dp)) {
                        Text(L10n.s("ui.tagline_caps"), color = Palette.maroon, fontSize = 11.sp,
                            fontWeight = FontWeight.Bold, letterSpacing = 2.sp, fontFamily = Fonts.rounded)
                        Text("History Teller", color = Palette.ink, fontSize = 40.sp,
                            fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
                        Box(Modifier.padding(top = 6.dp).width(120.dp).height(3.dp)
                            .clip(RoundedCornerShape(2.dp)).background(Palette.gold))
                        Text(L10n.s("ui.menu_sub"), color = Palette.inkSoft, fontSize = 14.sp,
                            fontFamily = Fonts.rounded, modifier = Modifier.padding(top = 10.dp))
                        Row(Modifier.padding(top = 16.dp), horizontalArrangement = Arrangement.spacedBy(12.dp),
                            verticalAlignment = Alignment.CenterVertically) {
                            Row(Modifier.clip(RoundedCornerShape(30.dp)).background(Palette.maroon).clickable { onPlay() }
                                    .padding(horizontal = 32.dp, vertical = 12.dp),
                                verticalAlignment = Alignment.CenterVertically) {
                                Icon(Icons.Filled.PlayArrow, null, tint = Palette.paper)
                                Spacer(Modifier.width(8.dp))
                                Text(L10n.s("ui.play"), color = Palette.paper, fontSize = 21.sp,
                                    fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
                            }
                            Row(Modifier.clip(RoundedCornerShape(30.dp)).background(Palette.panel)
                                    .border(2.dp, Palette.gold, RoundedCornerShape(30.dp)).clickable { onAlbum() }
                                    .padding(horizontal = 22.dp, vertical = 11.dp),
                                verticalAlignment = Alignment.CenterVertically) {
                                Text("📖", fontSize = 16.sp)
                                Spacer(Modifier.width(8.dp))
                                Text(L10n.s("ui.album"), color = Palette.ink, fontSize = 18.sp,
                                    fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
                            }
                        }
                        Text(L10n.s("ui.reset"), color = Palette.inkSoft, fontSize = 12.sp,
                            fontFamily = Fonts.rounded, modifier = Modifier.padding(top = 12.dp).clickable { onReset() })
                    }
                    Daily.pick(progress)?.let { (ch, id) -> DailyCard(ch, id) { onDaily(ch, id) } }
                }
            }
        }
    }
}

@Composable
private fun MenuTopBar(onSettings: () -> Unit, onStreak: () -> Unit) {
    Row(Modifier.fillMaxWidth().padding(start = 4.dp, end = 4.dp), verticalAlignment = Alignment.CenterVertically) {
        val lvl = Meta.level
        RankEmblem(lvl, 38.dp)
        Spacer(Modifier.width(10.dp))
        Column(Modifier.width(190.dp)) {
            Text(L10n.s("ui.lvl_short", lvl) + " · " + L10n.s(Meta.rankKey(lvl)), color = Palette.ink, fontSize = 14.sp,
                fontWeight = FontWeight.Bold, fontFamily = Fonts.serif, maxLines = 1, overflow = TextOverflow.Ellipsis)
            Spacer(Modifier.height(4.dp))
            XpBar(Meta.levelProgress(Meta.xp), Modifier.fillMaxWidth().height(9.dp))
        }
        Spacer(Modifier.weight(1f))
        FlameChip(Meta.currentStreak, onStreak)
        Spacer(Modifier.width(8.dp))
        StatChip("💡", "${Meta.hints}")
        Spacer(Modifier.width(8.dp))
        IconButtonCircle(Icons.Filled.Settings, onClick = onSettings)
    }
}

/** Чип пламени: стадия серии и число дней, ведёт на «Путь огня». */
@Composable
private fun FlameChip(streak: Int, onTap: () -> Unit) {
    val tier = Meta.flameTier(streak)
    Row(Modifier.clip(RoundedCornerShape(50)).background(Palette.panel)
        .border(1.5.dp, Flame.colors(tier).first.copy(0.8f), RoundedCornerShape(50)).clickable { onTap() }
        .padding(start = 8.dp, end = 12.dp, top = 3.dp, bottom = 3.dp),
        verticalAlignment = Alignment.CenterVertically) {
        FlameBadge(tier, 22.dp)
        Spacer(Modifier.width(4.dp))
        Text("$streak", color = Palette.ink, fontSize = 15.sp, fontWeight = FontWeight.Bold, fontFamily = Fonts.rounded)
    }
}

@Composable
private fun StatChip(icon: String, value: String) {
    Row(Modifier.clip(RoundedCornerShape(50)).background(Palette.panel)
        .border(1.5.dp, Palette.ink.copy(0.25f), RoundedCornerShape(50)).padding(horizontal = 12.dp, vertical = 6.dp),
        verticalAlignment = Alignment.CenterVertically) {
        Text(icon, fontSize = 15.sp)
        Spacer(Modifier.width(5.dp))
        Text(value, color = Palette.ink, fontSize = 15.sp, fontWeight = FontWeight.Bold, fontFamily = Fonts.rounded)
    }
}

@Composable
private fun StreakLostBanner(days: Int, onRestore: () -> Unit) {
    Row(Modifier.fillMaxWidth().padding(top = 8.dp).clip(RoundedCornerShape(14.dp))
        .background(Palette.love.copy(0.14f)).border(1.5.dp, Palette.love.copy(0.5f), RoundedCornerShape(14.dp))
        .padding(horizontal = 14.dp, vertical = 6.dp), verticalAlignment = Alignment.CenterVertically) {
        Text("🔥", fontSize = 18.sp, modifier = Modifier.graphicsLayer { alpha = 0.55f })
        Spacer(Modifier.width(8.dp))
        Text(L10n.s("ui.streak_lost", days), color = Palette.ink, fontSize = 14.sp,
            fontWeight = FontWeight.Bold, fontFamily = Fonts.rounded, modifier = Modifier.weight(1f))
        // Без ролика — только подписчикам; покупка главы серию не касается.
        val premium = Billing.subscribed
        val canWatch = premium || (AdService.isEnabled && AdService.isReady && AdService.cooldownLeft == 0 && !AdService.isShowing)
        Box(Modifier.clip(RoundedCornerShape(20.dp)).background(if (canWatch) Palette.maroon else Palette.inkSoft)
            .clickable(enabled = canWatch) { onRestore() }.padding(horizontal = 14.dp, vertical = 6.dp)) {
            Text((if (premium) "" else "▶ ") + if (canWatch) L10n.s("ui.streak_restore") else L10n.s("ui.video_loading"),
                color = Palette.paper, fontSize = 13.sp, fontWeight = FontWeight.Bold, fontFamily = Fonts.rounded)
        }
    }
}

/** Карточка эпизода дня: обложка главы, название эпизода, глава, «×2 XP · +1 💡» или «Готово». */
@Composable
private fun DailyCard(chapter: String, levelId: String, onOpen: () -> Unit) {
    val done = Meta.dailyDoneToday
    val cover = ContentSync.availableChapters().firstOrNull { it.id == chapter }?.cover
    val glow = rememberInfiniteTransition(label = "daily")
    val g by glow.animateFloat(0.35f, 1f, infiniteRepeatable(tween(1300), RepeatMode.Reverse), label = "g")
    Column(Modifier.width(230.dp)
        .shadow(if (done) 3.dp else (4 + 8 * g).dp, RoundedCornerShape(16.dp), ambientColor = Palette.gold, spotColor = Palette.gold)
        .clip(RoundedCornerShape(16.dp)).background(Palette.panel)
        .border(2.5.dp, if (done) Palette.success else Palette.gold, RoundedCornerShape(16.dp))
        .clickable(enabled = !done) { onOpen() }) {
        Box(Modifier.fillMaxWidth().aspectRatio(16f / 9f).background(Palette.paper)) {
            if (cover != null) ArtImage("scene_$cover", Modifier.fillMaxSize(), ContentScale.Crop)
            Box(Modifier.align(Alignment.TopStart).padding(8.dp).clip(RoundedCornerShape(50))
                .background(Palette.maroon).padding(horizontal = 10.dp, vertical = 4.dp)) {
                Text("☀️ " + L10n.s("ui.daily_title"), color = Palette.paper, fontSize = 11.sp,
                    fontWeight = FontWeight.Bold, fontFamily = Fonts.rounded)
            }
            if (done) Box(Modifier.fillMaxSize().background(Color.Black.copy(0.35f)), contentAlignment = Alignment.Center) {
                Text("✓", color = Color.White, fontSize = 40.sp, fontWeight = FontWeight.Bold)
            }
        }
        Column(Modifier.fillMaxWidth().padding(horizontal = 10.dp, vertical = 8.dp)) {
            // Выбор дня стабилен (ht.meta.dailyPick) — название показываем и на решённой карточке.
            Text(L10n.s("level.$levelId.title"), color = Palette.ink, fontSize = 15.sp, fontWeight = FontWeight.Bold,
                fontFamily = Fonts.serif, maxLines = 2, lineHeight = 17.sp, overflow = TextOverflow.Ellipsis)
            if (done) {
                Text(L10n.s("ui.daily_done"), color = Palette.success, fontSize = 13.sp, fontWeight = FontWeight.Bold,
                    fontFamily = Fonts.rounded, maxLines = 2)
            } else {
                Text(L10n.s("chapter.$chapter.title"), color = Palette.inkSoft, fontSize = 11.sp,
                    fontFamily = Fonts.rounded, maxLines = 1, overflow = TextOverflow.Ellipsis)
                Spacer(Modifier.height(4.dp))
                Text("×2 XP · +1 💡", color = Palette.maroon, fontSize = 13.sp, fontWeight = FontWeight.Bold,
                    fontFamily = Fonts.rounded)
            }
        }
    }
}

// ---- Подарок дня ----

/** Окно подарка: календарь на 7 дней, текущий шаг подсвечен, «Забрать» → +N 💡. */
@Composable
fun GiftPopup(onClaimed: () -> Unit) {
    val ctx = LocalContext.current
    val step = Meta.nextGiftStep
    var claimed by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()
    val pop = remember { Animatable(0.6f) }
    LaunchedEffect(Unit) { Audio.sfx("accent"); pop.animateTo(1f, spring(dampingRatio = 0.5f, stiffness = Spring.StiffnessMediumLow)) }
    val swallow = remember { MutableInteractionSource() }
    Box(Modifier.fillMaxSize().background(Color.Black.copy(0.5f))
        .clickable(interactionSource = swallow, indication = null) { }, contentAlignment = Alignment.Center) {
        BookPage(Modifier.widthIn(max = 620.dp).padding(16.dp).graphicsLayer { scaleX = pop.value; scaleY = pop.value }) {
            Column(Modifier.padding(horizontal = 26.dp, vertical = 18.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                Text("🎁", fontSize = 34.sp)
                Text(L10n.s("ui.gift_title"), color = Palette.ink, fontSize = 24.sp, fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
                Text(L10n.s("ui.gift_body"), color = Palette.inkSoft, fontSize = 13.sp, fontFamily = Fonts.rounded,
                    textAlign = TextAlign.Center)
                Spacer(Modifier.height(12.dp))
                val pulse = rememberInfiniteTransition(label = "gift")
                val ps by pulse.animateFloat(1f, 1.08f, infiniteRepeatable(tween(650), RepeatMode.Reverse), label = "ps")
                Row(horizontalArrangement = Arrangement.spacedBy(6.dp), verticalAlignment = Alignment.CenterVertically) {
                    for (d in 1..7) {
                        val current = d == step
                        val past = d < step || (claimed && current)
                        Column(Modifier.width(66.dp)
                            .graphicsLayer { if (current && !claimed) { scaleX = ps; scaleY = ps } }
                            .clip(RoundedCornerShape(10.dp))
                            .background(when { current -> Palette.gold.copy(0.35f); past -> Palette.success.copy(0.15f); else -> Palette.panel })
                            .border(if (current) 2.5.dp else 1.dp, if (current) Palette.gold else Palette.ink.copy(0.2f), RoundedCornerShape(10.dp))
                            .padding(vertical = 7.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                            Text(L10n.s("ui.gift_day", d), color = Palette.inkSoft, fontSize = 10.sp, fontFamily = Fonts.rounded, maxLines = 1)
                            Text(if (past) "✓" else "💡", fontSize = 18.sp, color = Palette.success)
                            Text("+${Meta.GIFTS[d - 1]}", color = Palette.ink, fontSize = 14.sp, fontWeight = FontWeight.Bold,
                                fontFamily = Fonts.rounded)
                        }
                    }
                }
                Spacer(Modifier.height(14.dp))
                Box(Modifier.clip(RoundedCornerShape(30.dp)).background(Palette.maroon)
                    .border(2.dp, Palette.gold, RoundedCornerShape(30.dp))
                    .clickable(enabled = !claimed) {
                        claimed = true
                        val n = Meta.claimGift()
                        Telemetry.track("gift_claim", "$n")
                        Audio.sfx("win"); Haptics.success(ctx, Settings(ctx).haptics)
                        scope.launch { kotlinx.coroutines.delay(650); onClaimed() }
                    }.padding(horizontal = 40.dp, vertical = 11.dp)) {
                    Text(if (claimed) "+${Meta.GIFTS[step - 1]} 💡" else L10n.s("ui.gift_claim"), color = Palette.paper,
                        fontSize = 18.sp, fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
                }
            }
        }
    }
}

// ---- Альбом ----

/**
 * Альбом карточек: вкладки-главы в порядке манифеста с «N / M» и золотой печатью за полную,
 * сетка — решённые с обложкой и названием, нерешённые тёмные с номером и «?».
 */
@Composable
fun AlbumScreen(progress: Progress, onBack: () -> Unit) {
    val chapters = ContentSync.availableChapters()
    var tab by remember { mutableStateOf(chapters.firstOrNull()?.id ?: "rome") }
    var openFact by remember { mutableStateOf<String?>(null) }
    Box(Modifier.fillMaxSize().padding(16.dp)) {
        BookPage(Modifier.fillMaxSize()) {
            Column(Modifier.fillMaxSize().padding(horizontal = 26.dp, vertical = 12.dp)) {
                Text("📖 " + L10n.s("ui.album"), color = Palette.ink, fontSize = 24.sp, fontWeight = FontWeight.Bold,
                    fontFamily = Fonts.serif, modifier = Modifier.align(Alignment.CenterHorizontally))
                Spacer(Modifier.height(8.dp))
                Row(Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()).padding(start = 60.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                    for (ch in chapters) {
                        val ids = ch.levels.filterNot { ContentSync.isLevelDisabled(it) }
                        val done = ids.count { progress.isCompleted(it) }
                        val sel = ch.id == tab
                        Row(Modifier.clip(RoundedCornerShape(50)).background(if (sel) Palette.maroon else Palette.panel)
                            .border(1.5.dp, if (sel) Palette.gold else Palette.ink.copy(0.25f), RoundedCornerShape(50))
                            .clickable { Audio.sfx("select"); tab = ch.id }.padding(horizontal = 12.dp, vertical = 6.dp),
                            verticalAlignment = Alignment.CenterVertically) {
                            if (ids.isNotEmpty() && done >= ids.size) {
                                MasterSeal(size = 18.dp, animate = false); Spacer(Modifier.width(6.dp))
                            }
                            Text(L10n.s("chapter.${ch.id}.title"), color = if (sel) Palette.paper else Palette.ink, fontSize = 13.sp,
                                fontWeight = FontWeight.Bold, fontFamily = Fonts.serif, maxLines = 1)
                            Spacer(Modifier.width(6.dp))
                            Text("$done / ${ids.size}", color = if (sel) Palette.gold else Palette.inkSoft, fontSize = 11.sp,
                                fontFamily = Fonts.rounded)
                        }
                    }
                }
                Spacer(Modifier.height(10.dp))
                val ch = chapters.firstOrNull { it.id == tab }
                val ids = ch?.levels?.filterNot { ContentSync.isLevelDisabled(it) }.orEmpty()
                LazyVerticalGrid(GridCells.Adaptive(118.dp), Modifier.fillMaxWidth().weight(1f),
                    horizontalArrangement = Arrangement.spacedBy(10.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    itemsIndexed(ids, key = { _, id -> id }) { i, id ->
                        AlbumCard(i + 1, id, ch?.cover, progress.isCompleted(id)) { Audio.sfx("select"); openFact = id }
                    }
                }
            }
            BackButton(Modifier.align(Alignment.TopStart), onBack)
        }
        openFact?.let { id -> AlbumFact(id) { openFact = null } }
    }
}

/** Герои кадра — из эталона (кто реально в сцене), иначе из состава уровня. */
private fun albumCast(id: String): List<String> {
    val lv = GameContent.level(id) ?: return emptyList()
    val fromSolution = lv.solution.orEmpty().flatMap { it.characters }.distinct()
    return fromSolution.ifEmpty { lv.characters }
}

/** Карточка альбома: фон сцены + до 2 героев, подпись — на бумажной полоске под картинкой. */
@Composable
private fun AlbumCard(number: Int, id: String, chapterCover: String?, solved: Boolean, onTap: () -> Unit) {
    val shape = RoundedCornerShape(8.dp)
    Column(Modifier.fillMaxWidth().clip(shape)
        .border(if (solved) 2.dp else 1.dp, if (solved) Palette.gold else Palette.ink.copy(0.3f), shape)
        .clickable(enabled = solved) { onTap() }) {
        Box(Modifier.fillMaxWidth().height(92.dp).clip(RoundedCornerShape(topStart = 8.dp, topEnd = 8.dp))) {
            if (solved) {
                val lv = GameContent.level(id)
                val cover = lv?.let { it.cover ?: it.scenes.firstOrNull() } ?: chapterCover
                Box(Modifier.fillMaxSize().background(Palette.paperEdge))
                cover?.let { ArtImage("scene_$it", Modifier.fillMaxSize(), ContentScale.Crop) }
                Row(Modifier.align(Alignment.BottomCenter), horizontalArrangement = Arrangement.spacedBy((-14).dp),
                    verticalAlignment = Alignment.Bottom) {
                    for (c in remember(id) { albumCast(id).take(2) }) {
                        ArtImage(charDrawable(c), Modifier.height(75.dp).widthIn(max = 70.dp)
                            .shadow(0.dp), ContentScale.Fit)
                    }
                }
            } else {
                Box(Modifier.fillMaxSize().background(Brush.verticalGradient(listOf(Palette.ink.copy(0.85f), Palette.backdrop))),
                    contentAlignment = Alignment.Center) {
                    Text("?", color = Palette.paper.copy(0.35f), fontSize = 30.sp, fontWeight = FontWeight.Black, fontFamily = Fonts.serif)
                }
            }
        }
        Box(Modifier.fillMaxWidth().heightIn(min = 30.dp).background(Palette.panel).padding(horizontal = 4.dp, vertical = 3.dp),
            contentAlignment = Alignment.Center) {
            Text(if (solved) L10n.s("level.$id.title") else "$number", color = if (solved) Palette.ink else Palette.inkSoft,
                fontSize = 10.sp, fontWeight = FontWeight.Bold, fontFamily = Fonts.serif, textAlign = TextAlign.Center,
                maxLines = 2, lineHeight = 12.sp, overflow = TextOverflow.Ellipsis)
        }
    }
}

/** Факт решённой карточки: `level.<id>.fact` и `level.<id>.source`. */
@Composable
private fun AlbumFact(id: String, onClose: () -> Unit) {
    val dismiss = remember { MutableInteractionSource() }
    val swallow = remember { MutableInteractionSource() }
    val fact = L10n.opt("level.$id.fact") ?: GameContent.level(id)?.factCard?.text
    val source = L10n.opt("level.$id.source") ?: GameContent.level(id)?.factCard?.source
    Box(Modifier.fillMaxSize().background(Color.Black.copy(0.5f))
        .clickable(interactionSource = dismiss, indication = null) { onClose() }, contentAlignment = Alignment.Center) {
        BookPage(Modifier.fillMaxWidth(0.9f).fillMaxHeight(0.9f).widthIn(max = 680.dp)
            .clickable(interactionSource = swallow, indication = null) { }) {
            Box(Modifier.align(Alignment.TopEnd).padding(10.dp).size(32.dp).clip(CircleShape)
                .background(Palette.paper).border(1.5.dp, Palette.ink.copy(0.25f), CircleShape)
                .clickable { onClose() }, contentAlignment = Alignment.Center) {
                Icon(Icons.Filled.Close, null, tint = Palette.inkSoft, modifier = Modifier.size(15.dp))
            }
            Column(Modifier.fillMaxSize().padding(horizontal = 24.dp, vertical = 18.dp).verticalScroll(rememberScrollState()),
                horizontalAlignment = Alignment.CenterHorizontally) {
                Text(L10n.s("level.$id.title"), color = Palette.ink, fontSize = 22.sp, fontWeight = FontWeight.Bold,
                    fontFamily = Fonts.serif, textAlign = TextAlign.Center, modifier = Modifier.padding(horizontal = 30.dp))
                if (fact != null) {
                    Spacer(Modifier.height(10.dp))
                    Text(fact, color = Palette.ink, fontSize = 14.sp, fontFamily = Fonts.rounded)
                }
                if (source != null) {
                    Spacer(Modifier.height(8.dp))
                    Text(source, color = Palette.inkSoft, fontSize = 11.sp, fontStyle = FontStyle.Italic, fontFamily = Fonts.rounded)
                }
            }
        }
    }
}
