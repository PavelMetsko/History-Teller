import SwiftUI
import Simulation
import GameContent
import DesignSystem

struct FlyingBadge: Identifiable, Equatable {
    let id = UUID()
    let panelIndex: Int
    let symbol: String
}

/// Кадры панелей в системе координат "board" — для хит-теста дропа.
private struct PanelFramesKey: PreferenceKey {
    static var defaultValue: [Int: CGRect] = [:]
    static func reduce(value: inout [Int: CGRect], nextValue: () -> [Int: CGRect]) {
        value.merge(nextValue()) { _, new in new }
    }
}

private func juice(forRule id: String) -> (symbol: String, sfx: Audio.SFX) {
    switch id {
    case "charm":                            return ("❤️", .love)
    case "befriend":                         return ("🤝", .ally)
    case "conspire":                         return ("🗡", .conspire)
    case "betrayal_kill":                    return ("☠️", .kill)
    case "battle_justice", "conquer":        return ("⚔️", .kill)
    case "offer_crown", "enthrone", "honor": return ("👑", .crown)
    case "rivals", "senate_envy":            return ("💢", .envy)
    case "smuggle":                          return ("📦", .place)
    case "voyage":                           return ("⛵", .place)
    case "beget_heir":                       return ("👶", .crown)
    case "back_ruler":                       return ("🛡", .ally)
    default:                                 return ("✨", .select)
    }
}

private extension Font {
    static func serifTitle(_ size: CGFloat) -> Font { .system(size: size, weight: .bold, design: .serif) }
}

public struct LevelBoardView: View {
    @State private var model: LevelBoardModel
    @State private var badges: [FlyingBadge] = []
    @State private var celebrate = false
    @State private var showInfo = false
    @State private var demoMode = false
    @State private var shakeData: CGFloat = 0

    // Кастомный драг
    @State private var draggingItem: LevelBoardModel.Selection?
    @State private var dragLocation: CGPoint = .zero
    @State private var panelFrames: [Int: CGRect] = [:]
    @State private var hoverPanel: Int?

    private let onSolved: (() -> Void)?
    private let onExit: (() -> Void)?
    private let boardSpace = "board"

    public init(level: LevelDef,
                db: ContentDb,
                onSolved: (() -> Void)? = nil,
                onExit: (() -> Void)? = nil) {
        _model = State(initialValue: LevelBoardModel(level: level, db: db))
        self.onSolved = onSolved
        self.onExit = onExit
    }

    public var body: some View {
        ZStack {
            DS.Palette.backdrop.ignoresSafeArea()

            BookPage {
                VStack(spacing: 8) {
                    titleBar
                    panelsGrid
                    tokenTray
                }
                .padding(EdgeInsets(top: 12, leading: 20, bottom: 12, trailing: 20))
            }
            .padding(EdgeInsets(top: 14, leading: 18, bottom: 14, trailing: 18))
            .overlay(alignment: .topLeading) { bookmark.offset(x: 42, y: -12) }
            .overlay(alignment: .topTrailing) { controls.offset(x: -24, y: 50) }
            .modifier(Shake(animatableData: shakeData))

            // призрак перетаскиваемого токена — едет за пальцем
            if let item = draggingItem {
                dragGhost(item)
                    .position(x: dragLocation.x, y: dragLocation.y - 44)
                    .allowsHitTesting(false)
                    .transition(.identity)
            }

            if celebrate { ConfettiView().allowsHitTesting(false).transition(.opacity) }
            if model.showFact { factPopup.zIndex(10) }
        }
        .coordinateSpace(.named(boardSpace))
        .onPreferenceChange(PanelFramesKey.self) { panelFrames = $0 }
        .onChange(of: model.changeToken) { _, _ in
            reactToEvents()
            if !model.isSolved && model.isBoardComplete { triggerWrong() }
        }
        .onChange(of: model.isSolved) { _, solved in if solved { win() } }
        .alert(model.level.title, isPresented: $showInfo) {
            Button("Понятно", role: .cancel) {}
        } message: {
            Text([model.level.initialText, model.level.goalHint]
                .compactMap { $0 }.joined(separator: "\n\n"))
        }
        .onAppear {
            Audio.shared.preload(); Audio.shared.startMusic()
            if ProcessInfo.processInfo.environment["HT_DEMO"] == "1" {
                demoMode = true; model.applySolution(); model.showFact = false
            }
            if ProcessInfo.processInfo.environment["HT_WRONG"] == "1" {
                model.fillDebugWrong()
            }
        }
        .onDisappear { Audio.shared.stopMusic() }
    }

    // MARK: Drag

    private func dragGesture(for item: LevelBoardModel.Selection) -> some Gesture {
        DragGesture(minimumDistance: 8, coordinateSpace: .named(boardSpace))
            .onChanged { v in
                if draggingItem == nil {
                    draggingItem = item
                    model.selected = nil
                    Haptics.light()
                }
                dragLocation = v.location
                hoverPanel = panelIndex(at: v.location)
            }
            .onEnded { v in
                if let idx = panelIndex(at: v.location) { applyDrag(item, to: idx) }
                draggingItem = nil
                hoverPanel = nil
            }
    }

    private func panelIndex(at p: CGPoint) -> Int? {
        panelFrames.first { $0.value.contains(p) }?.key
    }

    private func applyDrag(_ item: LevelBoardModel.Selection, to idx: Int) {
        switch item {
        case .scene(let sid):
            model.setScene(sid, at: idx); Audio.shared.play(.select)
        case .character(let cid):
            let before = model.panels[idx].characters.count
            model.place(cid, at: idx)
            if model.panels[idx].characters.count > before { Audio.shared.play(.place); Haptics.light() }
        }
    }

    @ViewBuilder private func dragGhost(_ item: LevelBoardModel.Selection) -> some View {
        switch item {
        case .scene(let sid):
            Image.scene(sid).resizable().scaledToFill()
                .frame(width: 80, height: 56)
                .clipShape(RoundedRectangle(cornerRadius: 8))
                .shadow(color: .black.opacity(0.35), radius: 6, y: 4)
                .opacity(0.95)
        case .character(let cid):
            Image.character(cid).resizable().scaledToFit().frame(height: 110)
                .shadow(color: .black.opacity(0.35), radius: 6, y: 4)
                .opacity(0.95)
        }
    }

    // MARK: Juice

    private func reactToEvents() {
        for event in model.lastFiredEvents {
            let j = juice(forRule: event.ruleId)
            Audio.shared.play(j.sfx); Haptics.rigid()
            let badge = FlyingBadge(panelIndex: event.panelIndex, symbol: j.symbol)
            badges.append(badge)
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.3) { badges.removeAll { $0.id == badge.id } }
        }
    }

    private func win() {
        Audio.shared.play(.win); Haptics.success()
        withAnimation(.spring(response: 0.4, dampingFraction: 0.5)) { celebrate = true }
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.6) { withAnimation { celebrate = false } }
        if !demoMode {
            // даём налюбоваться решённой сценой (конфетти + зелёная галочка), потом плавно выезжает справка
            DispatchQueue.main.asyncAfter(deadline: .now() + 2.4) {
                withAnimation(.spring(response: 0.5, dampingFraction: 0.72)) { model.showFact = true }
            }
        }
        onSolved?()
    }

    private func dismissFact() {
        withAnimation(.easeInOut(duration: 0.2)) { model.showFact = false }
        onExit?()
    }

    /// Неверная попытка: доска заполнена, но цель не достигнута — звук + встряска.
    /// Конкретика (что не так) показывается пообъектно на самих панелях.
    private func triggerWrong() {
        Audio.shared.play(.error)
        Haptics.error()
        withAnimation(.linear(duration: 0.45)) { shakeData += 1 }
    }

    // MARK: Title (horizontal, top)

    private var titleBar: some View {
        HStack(spacing: 8) {
            Image(systemName: model.isSolved ? "checkmark.square.fill" : "square")
                .font(.system(size: 16, weight: .bold))
                .foregroundStyle(model.isSolved ? DS.Palette.success : DS.Palette.ink)
            Text(model.level.goalText ?? model.level.title)
                .font(.serifTitle(19))
                .foregroundStyle(DS.Palette.ink)
                .lineLimit(1)
                .minimumScaleFactor(0.6)
        }
        .frame(maxWidth: .infinity)
        .padding(.horizontal, 100)
        .frame(height: 34)
    }

    // MARK: Comic grid (middle) — панели с 16px зазором

    private var panelsGrid: some View {
        GeometryReader { geo in
            let n = max(1, model.panels.count)
            let gap: CGFloat = 16
            let cellH = geo.size.height
            let maxCellW = cellH * 1.2
            let cellW = min((geo.size.width - gap * CGFloat(n - 1)) / CGFloat(n), maxCellW)
            HStack(spacing: gap) {
                ForEach(model.panels.indices, id: \.self) { i in
                    PanelCell(model: model, index: i,
                              size: CGSize(width: cellW, height: cellH),
                              highlighted: hoverPanel == i || (model.selected != nil),
                              diagnosis: model.panelDiagnoses.indices.contains(i) ? model.panelDiagnoses[i] : .ok,
                              boardSpace: boardSpace,
                              badges: badges.filter { $0.panelIndex == i })
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
    }

    // MARK: Token tray (horizontal, bottom)

    private var tokenTray: some View {
        HStack(spacing: 12) {
            Spacer(minLength: 0)
            ForEach(model.level.scenes, id: \.self) { sid in
                SceneToken(sceneId: sid, name: model.sceneName(sid), selected: model.selected == .scene(sid))
                    .opacity(draggingItem == .scene(sid) ? 0.35 : 1)
                    .onTapGesture { Audio.shared.play(.select); model.selectItem(.scene(sid)) }
                    .gesture(dragGesture(for: .scene(sid)))
            }
            Rectangle().fill(DS.Palette.ink.opacity(0.3)).frame(width: 1.5, height: 60).padding(.horizontal, 2)
            ForEach(model.roster, id: \.self) { id in
                CharToken(id: id, name: model.characterName(id),
                          badges: StateBadges.emojis(for: id, in: model.world),
                          selected: model.selected == .character(id))
                    .opacity(draggingItem == .character(id) ? 0.35 : 1)
                    .onTapGesture { Audio.shared.play(.select); model.selectItem(.character(id)) }
                    .gesture(dragGesture(for: .character(id)))
            }
            Spacer(minLength: 0)
        }
        .frame(height: 90)
    }

    // MARK: Chrome

    private var bookmark: some View {
        Group {
            if onExit != nil {
                RibbonButton(systemImage: "chevron.left") { Audio.shared.play(.select); onExit?() }
            }
        }
    }

    private var controls: some View {
        HStack(spacing: 8) {
            iconButton("info.circle", tint: DS.Palette.ink) { showInfo = true }
            iconButton("arrow.counterclockwise", tint: DS.Palette.maroon) { Audio.shared.play(.remove); model.reset() }
        }
    }

    private func iconButton(_ name: String, tint: Color, _ action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Image(systemName: name)
                .font(.system(size: 13, weight: .bold))
                .foregroundStyle(tint)
                .frame(width: 32, height: 32)
                .background(Circle().fill(DS.Palette.paper))
                .overlay(Circle().strokeBorder(DS.Palette.ink.opacity(0.5), lineWidth: 1.5))
        }
    }

    private var factPopup: some View {
        ZStack {
            Color.black.opacity(0.5).ignoresSafeArea()
                .onTapGesture { dismissFact() }
                .transition(.opacity)
            FactPopupCard(level: model.level, onClose: dismissFact)
                .padding(.horizontal, 40)
                .transition(.scale(scale: 0.8).combined(with: .opacity))
        }
    }
}

// MARK: - Bottom tokens

private struct SceneToken: View {
    let sceneId: String
    let name: String
    let selected: Bool

    var body: some View {
        VStack(spacing: 3) {
            Image.scene(sceneId)
                .resizable().scaledToFill()
                .frame(width: 66, height: 46)
                .clipShape(RoundedRectangle(cornerRadius: 7, style: .continuous))
                .overlay(RoundedRectangle(cornerRadius: 7, style: .continuous)
                    .strokeBorder(selected ? DS.Palette.gold : DS.Palette.ink.opacity(0.55),
                                  lineWidth: selected ? 3 : 2))
            Text(name).font(.dsCaption(9)).foregroundStyle(DS.Palette.inkSoft).lineLimit(1)
        }
        .contentShape(Rectangle())
    }
}

private struct CharToken: View {
    let id: String
    let name: String
    let badges: [String]
    let selected: Bool

    var body: some View {
        VStack(spacing: 1) {
            ZStack(alignment: .topTrailing) {
                Image.character(id).resizable().scaledToFit().frame(height: 52)
                if !badges.isEmpty {
                    Text(badges.joined()).font(.system(size: 10))
                        .padding(2).background(Circle().fill(DS.Palette.paper)).offset(x: 5, y: -1)
                }
            }
            .frame(width: 58, height: 54)
            .background(selected ? RoundedRectangle(cornerRadius: 9).fill(DS.Palette.gold.opacity(0.28)) : nil)
            .overlay(selected ? RoundedRectangle(cornerRadius: 9).strokeBorder(DS.Palette.gold, lineWidth: 3) : nil)
            Text(name).font(.dsCaption(9)).foregroundStyle(DS.Palette.inkSoft).lineLimit(1)
        }
        .contentShape(Rectangle())
    }
}

// MARK: - Panel cell

private struct PanelCell: View {
    @Bindable var model: LevelBoardModel
    let index: Int
    let size: CGSize
    let highlighted: Bool
    let diagnosis: LevelBoardModel.PanelDiagnosis
    let boardSpace: String
    let badges: [FlyingBadge]

    private var panel: Panel { model.panels[index] }
    private var isTapTarget: Bool { model.selected != nil }
    private var isWrong: Bool { diagnosis != .ok }

    /// Литературная подсказка «почему пусто».
    private var wrongHint: String? {
        switch diagnosis {
        case .ok:              return nil
        case .wrongCharacters: return "Место то — да не те лица"
        case .wrongScene:      return "Верные герои — да не то место"
        case .inert:           return "Совсем не то — ни место, ни лица"
        }
    }

    private var borderColor: Color {
        if highlighted { return DS.Palette.gold }
        if isWrong { return DS.Palette.maroon }
        return DS.Palette.ink.opacity(0.55)
    }

    var body: some View {
        ZStack {
            if let sid = panel.sceneId {
                Image.scene(sid).resizable().scaledToFill()
                    .frame(width: size.width, height: size.height).clipped()
                if let action = model.sceneAction(sid) {
                    VStack { HStack { PillLabel(action, background: DS.Palette.paper.opacity(0.92)); Spacer() }; Spacer() }
                        .padding(7)
                }
                charactersOverlay(sceneId: sid)
            } else {
                DS.Palette.panel
                VStack(spacing: 4) {
                    Image(systemName: isTapTarget ? "hand.point.up.left.fill" : "photo")
                        .font(.system(size: 20))
                        .foregroundStyle(isTapTarget ? DS.Palette.maroon : DS.Palette.inkSoft.opacity(0.6))
                    Text(isTapTarget ? "тапни" : "сцена")
                        .font(.dsCaption(10)).foregroundStyle(DS.Palette.inkSoft.opacity(0.7))
                }
            }
        }
        .frame(width: size.width, height: size.height)
        .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 10, style: .continuous)
                .strokeBorder(borderColor, lineWidth: (highlighted || isWrong) ? 3 : 2)
        )
        .overlay(alignment: .bottom) {
            if let hint = wrongHint {
                Text(hint)
                    .font(.dsCaption(10))
                    .foregroundStyle(.white)
                    .padding(.horizontal, 10).padding(.vertical, 5)
                    .background(Capsule().fill(DS.Palette.maroon.opacity(0.94)))
                    .overlay(Capsule().strokeBorder(.white.opacity(0.3), lineWidth: 1))
                    .padding(.bottom, 8)
                    .shadow(color: .black.opacity(0.3), radius: 3, y: 1)
                    .transition(.opacity.combined(with: .scale(scale: 0.9)))
            }
        }
        .overlay(alignment: .top) {
            ZStack { ForEach(badges) { b in FlyingBadgeView(symbol: b.symbol) } }
                .padding(.top, size.height * 0.14)
        }
        .animation(.easeInOut(duration: 0.2), value: isWrong)
        .background(
            GeometryReader { g in
                Color.clear.preference(key: PanelFramesKey.self,
                                       value: [index: g.frame(in: .named(boardSpace))])
            }
        )
        .contentShape(Rectangle())
        .onTapGesture { applyTap() }
    }

    private func applyTap() {
        guard let sel = model.selected else { return }
        let before = model.panels[index].characters.count
        model.applySelection(at: index)
        if case .scene = sel { Audio.shared.play(.select) }
        else if model.panels[index].characters.count > before { Audio.shared.play(.place); Haptics.light() }
    }

    private func charactersOverlay(sceneId: String) -> some View {
        let slots = model.slots(at: index)
        let spriteH = size.height * 0.62
        return VStack {
            Spacer(minLength: 0)
            HStack(alignment: .bottom, spacing: 4) {
                ForEach(0..<slots, id: \.self) { slot in
                    if slot < panel.characters.count {
                        let charId = panel.characters[slot]
                        let dead = model.snapshot(after: index).hasFlag(charId, "dead")
                        Button {
                            Audio.shared.play(.remove); Haptics.light()
                            model.removeCharacter(charId, at: index)
                        } label: {
                            Image.character(charId)
                                .resizable().scaledToFit().frame(height: spriteH)
                                // погиб — заваливается набок, сереет и притухает
                                .grayscale(dead ? 0.9 : 0)
                                .opacity(dead ? 0.8 : 1)
                                .rotationEffect(.degrees(dead ? 74 : 0), anchor: .bottom)
                                .offset(y: dead ? spriteH * 0.08 : 0)
                                .animation(.spring(response: 0.5, dampingFraction: 0.55), value: dead)
                        }
                        .buttonStyle(.plain)
                        .transition(.scale(scale: 0.4).combined(with: .opacity))
                    } else {
                        RoundedRectangle(cornerRadius: 10, style: .continuous)
                            .strokeBorder(DS.Palette.ink.opacity(0.3),
                                          style: StrokeStyle(lineWidth: 2, dash: [5, 4]))
                            .frame(width: spriteH * 0.5, height: spriteH * 0.8)
                    }
                }
            }
            .padding(.bottom, 6)
            .animation(.spring(response: 0.35, dampingFraction: 0.6), value: panel.characters)
        }
    }
}

private struct FlyingBadgeView: View {
    let symbol: String
    @State private var scaleUp = false
    @State private var floatUp = false

    var body: some View {
        Text(symbol)
            .font(.system(size: 40))
            .shadow(color: DS.Palette.ink.opacity(0.3), radius: 3, y: 2)
            .scaleEffect(scaleUp ? 1.0 : 0.2)
            .offset(y: floatUp ? -60 : 0)
            .opacity(floatUp ? 0 : 1)
            .onAppear {
                withAnimation(.spring(response: 0.3, dampingFraction: 0.45)) { scaleUp = true }
                withAnimation(.easeOut(duration: 1.0).delay(0.2)) { floatUp = true }
            }
    }
}

/// Горизонтальная встряска (для неверного хода).
private struct Shake: GeometryEffect {
    var travel: CGFloat = 9
    var shakes: CGFloat = 3
    var animatableData: CGFloat
    func effectValue(size: CGSize) -> ProjectionTransform {
        ProjectionTransform(CGAffineTransform(translationX: travel * sin(animatableData * .pi * shakes), y: 0))
    }
}

// MARK: - Confetti

private struct ConfettiView: View {
    private struct Piece: Identifiable { let id: Int; let x: CGFloat; let symbol: String; let size: CGFloat; let delay: Double; let dur: Double; let rot: Double }
    @State private var pieces: [Piece] = ConfettiView.make()
    @State private var go = false

    private static let symbols = ["🎉", "✨", "🎊", "⭐️", "👑", "❤️"]
    private static func make() -> [Piece] {
        (0..<28).map { i in
            Piece(id: i, x: .random(in: 0.02...0.98), symbol: symbols[i % symbols.count],
                  size: .random(in: 20...38), delay: .random(in: 0...0.35),
                  dur: .random(in: 1.3...2.1), rot: .random(in: -260...260))
        }
    }

    var body: some View {
        GeometryReader { geo in
            ZStack {
                ForEach(pieces) { p in
                    Text(p.symbol).font(.system(size: p.size))
                        .position(x: p.x * geo.size.width, y: go ? geo.size.height + 40 : -40)
                        .rotationEffect(.degrees(go ? p.rot : 0))
                        .opacity(go ? 0 : 1)
                        .animation(.easeIn(duration: p.dur).delay(p.delay), value: go)
                }
            }
            .onAppear { go = true }
        }
    }
}

// MARK: - Fact popup

private struct FactPopupCard: View {
    let level: LevelDef
    let onClose: () -> Void

    private var accuracyLabel: String {
        switch level.factCard?.accuracy {
        case "fact": return "Факт"
        case "simplification": return "Упрощение"
        case "legend": return "Легенда"
        default: return "Как было"
        }
    }

    var body: some View {
        BookPage {
            ScrollView {
                VStack(spacing: 12) {
                    PillLabel("Разгадано!", systemImage: "checkmark.seal.fill",
                              background: DS.Palette.success.opacity(0.2))
                    Text(level.title).font(.serifTitle(22)).foregroundStyle(DS.Palette.ink)
                        .multilineTextAlignment(.center)
                    if let card = level.factCard {
                        PillLabel(accuracyLabel, background: DS.Palette.gold.opacity(0.25))
                        Text(card.text).font(.dsBody(14)).foregroundStyle(DS.Palette.ink)
                            .multilineTextAlignment(.leading)
                        Text(card.source).font(.dsCaption(11)).italic().foregroundStyle(DS.Palette.inkSoft)
                    }
                    Button(action: onClose) {
                        Text("Дальше").font(.dsBody())
                            .foregroundStyle(DS.Palette.paper)
                            .padding(.horizontal, 30).padding(.vertical, 11)
                            .background(Capsule().fill(DS.Palette.maroon))
                    }
                    .padding(.top, 4)
                }
                .padding(24)
            }
        }
        .frame(maxWidth: 540, maxHeight: 440)
    }
}
