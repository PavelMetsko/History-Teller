import SwiftUI
import DesignSystem
import GameContent

/// Альбом истории: каждая решённая глава-эпизод — карточка с обложкой и фактом, нерешённые —
/// тёмные силуэты с номером. Пустые ячейки и «12 / 71» на вкладке тянут собрать главу целиком.
public struct AlbumView: View {
    public struct Section: Identifiable {
        public let id: String
        public let title: String
        public let levels: [String]

        public init(id: String, title: String, levels: [String]) {
            self.id = id
            self.title = title
            self.levels = levels
        }
    }

    private let sections: [Section]
    private let isCompleted: (String) -> Bool
    private let cover: (String) -> String?
    private let cast: (String) -> [String]
    private let onClose: () -> Void

    @State private var selected: String
    @State private var opened: String?

    public init(sections: [Section], initial: String?, isCompleted: @escaping (String) -> Bool,
                cover: @escaping (String) -> String?, cast: @escaping (String) -> [String] = { _ in [] },
                onClose: @escaping () -> Void) {
        self.sections = sections
        self.isCompleted = isCompleted
        self.cover = cover
        self.cast = cast
        self.onClose = onClose
        _selected = State(initialValue: initial ?? sections.first?.id ?? "")
    }

    private var current: Section? { sections.first { $0.id == selected } }

    public var body: some View {
        ZStack {
            DS.Palette.backdrop.ignoresSafeArea()
            BookPage {
                VStack(spacing: 10) {
                    Text(L10n.s("ui.album")).font(.dsSerif(24)).foregroundStyle(DS.Palette.ink)
                    tabs
                    if let current { grid(current) }
                }
                .padding(EdgeInsets(top: 14, leading: 26, bottom: 12, trailing: 26))
            }
            .padding(EdgeInsets(top: 14, leading: 18, bottom: 14, trailing: 18))
            .overlay(alignment: .topLeading) {
                RibbonButton(systemImage: "chevron.left") { onClose() }.offset(x: 42, y: -12)
            }

            if let id = opened { factCard(id).transition(.scale(scale: 0.85).combined(with: .opacity)).zIndex(5) }
        }
    }

    private var tabs: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(sections) { s in
                    let done = s.levels.filter(isCompleted).count
                    let complete = done == s.levels.count && !s.levels.isEmpty
                    Button {
                        Audio.shared.play(.select)
                        withAnimation(.easeInOut(duration: 0.2)) { selected = s.id }
                    } label: {
                        HStack(spacing: 5) {
                            if complete { Image(systemName: "seal.fill").foregroundStyle(DS.Palette.gold) }
                            Text(s.title).lineLimit(1)
                            Text("\(done)/\(s.levels.count)").monospacedDigit().opacity(0.7)
                        }
                        .font(.dsCaption(12))
                        .foregroundStyle(selected == s.id ? DS.Palette.paper : DS.Palette.ink)
                        .padding(.horizontal, 12).padding(.vertical, 7)
                        .background(Capsule().fill(selected == s.id ? DS.Palette.maroon : DS.Palette.panel))
                        .overlay(Capsule().strokeBorder(DS.Palette.ink.opacity(0.3), lineWidth: 1))
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(.horizontal, 4)
        }
        .frame(height: 36)
    }

    private func grid(_ s: Section) -> some View {
        ScrollView {
            LazyVGrid(columns: [GridItem(.adaptive(minimum: 118, maximum: 150), spacing: 12)], spacing: 12) {
                ForEach(Array(s.levels.enumerated()), id: \.element) { i, id in
                    card(id, number: i + 1)
                }
            }
            .padding(.vertical, 4)
        }
    }

    @ViewBuilder private func card(_ id: String, number: Int) -> some View {
        let solved = isCompleted(id)
        Button {
            guard solved else { return }
            Audio.shared.play(.select)
            withAnimation(.spring(response: 0.45, dampingFraction: 0.8)) { opened = id }
        } label: {
            AlbumCard(number: number, solved: solved,
                      title: L10n.opt("level.\(id).title") ?? id,
                      sceneId: solved ? cover(id) : nil,
                      cast: solved ? cast(id) : [])
        }
        .buttonStyle(.plain)
        .accessibilityLabel(solved ? (L10n.opt("level.\(id).title") ?? id) : L10n.s("ui.album_locked"))
    }

    private func factCard(_ id: String) -> some View {
        ZStack {
            Color.black.opacity(0.5).ignoresSafeArea()
                .onTapGesture { withAnimation { opened = nil } }
            BookPage {
                VStack(spacing: 0) {
                    ScrollView {
                        VStack(spacing: 10) {
                            if let sid = cover(id) {
                                Image.scene(sid).resizable().scaledToFill()
                                    .frame(height: 120).frame(maxWidth: .infinity).clipped()
                                    .clipShape(RoundedRectangle(cornerRadius: 8))
                            }
                            Text(L10n.opt("level.\(id).title") ?? id).font(.dsSerif(20)).foregroundStyle(DS.Palette.ink)
                                .multilineTextAlignment(.center)
                            if let fact = L10n.opt("level.\(id).fact") {
                                Text(fact).font(.dsBody(14)).foregroundStyle(DS.Palette.ink)
                            }
                            if let src = L10n.opt("level.\(id).source") {
                                Text(src).font(.dsCaption(11)).italic().foregroundStyle(DS.Palette.inkSoft)
                            }
                        }
                        .padding(EdgeInsets(top: 20, leading: 24, bottom: 16, trailing: 24))
                    }
                }
            }
            .frame(maxWidth: 520, maxHeight: 340)
            .overlay(alignment: .topTrailing) { CloseButton { withAnimation { opened = nil } } }
        }
    }
}

/// Карточка альбома: кадр эпизода — фон сцены и герои на нём, как на доске, — и подпись под кадром.
/// Арт берётся миниатюрами с фонового потока: в главе под сотню карточек, полные кадры не нужны.
private struct AlbumCard: View {
    let number: Int
    let solved: Bool
    let title: String
    let sceneId: String?
    let cast: [String]

    @State private var scene: UIImage?
    @State private var heroes: [UIImage] = []

    private static let imageHeight: CGFloat = 92

    var body: some View {
        VStack(spacing: 0) {
            Color.clear
                .frame(height: Self.imageHeight)
                .frame(maxWidth: .infinity)
                .overlay { art }
                .clipped()
            Text(solved ? title : "\(number)")
                .font(.dsCaption(10))
                .foregroundStyle(solved ? DS.Palette.ink : DS.Palette.inkSoft)
                .lineLimit(2)
                .minimumScaleFactor(0.8)
                .multilineTextAlignment(.center)
                .frame(maxWidth: .infinity, minHeight: 30)
                .padding(.horizontal, 4)
                .background(DS.Palette.panel)
        }
        .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
        .overlay(RoundedRectangle(cornerRadius: 8, style: .continuous)
            .strokeBorder(solved ? DS.Palette.gold : DS.Palette.ink.opacity(0.3), lineWidth: solved ? 2 : 1))
        .task(id: sceneId) { await load() }
    }

    @ViewBuilder private var art: some View {
        if solved {
            ZStack(alignment: .bottom) {
                if let scene {
                    Image(uiImage: scene).resizable().scaledToFill()
                } else {
                    DS.Palette.paperEdge
                }
                HStack(alignment: .bottom, spacing: -14) {
                    ForEach(heroes.indices, id: \.self) { i in
                        Image(uiImage: heroes[i]).resizable().scaledToFit()
                            .frame(height: Self.imageHeight * 0.82)
                            .shadow(color: .black.opacity(0.35), radius: 2, y: 1)
                    }
                }
            }
        } else {
            ZStack {
                LinearGradient(colors: [DS.Palette.ink.opacity(0.85), DS.Palette.backdrop],
                               startPoint: .top, endPoint: .bottom)
                Text("?").font(.system(size: 30, weight: .heavy, design: .serif))
                    .foregroundStyle(DS.Palette.paper.opacity(0.35))
            }
        }
    }

    private func load() async {
        guard solved, scene == nil else { return }
        let sceneName = sceneId.map(GameAssets.sceneImageName)
        let names = cast.prefix(2).map(GameAssets.characterImageName)
        let loaded = await Task.detached(priority: .utility) {
            (sceneName.flatMap { ArtStore.thumbnail($0, maxPixel: 320) },
             names.compactMap { ArtStore.thumbnail($0, maxPixel: 240) })
        }.value
        scene = loaded.0
        heroes = loaded.1
    }
}
