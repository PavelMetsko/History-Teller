import SwiftUI
import Simulation
import GameContent
import DesignSystem

/// Кадры панелей в системе координат "board" — для хит-теста дропа.
private struct PanelFramesKey: PreferenceKey {
    static var defaultValue: [Int: CGRect] = [:]
    static func reduce(value: inout [Int: CGRect], nextValue: () -> [Int: CGRect]) {
        value.merge(nextValue()) { _, new in new }
    }
}

/// Звук по типу события (сами события выводятся из эффектов правила — см. LevelBoardModel.beat).
private func sfx(for beat: LevelBoardModel.Beat) -> Audio.SFX {
    // Один акцент на все события доски. Раньше их было двенадцать (удар меча, приговор, корона,
    // барабан…), но за игру большинство звучало по два-три раза и только пестрило; общий акцент
    // читается как «на доске что-то произошло» и не спорит с музыкой.
    beat.kind == .downfall ? .error : .accent
}

private extension Font {
    static func serifTitle(_ size: CGFloat) -> Font { .system(size: size, weight: .bold, design: .serif) }
}

public struct LevelBoardView: View {
    @State private var model: LevelBoardModel
    @State private var activeBeats: [LevelBoardModel.Beat] = []
    @State private var celebrate = false
    /// Уровень решён, история ещё не открыта: на доске висит зов «Дальше».
    @State private var awaitingReveal = false
    /// Подсказка «кадры можно менять местами»: показывается, когда стоят ≥2 сцен, первые три раза.
    @State private var showSwapHint = false
    @State private var revealPulse = false
    @State private var showInfo = false
    @State private var demoMode = false
    @State private var shakeData: CGFloat = 0

    // Кастомный драг
    @State private var draggingItem: LevelBoardModel.Selection?
    @State private var dragLocation: CGPoint = .zero
    @State private var panelFrames: [Int: CGRect] = [:]
    @State private var hoverPanel: Int?
    @State private var draggingPanel: Int?
    @State private var dragPanelOffset: CGSize = .zero

    private let onSolved: (() -> Void)?
    private let onExit: (() -> Void)?
    private let boardSpace = "board"

    public init(level: LevelDef,
                db: ContentDb,
                onSolved: (() -> Void)? = nil,
                onExit: (() -> Void)? = nil,
                debugArrangement: [(scene: String?, chars: [String])]? = nil,
                debugShowFact: Bool = false) {
        let m = LevelBoardModel(level: level, db: db)
        if let arr = debugArrangement { m.applyArrangement(arr) }
        if debugShowFact { m.showFact = true }
        _model = State(initialValue: m)
        self.onSolved = onSolved
        self.onExit = onExit
    }

    public var body: some View {
        ZStack {
            DS.Palette.backdrop.ignoresSafeArea()

            BookPage {
                GeometryReader { boardGeo in
                    VStack(spacing: 8) {
                        titleBar
                        panelsGrid
                            .overlay(alignment: .top) {
                                if showSwapHint {
                                    HStack(spacing: 6) {
                                        Image(systemName: "arrow.left.arrow.right").font(.system(size: 12, weight: .bold))
                                        Text(L10n.s("ui.swap_hint")).font(.dsCaption(12))
                                    }
                                    .foregroundStyle(DS.Palette.ink)
                                    .padding(.horizontal, 12).padding(.vertical, 6)
                                    .background(Capsule().fill(DS.Palette.gold.opacity(0.95)))
                                    .shadow(color: .black.opacity(0.3), radius: 3, y: 1)
                                    .padding(.top, 6)
                                    .transition(.move(edge: .top).combined(with: .opacity))
                                }
                            }
                        if let step = model.coachStep, !model.showFact, !awaitingReveal {
                            coachBubble(step)
                        }
                        tokenTray(scale: trayScale(size: boardGeo.size))
                    }
                    .padding(EdgeInsets(top: 8, leading: 20, bottom: 8, trailing: 20))
                }
            }
            .padding(EdgeInsets(top: 6, leading: 18, bottom: 6, trailing: 18))
            .overlay(alignment: .topLeading) { bookmark.offset(x: 42, y: -12) }
            .modifier(Shake(animatableData: shakeData))

            // призрак перетаскиваемого токена — едет за пальцем
            if let item = draggingItem {
                dragGhost(item)
                    .position(x: dragLocation.x, y: dragLocation.y - 44)
                    .allowsHitTesting(false)
                    .transition(.identity)
            }

            if celebrate { ConfettiView().allowsHitTesting(false).transition(.opacity) }
            if awaitingReveal && !model.showFact { revealButton.zIndex(9) }
            if model.showFact { factPopup.zIndex(10) }
            if showInfo { hintPopup.zIndex(11) }
        }
        .coordinateSpace(.named(boardSpace))
        .onPreferenceChange(PanelFramesKey.self) { panelFrames = $0 }
        .onChange(of: model.changeToken) { _, _ in
            maybeShowSwapHint()
            reactToEvents()
            // Полная, но нерешённая доска без единого диагноза (уровень без эталона) — общая тряска.
            if !model.isSolved && model.isBoardComplete && model.panelDiagnoses.allSatisfy({ $0 == .ok }) { triggerWrong() }
        }
        // Валидация мгновенная: как только у панели появился диагноз — звук и тряска.
        .onChange(of: model.wrongToken) { _, _ in triggerWrong() }
        .onChange(of: model.isSolved) { _, solved in
            if solved { win() }
            // Доска разобрана («заново» или снятый токен) — звать к истории больше нечем.
            else { awaitingReveal = false; celebrate = false }
        }
        .onAppear {
            // музыкой рулит координатор (RootView) — сквозняком между экранами
            if ProcessInfo.processInfo.environment["HT_DEMO"] == "1" {
                demoMode = true; model.applySolution(); model.showFact = false
            }
            if ProcessInfo.processInfo.environment["HT_WRONG"] == "1" {
                model.fillDebugWrong()
            }
            // Как HT_DEMO, но с полным финалом: демо-режим глушит победу ради снапшот-тестов,
            // а посмотреть на зов к истории и карточку иначе можно только руками.
            if ProcessInfo.processInfo.environment["HT_SOLVED"] == "1" { model.applySolution() }
        }
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

    /// Цель для перетаскивания панели.
    ///
    /// Опираемся только на рамки ОСТАЛЬНЫХ кадров: рамка перетаскиваемого меряется геометрией
    /// внутри него самого и едет за пальцем, поэтому по ней ничего определить нельзя — ни того,
    /// что палец над чужим кадром, ни того, что над своим.
    ///
    /// Между кадрами есть зазоры, и палец нередко отпускают там. Чтобы бросок не пропадал,
    /// добираем ближайший кадр — но только когда палец реально ушёл в сторону: иначе
    /// удержание с микросдвигом меняло кадры местами само по себе.
    private func panelDropTarget(at p: CGPoint, shift: CGFloat) -> Int? {
        let others = panelFrames.filter { $0.key != draggingPanel }
        if let hit = others.first(where: { $0.value.contains(p) })?.key { return hit }
        guard let (idx, frame) = others.min(by: { a, b in
            hypot(a.value.midX - p.x, a.value.midY - p.y) < hypot(b.value.midX - p.x, b.value.midY - p.y)
        }) else { return nil }
        guard shift >= frame.width * 0.5 else { return nil }
        return hypot(frame.midX - p.x, frame.midY - p.y) <= frame.width * 1.2 ? idx : nil
    }

    /// Перестановка кадров: удержание «берёт» кадр, затем его ведут пальцем.
    ///
    /// Раньше это был один sequenced-жест, и у него не приходил `onEnded`, если палец после
    /// удержания не двигался, — кадр так и оставался увеличенным, будто всё ещё выделен.
    /// Поэтому перенос вынесен в обычный DragGesture: он получает отпускание всегда и
    /// служит единственной точкой сброса состояния.
    private func panelReorderGesture(_ i: Int) -> some Gesture {
        let minShift: CGFloat = 24        // меньше — считаем, что игрок кадр не двигал

        let pick = LongPressGesture(minimumDuration: 0.45)
            .onEnded { _ in
                if draggingPanel == nil {
                    draggingPanel = i; model.selected = nil; Haptics.light()
                }
            }

        let move = DragGesture(minimumDistance: 0, coordinateSpace: .named(boardSpace))
            .onChanged { v in
                guard draggingPanel == i else { return }
                let shift = hypot(v.translation.width, v.translation.height)
                dragPanelOffset = shift < 8 ? .zero : v.translation
                let target = shift < minShift ? nil : panelDropTarget(at: v.location, shift: shift)
                if target != hoverPanel, target != nil { Haptics.light() }
                hoverPanel = target
            }
            .onEnded { v in
                guard draggingPanel == i else { return }
                let shift = hypot(v.translation.width, v.translation.height)
                if shift >= minShift, let to = panelDropTarget(at: v.location, shift: shift), to != i {
                    model.movePanel(from: i, to: to); Audio.shared.play(.select); Haptics.light()
                }
                draggingPanel = nil; dragPanelOffset = .zero; hoverPanel = nil
            }

        return pick.simultaneously(with: move)
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
        for beat in model.lastBeats {
            Audio.shared.play(sfx(for: beat))
            if beat.kind == .kill { Haptics.error() } else { Haptics.rigid() }
            let id = beat.id
            activeBeats.append(beat)
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.4) { activeBeats.removeAll { $0.id == id } }
        }
    }

    /// Первые три уровня: как только стоят две сцены — на 6 секунд всплывает «зажми и перетащи».
    private func maybeShowSwapHint() {
        let key = "ht.swap_hint_shown"
        let shown = UserDefaults.standard.integer(forKey: key)
        // На туториальных уровнях плашку не показываем: там про перетаскивание говорит гид,
        // и две подсказки одновременно только загромождают доску.
        guard shown < 3, !showSwapHint, !model.isSolved, model.level.coach.isEmpty,
              model.panels.filter({ $0.sceneId != nil }).count >= 2 else { return }
        UserDefaults.standard.set(shown + 1, forKey: key)
        withAnimation(.spring(response: 0.4, dampingFraction: 0.8)) { showSwapHint = true }
        DispatchQueue.main.asyncAfter(deadline: .now() + 6) { withAnimation { showSwapHint = false } }
    }

    private func win() {
        Audio.shared.play(.win); Haptics.success()
        withAnimation(.spring(response: 0.4, dampingFraction: 0.5)) { celebrate = true }
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.6) { withAnimation { celebrate = false } }
        if !demoMode {
            // Историю не выкидываем сама собой: игрок только что собрал сцену и хочет
            // разглядеть, что получилось. Вместо этого зовём кнопкой — открыть её можно
            // когда захочется, а из карточки вернуться назад на доску.
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
                // За эту секунду доску могли уже разобрать — тогда звать некуда.
                guard model.isSolved else { return }
                withAnimation(.spring(response: 0.5, dampingFraction: 0.7)) { awaitingReveal = true }
            }
        }
        onSolved?()
    }

    private func dismissFact() {
        withAnimation(.easeInOut(duration: 0.2)) { model.showFact = false }
        onExit?()
    }

    /// «Ещё раз» — сбросить доску и играть тот же уровень заново.
    private func replayLevel() {
        Audio.shared.play(.select)
        withAnimation(.easeInOut(duration: 0.2)) { model.showFact = false }
        model.reset()
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
        ZStack(alignment: .topTrailing) {
            HStack(alignment: .top, spacing: 8) {
                Image(systemName: model.isSolved ? "checkmark.square.fill" : "square")
                    .font(.system(size: 16, weight: .bold))
                    .foregroundStyle(model.isSolved ? DS.Palette.success : DS.Palette.ink)
                    .padding(.top, 2)
                // Цель — это условие задачи: обрезать её многоточием нельзя. Три строки и
                // ужатие шрифта до 60% — длинные формулировки влезают целиком.
                Text(model.level.goalText ?? model.level.title)
                    .font(.serifTitle(18))
                    .foregroundStyle(DS.Palette.ink)
                    .lineLimit(3)
                    .minimumScaleFactor(0.6)
                    .multilineTextAlignment(.center)
                    .fixedSize(horizontal: false, vertical: true)
            }
            .frame(maxWidth: .infinity)
            .padding(.horizontal, 104)   // резерв под угловые кнопки, текст переносится

            controls
        }
        .padding(.top, 18)   // отступ сверху, чтобы кнопки не наезжали на золотой уголок
    }

    // MARK: Comic grid (middle) — панели с 16px зазором

    private var panelsGrid: some View {
        GeometryReader { geo in
            let n = max(1, model.panels.count)
            let gap: CGFloat = 16
            let cellH = min(geo.size.height, 370)   // не даём панелям разрастаться на iPad
            let maxCellW = cellH * 1.2
            let cellW = min((geo.size.width - gap * CGFloat(n - 1)) / CGFloat(n), maxCellW)
            HStack(spacing: gap) {
                ForEach(model.panels.indices, id: \.self) { i in
                    PanelCell(model: model, index: i,
                              size: CGSize(width: cellW, height: cellH),
                              highlighted: hoverPanel == i || (model.selected != nil),
                              diagnosis: model.panelDiagnoses.indices.contains(i) ? model.panelDiagnoses[i] : .ok,
                              boardSpace: boardSpace,
                              beats: activeBeats.filter { $0.panelIndex == i },
                              isReordering: draggingPanel != nil)
                        // Без наклона: кадр — страница комикса, перекошенная она читается как сбой.
                        .scaleEffect(draggingPanel == i ? 1.04
                                     : (draggingPanel != nil && hoverPanel == i ? 0.96 : 1))
                        .offset(draggingPanel == i ? dragPanelOffset : .zero)
                        .shadow(color: .black.opacity(draggingPanel == i ? 0.38 : 0),
                                radius: draggingPanel == i ? 18 : 0, y: draggingPanel == i ? 12 : 0)
                        .overlay {
                            // Цель-своп под пальцем: золотая подсветка + стрелки ⇄ «поменять местами».
                            if draggingPanel != nil && draggingPanel != i && hoverPanel == i {
                                RoundedRectangle(cornerRadius: 10, style: .continuous)
                                    .fill(DS.Palette.gold.opacity(0.22))
                                    .overlay(
                                        Image(systemName: "arrow.left.arrow.right")
                                            .font(.system(size: 24, weight: .bold))
                                            .foregroundStyle(DS.Palette.gold)
                                            .shadow(color: .black.opacity(0.35), radius: 2, y: 1)
                                    )
                                    .allowsHitTesting(false)
                                    .transition(.opacity)
                            }
                        }
                        .zIndex(draggingPanel == i ? 10 : 0)
                        .animation(.spring(response: 0.3, dampingFraction: 0.7), value: draggingPanel)
                        .animation(.spring(response: 0.3, dampingFraction: 0.7), value: hoverPanel)
                        // simultaneous, а не highPriority: жест начинается только после удержания,
                        // поэтому обычные тапы должны свободно доходить до кнопок персонажей.
                        .simultaneousGesture(panelReorderGesture(i),
                                 including: model.panels[i].sceneId != nil ? .all : .subviews)
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
    }

    // MARK: Token tray (horizontal, bottom)

    private func tokenTray(scale: CGFloat) -> some View {
        HStack(spacing: 12 * scale) {
            Spacer(minLength: 0)
            ForEach(model.level.scenes, id: \.self) { sid in
                SceneToken(sceneId: sid, name: model.sceneName(sid),
                           selected: model.selected == .scene(sid), scale: scale,
                           coached: model.coachHighlightScenes.contains(sid))
                    .modifier(CoachPulse(active: model.coachHighlightScenes.contains(sid)))
                    .opacity(draggingItem == .scene(sid) ? 0.35 : 1)
                    .onTapGesture { Audio.shared.play(.select); model.selectItem(.scene(sid)) }
                    .gesture(dragGesture(for: .scene(sid)))
            }
            Rectangle().fill(DS.Palette.ink.opacity(0.3))
                .frame(width: 1.5, height: 60 * scale).padding(.horizontal, 2)
            ForEach(model.roster, id: \.self) { id in
                CharToken(id: id, name: model.characterName(id),
                          badges: StateBadges.emojis(for: id, in: model.world),
                          selected: model.selected == .character(id), scale: scale,
                          coached: model.coachHighlightChars.contains(id))
                    .modifier(CoachPulse(active: model.coachHighlightChars.contains(id)))
                    .opacity(draggingItem == .character(id) ? 0.35 : 1)
                    .onTapGesture { Audio.shared.play(.select); model.selectItem(.character(id)) }
                    .gesture(dragGesture(for: .character(id)))
            }
            Spacer(minLength: 0)
        }
        .frame(height: 90 * scale)
    }

    /// Крупнее токены на широких экранах (iPad), на iPhone — как было.
    /// Масштаб нижнего ряда токенов.
    ///
    /// Считался по одной ширине — а телефон в ландшафте как раз широкий и низкий (у 15 Pro
    /// 852×393): ширина давала множитель больше единицы, и ряд не помещался по высоте.
    /// Теперь берём меньшее из двух ограничений.
    private func trayScale(size: CGSize) -> CGFloat {
        min(1.7, max(0.78, min(size.width / 720, size.height / 440)))
    }

    /// Реплика гида-помощника. Висит над рядом токенов и не перехватывает касания:
    /// игрок должен продолжать играть, а не закрывать окошки.
    @ViewBuilder
    private func coachBubble(_ step: CoachStep) -> some View {
        HStack(alignment: .top, spacing: 8) {
                Image(systemName: "hand.point.right.fill")
                    .font(.system(size: 13)).foregroundStyle(DS.Palette.maroon)
                Text(L10n.s("level.\(model.level.id).coach.\(step.text)"))
                    .font(.dsBody(13)).foregroundStyle(DS.Palette.ink)
                    .fixedSize(horizontal: false, vertical: true)
            }
            .padding(.horizontal, 14).padding(.vertical, 6)
            .background(
                RoundedRectangle(cornerRadius: 12, style: .continuous)
                    .fill(DS.Palette.paper)
                    .shadow(color: DS.Palette.ink.opacity(0.28), radius: 8, y: 3))
            .overlay(RoundedRectangle(cornerRadius: 12, style: .continuous)
                .strokeBorder(DS.Palette.gold, lineWidth: 2))
        .frame(maxWidth: 520)
        .id(step.text)                          // смена шага — новая реплика, а не правка старой
        .allowsHitTesting(false)
        .animation(.easeInOut(duration: 0.28), value: step.text)
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
            iconButton("info.circle", tint: DS.Palette.ink) {
                withAnimation(.spring(response: 0.4, dampingFraction: 0.8)) { showInfo = true }
            }
            iconButton("arrow.counterclockwise", tint: DS.Palette.maroon) { Audio.shared.play(.place); model.reset() }
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

    /// Зов к истории: появляется на решённой доске и ждёт столько, сколько нужно игроку.
    private var revealButton: some View {
        VStack {
            Spacer()
            HStack {
                Spacer()
                Button {
                    Audio.shared.play(.select)
                    withAnimation(.spring(response: 0.5, dampingFraction: 0.72)) { model.showFact = true }
                } label: {
                    HStack(spacing: 8) {
                        Image(systemName: "scroll.fill").font(.system(size: 14))
                        Text(L10n.s("ui.next")).font(.dsBody(15))
                    }
                    .foregroundStyle(DS.Palette.paper)
                    .padding(.horizontal, 24).padding(.vertical, 12)
                    .background(
                        Capsule().fill(DS.Palette.maroon)
                            .overlay(Capsule().strokeBorder(DS.Palette.gold.opacity(0.7), lineWidth: 2))
                    )
                    .shadow(color: DS.Palette.gold.opacity(revealPulse ? 0.55 : 0.15),
                            radius: revealPulse ? 12 : 4)
                }
                .buttonStyle(.plain)
            }
        }
        .padding(.trailing, 34)
        .padding(.bottom, 26)
        .transition(.move(edge: .bottom).combined(with: .opacity))
        .onAppear {
            withAnimation(.easeInOut(duration: 1.2).repeatForever(autoreverses: true)) { revealPulse = true }
        }
    }

    private var factPopup: some View {
        ZStack {
            Color.black.opacity(0.5).ignoresSafeArea()
                .onTapGesture { hideFact() }
                .transition(.opacity)
            // Высота — от экрана, а не фиксированные 440: айфон в ландшафте ниже этого,
            // и карточка вылезала за верх и низ вместе с кнопками.
            GeometryReader { geo in
                FactPopupCard(level: model.level, onClose: dismissFact,
                              onReplay: replayLevel, onBack: hideFact)
                    .frame(maxHeight: max(200, geo.size.height - 24))
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            }
            .padding(.horizontal, 40)
            .transition(.scale(scale: 0.8).combined(with: .opacity))
        }
    }

    /// Закрыть историю, оставшись на решённой доске (кнопка «Дальше» никуда не девается).
    private func hideFact() {
        withAnimation(.easeInOut(duration: 0.2)) { model.showFact = false }
    }

    private func closeHint() { withAnimation(.easeInOut(duration: 0.2)) { showInfo = false } }

    private var hintPopup: some View {
        ZStack {
            Color.black.opacity(0.5).ignoresSafeArea()
                .onTapGesture { closeHint() }
                .transition(.opacity)
            GeometryReader { geo in
                HintPopupCard(
                    title: model.level.title,
                    text: [model.level.initialText, model.level.goalHint].compactMap { $0 }.joined(separator: "\n\n"),
                    onClose: closeHint
                )
                .frame(maxHeight: max(200, geo.size.height - 24))
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            }
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
    var scale: CGFloat = 1
    var coached: Bool = false

    var body: some View {
        VStack(spacing: 3 * scale) {
            Image.scene(sceneId)
                .resizable().scaledToFill()
                .frame(width: 66 * scale, height: 46 * scale)
                .clipShape(RoundedRectangle(cornerRadius: 7 * scale, style: .continuous))
                .overlay(RoundedRectangle(cornerRadius: 7 * scale, style: .continuous)
                    .strokeBorder(selected ? DS.Palette.gold : DS.Palette.ink.opacity(0.55),
                                  lineWidth: selected ? 3 : 2))
                .overlay(coached ? RoundedRectangle(cornerRadius: 7 * scale, style: .continuous)
                    .strokeBorder(DS.Palette.gold, lineWidth: 3) : nil)
            Text(name).font(.dsCaption(9 * scale)).foregroundStyle(DS.Palette.inkSoft)
                // Длинные имена («Марк Манлий Капитолин») раньше обрезались многоточием.
                // Ужимаем кегль вместо обрезки: высота строки не меняется, вёрстка не едет.
                .lineLimit(1).minimumScaleFactor(0.6).allowsTightening(true)
        }
        .contentShape(Rectangle())
    }
}

private struct CharToken: View {
    let id: String
    let name: String
    let badges: [String]
    let selected: Bool
    var scale: CGFloat = 1
    var coached: Bool = false

    var body: some View {
        VStack(spacing: 1) {
            ZStack(alignment: .topTrailing) {
                Image.character(id).resizable().scaledToFit().frame(height: 52 * scale)
                if !badges.isEmpty {
                    Text(badges.joined()).font(.system(size: 10 * scale))
                        .padding(2).background(Circle().fill(DS.Palette.paper)).offset(x: 5, y: -1)
                }
            }
            .frame(width: 58 * scale, height: 54 * scale)
            .background(selected ? RoundedRectangle(cornerRadius: 9).fill(DS.Palette.gold.opacity(0.28)) : nil)
            .overlay(selected ? RoundedRectangle(cornerRadius: 9).strokeBorder(DS.Palette.gold, lineWidth: 3) : nil)
            .overlay(coached ? RoundedRectangle(cornerRadius: 9)
                .strokeBorder(DS.Palette.gold, lineWidth: 3) : nil)
            Text(name).font(.dsCaption(9 * scale)).foregroundStyle(DS.Palette.inkSoft)
                // Длинные имена («Марк Манлий Капитолин») раньше обрезались многоточием.
                // Ужимаем кегль вместо обрезки: высота строки не меняется, вёрстка не едет.
                .lineLimit(1).minimumScaleFactor(0.6).allowsTightening(true)
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
    let beats: [LevelBoardModel.Beat]
    /// Кадр сейчас «взят» долгим нажатием — касания по героям не должны их удалять.
    let isReordering: Bool

    @State private var killShake: CGFloat = 0

    private var panel: Panel { model.panels[index] }
    private var isTapTarget: Bool { model.selected != nil }
    private var isWrong: Bool { diagnosis != .ok }
    /// Панель верна сама по себе — беда лишь в порядке: мягкий золотой «намёк», не красная ошибка.
    private var isOrderHint: Bool { diagnosis == .wrongOrder || diagnosis == .wrongSlots }
    /// Удар-тряска панели на «жёстких» событиях — гибель, битва, поход/война.
    private var hasImpact: Bool { beats.contains { $0.kind == .kill || $0.kind == .battle || $0.kind == .conquer } }
    /// Сцена-гильотина — для падающего ножа.
    private var isGuillotine: Bool {
        (panel.sceneId.flatMap { model.db.scenes[$0]?.tags })?.contains("guillotine") ?? false
    }

    /// Литературная подсказка «почему пусто».
    private var wrongHint: String? {
        switch diagnosis {
        case .ok:              return nil
        case .wrongCharacters: return L10n.s("ui.wrong_chars")
        case .wrongScene:      return L10n.s("ui.wrong_scene")
        case .inert:           return L10n.s("ui.wrong_inert")
        case .wrongOrder:      return L10n.s("ui.wrong_order")
        case .wrongSlots:      return L10n.s("ui.wrong_slots")
        case .sceneUnused:     return L10n.s("ui.wrong_unused")
        }
    }

    private var borderColor: Color {
        if highlighted { return DS.Palette.gold }
        if isOrderHint { return DS.Palette.gold }
        if isWrong { return DS.Palette.maroon }
        return DS.Palette.ink.opacity(0.55)
    }

    /// Переходный «сок» события поверх панели (вспышка, мечи, нож, сердца, символ).
    @ViewBuilder private var juiceOverlay: some View {
        let impact = beats.filter { $0.kind == .kill || $0.kind == .battle || $0.kind == .conquer }
        let swords = beats.filter { $0.kind == .battle || $0.kind == .conquer }
        let kills = beats.filter { $0.kind == .kill }
        let love = beats.filter { $0.kind == .love }
        let badges = beats.filter {
            $0.kind != .crown && $0.kind != .love && $0.kind != .kill && $0.kind != .battle
                && $0.kind != .conquer && $0.kind != .march
        }
        ZStack {
            // удар-вспышка (красная — гибель, золотая — битва/поход)
            ForEach(impact) { b in
                ImpactFlash(color: b.kind == .kill ? DS.Palette.maroon : DS.Palette.gold)
            }
            // битва/поход — скрещённые мечи в центре
            ForEach(swords) { _ in
                PropBurst(name: "swords", size: min(size.width, size.height) * 0.5, rise: 4, hold: 0.5)
            }
            // гильотина — нож падает сверху
            if isGuillotine {
                ZStack { ForEach(kills) { _ in GuillotineBlade(panelHeight: size.height) } }
                    .frame(maxHeight: .infinity, alignment: .top)
            }
            // сердца между влюблёнными
            ZStack { ForEach(love) { _ in HeartsRise().padding(.bottom, size.height * 0.28) } }
                .frame(maxHeight: .infinity, alignment: .bottom)
            // всплывающий символ прочих событий
            ZStack { ForEach(badges) { b in FlyingBadgeView(symbol: b.symbol) } }
                .padding(.top, size.height * 0.14)
                .frame(maxHeight: .infinity, alignment: .top)
        }
    }

    var body: some View {
        ZStack {
            if let sid = panel.sceneId {
                Image.scene(sid).resizable().scaledToFill()
                    .frame(width: size.width, height: size.height).clipped()
                    .transition(.scale(scale: 0.88).combined(with: .opacity))
                    .id(sid)
                if let action = model.sceneAction(sid) {
                    // Отступ справа — под кнопку «убрать сцену»: длинные подписи вроде
                    // «заступничество» иначе переносились и заезжали ей под крестик.
                    VStack {
                        HStack {
                            PillLabel(action, background: DS.Palette.paper.opacity(0.92))
                                .lineLimit(1).minimumScaleFactor(0.7)
                            Spacer(minLength: 0)
                        }
                        Spacer(minLength: 0)
                    }
                    .padding(7)
                    .padding(.trailing, 26)
                }
                charactersOverlay(sceneId: sid)
            } else {
                DS.Palette.panel
                VStack(spacing: 4) {
                    Image(systemName: isTapTarget ? "hand.point.up.left.fill" : "photo")
                        .font(.system(size: 20))
                        .foregroundStyle(isTapTarget ? DS.Palette.maroon : DS.Palette.inkSoft.opacity(0.6))
                    Text(isTapTarget ? L10n.s("ui.tap") : L10n.s("ui.scene"))
                        .font(.dsCaption(10)).foregroundStyle(DS.Palette.inkSoft.opacity(0.7))
                }
            }
        }
        .frame(width: size.width, height: size.height)
        .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
        .animation(.spring(response: 0.4, dampingFraction: 0.72), value: panel.sceneId)
        .overlay(
            RoundedRectangle(cornerRadius: 10, style: .continuous)
                .strokeBorder(borderColor, lineWidth: (highlighted || isWrong) ? 3 : 2)
        )
        .overlay(alignment: .bottom) {
            if let hint = wrongHint {
                Text(hint)
                    .font(.dsCaption(10))
                    .foregroundStyle(isOrderHint ? DS.Palette.ink : .white)
                    .padding(.horizontal, 10).padding(.vertical, 5)
                    .background(Capsule().fill((isOrderHint ? DS.Palette.gold : DS.Palette.maroon).opacity(0.94)))
                    .overlay(Capsule().strokeBorder(.white.opacity(0.3), lineWidth: 1))
                    .padding(.bottom, 8)
                    .shadow(color: .black.opacity(0.3), radius: 3, y: 1)
                    .transition(.opacity.combined(with: .scale(scale: 0.9)))
            }
        }
        .overlay(alignment: .top) {
            // Постоянный значок «что тут происходит» — сердце, мечи, корона… (см. panelSymbols).
            if let sym = model.panelSymbols.indices.contains(index) ? model.panelSymbols[index] : nil,
               panel.sceneId != nil {
                Text(sym)
                    .font(.system(size: 20))
                    .padding(5)
                    .background(Circle().fill(DS.Palette.paper.opacity(0.9)))
                    .overlay(Circle().strokeBorder(DS.Palette.ink.opacity(0.35), lineWidth: 1))
                    .shadow(color: .black.opacity(0.25), radius: 2, y: 1)
                    .padding(.top, 34)
                    .transition(.scale.combined(with: .opacity))
                    .id(sym)
            }
        }
        .animation(.spring(response: 0.35, dampingFraction: 0.7), value: model.panelSymbols.indices.contains(index) ? model.panelSymbols[index] : nil)
        .overlay(alignment: .bottomLeading) {
            // Постоянная «ручка»: кадр со сценой можно взять долгим нажатием и поменять местами.
            // Иконка без текста — не зависит от каталога переводов и не мешает читать кадр.
            if panel.sceneId != nil && model.panels.count > 1 && !isReordering {
                Image(systemName: "arrow.left.arrow.right")
                    .font(.system(size: 11, weight: .bold))
                    .foregroundStyle(DS.Palette.ink.opacity(0.75))
                    .padding(5)
                    .background(Circle().fill(DS.Palette.paper.opacity(0.8)))
                    .padding(6)
                    .allowsHitTesting(false)
            }
        }
        .overlay { juiceOverlay }
        .modifier(Shake(travel: 5, shakes: 3, animatableData: killShake))
        .onChange(of: hasImpact) { _, k in
            if k { withAnimation(.linear(duration: 0.4)) { killShake += 1 } }
        }
        .animation(.easeInOut(duration: 0.2), value: isWrong)
        .overlay(alignment: .topTrailing) {
            if panel.sceneId != nil {
                Button {
                    Audio.shared.play(.place); Haptics.light()
                    withAnimation(.spring(response: 0.35, dampingFraction: 0.7)) {
                        model.setScene(nil, at: index)
                    }
                } label: {
                    Image(systemName: "xmark")
                        .font(.system(size: 11, weight: .heavy))
                        .foregroundStyle(DS.Palette.maroon)
                        .frame(width: 24, height: 24)
                        .background(Circle().fill(DS.Palette.paper.opacity(0.95)))
                        .overlay(Circle().strokeBorder(DS.Palette.ink.opacity(0.4), lineWidth: 1.5))
                        .shadow(color: .black.opacity(0.3), radius: 2, y: 1)
                }
                .buttonStyle(.plain)
                .padding(6)
                .transition(.scale.combined(with: .opacity))
            }
        }
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

    /// Микро-состояние персонажа для значка над головой.
    private func microState(_ charId: String, in snap: World) -> String? {
        if snap.hasFlag(charId, "crowned") { return "👑" }
        if panel.characters.contains(where: { $0 != charId && snap.hasRelation("loves", charId, $0) }) { return "💕" }
        if snap.hasFlag(charId, "plotting") { return "🗡" }
        return nil
    }

    private func charactersOverlay(sceneId: String) -> some View {
        let slots = model.slots(at: index)
        let spriteH = size.height * 0.62
        return VStack {
            Spacer(minLength: 0)
            HStack(alignment: .bottom, spacing: 4) {
                ForEach(Array(panel.characters.enumerated()), id: \.element) { pair in
                        let slot = pair.offset
                        let charId = pair.element
                        let snap = model.snapshot(after: index)
                        let dead = snap.hasFlag(charId, "dead")
                        let state = microState(charId, in: snap)
                        let plotting = !dead && snap.hasFlag(charId, "plotting")
                        let crowned = !dead && snap.hasFlag(charId, "crowned")
                        // победные/боевые состояния → поза «триумф»
                        let triumphant = !dead && ["crowned", "reigns", "emperor", "empress", "victor",
                            "conqueror", "triumphant", "honored", "beloved", "first_consul", "supreme_head", "absolute", "at_war"]
                            .contains { snap.hasFlag(charId, $0) }
                        // взаимодействие: активная сторона (убийца/победитель/обвинитель) — выпад к цели
                        let aggroBeat = beats.first {
                            ($0.kind == .kill || $0.kind == .battle || $0.kind == .condemn) && $0.secondary == charId
                        }
                        let isAggressor = aggroBeat != nil
                        let lungeDX: CGFloat = {
                            guard let vp = aggroBeat?.primary,
                                  let vs = panel.characters.firstIndex(of: vp) else { return 0 }
                            return vs > slot ? 20 : -20
                        }()
                        // союз: оба наклоняются друг к другу (мягко)
                        let allyBeat = beats.first { $0.kind == .ally && ($0.primary == charId || $0.secondary == charId) }
                        let isAlly = allyBeat != nil
                        let allyLeanDX: CGFloat = {
                            guard let ab = allyBeat else { return 0 }
                            let partner = ab.primary == charId ? ab.secondary : ab.primary
                            guard let p = partner, let ps = panel.characters.firstIndex(of: p) else { return 0 }
                            return ps > slot ? 12 : -12
                        }()
                        // разгромлен, но жив (беглец/разбит/изгнан/отвергнут/овдовел/опала) → поза «повержен-живой»
                        let defeated = !dead && ["fugitive", "defeated", "exiled", "cast_off", "widowed", "disgraced", "grieving"]
                            .contains { snap.hasFlag(charId, $0) }
                        // реакция того, «над кем» действие: отшатнуться / поникнуть / вскинуться
                        // (slump не нужен, если уже показываем позу «разгромлен»)
                        let motion: SpriteMotion = {
                            if beats.contains(where: { $0.kind == .condemn && $0.primary == charId }) { return .recoil }
                            if !defeated && beats.contains(where: { ($0.kind == .battle || $0.kind == .downfall) && $0.primary == charId }) { return .slump }
                            if beats.contains(where: { ($0.kind == .triumph || $0.kind == .conquer || $0.kind == .march) && $0.primary == charId }) { return .hop }
                            return .none
                        }()
                        // корона опускается на голову именно этого персонажа
                        let crownDrop = beats.contains { $0.kind == .crown && $0.primary == charId }
                        // этот персонаж — жертва убийства: брызги крови
                        let killVictim = beats.contains { $0.kind == .kill && $0.primary == charId }
                        Button {
                            // панель сейчас перетаскивают — касание не должно удалить героя
                            if isReordering { return }
                            // если есть выделенный элемент — ставим его, а не удаляем текущего
                            if model.selected != nil {
                                applyTap()
                            } else {
                                Audio.shared.play(.place); Haptics.light()
                                model.removeCharacter(charId, at: index)
                            }
                        } label: {
                            CharacterSprite(charId: charId, spriteH: spriteH, dead: dead, state: state,
                                            plotting: plotting, crowned: crowned, triumphant: triumphant,
                                            defeated: defeated, isAggressor: isAggressor, lungeDX: lungeDX,
                                            isAlly: isAlly, allyLeanDX: allyLeanDX, motion: motion,
                                            crownDrop: crownDrop, killVictim: killVictim,
                                            fallsLeft: slot * 2 >= panel.characters.count)
                        }
                        .buttonStyle(.plain)
                        .transition(.scale(scale: 0.4).combined(with: .opacity))
                }
                ForEach(0..<max(0, slots - panel.characters.count), id: \.self) { _ in
                    // Явный намёк «сюда нужен ещё персонаж»: пунктирная рамка + «+» (как на Android).
                    RoundedRectangle(cornerRadius: 10, style: .continuous)
                        .strokeBorder(DS.Palette.ink.opacity(0.32),
                                      style: StrokeStyle(lineWidth: 2, dash: [6, 5]))
                        .frame(width: spriteH * 0.55, height: spriteH * 0.85)
                        .overlay(
                            Text("+")
                                .font(.system(size: spriteH * 0.28, weight: .bold, design: .serif))
                                .foregroundStyle(DS.Palette.ink.opacity(0.32))
                        )
                }
            }
            .padding(.bottom, 6)
            .animation(.spring(response: 0.35, dampingFraction: 0.6), value: panel.characters)
        }
    }
}

/// Спрайт персонажа со всей «живостью»: дрожь, падение, выпад, реакция, корона, кровь, пыль.
/// Вынесен в отдельную структуру — иначе SwiftUI-компилятор не вытягивает такую цепочку по времени.
private struct CharacterSprite: View {
    let charId: String
    let spriteH: CGFloat
    let dead: Bool
    let state: String?
    let plotting: Bool
    let crowned: Bool
    let triumphant: Bool
    let defeated: Bool
    let isAggressor: Bool
    let lungeDX: CGFloat
    let isAlly: Bool
    let allyLeanDX: CGFloat
    let motion: SpriteMotion
    let crownDrop: Bool
    let killVictim: Bool
    /// Валиться внутрь кадра, а не наружу: тот, кто стоит справа, падает влево.
    /// Поворот на 80° вокруг ступней уводит голову на целый рост вбок — у крайнего
    /// персонажа она оказывалась за кромкой кадра и уезжала за экран.
    var fallsLeft: Bool = false

    /// Есть отдельная поза «повержен» (слой 3) — тогда показываем её, без ч/б и заваливания.
    private var useDeadPose: Bool { dead && GameAssets.hasDeadPose(charId) }
    /// Поза «разгромлен, но жив» (если гибели нет).
    private var useDefeatedPose: Bool { defeated && !dead && GameAssets.hasDefeatedPose(charId) }
    /// Поза «заговорщик» (флаг plotting) — если не мёртв/не разгромлен.
    private var usePlotPose: Bool { plotting && !dead && !defeated && GameAssets.hasPlotPose(charId) }
    /// Поза «триумф» на победных состояниях (если гибели/разгрома/заговора нет).
    private var useTriumphPose: Bool { triumphant && !dead && !defeated && !usePlotPose && GameAssets.hasTriumphPose(charId) }
    /// Старый трюк (ч/б + поворот на 80°) — только когда позы «повержен» нет.
    private var topple: Bool { dead && !useDeadPose }
    private var baseImageName: String {
        if useDeadPose { return GameAssets.deadImageName(charId) }
        if useDefeatedPose { return GameAssets.defeatedImageName(charId) }
        if usePlotPose { return GameAssets.plotImageName(charId) }
        if useTriumphPose { return GameAssets.triumphImageName(charId) }
        return GameAssets.characterImageName(charId)
    }

    var body: some View {
        Image(art: baseImageName)
            .resizable().scaledToFit().frame(height: spriteH)
            .modifier(Tremble(active: plotting && !usePlotPose))     // дрожь-фолбэк, если нет позы «заговорщик»
            // нет позы «повержен» → старый фолбэк: сереет, валится набок
            .grayscale(topple ? 0.9 : 0)
            .opacity(topple ? 0.82 : 1)
            .scaleEffect(topple ? 0.9 : 1)
            // Вращаем вокруг ступней: раньше поворот шёл вокруг центра, и тело приходилось
            // опускать на четверть роста, чтобы «легло на пол», — из-за чего оно уходило
            // под нижнюю кромку кадра и обрезалось.
            .rotationEffect(.degrees(topple ? (fallsLeft ? -80 : 80) : 0), anchor: .bottom)
            .offset(y: topple ? spriteH * 0.04 : 0)
            .animation(.spring(response: 0.5, dampingFraction: 0.55), value: dead)
            // короткое оседание при гибели (когда есть поза)
            .keyframeAnimator(initialValue: CGFloat(0), trigger: useDeadPose) { v, y in
                v.offset(y: y)
            } keyframes: { _ in
                KeyframeTrack {
                    CubicKeyframe(useDeadPose ? -8 : 0, duration: 0.07)
                    SpringKeyframe(0, duration: 0.3)
                }
            }
            // активная сторона делает резкий выпад к цели и отскакивает
            .keyframeAnimator(initialValue: CGFloat(0), trigger: isAggressor) { v, x in
                v.offset(x: x)
            } keyframes: { _ in
                KeyframeTrack {
                    CubicKeyframe(lungeDX, duration: 0.10)
                    SpringKeyframe(0, duration: 0.34)
                }
            }
            // союзники мягко наклоняются друг к другу и возвращаются
            .keyframeAnimator(initialValue: CGFloat(0), trigger: isAlly) { v, x in
                v.offset(x: x)
            } keyframes: { _ in
                KeyframeTrack {
                    CubicKeyframe(allyLeanDX, duration: 0.22)
                    SpringKeyframe(0, duration: 0.5)
                }
            }
            // реакция пострадавшего/триумфатора
            .modifier(ReactionMotion(motion: motion))
            .overlay(alignment: .top) { if let s = state, !dead { StateFloatie(symbol: s) } }
            .overlay(alignment: .top) { if crowned { CrownFlash() } }
            .overlay(alignment: .top) { if crownDrop { DescendingCrown() } }
            .overlay { if killVictim { PropBurst(name: "blood", size: spriteH * 0.72, rise: 6, hold: 0.75) } }
            .overlay(alignment: .bottom) { if dead { DustPuff() } }
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

/// Значок живого состояния над головой (корона/сердечки/кинжал) — мягко покачивается.
private struct StateFloatie: View {
    let symbol: String
    @State private var up = false
    var body: some View {
        Text(symbol)
            .font(.system(size: 24))
            .shadow(color: .black.opacity(0.25), radius: 2, y: 1)
            .offset(y: up ? -22 : -14)
            .scaleEffect(up ? 1.08 : 0.94)
            .onAppear {
                withAnimation(.easeInOut(duration: 0.9).repeatForever(autoreverses: true)) { up = true }
            }
            .transition(.scale.combined(with: .opacity))
    }
}

/// Пыль при падении — облачко частиц разлетается от ног и тает.
private struct DustPuff: View {
    @State private var go = false
    private let count = 7
    var body: some View {
        ZStack {
            ForEach(0..<count, id: \.self) { i in
                let a = Double(i) / Double(count - 1) * .pi   // веер 0..π
                Circle()
                    .fill(DS.Palette.paperEdge.opacity(0.9))
                    .frame(width: 9, height: 9)
                    .offset(x: go ? CGFloat(cos(a)) * 28 : 0,
                            y: go ? CGFloat(-sin(a)) * 14 : 0)
                    .scaleEffect(go ? 1.5 : 0.4)
                    .opacity(go ? 0 : 0.7)
            }
        }
        .offset(y: 8)
        .allowsHitTesting(false)
        .onAppear { withAnimation(.easeOut(duration: 0.55)) { go = true } }
    }
}

/// Золотая вспышка-лучи при короновании.
private struct CrownFlash: View {
    @State private var go = false
    private let count = 9
    var body: some View {
        ZStack {
            ForEach(0..<count, id: \.self) { i in
                Capsule()
                    .fill(DS.Palette.gold)
                    .frame(width: 3, height: 12)
                    .offset(y: go ? -34 : -16)
                    .rotationEffect(.degrees(Double(i) / Double(count) * 360))
                    .scaleEffect(go ? 1.2 : 0.4)
                    .opacity(go ? 0 : 0.9)
            }
        }
        .offset(y: -6)
        .allowsHitTesting(false)
        .onAppear { withAnimation(.easeOut(duration: 0.5)) { go = true } }
    }
}

/// Удар — цветная вспышка на всю панель, быстро гаснет (поверх идёт пропс: кровь/мечи).
/// Красная — гибель, золотая — исход битвы.
private struct ImpactFlash: View {
    var color: Color = DS.Palette.maroon
    @State private var go = false
    var body: some View {
        RoundedRectangle(cornerRadius: 10, style: .continuous)
            .fill(color)
            .opacity(go ? 0 : 0.42)
            .allowsHitTesting(false)
            .onAppear { withAnimation(.easeOut(duration: 0.45)) { go = true } }
    }
}

/// Пропс-объект, вылетающий на событии: выпрыгивает с пружиной, держится и тает вверх.
private struct PropBurst: View {
    let name: String
    var size: CGFloat = 60
    var rise: CGFloat = 8
    var spin: Double = 0
    var hold: Double = 0.55
    @State private var appear = false
    @State private var gone = false
    var body: some View {
        Image.prop(name).resizable().scaledToFit()
            .frame(width: size, height: size)
            .rotationEffect(.degrees(appear ? 0 : spin))
            .scaleEffect(appear ? 1 : 0.2)
            .offset(y: gone ? -rise : 0)
            .opacity(gone ? 0 : 1)
            .shadow(color: .black.opacity(0.25), radius: 3, y: 2)
            .allowsHitTesting(false)
            .onAppear {
                withAnimation(.spring(response: 0.3, dampingFraction: 0.5)) { appear = true }
                withAnimation(.easeOut(duration: 0.55).delay(hold)) { gone = true }
            }
    }
}

/// Нож гильотины падает сверху вниз по центру панели.
private struct GuillotineBlade: View {
    let panelHeight: CGFloat
    @State private var drop = false
    var body: some View {
        Image.prop("blade").resizable().scaledToFit()
            .frame(height: panelHeight * 0.52)
            .offset(y: drop ? -panelHeight * 0.10 : -panelHeight * 0.78)
            .opacity(drop ? 1 : 0.9)
            .allowsHitTesting(false)
            .onAppear { withAnimation(.easeIn(duration: 0.26)) { drop = true } }
    }
}

/// Переходная реакция спрайта на событие «над ним».
enum SpriteMotion: Equatable { case none, hop, slump, recoil }

/// Проигрывает короткую реакцию при смене `motion`: вскинуться (триумф),
/// поникнуть (низложение/поражение), отшатнуться (обвинение). Затем возврат в норму.
private struct ReactionMotion: ViewModifier {
    let motion: SpriteMotion
    @State private var active = false

    func body(content: Content) -> some View {
        content
            .rotationEffect(.degrees(active ? rot : 0), anchor: .bottom)
            .scaleEffect(active ? scale : 1, anchor: .bottom)
            .offset(y: active ? dy : 0)
            .onChange(of: motion) { _, m in if m != .none { play(m) } }
            .onAppear { if motion != .none { play(motion) } }
    }

    private var dy: CGFloat { motion == .hop ? -20 : motion == .slump ? 8 : 0 }
    private var rot: Double { motion == .slump ? 10 : motion == .recoil ? -12 : 0 }
    private var scale: CGFloat { motion == .recoil ? 0.9 : motion == .hop ? 1.06 : 1 }

    private func play(_ m: SpriteMotion) {
        active = false
        withAnimation(.spring(response: 0.28, dampingFraction: 0.45)) { active = true }
        DispatchQueue.main.asyncAfter(deadline: .now() + (m == .hop ? 0.42 : 0.85)) {
            withAnimation(.spring(response: 0.5, dampingFraction: 0.7)) { active = false }
        }
    }
}

/// Сердечки между влюблёнными — стайка поднимается вверх и тает.
private struct HeartsRise: View {
    @State private var go = false
    private let count = 5
    var body: some View {
        ZStack {
            ForEach(0..<count, id: \.self) { i in
                let dx = CGFloat(i - count / 2) * 16
                Text("❤️")
                    .font(.system(size: go ? 22 : 12))
                    .offset(x: dx * (go ? 1.4 : 0.5),
                            y: go ? -64 - CGFloat(i) * 6 : 0)
                    .opacity(go ? 0 : 1)
                    .animation(.easeOut(duration: 1.0).delay(Double(i) * 0.06), value: go)
            }
        }
        .allowsHitTesting(false)
        .onAppear { go = true }
    }
}

/// Корона (пропс-объект) падает сверху на голову и оседает с лёгким отскоком.
private struct DescendingCrown: View {
    @State private var landed = false
    var body: some View {
        Image.prop("crown").resizable().scaledToFit()
            .frame(width: 34, height: 34)
            .shadow(color: DS.Palette.gold.opacity(0.6), radius: landed ? 5 : 0)
            .scaleEffect(landed ? 1.0 : 1.6)
            .opacity(landed ? 1 : 0)
            .offset(y: landed ? -30 : -74)
            .allowsHitTesting(false)
            .onAppear {
                withAnimation(.spring(response: 0.4, dampingFraction: 0.5)) { landed = true }
            }
    }
}

/// Нервная дрожь заговорщика.
private struct Tremble: ViewModifier {
    let active: Bool
    @State private var on = false
    func body(content: Content) -> some View {
        content
            .rotationEffect(.degrees(active ? (on ? 2.5 : -2.5) : 0), anchor: .bottom)
            .onAppear { if active { start() } }
            .onChange(of: active) { _, a in if a { start() } else { on = false } }
    }
    private func start() {
        withAnimation(.easeInOut(duration: 0.11).repeatForever(autoreverses: true)) { on = true }
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

/// Подсказка в стиле финального окна: пергамент-карточка с плашкой «Подсказка», заголовком и текстом.
private struct HintPopupCard: View {
    let title: String
    let text: String
    let onClose: () -> Void

    var body: some View {
        BookPage {
            VStack(spacing: 0) {
                ScrollView {
                    VStack(spacing: 12) {
                        PillLabel(L10n.s("ui.hint"), systemImage: "lightbulb.fill",
                                  background: DS.Palette.gold.opacity(0.25))
                        Text(title).font(.serifTitle(22)).foregroundStyle(DS.Palette.ink)
                            .multilineTextAlignment(.center)
                        if !text.isEmpty {
                            Text(text).font(.dsBody(14)).foregroundStyle(DS.Palette.ink)
                                .multilineTextAlignment(.leading)
                        }
                    }
                    .padding(.horizontal, 24).padding(.top, 22).padding(.bottom, 12)
                }
                Button(action: onClose) {
                    Text(L10n.s("ui.ok")).font(.dsBody())
                        .foregroundStyle(DS.Palette.paper)
                        .padding(.horizontal, 30).padding(.vertical, 11)
                        .background(Capsule().fill(DS.Palette.maroon))
                }
                .padding(.bottom, 18)
            }
        }
        .frame(maxWidth: 540, maxHeight: 440)
    }
}

private struct FactPopupCard: View {
    let level: LevelDef
    let onClose: () -> Void
    var onReplay: (() -> Void)? = nil
    /// Вернуться на решённую доску, не уходя с уровня.
    var onBack: (() -> Void)? = nil

    private var accuracyLabel: String {
        switch level.factCard?.accuracy {
        case "fact": return L10n.s("ui.acc_fact")
        case "simplification": return L10n.s("ui.acc_simplification")
        case "legend": return L10n.s("ui.acc_legend")
        default: return L10n.s("ui.acc_fact")
        }
    }

    var body: some View {
        BookPage {
            // Прокручивается только текст, кнопки закреплены снизу: иначе на длинной истории
            // «Дальше» уезжает за нижнюю кромку — в ландшафте догадаться, что надо доскроллить,
            // невозможно.
            VStack(spacing: 0) {
                ScrollView {
                    VStack(spacing: 12) {
                        PillLabel(L10n.s("ui.solved"), systemImage: "checkmark.seal.fill",
                                  background: DS.Palette.success.opacity(0.2))
                        Text(level.title).font(.serifTitle(22)).foregroundStyle(DS.Palette.ink)
                            .multilineTextAlignment(.center)
                        if let card = level.factCard {
                            PillLabel(accuracyLabel, background: DS.Palette.gold.opacity(0.25))
                            Text(card.text).font(.dsBody(14)).foregroundStyle(DS.Palette.ink)
                                .multilineTextAlignment(.leading)
                            Text(card.source).font(.dsCaption(11)).italic().foregroundStyle(DS.Palette.inkSoft)
                        }
                    }
                    .padding(.horizontal, 24).padding(.top, 22).padding(.bottom, 12)
                }
                HStack(spacing: 12) {
                    if let onReplay {
                        Button(action: onReplay) {
                            Label(L10n.s("ui.replay"), systemImage: "arrow.counterclockwise")
                                .font(.dsBody())
                                .foregroundStyle(DS.Palette.maroon)
                                .padding(.horizontal, 22).padding(.vertical, 11)
                                .background(Capsule().fill(DS.Palette.paper))
                                .overlay(Capsule().strokeBorder(DS.Palette.maroon.opacity(0.5), lineWidth: 1.5))
                        }
                    }
                    Button(action: onClose) {
                        Text(L10n.s("ui.next")).font(.dsBody())
                            .foregroundStyle(DS.Palette.paper)
                            .padding(.horizontal, 30).padding(.vertical, 11)
                            .background(Capsule().fill(DS.Palette.maroon))
                    }
                }
                .padding(.horizontal, 24).padding(.bottom, 18)
            }
        }
        .frame(maxWidth: 540, maxHeight: 440)
        .overlay(alignment: .topTrailing) {
            if let onBack {
                Button(action: onBack) {
                    Image(systemName: "xmark")
                        .font(.system(size: 13, weight: .bold))
                        .foregroundStyle(DS.Palette.inkSoft)
                        .frame(width: 32, height: 32)
                        .background(Circle().fill(DS.Palette.paper))
                        .overlay(Circle().strokeBorder(DS.Palette.ink.opacity(0.25), lineWidth: 1.5))
                }
                .buttonStyle(.plain)
                .padding(10)
            }
        }
    }
}


/// Пульсация всей карточки токена, на который показывает гид: больше — обычный — меньше.
///
/// Раньше пульсировало кольцо внутри токена, и его сильно перекрывала собственная тёмная
/// рамка — со стороны это читалось как мигание внутрь, а не как «посмотри сюда».
private struct CoachPulse: ViewModifier {
    let active: Bool
    @State private var phase = false

    func body(content: Content) -> some View {
        content
            .scaleEffect(active ? (phase ? 1.12 : 0.94) : 1.0)
            // Анимацию привязываем к признаку активности: пока гид зовёт — бесконечный цикл,
            // как только перестал — цикл снимается вместе с ней, и карточка встаёт на место.
            // С `withAnimation(.repeatForever)` анимация оставалась в полёте и продолжала дышать.
            .animation(active ? .easeInOut(duration: 0.75).repeatForever(autoreverses: true) : nil,
                       value: phase)
            .animation(.easeOut(duration: 0.18), value: active)
            .onAppear { phase = active }
            .onChange(of: active) { _, now in phase = now }
    }
}
