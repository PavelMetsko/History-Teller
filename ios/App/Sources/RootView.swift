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
            content
                .transition(.opacity)
        }
        .onChange(of: screen) { _, _ in updateMusic() }
    }

    /// Музыка сквозняком: тема настроения уровня, иначе базовая. Один трек не перезапускается.
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
                    onSelect: { ch in if ch.available { selectedEpoch = ch.id; go(.map) } },
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
            return "Пройдено \(ls.filter { progress.isCompleted($0.id) }.count) из \(ls.count)"
        }
        return [
            Chapter(id: "rome", number: 1, title: "Древний Рим",
                    subtitle: "Цезарь · Клеопатра · Брут",
                    coverSceneId: "forum", icon: "building.columns.fill",
                    available: true, progressText: prog("rome")),
            Chapter(id: "tudor", number: 2, title: "Тюдоры",
                    subtitle: "Генрих VIII и наследники",
                    coverSceneId: "tower", icon: "crown.fill",
                    available: true, progressText: prog("tudor")),
            Chapter(id: "egypt", number: 3, title: "Древний Египет",
                    subtitle: "Фараоны и боги",
                    coverSceneId: nil, icon: "pyramid.fill",
                    available: false, progressText: nil),
        ]
    }

    private func chapterTitle(_ epoch: String) -> String {
        switch epoch {
        case "tudor": return "Дом Тюдоров"
        case "egypt": return "Древний Египет"
        default:      return "Древний Рим"
        }
    }

    private func errorView(_ message: String) -> some View {
        VStack(spacing: 10) {
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.largeTitle).foregroundStyle(DS.Palette.maroon)
            Text("Не удалось загрузить контент").font(.dsBody()).foregroundStyle(DS.Palette.ink)
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
            pack = try RomeContent.load()
            Audio.shared.preload()
            updateMusic()
        } catch { loadError = error.localizedDescription }
    }
}
