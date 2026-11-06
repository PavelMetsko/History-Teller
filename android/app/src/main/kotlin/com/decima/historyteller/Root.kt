package com.decima.historyteller

import android.content.Context
import androidx.activity.compose.BackHandler
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.KeyboardArrowLeft
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

// ---- Прогресс (SharedPreferences) ----
class Progress(ctx: Context) {
    private val p = ctx.getSharedPreferences("ht.progress", Context.MODE_PRIVATE)
    fun isCompleted(id: String) = p.getBoolean("done.$id", false)
    fun markCompleted(id: String) = p.edit().putBoolean("done.$id", true).apply()
    fun reset() = p.edit().clear().apply()
    fun solvedCount(ids: List<String>) = ids.count { isCompleted(it) }
    fun isUnlocked(id: String, ordered: List<String>): Boolean {
        if (BuildConfig.DEBUG) return true   // ВРЕМЕННО: в debug-сборках всё открыто для плейтеста
        val i = ordered.indexOf(id)
        if (i <= 0) return true
        // Уже пройденный уровень открыт всегда: иначе вставка новых уровней в начало главы
        // (приквел к Риму) заперла бы прогресс тех, кто прошёл главу до обновления.
        return isCompleted(id) || isCompleted(ordered[i - 1])
    }
}

sealed class Screen {
    data object Menu : Screen()
    data object Chapters : Screen()
    data class Map(val epoch: String) : Screen()
    data class Level(val id: String) : Screen()
    data object Album : Screen()
    data object Streak : Screen()
}

/** Все уровни из манифеста (включая главы, которые ещё не скачаны), без выключенных. */
private fun allLevelIds(): List<String> =
    ContentSync.availableChapters().flatMap { it.levels }.filterNot { ContentSync.isLevelDisabled(it) }
        .ifEmpty { GameContent.levels.map { it.id } }

@Composable
fun Root(startLevel: String? = null) {
    val ctx = LocalContext.current
    val progress = remember { Progress(ctx) }
    val settings = remember { Settings(ctx) }
    var tick by remember { mutableIntStateOf(0) }
    var showSettings by remember { mutableStateOf(false) }
    /** Глава, для которой открыто окно «Без рекламы» (поглавная покупка). */
    var premiumEpoch by remember { mutableStateOf<String?>(null) }
    var showGift by remember { mutableStateOf(false) }
    /** Эпизод дня из чужой, ещё не скачанной главы: после загрузки её описаний — сразу в уровень. */
    var levelAfterIndex by remember { mutableStateOf<String?>(null) }
    var screen by remember { mutableStateOf<Screen>(if (startLevel != null) Screen.Level(startLevel) else Screen.Menu) }
    // Первый запуск: выбор языка → онбординг (пропускаем при deep-link на уровень).
    // Поднимаем ТОЛЬКО после загрузки контента: раньше эти экраны всплывали поверх загрузки,
    // и новичка встречали голые ключи — каталог переводов в этот момент ещё ехал.
    var showLangPicker by remember { mutableStateOf(false) }
    var showOnboarding by remember { mutableStateOf(false) }
    var loadingEpoch by remember { mutableStateOf<String?>(null) }
    var loadingLevel by remember { mutableStateOf<String?>(null) }

    // Системная кнопка «назад» повторяет навигацию лент; на Меню — выход из app (не перехватываем).
    BackHandler(enabled = screen != Screen.Menu) {
        screen = when (val s = screen) {
            Screen.Chapters -> Screen.Menu
            Screen.Album -> Screen.Menu
            Screen.Streak -> Screen.Menu
            is Screen.Map -> Screen.Chapters
            is Screen.Level -> Screen.Map(GameContent.level(s.id)?.epoch ?: "rome")
            Screen.Menu -> Screen.Menu
        }
    }

    // Старт: подтянуть манифест и core, затем собрать контент. Офлайн с пустым кешем —
    // единственный случай, когда игру показать нечем; иначе работаем на уже скачанном.
    var booted by remember { mutableStateOf(false) }
    var bootAttempt by remember { mutableIntStateOf(0) }
    var bootError by remember { mutableStateOf<String?>(null) }
    LaunchedEffect(bootAttempt) {
        Telemetry.track("session")
        ContentSync.syncCore(ctx)
        // Вшитого контента больше нет: если core не приехал, собирать нечего — остаёмся
        // на экране загрузки с кнопкой «Повторить», а не падаем на первом же чтении.
        runCatching { GameContent.load(ctx.assets, langOverride = settings.lang.ifEmpty { null }) }
            .onSuccess {
                // Мета 4.0: стартовые подсказки и опыт за пройденное — один раз.
                Meta.bootstrap(progress.solvedCount(allLevelIds()))
                booted = true; tick++
                if (!settings.onboarded && startLevel == null) showLangPicker = true
                // Согласие спрашиваем после онбординга; кто его уже прошёл — сразу на старте.
                if (settings.onboarded) (ctx as? android.app.Activity)?.let { ConsentService.start(it) }
            }
            .onFailure { bootError = it.message ?: L10n.s("ui.load_fail") }
    }

    /** В уровень — сразу, если файлы уже на диске, иначе через экран загрузки. */
    fun openLevel(id: String) {
        if (ContentSync.isLevelReady(id)) screen = Screen.Level(id) else loadingLevel = id
    }

    // Подарок дня — при открытии меню, если сегодня ещё не забирали. Не поверх выбора языка
    // и онбординга: новичок увидит его сразу после них.
    LaunchedEffect(booted, screen, showLangPicker, showOnboarding) {
        if (booted && screen == Screen.Menu && !showLangPicker && !showOnboarding && Meta.giftAvailable) showGift = true
    }

    // Отступы под системные панели и вырез — один раз на всё приложение, после фона: подложка
    // остаётся во весь экран, а содержимое (включая онбординг, выбор языка и экран загрузки)
    // не лезет под статус-бар. Раньше их вешали точечно, и накрыто было далеко не всё.
    Box(Modifier.fillMaxSize().background(Palette.backdrop).safeDrawingPadding(),
        contentAlignment = Alignment.Center) {
        if (!booted) {
            BootScreen(bootError, onRetry = { bootError = null; bootAttempt++ })
            return@Box
        }
    fun restoreStreak() {
        val days = Meta.brokenStreak ?: return
        fun restore() {
            Meta.restoreStreak()
            Telemetry.track("streak_restore", days.toString())
            Audio.sfx("win")
        }
        // Без ролика — только подписчикам 3.x.
        if (Billing.subscribed) restore()
        else (ctx as? android.app.Activity)?.let { a -> AdService.show(a) { ok -> if (ok) restore() } }
    }
        BoxWithConstraints(Modifier.fillMaxSize()) {
            val stageH = if (maxWidth / maxHeight >= 1.7f) maxHeight else maxWidth / 1.7f
            Box(Modifier.width(maxWidth).height(stageH).align(Alignment.Center)) {
                key(tick) {
                    when (val s = screen) {
                        Screen.Menu -> MenuScreen(
                            progress = progress,
                            onPlay = { screen = Screen.Chapters },
                            onAlbum = { screen = Screen.Album },
                            onSettings = { showSettings = true },
                            onReset = { progress.reset(); Meta.reset(); Daily.invalidate(); tick++ },
                            onDaily = { ch, id ->
                                Telemetry.track("daily_open", id, ch)
                                // Эпизод дня обходит линейный замок главы: открываем его напрямую.
                                if (GameContent.level(id) != null && ContentSync.isChapterIndexReady(ch)) openLevel(id)
                                else { levelAfterIndex = id; loadingEpoch = ch }
                            },
                            onRestoreStreak = { restoreStreak() },
                            onStreak = { screen = Screen.Streak })
                        Screen.Streak -> StreakRoadScreen(onRestore = { restoreStreak() }, onBack = { screen = Screen.Menu })
                        Screen.Album -> AlbumScreen(progress = progress, onBack = { screen = Screen.Menu })
                        Screen.Chapters -> ChaptersScreen(
                            progress = progress,
                            onSelect = { if (ContentSync.isChapterIndexReady(it)) screen = Screen.Map(it) else loadingEpoch = it },
                            onBack = { screen = Screen.Menu })
                        is Screen.Map -> {
                            // Фоновая докачка открытой главы — с того эпизода, куда игрок пойдёт
                            // дальше. Карта уже на экране, картинки наливаются на глазах.
                            LaunchedEffect(s.epoch) {
                                val ids = GameContent.levels(s.epoch).map { it.id }
                                ContentSync.prefetchChapter(ctx, s.epoch,
                                    ids.firstOrNull { progress.isUnlocked(it, ids) && !progress.isCompleted(it) })
                            }
                            MapScreen(
                                epoch = s.epoch, progress = progress,
                                onNoAds = { premiumEpoch = s.epoch },
                                // С 4.0 все главы бесплатны: замок — только линейный, внутри главы.
                                // Обычно фон успевает раньше игрока и экран загрузки не нужен;
                                // если нет — ждём здесь, а не перед входом в главу.
                                onSelect = { id -> openLevel(id) },
                                onBack = { ContentSync.cancelPrefetch(); screen = Screen.Chapters })
                        }
                        is Screen.Level -> {
                          val epoch = GameContent.level(s.id)?.epoch ?: "rome"
                          LaunchedEffect(s.id) {
                              Meta.lastLevel = s.id
                              Telemetry.track("level_start", s.id, epoch)
                          }
                          // Следующий эпизод главы — для кнопки «Следующий эпизод ▶» на экране награды.
                          val nextId = remember(s.id) {
                              val ids = GameContent.levels(epoch).map { it.id }
                              ids.getOrNull(ids.indexOf(s.id) + 1)
                          }
                          fun toMap() {
                              screen = Screen.Map(epoch)
                              // Просьба оценить игру — после выхода с уровня, когда награда уже прочитана.
                              val done = GameContent.levels.filter { progress.isCompleted(it.id) }
                              if (ReviewPrompt.shouldAsk(ctx, done.size, done.map { it.epoch }.distinct().size)) {
                                  (ctx as? android.app.Activity)?.let { ReviewPrompt.ask(it) }
                              }
                          }
                          BoardScreen(
                            levelId = s.id,
                            nextLevelId = nextId,
                            onSolved = {
                                val first = !progress.isCompleted(s.id)
                                // Эпизод дня — до отметки «пройден»: пул дня пройденные исключает.
                                val daily = Daily.isDaily(progress, s.id)
                                val r = Meta.recordSolve(s.id, firstSolve = first, isDaily = daily)
                                progress.markCompleted(s.id)
                                Meta.noteLevelFinished()
                                Telemetry.track("level_complete", s.id, epoch)
                                if (r.isDaily) Telemetry.track("daily_done", s.id, epoch)
                                if (r.rankedUp) Telemetry.track("rank_up", "${r.levelAfter}", epoch)
                                runCatching { Notifications.reschedule(ctx) }
                                if (first) r else null
                            },
                            onExit = { toMap() },
                            onRewardDone = { goNext ->
                                val activity = ctx as? android.app.Activity
                                AdService.showInterstitialIfDue(activity, progress.solvedCount(allLevelIds()), s.id, epoch) {
                                    if (goNext && nextId != null) openLevel(nextId) else toMap()
                                    // Разрешение на напоминания — один раз, после первого экрана награды
                                    // (порядок как на iOS: интерстишел → переход → системный запрос).
                                    Notifications.askOnce(activity)
                                }
                            },
                            onPremium = { premiumEpoch = it })
                        }
                    }
                }
            }
        }

        if (showSettings) SettingsScreen(
            settings = settings,
            onLangChange = { code ->
                GameContent.load(ctx.assets, langOverride = code.ifEmpty { null })
                tick++   // перерисовать экраны под новым языком
            },
            onClose = { showSettings = false })

        if (showGift && screen == Screen.Menu && !showLangPicker && !showOnboarding) GiftPopup(onClaimed = { showGift = false })

        premiumEpoch?.let { ep -> PremiumScreen(ep, onClose = { premiumEpoch = null }) }

        // Экран загрузки главы (порт iOS ChapterLoadingView).
        loadingEpoch?.let { ep ->
            ChapterLoadingScreen(
                job = LoadJob.ChapterIndex(ep),
                title = L10n.s("map.$ep"),
                onReady = {
                    // Описания уровней приезжают вместе с главой — контент надо пересобрать,
                    // иначе глава откроется пустой.
                    runCatching { GameContent.load(ctx.assets, langOverride = settings.lang.ifEmpty { null }) }
                    loadingEpoch = null
                    // Пришли из эпизода дня — сразу в уровень, мимо карты и её линейного замка.
                    val target = levelAfterIndex; levelAfterIndex = null
                    if (target != null && GameContent.level(target) != null) openLevel(target)
                    else screen = Screen.Map(ep)
                    tick++
                })
        }

        loadingLevel?.let { id ->
            ChapterLoadingScreen(
                job = LoadJob.Level(id),
                title = GameContent.level(id)?.title ?: "",
                onReady = {
                    loadingLevel = null
                    // Не доехало (офлайн, «Отмена») — остаёмся на карте, а не открываем пустую доску.
                    if (ContentSync.isLevelReady(id)) { screen = Screen.Level(id); tick++ }
                })
        }

        // Первый запуск: выбор языка → онбординг.
        if (showLangPicker) LanguagePickerScreen(onSelect = { code ->
            settings.lang = code
            GameContent.load(ctx.assets, code)
            tick++
            showLangPicker = false; showOnboarding = true
        })
        if (showOnboarding) OnboardingScreen(onFinish = {
            settings.onboarded = true; showOnboarding = false
            (ctx as? android.app.Activity)?.let { ConsentService.start(it) }
        })
    }
}

@Composable
internal fun IconButtonCircle(icon: androidx.compose.ui.graphics.vector.ImageVector, modifier: Modifier = Modifier, onClick: () -> Unit) {
    Box(modifier.size(44.dp).clip(CircleShape).background(Palette.paper)
        .border(1.5.dp, Palette.ink.copy(alpha = 0.3f), CircleShape).clickable { onClick() },
        contentAlignment = Alignment.Center) {
        Icon(icon, null, tint = Palette.ink.copy(alpha = 0.7f), modifier = Modifier.size(20.dp))
    }
}

// ---- Выбор главы ----
private data class Chapter(val id: String, val number: Int, val cover: String?, val available: Boolean)

@Composable
private fun ChaptersScreen(progress: Progress, onSelect: (String) -> Unit, onBack: () -> Unit) {
    // Список глав задаёт манифест — иначе глава, выложенная в облако, не появилась бы в меню.
    // Без манифеста (первый запуск офлайн) показываем то, что лежит в бандле.
    val fromManifest = ContentSync.availableChapters()
    val chapters = if (fromManifest.isEmpty()) {
        listOf(Chapter("rome", 1, "scene_forum", true))
    } else {
        fromManifest.map { Chapter(it.id, it.number, "scene_${it.cover}", true) }
    }
    Box(Modifier.fillMaxSize().padding(16.dp)) {
        BookPage(Modifier.fillMaxSize()) {
            Column(Modifier.fillMaxSize().padding(20.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                Text("History Teller", color = Palette.ink, fontSize = 26.sp, fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
                Text(L10n.s("ui.choose_epoch"), color = Palette.inkSoft, fontSize = 12.sp, fontFamily = Fonts.rounded)
                Spacer(Modifier.height(16.dp))
                Row(Modifier.fillMaxWidth().weight(1f).horizontalScroll(rememberScrollState())
                        .padding(horizontal = 8.dp),
                    horizontalArrangement = Arrangement.spacedBy(20.dp, Alignment.CenterHorizontally),
                    verticalAlignment = Alignment.CenterVertically) {
                    for (ch in chapters) {
                        // С 4.0 все главы бесплатны — ни цены, ни замка на карточке.
                        ChapterCard(ch, progress) {
                            if (ch.available) onSelect(ch.id)
                        }
                    }
                }
            }
            BackButton(Modifier.align(Alignment.TopStart), onBack)
        }
    }
}

@Composable
private fun ChapterCard(ch: Chapter, progress: Progress, onTap: () -> Unit) {
    // Всего уровней берём из манифеста: файлы уровней приезжают вместе с главой,
    // и до входа в неё пак пуст — на карточке было «0 из 0».
    val ls = ContentSync.availableChapters().firstOrNull { it.id == ch.id }?.levels
        ?: GameContent.levels(ch.id).map { it.id }
    val clickable = ch.available
    // Карточка тянется по высоте строки, а обложка забирает остаток: при фиксированных 150 dp
    // на невысоком экране карточка не влезала и обрезалась ровно по середине названия.
    Column(
        Modifier.width(210.dp).fillMaxHeight().heightIn(max = 240.dp)
            .clip(RoundedCornerShape(16.dp)).background(Palette.paper)
            .border(2.5.dp, Palette.ink.copy(alpha = if (ch.available) 0.6f else 0.35f), RoundedCornerShape(16.dp))
            .clickable(enabled = clickable) { onTap() }
    ) {
        Box(Modifier.fillMaxWidth().weight(1f).background(Palette.panel), contentAlignment = Alignment.Center) {
            if (ch.cover != null && ch.available) {
                ArtImage(ch.cover, Modifier.fillMaxSize(), ContentScale.Crop)
            }
            if (!ch.available)
                Icon(Icons.Filled.Lock, null, tint = Palette.ink.copy(alpha = 0.5f), modifier = Modifier.size(26.dp))
        }
        // Подписи с отступами и переносом: карточка фиксированной ширины, а названия глав на
        // разных языках сильно разной длины — без этого «Французская революция» обрезалась
        // прямо по букве, упираясь в край карточки.
        Column(Modifier.fillMaxWidth().padding(horizontal = 10.dp, vertical = 8.dp),
            horizontalAlignment = Alignment.CenterHorizontally) {
            Text(L10n.s("chapter.${ch.id}.title"), color = if (ch.available) Palette.ink else Palette.inkSoft,
                fontSize = 17.sp, fontWeight = FontWeight.Bold, fontFamily = Fonts.serif, maxLines = 2,
                lineHeight = 20.sp, overflow = TextOverflow.Ellipsis, textAlign = TextAlign.Center)
            Text(L10n.s("chapter.${ch.id}.subtitle"), color = Palette.inkSoft, fontSize = 10.sp,
                fontFamily = Fonts.rounded, maxLines = 2, lineHeight = 13.sp,
                overflow = TextOverflow.Ellipsis, textAlign = TextAlign.Center)
            when {
                !ch.available -> Text(L10n.s("ui.soon"), color = Palette.maroon, fontSize = 11.sp, fontFamily = Fonts.rounded)
                else -> Text(L10n.s("ui.progress", progress.solvedCount(ls), ls.size),
                    color = Palette.success, fontSize = 10.sp, fontFamily = Fonts.rounded)
            }
        }
    }
}

// ---- Карта уровней (акты + адаптивная сетка) ----
@OptIn(androidx.compose.foundation.layout.ExperimentalLayoutApi::class)
@Composable
private fun MapScreen(epoch: String, progress: Progress, onNoAds: () -> Unit, onSelect: (String) -> Unit, onBack: () -> Unit) {
    val levels = GameContent.levels(epoch)
    val orderedIds = levels.map { it.id }
    val sections = remember(levels) {
        val out = ArrayList<Pair<String?, MutableList<Pair<Int, teller.engine.LevelDef>>>>()
        levels.forEachIndexed { idx, lv ->
            if (out.isNotEmpty() && out.last().first == lv.act) out.last().second.add(idx to lv)
            else out.add(lv.act to mutableListOf(idx to lv))
        }
        out
    }
    Box(Modifier.fillMaxSize().padding(16.dp)) {
        BookPage(Modifier.fillMaxSize()) {
            Column(Modifier.fillMaxSize().padding(horizontal = 26.dp, vertical = 14.dp)) {
                Text(L10n.s("map.$epoch"), color = Palette.ink, fontSize = 26.sp, fontWeight = FontWeight.Bold,
                    fontFamily = Fonts.serif, modifier = Modifier.align(Alignment.CenterHorizontally))
                Text(L10n.s("ui.progress", progress.solvedCount(orderedIds), levels.size),
                    color = Palette.inkSoft, fontSize = 12.sp, fontFamily = Fonts.rounded,
                    modifier = Modifier.align(Alignment.CenterHorizontally))
                // «Глава без рекламы» — только пока не куплена и цена приехала из Play.
                val price = Billing.chapterPrice(epoch)
                if (!Premium.adsFree(epoch) && price.isNotEmpty()) {
                    Row(Modifier.align(Alignment.CenterHorizontally).padding(top = 4.dp)
                            .clip(RoundedCornerShape(50)).background(Palette.maroon)
                            .border(1.5.dp, Palette.gold, RoundedCornerShape(50))
                            .clickable { onNoAds() }.padding(horizontal = 14.dp, vertical = 6.dp),
                        verticalAlignment = Alignment.CenterVertically) {
                        Text("👑 " + L10n.s("ui.chapter_noads_cta", price), color = Palette.paper, fontSize = 12.sp,
                            fontFamily = Fonts.rounded)
                    }
                }
                Spacer(Modifier.height(10.dp))
                // автоскролл к секции с текущим (открытым, но не пройденным) эпизодом — в т.ч. после «Дальше»
                val listState = rememberLazyListState()
                val targetSection = run {
                    val targetId = orderedIds.firstOrNull { progress.isUnlocked(it, orderedIds) && !progress.isCompleted(it) }
                    if (targetId == null) 0
                    else sections.indexOfFirst { (_, e) -> e.any { it.second.id == targetId } }.coerceAtLeast(0)
                }
                LaunchedEffect(Unit) { if (targetSection > 0) listState.animateScrollToItem(targetSection) }
                LazyColumn(state = listState, verticalArrangement = Arrangement.spacedBy(14.dp)) {
                    items(sections) { (act, entries) ->
                        Column {
                            if (act != null) ActHeader(act)
                            androidx.compose.foundation.layout.FlowRow(
                                horizontalArrangement = Arrangement.spacedBy(16.dp),
                                verticalArrangement = Arrangement.spacedBy(16.dp)
                            ) {
                                for ((idx, lv) in entries) {
                                    LevelCard(
                                        number = idx + 1, level = lv,
                                        completed = progress.isCompleted(lv.id),
                                        unlocked = progress.isUnlocked(lv.id, orderedIds),
                                        onTap = { onSelect(lv.id) })
                                }
                            }
                        }
                    }
                }
            }
            BackButton(Modifier.align(Alignment.TopStart), onBack)
        }
    }
}

@Composable
private fun ActHeader(title: String) {
    Row(Modifier.fillMaxWidth().padding(vertical = 6.dp), verticalAlignment = Alignment.CenterVertically) {
        Box(Modifier.weight(1f).height(1.5.dp).background(Palette.gold.copy(alpha = 0.5f)))
        Text(title.uppercase(), color = Palette.maroon, fontSize = 14.sp, fontWeight = FontWeight.Bold,
            fontFamily = Fonts.serif, letterSpacing = 1.5.sp, modifier = Modifier.padding(horizontal = 12.dp))
        Box(Modifier.weight(1f).height(1.5.dp).background(Palette.gold.copy(alpha = 0.5f)))
    }
}

@Composable
private fun LevelCard(number: Int, level: teller.engine.LevelDef, completed: Boolean, unlocked: Boolean, onTap: () -> Unit) {
    Column(
        Modifier.width(230.dp).clip(RoundedCornerShape(14.dp)).background(Palette.paper)
            .border(2.dp, Palette.ink.copy(alpha = if (unlocked) 0.6f else 0.35f), RoundedCornerShape(14.dp))
            .clickable(enabled = unlocked) { onTap() }.padding(8.dp)
    ) {
        Box(Modifier.fillMaxWidth().aspectRatio(16f / 9f).clip(RoundedCornerShape(10.dp)).background(Palette.panel),
            contentAlignment = Alignment.Center) {
            val cover = level.cover ?: level.scenes.firstOrNull()
            val coverPainter = if (cover != null) artPainter("scene_$cover") else null
            if (coverPainter != null) Image(coverPainter, null, Modifier.fillMaxSize(), contentScale = ContentScale.Crop)
            if (!unlocked) {
                Box(Modifier.fillMaxSize().background(Color.Black.copy(alpha = 0.4f)), contentAlignment = Alignment.Center) {
                    Icon(Icons.Filled.Lock, null, tint = Color.White.copy(alpha = 0.9f), modifier = Modifier.size(26.dp))
                }
            } else if (completed) {
                Box(Modifier.fillMaxSize().padding(6.dp), contentAlignment = Alignment.TopEnd) {
                    Box(Modifier.size(24.dp).clip(CircleShape).background(Palette.success), contentAlignment = Alignment.Center) {
                        Icon(Icons.Filled.Check, null, tint = Color.White, modifier = Modifier.size(15.dp))
                    }
                }
            }
        }
        Text("$number. ${level.title}", color = if (unlocked) Palette.ink else Palette.inkSoft,
            fontSize = 12.sp, fontWeight = FontWeight.Bold, fontFamily = Fonts.serif,
            textAlign = TextAlign.Center, maxLines = 2,
            modifier = Modifier.fillMaxWidth().padding(top = 6.dp))
    }
}

@Composable
internal fun BackButton(modifier: Modifier, onBack: () -> Unit) {
    Box(modifier.offset(x = 42.dp, y = (-4).dp).size(width = 40.dp, height = 52.dp)
        .shadow(3.dp, RibbonShape).clip(RibbonShape).background(Palette.ribbon)
        .border(1.5.dp, Palette.ink.copy(alpha = 0.35f), RibbonShape)
        .clickable { onBack() }, contentAlignment = Alignment.Center) {
        Icon(Icons.Filled.KeyboardArrowLeft, null, tint = Color.White,
            modifier = Modifier.size(22.dp).offset(y = (-4).dp))
    }
}
