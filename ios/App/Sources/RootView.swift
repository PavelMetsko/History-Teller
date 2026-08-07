import SwiftUI
import Simulation
import GameContent
import GameProgress
import MenuFeature
import EpochMapFeature
import LevelFeature
import DesignSystem

/// Координатор экранов: меню → выбор эпохи → карта уровней → уровень. Прогресс в UserDefaults.
struct RootView: View {
    @State private var pack: RomeContent.Pack?
    @State private var loadError: String?
    @State private var progress = ProgressStore()
    @State private var selectedEpoch = ProcessInfo.processInfo.environment["HT_EPOCH"] ?? "rome"
    @State private var store = Store.shared
    @State private var showPaywall = false
    @State private var pendingEpoch: String?
    @State private var sync = ContentSync.shared
    @State private var loadingEpoch: String?
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
        case level(String)
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

            if showPaywall {
                PaywallView(
                    epoch: pendingEpoch ?? "",
                    chapterTitle: L10n.s("chapter.\(pendingEpoch ?? "").title"),
                    onClose: { withAnimation(.easeOut(duration: 0.2)) { showPaywall = false } },
                    onUnlocked: {
                        withAnimation(.easeOut(duration: 0.2)) { showPaywall = false }
                        if let e = pendingEpoch { openChapter(e) }
                    }
                )
                .transition(.opacity)
                .zIndex(30)
            }

            if let ep = loadingEpoch, let pack {
                ChapterLoadingView(
                    chapterNumber: chapterNumber(ep),
                    chapterTitle: chapterTitle(ep),
                    epoch: ep,
                    demoLevel: demoLevel(pack),
                    db: pack.db,
                    onReady: {
                        // Уровни главы приезжают вместе с ней — пак надо пересобрать,
                        // иначе глава откроется пустой.
                        load()
                        selectedEpoch = ep
                        loadingEpoch = nil
                        go(.map)
                    }
                )
                .transition(.opacity)
                .zIndex(40)
            }

            if showOnboarding {
                OnboardingView(level: pack.flatMap { demoLevel($0) }, db: pack?.db, onFinish: {
                    onboarded = true
                    withAnimation(.easeOut(duration: 0.25)) { showOnboarding = false }
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
            if ProcessInfo.processInfo.environment["HT_PAYWALL"] == "1" {
                pendingEpoch = ProcessInfo.processInfo.environment["HT_EPOCH"] ?? "tudor"
                showPaywall = true
            }
        }
        .onChange(of: screen) { _, _ in updateMusic() }
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
                    onPlay: { go(.chapters) },
                    onReset: { progress.reset() }
                )
            case .chapters:
                ChapterSelectView(
                    chapters: chapters(pack),
                    isUnlocked: { store.isUnlocked($0.id) || ProgressStore.unlockAll },
                    priceText: { store.chapterPrice($0.id) },
                    onSelect: { ch in
                        guard ch.available else { return }
                        if store.isUnlocked(ch.id) || ProgressStore.unlockAll {
                            openChapter(ch.id)
                        } else {
                            pendingEpoch = ch.id
                            withAnimation(.easeIn(duration: 0.2)) { showPaywall = true }
                        }
                    },
                    onBack: { go(.menu) }
                )
            case .map:
                EpochMapView(
                    title: chapterTitle(selectedEpoch),
                    levels: pack.levels(epoch: selectedEpoch),
                    db: pack.db,
                    progress: progress,
                    onSelect: { go(.level($0)) },
                    onBack: { go(.chapters) }
                )
            case .level(let id):
                if let level = pack.levels.first(where: { $0.id == id }) {
                    LevelBoardView(
                        level: level,
                        db: pack.db,
                        onSolved: { progress.markCompleted(id) },
                        onExit: { go(.map) }
                    )
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

    private func chapters(_ pack: RomeContent.Pack) -> [Chapter] {
        // Всего уровней берём из манифеста, а не из загруженного пака: файлы уровней приезжают
        // вместе с главой, и до входа в неё пак пуст — на карточке было «0 из 0».
        func prog(_ epoch: String) -> String {
            let ids = sync.availableChapters.first { $0.id == epoch }?.levels
                ?? pack.levels(epoch: epoch).map(\.id)
            let done = ids.filter { progress.isCompleted($0) }.count
            return L10n.s("ui.progress", done, ids.count)
        }
        func ch(_ id: String, _ n: Int, _ cover: String?, _ icon: String,
                _ available: Bool, free: Bool = false) -> Chapter {
            Chapter(id: id, number: n,
                    title: L10n.s("chapter.\(id).title"),
                    subtitle: L10n.s("chapter.\(id).subtitle"),
                    coverSceneId: cover, icon: icon,
                    available: available, free: free,
                    progressText: available ? prog(id) : nil)
        }
        // Список глав задаёт манифест — иначе глава, выложенная в облако, не появилась бы в меню.
        // Без манифеста (первый запуск офлайн) показываем то, что лежит в бандле.
        let fromManifest = ContentSync.shared.availableChapters
        guard !fromManifest.isEmpty else {
            return [ch("rome", 1, "forum", "building.columns.fill", true, free: true)]
        }
        return fromManifest.map {
            ch($0.id, $0.number, $0.cover, $0.icon, true, free: $0.free)
        }
    }

    private func chapterTitle(_ epoch: String) -> String {
        L10n.s("map.\(epoch)")
    }

    /// Открыть главу: встроенная (Rome) — сразу; остальные — через экран загрузки арта.
    private func openChapter(_ id: String) {
        if sync.isChapterReady(id) {
            selectedEpoch = id; go(.map)
        } else {
            withAnimation(.easeIn(duration: 0.2)) { loadingEpoch = id }
        }
    }

    private func chapterNumber(_ epoch: String) -> Int {
        sync.availableChapters.first { $0.id == epoch }?.number ?? 1
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
            Text(L10n.s("ui.load_fail")).font(.dsBody()).foregroundStyle(DS.Palette.ink)
            Text(message)
                .font(.dsCaption())
                .foregroundStyle(DS.Palette.inkSoft)
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
