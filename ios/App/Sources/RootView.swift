import SwiftUI
import StoreKit
import Simulation
import GameContent
import GameProgress
import MenuFeature
import EpochMapFeature
import LevelFeature
import DesignSystem
import Ads

/// Координатор экранов: меню → выбор эпохи → карта уровней → уровень. Прогресс в UserDefaults.
struct RootView: View {
    @State private var pack: RomeContent.Pack?
    @State private var loadError: String?
    @State private var progress = ProgressStore()
    @State private var selectedEpoch = ProcessInfo.processInfo.environment["HT_EPOCH"] ?? "rome"
    @State private var store = Store.shared
    @State private var meta = Meta.shared
    /// Окно «глава без рекламы» для этой главы.
    @State private var premiumEpoch: String?
    /// Подсказки кончились: что применить, если игрок досмотрит ролик.
    @State private var hintRequest: HintRequest?
    /// Первое решение эпизода ждёт экрана награды (показываем при уходе с доски).
    @State private var pendingReward: PendingReward?
    @State private var reward: PendingReward?
    @State private var showGift = false
    /// Эпизод дня, открытый из меню: за его решение — двойной опыт.
    @State private var dailyActive: String?
    /// Уровень, который открыть сразу, как только приедут описания главы (эпизод дня из меню).
    @State private var levelAfterIndex: String?
    @Environment(\.scenePhase) private var scenePhase
    @State private var sync = ContentSync.shared
    @State private var loadingEpoch: String?
    @State private var loadingLevel: String?
    @AppStorage("ht.onboarded") private var onboarded = false
    @State private var showOnboarding = false
    /// Первый запуск уже предложен в этой сессии. Выбор языка пишет `langOverride`, на его
    /// изменение пак сбрасывается и boot идёт заново — без флага выбор языка всплывал дважды.
    @State private var firstRunOffered = false
    @State private var showLanguagePicker = false
    @AppStorage("ht.lang") private var langOverride = ""
    @State private var screen: Screen = {
        let env = ProcessInfo.processInfo.environment
        if let id = env["HT_LEVEL"] { return .level(id) }
        switch env["HT_SCREEN"] {
        case "map": return .map
        case "chapters": return .chapters
        default: return .menu
        }
    }()

    private enum Screen: Equatable {
        case menu
        case chapters
        case map
        case album
        case streak
        case level(String)
    }

    private struct HintRequest {
        let levelId: String
        let apply: () -> Void
    }

    private struct PendingReward {
        let levelId: String
        let epoch: String
        let reward: Meta.SolveReward
    }

    var body: some View {
        ZStack {
            DS.Palette.backdrop.ignoresSafeArea()

            // Контент рендерим в landscape-«сцене» с ограничением соотношения сторон:
            // на iPhone заполняет экран, на «квадратном» iPad — центрированная полоса
            // (иначе панели/меню растягиваются в пустоту).
            GeometryReader { geo in
                let stage = stageSize(geo.size)
                content
                    .frame(width: stage.width, height: stage.height)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                    .transition(.opacity)
            }

            if let r = reward, let pack { rewardOverlay(r, pack).zIndex(25) }

            if let req = hintRequest {
                HintsOutView(
                    onWatch: {
                        AdService.shared.show { ok in
                            guard ok else { return }
                            meta.markHinted(req.levelId)
                            req.apply()
                            Telemetry.shared.track("hint_ad", level: req.levelId, chapter: selectedEpoch)
                        }
                        withAnimation(.easeOut(duration: 0.2)) { hintRequest = nil }
                    },
                    onPremium: {
                        withAnimation(.easeOut(duration: 0.2)) { hintRequest = nil }
                        openPremium(selectedEpoch)
                    },
                    onClose: { withAnimation(.easeOut(duration: 0.2)) { hintRequest = nil } }
                )
                .transition(.opacity)
                .zIndex(28)
            }

            if let ep = premiumEpoch {
                PremiumView(epoch: ep, chapterTitle: L10n.s("chapter.\(ep).title"),
                            onClose: { withAnimation(.easeOut(duration: 0.2)) { premiumEpoch = nil } })
                    .transition(.opacity)
                    .zIndex(30)
            }

            if showGift {
                GiftView(step: meta.nextGiftStep, gifts: Meta.gifts, onClaim: {
                    let n = meta.claimGift()
                    Telemetry.shared.track("gift_claim", level: "\(n)")
                    withAnimation(.easeOut(duration: 0.25)) { showGift = false }
                })
                .transition(.opacity)
                .zIndex(35)
            }

            if let ep = loadingEpoch, let pack {
                ChapterLoadingView(
                    job: .chapterIndex(ep),
                    chapterTitle: chapterTitle(ep),
                    demoLevel: demoLevel(pack),
                    db: pack.db,
                    onReady: {
                        // Описания уровней приезжают вместе с главой — пак надо пересобрать,
                        // иначе глава откроется пустой.
                        load()
                        selectedEpoch = ep
                        loadingEpoch = nil
                        if let id = levelAfterIndex {
                            levelAfterIndex = nil
                            openLevel(id)
                        } else {
                            go(.map)
                        }
                    }
                )
                .transition(.opacity)
                .zIndex(40)
            }

            if let id = loadingLevel, let pack {
                ChapterLoadingView(
                    job: .level(id),
                    chapterTitle: pack.levels.first { $0.id == id }?.title ?? chapterTitle(selectedEpoch),
                    demoLevel: demoLevel(pack),
                    db: pack.db,
                    onReady: {
                        let target = id
                        loadingLevel = nil
                        // Не доехало (офлайн, «Отмена») — остаёмся на карте, а не открываем пустую доску.
                        if sync.isLevelReady(target) { go(.level(target)) } else { startPrefetch() }
                    }
                )
                .transition(.opacity)
                .zIndex(40)
            }

            if showOnboarding {
                OnboardingView(level: pack.flatMap { demoLevel($0) }, db: pack?.db, onFinish: {
                    onboarded = true
                    withAnimation(.easeOut(duration: 0.25)) { showOnboarding = false }
                    ConsentService.shared.start()
                    maybeOfferGift()
                })
                .transition(.opacity)
                .zIndex(50)
            }

            if showLanguagePicker {
                LanguagePickerView(onSelect: { code in
                    L10n.setLanguage(code)
                    langOverride = code   // сохраняет выбор и пересобирает пак на новом языке
                    withAnimation(.easeInOut(duration: 0.3)) {
                        showLanguagePicker = false
                        showOnboarding = true
                    }
                })
                .transition(.opacity)
                .zIndex(60)
            }
        }
        .onAppear {
            // Согласие спрашиваем после онбординга; кто его уже прошёл — сразу на старте.
            if onboarded { ConsentService.shared.start() }
            meta.bootstrap(solvedCount: progress.solvedCount)
            AdService.shared.onFullscreenShown = { Meta.shared.noteFullscreenShown() }
            if ProcessInfo.processInfo.environment["HT_PAYWALL"] == "1" { premiumEpoch = ProcessInfo.processInfo.environment["HT_EPOCH"] ?? "tudor" }
        }
        .onChange(of: screen) { _, now in
            updateMusic()
            if now == .menu { maybeOfferGift() }
        }
        .onChange(of: scenePhase) { _, phase in
            if phase == .background { rescheduleNotifications() }
        }
        .onChange(of: langOverride) { _, _ in
            // Смена языка: пересобрать пак (контент локализуется на загрузке) и перерисовать UI.
            pack = nil; loadError = nil
        }
    }

    /// Музыка сквозняком: тема настроения уровня, иначе базовая. Один трек не перезапускается.
    /// Ограничение «сцены» по минимальному соотношению сторон (ширина/высота).
    /// Экран элонгированнее — заполняем; «квадратнее» (iPad) — центрируем полосу.
    private func stageSize(_ s: CGSize) -> CGSize {
        let minAspect: CGFloat = 1.7
        guard s.height > 0 else { return s }
        return (s.width / s.height) >= minAspect ? s : CGSize(width: s.width, height: s.width / minAspect)
    }

    private func updateMusic() {
        guard let pack else { return }
        let track: String
        switch screen {
        case .level(let id):
            track = pack.levels.first { $0.id == id }?.music ?? "theme"
        default:
            track = "theme"
        }
        Audio.shared.startMusic(named: track)
    }

    @ViewBuilder private var content: some View {
        if let pack {
            switch screen {
            case .menu:
                MenuView(
                    meta: menuMeta(pack),
                    onPlay: { go(.chapters) },
                    onReset: { progress.reset(); meta.reset() },
                    onAlbum: { go(.album) },
                    onDaily: { openDaily() },
                    onStreak: { go(.streak) },
                    onRestoreStreak: { restoreStreak() }
                )
                .onAppear { maybeOfferGift() }
            case .chapters:
                ChapterSelectView(
                    chapters: chapters(pack),
                    onSelect: { ch in
                        guard ch.available else { return }
                        openChapter(ch.id)
                    },
                    onBack: { go(.menu) }
                )
            case .map:
                EpochMapView(
                    title: chapterTitle(selectedEpoch),
                    levels: pack.levels(epoch: selectedEpoch),
                    db: pack.db,
                    progress: progress,
                    noAdsTitle: noAdsTitle(selectedEpoch),
                    onNoAds: { openPremium(selectedEpoch) },
                    onSelect: { dailyActive = nil; openLevel($0) },
                    onBack: { sync.cancelPrefetch(); go(.chapters) }
                )
                .onAppear { startPrefetch() }
            case .album:
                AlbumView(
                    sections: sync.availableChapters.map {
                        AlbumView.Section(id: $0.id, title: L10n.s("chapter.\($0.id).title"), levels: $0.levels)
                    },
                    initial: selectedEpoch,
                    isCompleted: { progress.isCompleted($0) },
                    cover: { id in pack.levels.first { $0.id == id }.flatMap { $0.cover ?? $0.scenes.first } },
                    cast: { id in
                        // Герои кадра — из эталона (кто реально в сцене), иначе из состава уровня.
                        guard let lv = pack.levels.first(where: { $0.id == id }) else { return [] }
                        var seen = Set<String>()
                        let fromSolution = (lv.solution ?? []).flatMap(\.characters).filter { seen.insert($0).inserted }
                        return fromSolution.isEmpty ? lv.characters : fromSolution
                    },
                    onClose: { go(.menu) }
                )
            case .streak:
                StreakRoadView(streak: meta.currentStreak, best: meta.bestStreak, solvedToday: meta.solvedToday,
                               brokenStreak: meta.brokenStreak, freeRestore: store.subscribed,
                               onRestore: { restoreStreak() }, onClose: { go(.menu) })
            case .level(let id):
                if let level = pack.levels.first(where: { $0.id == id }) {
                    LevelBoardView(
                        level: level,
                        db: pack.db,
                        hint: HintConfig(badge: store.adsFree(level.epoch) ? "∞" : "\(meta.hints)",
                                         request: { apply in requestHint(id, apply) }),
                        onSolved: { solved(level) },
                        onExit: {
                            if let r = pendingReward, r.levelId == id {
                                pendingReward = nil
                                withAnimation(.spring(response: 0.45, dampingFraction: 0.8)) { reward = r }
                            } else {
                                go(.map); maybeAskForReview(pack)
                            }
                        }
                    )
                    .onAppear {
                        meta.lastLevel = id
                        Telemetry.shared.track("level_start", level: id, chapter: level.epoch)
                    }
                    .id(id)
                } else {
                    Color.clear.onAppear { go(.map) }
                }
            }
        } else if let loadError {
            errorView(loadError)
        } else {
            bootView.task { await boot() }
        }
    }

    /// Просьба оценить игру в магазине. Зовём после выхода с уровня — игрок только что выиграл
    /// и закрыл факт-карточку; правила («втянулся», «не чаще раза в сутки») живут в ReviewPrompt.
    private func maybeAskForReview(_ pack: RomeContent.Pack) {
        let epochs = Set(pack.levels.filter { progress.isCompleted($0.id) }.map(\.epoch))
        guard ReviewPrompt.shouldAsk(solvedCount: progress.solvedCount, chaptersTouched: epochs.count) else { return }
        ReviewPrompt.recordAsked()
        // Небольшая пауза: окно магазина поверх анимации возврата на карту выглядит рвано.
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.2) {
            guard let scene = UIApplication.shared.connectedScenes
                .first(where: { $0.activationState == .foregroundActive }) as? UIWindowScene else { return }
            AppStore.requestReview(in: scene)
        }
    }

    private func chapters(_ pack: RomeContent.Pack) -> [Chapter] {
        // Всего уровней берём из манифеста, а не из загруженного пака: файлы уровней приезжают
        // вместе с главой, и до входа в неё пак пуст — на карточке было «0 из 0».
        func prog(_ epoch: String) -> String {
            let ids = sync.availableChapters.first { $0.id == epoch }?.levels
                ?? pack.levels(epoch: epoch).map(\.id)
            let done = ids.filter { progress.isCompleted($0) }.count
            return L10n.s("ui.progress", done, ids.count)
        }
        func ch(_ id: String, _ n: Int, _ cover: String?, _ icon: String, _ available: Bool) -> Chapter {
            let ids = sync.availableChapters.first { $0.id == id }?.levels ?? pack.levels(epoch: id).map(\.id)
            return Chapter(id: id, number: n,
                           title: L10n.s("chapter.\(id).title"),
                           subtitle: L10n.s("chapter.\(id).subtitle"),
                           coverSceneId: cover, icon: icon,
                           available: available,
                           progressText: available ? prog(id) : nil,
                           done: ids.filter { progress.isCompleted($0) }.count, total: ids.count)
        }
        // Список глав задаёт манифест — иначе глава, выложенная в облако, не появилась бы в меню.
        // Без манифеста (первый запуск офлайн) показываем то, что лежит в бандле.
        let fromManifest = ContentSync.shared.availableChapters
        guard !fromManifest.isEmpty else {
            return [ch("rome", 1, "forum", "building.columns.fill", true)]
        }
        return fromManifest.map { ch($0.id, $0.number, $0.cover, $0.icon, true) }
    }

    private func chapterTitle(_ epoch: String) -> String {
        L10n.s("map.\(epoch)")
    }

    /// Открыть главу. Ждать нечего, кроме описаний уровней: арт главы едет фоном уже на карте,
    /// а до появления поуровневой загрузки здесь стояла вся глава целиком — под сорок мегабайт.
    private func openChapter(_ id: String) {
        if sync.isChapterIndexReady(id) {
            selectedEpoch = id; go(.map)
        } else {
            withAnimation(.easeIn(duration: 0.2)) { loadingEpoch = id }
        }
    }

    // MARK: - Мета: решение, награда, реклама

    /// Уровень решён. Первое решение копит экран награды — он откроется, когда игрок уйдёт с доски.
    private func solved(_ level: LevelDef) {
        let id = level.id
        let first = !progress.isCompleted(id)
        progress.markCompleted(id)
        meta.noteLevelFinished()
        let isDaily = dailyActive == id
        let r = meta.recordSolve(levelId: id, firstSolve: first, isDaily: isDaily)
        Telemetry.shared.track("level_complete", level: id, chapter: level.epoch)
        if r.isDaily { Telemetry.shared.track("daily_done", level: id, chapter: level.epoch) }
        if r.rankedUp { Telemetry.shared.track("rank_up", level: "\(r.levelAfter)") }
        if first { pendingReward = PendingReward(levelId: id, epoch: level.epoch, reward: r) }
        rescheduleNotifications()
    }

    @ViewBuilder
    private func rewardOverlay(_ r: PendingReward, _ pack: RomeContent.Pack) -> some View {
        let levels = pack.levels(epoch: r.epoch)
        let ids = sync.availableChapters.first { $0.id == r.epoch }?.levels ?? levels.map(\.id)
        let level = levels.first { $0.id == r.levelId }
        let next = nextLevel(after: r.levelId, epoch: r.epoch, pack)
        RewardView(
            reward: r.reward,
            levelTitle: level?.title ?? r.levelId,
            coverSceneId: level.flatMap { $0.cover ?? $0.scenes.first },
            chapterTitle: L10n.s("chapter.\(r.epoch).title"),
            chapterDone: ids.filter { progress.isCompleted($0) }.count,
            chapterTotal: ids.count,
            hasNext: next != nil,
            onNext: { finishReward(next: next) },
            onMap: { finishReward(next: nil) }
        )
        .transition(.opacity)
    }

    /// Следующий эпизод главы, если он уже открыт прогрессом (после решённого — открыт всегда,
    /// кроме эпизода дня, решённого вне очереди).
    private func nextLevel(after id: String, epoch: String, _ pack: RomeContent.Pack) -> String? {
        let ids = pack.levels(epoch: epoch).map(\.id)
        guard let i = ids.firstIndex(of: id), i + 1 < ids.count else { return nil }
        let next = ids[i + 1]
        guard !sync.isLevelDisabled(next), progress.isUnlocked(levelId: next, orderedIds: ids) else { return nil }
        return next
    }

    private func finishReward(next: String?) {
        withAnimation(.easeOut(duration: 0.2)) { reward = nil }
        dailyActive = nil
        maybeShowInterstitial {
            if let next {
                openLevel(next)
            } else {
                go(.map)
                if let pack { maybeAskForReview(pack) }
            }
            Notifications.askOnce()
        }
    }

    /// Интерстишел между эпизодами — по правилам из манифеста (`docs/f2p-patch-4.0.md` §1).
    private func maybeShowInterstitial(then proceed: @escaping () -> Void) {
        let ads = AdService.shared
        let gap = Date().timeIntervalSince1970 - meta.lastFullscreen
        guard !store.adsFree(selectedEpoch), sync.interstitialEnabled, ads.interstitialReady,
              progress.solvedCount >= sync.interAfter,
              meta.sinceInterstitial >= sync.interEvery,
              gap >= Double(sync.interGapSec) else { return proceed() }
        Telemetry.shared.track("inter_show", level: meta.lastLevel, chapter: selectedEpoch)
        meta.noteInterstitialShown()
        ads.showInterstitial(completion: proceed)
    }

    /// Подсказка: Premium — бесплатно, есть запас — тратим, нет — окно «за ролик».
    private func requestHint(_ levelId: String, _ apply: @escaping () -> Void) {
        if meta.spendHint(levelId: levelId, premium: store.adsFree(selectedEpoch)) {
            apply()
            Telemetry.shared.track("hint_use", level: levelId, chapter: selectedEpoch)
        } else {
            withAnimation(.easeIn(duration: 0.2)) { hintRequest = HintRequest(levelId: levelId, apply: apply) }
        }
    }

    /// Кнопка «Убрать рекламу — цена» на карте: глава не куплена и продукт с ценой загрузился.
    private func noAdsTitle(_ epoch: String) -> String? {
        let price = store.chapterPrice(epoch)
        guard !store.adsFree(epoch), !price.isEmpty else { return nil }
        return L10n.s("ui.chapter_noads_cta", price)
    }

    private func openPremium(_ epoch: String) {
        Telemetry.shared.track("premium_open", chapter: epoch)
        withAnimation(.easeIn(duration: 0.2)) { premiumEpoch = epoch }
    }

    private func restoreStreak() {
        let done = {
            meta.restoreStreak()
            Telemetry.shared.track("streak_restore")
        }
        if store.subscribed { done() } else { AdService.shared.show { if $0 { done() } } }
    }

    /// Подарок дня — в меню, когда поверх ничего не открыто (язык, онбординг).
    private func maybeOfferGift() {
        guard pack != nil, onboarded, !showOnboarding, !showLanguagePicker,
              screen == .menu, meta.giftAvailable, !showGift else { return }
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            guard screen == .menu, meta.giftAvailable else { return }
            withAnimation(.spring(response: 0.45, dampingFraction: 0.8)) { showGift = true }
        }
    }

    // MARK: - Эпизод дня

    /// Эпизод дня. Выбор на сегодня запоминается: пул исключает пройденное, и без этого решённый
    /// эпизод дня сразу сменился бы другим.
    private func dailyPick(day: Int) -> (chapter: String, level: String)? {
        let key = "ht.meta.dailyPick"
        let parts = UserDefaults.standard.string(forKey: key)?.split(separator: "|").map(String.init) ?? []
        if parts.count == 3, Int(parts[0]) == day { return (parts[1], parts[2]) }
        guard let pick = Meta.dailyLevel(day: day,
                                         chapters: sync.availableChapters.map { ($0.id, $0.levels) },
                                         isCompleted: { progress.isCompleted($0) },
                                         isDisabled: { sync.isLevelDisabled($0) }) else { return nil }
        if day == meta.today { UserDefaults.standard.set("\(day)|\(pick.chapter)|\(pick.level)", forKey: key) }
        return pick
    }

    private func menuMeta(_ pack: RomeContent.Pack) -> MenuMeta {
        var daily: MenuMeta.Daily?
        if let pick = dailyPick(day: meta.today) {
            let lv = pack.levels.first { $0.id == pick.level }
            let chCover = sync.availableChapters.first { $0.id == pick.chapter }?.cover
            daily = MenuMeta.Daily(
                title: lv?.title ?? L10n.opt("level.\(pick.level).title") ?? pick.level,
                chapterTitle: L10n.s("chapter.\(pick.chapter).title"),
                coverSceneId: lv.flatMap { $0.cover ?? $0.scenes.first } ?? chCover,
                done: meta.dailyDoneToday)
        }
        return MenuMeta(level: meta.level,
                        rankName: L10n.s(Meta.rankKey(meta.level)),
                        xpProgress: Meta.levelProgress(meta.xp),
                        streak: meta.currentStreak,
                        flameTier: meta.flameTier,
                        hintsBadge: store.subscribed ? "∞" : "\(meta.hints)",
                        freeRestore: store.subscribed,
                        daily: daily,
                        brokenStreak: meta.brokenStreak)
    }

    /// Эпизод дня открывается мимо линейного замка главы; описания главы, если их нет, — догрузить.
    private func openDaily() {
        guard let pick = dailyPick(day: meta.today) else { return }
        Telemetry.shared.track("daily_open", level: pick.level, chapter: pick.chapter)
        dailyActive = meta.dailyDoneToday ? nil : pick.level
        selectedEpoch = pick.chapter
        if sync.isChapterIndexReady(pick.chapter) {
            openLevel(pick.level)
        } else {
            levelAfterIndex = pick.level
            withAnimation(.easeIn(duration: 0.2)) { loadingEpoch = pick.chapter }
        }
    }

    private func rescheduleNotifications() {
        let tomorrow = dailyPick(day: meta.today + 1).map { L10n.opt("level.\($0.level).title") ?? $0.level }
        var last: String?
        if let id = meta.lastLevel {
            let next = pack.flatMap { p in p.levels.first { $0.id == id }.flatMap { nextLevel(after: id, epoch: $0.epoch, p) } }
            let target = progress.isCompleted(id) ? (next ?? id) : id
            last = L10n.opt("level.\(target).title") ?? pack?.levels.first { $0.id == target }?.title
        }
        Notifications.reschedule(tomorrowDaily: tomorrow, lastTitle: last)
    }

    /// Открыть уровень. Фоновая докачка обычно успевает раньше игрока, и экран загрузки
    /// не показывается вовсе; если нет — ждать приходится здесь, а не перед входом в главу.
    private func openLevel(_ id: String) {
        if sync.isLevelReady(id) {
            go(.level(id))
        } else {
            withAnimation(.easeIn(duration: 0.2)) { loadingLevel = id }
        }
    }

    /// Фоновая докачка открытой главы — с того эпизода, куда игрок пойдёт дальше.
    private func startPrefetch() {
        guard let pack else { return }
        let ids = pack.levels(epoch: selectedEpoch).map(\.id)
        let next = ids.first { progress.isUnlocked(levelId: $0, orderedIds: ids) && !progress.isCompleted($0) }
        sync.prefetchChapter(selectedEpoch, startingAt: next)
    }

    /// Показательный уровень для онбординга и экрана загрузки. Задан в `Content/demo.json`,
    /// его файлы входят в core — поэтому он на диске с первого запуска, ещё до любой главы.
    /// Раньше брался из скачанного Рима, и первая же загрузка главы показывала пустую доску.
    private func demoLevel(_ pack: RomeContent.Pack) -> LevelDef? {
        if let id = sync.demoLevelId, let lv = pack.levels.first(where: { $0.id == id }) { return lv }
        return pack.levels.first { $0.panels == 3 && ($0.solution?.isEmpty == false) }
            ?? pack.levels.first { $0.solution?.isEmpty == false }
    }

    private func errorView(_ message: String) -> some View {
        VStack(spacing: 10) {
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.largeTitle).foregroundStyle(DS.Palette.maroon)
            // Экран лежит на тёмном backdrop (см. body), поэтому текст бумажный:
            // ink по баклажану давал контраст около 1.1:1 — ошибку невозможно было прочитать.
            Text(L10n.s("ui.load_fail")).font(.dsBody()).foregroundStyle(DS.Palette.paper)
            Text(message)
                .font(.dsCaption())
                .foregroundStyle(DS.Palette.paper.opacity(0.75))
                .multilineTextAlignment(.center)
        }
        .padding()
    }

    private func go(_ next: Screen) {
        withAnimation(.easeInOut(duration: 0.25)) { screen = next }
    }

    /// Старт: подтянуть манифест и core, затем собрать пак. Офлайн с пустым кешем — единственный
    /// случай, когда игру показать нечем; во всех остальных работаем на том, что уже скачано.
    private func boot() async {
        // Язык — до сети: иначе строки экрана ошибки идут на дефолтном русском,
        // независимо от того, на каком говорит игрок.
        L10n.configure()
        Telemetry.shared.track("session")
        await sync.syncCore()
        load()
    }

    private func load() {
        do {
            L10n.configure()
            pack = try RomeContent.load()
            Audio.shared.preload()
            updateMusic()
            offerFirstRun()
        } catch { loadError = error.localizedDescription }
    }

    /// Выбор языка и онбординг — только после того, как контент на диске. Раньше они всплывали
    /// поверх экрана загрузки, и первый экран игры встречал новичка голыми ключами: каталог
    /// переводов в этот момент ещё ехал.
    private func offerFirstRun() {
        guard !firstRunOffered else { return }
        let env = ProcessInfo.processInfo.environment
        // Отсмотр онбординга без сноса приложения (как HT_RESETDLG / HT_SETTINGS в меню).
        if env["HT_ONBOARDING"] == "1" {
            firstRunOffered = true
            showOnboarding = true
            return
        }
        guard !onboarded else { return }
        let testing = env["HT_SCREEN"] != nil || env["HT_LEVEL"] != nil || env["HT_PAYWALL"] == "1"
        guard !testing else { return }
        firstRunOffered = true
        withAnimation(.easeIn(duration: 0.25)) { showLanguagePicker = true }
    }

    /// Первый запуск: пока едет core, показываем прогресс, а не бесконечный спиннер.
    @ViewBuilder
    private var bootView: some View {
        VStack(spacing: 12) {
            if let failure = sync.failure, !sync.hasCore {
                Text(L10n.s("ui.load_fail")).font(.dsSerif(20)).foregroundStyle(DS.Palette.paper)
                Text(failure).font(.dsCaption(12)).foregroundStyle(DS.Palette.paper.opacity(0.7))
                    .multilineTextAlignment(.center)
                Button(L10n.s("ui.retry")) { Task { await boot() } }
                    .font(.dsBody(14)).buttonStyle(.borderedProminent).tint(DS.Palette.maroon)
            } else {
                BootLoader(progress: sync.progressValue)
            }
        }
        .padding(32)
    }
}

/// Лоадер первого запуска: страница книги с сургучной печатью, вокруг которой золотое
/// кольцо наливается по мере загрузки. Тот же словарь, что и на остальных экранах —
/// пергамент, чернильный контур, золотые уголки.
///
/// Единственная надпись — название игры: оно одинаково на всех языках. Каталог переводов
/// в этот момент ещё едет, а `L10n` до его появления сидит на русском, поэтому любая
/// переводимая строка здесь оказалась бы не на языке игрока.
private struct BootLoader: View {
    let progress: Double

    @State private var spin = false
    @State private var pulse = false

    var body: some View {
        BookPage {
            VStack(spacing: 16) {
                ZStack {
                    // Дорожка кольца.
                    Circle()
                        .stroke(DS.Palette.ink.opacity(0.14), lineWidth: 7)

                    // Реальный прогресс.
                    Circle()
                        .trim(from: 0, to: max(0.02, progress))
                        .stroke(DS.Palette.gold,
                                style: StrokeStyle(lineWidth: 7, lineCap: .round))
                        .rotationEffect(.degrees(-90))
                        .animation(.easeOut(duration: 0.4), value: progress)

                    // Бегущая искра: прогресс может стоять на месте, а экран должен жить.
                    Circle()
                        .trim(from: 0, to: 0.12)
                        .stroke(DS.Palette.gold.opacity(0.55),
                                style: StrokeStyle(lineWidth: 3, lineCap: .round))
                        .rotationEffect(.degrees(spin ? 360 : 0))

                    // Сургучная печать.
                    Circle()
                        .fill(DS.Palette.maroon)
                        .overlay(Circle().strokeBorder(DS.Palette.ink.opacity(0.4), lineWidth: 2))
                        .overlay(
                            Image(systemName: "book.closed.fill")
                                .font(.system(size: 22, weight: .semibold))
                                .foregroundStyle(DS.Palette.paper.opacity(0.9))
                        )
                        .padding(16)
                        .scaleEffect(pulse ? 1.05 : 0.97)
                        .shadow(color: .black.opacity(0.3), radius: 4, y: 2)
                }
                .frame(width: 96, height: 96)

                Text("History Teller")
                    .font(.dsSerif(19))
                    .foregroundStyle(DS.Palette.ink)
            }
            .padding(.horizontal, 34)
            .padding(.vertical, 26)
        }
        .fixedSize()
        .onAppear {
            withAnimation(.linear(duration: 2.2).repeatForever(autoreverses: false)) { spin = true }
            withAnimation(.easeInOut(duration: 1.1).repeatForever(autoreverses: true)) { pulse = true }
        }
    }
}
