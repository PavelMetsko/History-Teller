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
                    onClose: { withAnimation(.easeOut(duration: 0.2)) { showPaywall = false } },
                    onUnlocked: {
                        withAnimation(.easeOut(duration: 0.2)) { showPaywall = false }
                        if let e = pendingEpoch { selectedEpoch = e; go(.map) }
                    }
                )
                .transition(.opacity)
                .zIndex(30)
            }
        }
        .onAppear {
            if ProcessInfo.processInfo.environment["HT_PAYWALL"] == "1" { showPaywall = true }
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
                    unlocked: store.isUnlocked,
                    priceText: store.priceText,
                    onSelect: { ch in
                        guard ch.available else { return }
                        if ch.free || store.isUnlocked {
                            selectedEpoch = ch.id; go(.map)
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
            ProgressView().task { load() }
        }
    }

    private func chapters(_ pack: RomeContent.Pack) -> [Chapter] {
        func prog(_ epoch: String) -> String {
            let ls = pack.levels(epoch: epoch)
            return L10n.s("ui.progress", ls.filter { progress.isCompleted($0.id) }.count, ls.count)
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
        return [
            ch("rome", 1, "forum", "building.columns.fill", true, free: true),
            ch("tudor", 2, "tower", "crown.fill", true),
            ch("revolution", 3, "guillotine", "flame.fill", true),
            ch("empire", 4, "sobor", "seal.fill", true),
            ch("borgia", 5, "curia", "flame.fill", true),
            ch("byzantium", 6, "hagia", "cross.fill", true),
        ]
    }

    private func chapterTitle(_ epoch: String) -> String {
        L10n.s("map.\(epoch)")
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

    private func load() {
        do {
            L10n.configure()
            pack = try RomeContent.load()
            Audio.shared.preload()
            updateMusic()
        } catch { loadError = error.localizedDescription }
    }
}
