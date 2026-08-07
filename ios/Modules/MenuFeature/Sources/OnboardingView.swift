import SwiftUI
import Simulation
import DesignSystem
import GameContent

/// Онбординг (landscape): не абстрактные правила, а разбор одного настоящего уровня.
/// На глазах новичка пустые кадры получают цель, каст и — по эталонному решению — героев,
/// после чего открывается факт-карточка. Показывается один раз.
///
/// Уровень задан в `Content/demo.json` и лежит в core, поэтому доступен на первом запуске.
/// Без него (старый манифест, офлайн) экран откатывается на текстовые шаги без доски.
public struct OnboardingView: View {
    private let level: LevelDef?
    private let db: ContentDb?
    private let onFinish: () -> Void

    public init(level: LevelDef? = nil, db: ContentDb? = nil, onFinish: @escaping () -> Void) {
        self.level = level
        self.db = db
        self.onFinish = onFinish
    }

    /// Шаг: что написано внизу и сколько кадров доски к этому моменту собрано.
    private struct Step {
        let key: Int
        let filled: Int      // сколько панелей заполнено героями
        var goal = false     // показывать баннер цели
        var cast = false     // показывать трей персонажей
        var fact = false     // показывать факт-карточку
    }

    private static let steps: [Step] = [
        .init(key: 1, filled: 0),
        .init(key: 2, filled: 0, goal: true),
        .init(key: 3, filled: 0, goal: true, cast: true),
        .init(key: 4, filled: 1, goal: true, cast: true),
        .init(key: 5, filled: 3, goal: true, cast: true),
        .init(key: 6, filled: 3, fact: true),
    ]

    /// Стартовый шаг из окружения — чтобы отсматривать вёрстку каждого шага без прокликивания.
    @State private var step = Int(ProcessInfo.processInfo.environment["HT_ONB_STEP"] ?? "") ?? 0
    private var cur: Step { Self.steps[step] }
    private var isLast: Bool { step == Self.steps.count - 1 }

    /// Панели эталонного решения — только со сценой (пустые кадры разбирать нечего).
    private var panels: [Panel] { (level?.solution ?? []).filter { $0.sceneId != nil } }
    private var hasBoard: Bool { !panels.isEmpty }

    public var body: some View {
        ZStack {
            DS.Palette.backdrop.ignoresSafeArea()

            // Единственный тянущийся блок — доска: она забирает ровно то, что осталось от
            // шапки, цели, трея, подписи и кнопок. Это работает только потому, что картинки
            // внутри кадров вынесены в `overlay` (см. panelView) и размер кадра не раздувают.
            //
            // Скрытые блоки не держат за собой место: пока цель и каст не показаны,
            // их полосы читались как пустой провал между доской и подписью.
            GeometryReader { geo in
                VStack(spacing: 8) {
                    header
                    if hasBoard {
                        if cur.goal { goalBanner }
                        board.frame(maxHeight: .infinity)
                            .overlay {
                                // Награда ложится поверх собранной доски — как в игре.
                                // Затемнение ограничено доской: во весь экран оно гасило
                                // и подпись, и кнопку «Начать», будто они недоступны.
                                if cur.fact, let level, level.factCard != nil { factCard(level) }
                            }
                        if cur.cast { castTray }
                    } else {
                        Spacer(minLength: 0)
                    }
                    caption
                    controls
                }
                .animation(.easeInOut(duration: 0.28), value: step)
                .padding(.horizontal, 40)
                .padding(.top, 10)
                .padding(.bottom, 16)
                .frame(maxWidth: 860)
                .frame(width: geo.size.width, height: geo.size.height)
            }
        }
    }

    // MARK: - Шапка

    private var header: some View {
        HStack {
            Text(L10n.s("ui.how_to_play").uppercased())
                .font(.dsCaption(11)).tracking(2).foregroundStyle(DS.Palette.gold)
            Spacer()
            if !isLast {
                Button(L10n.s("ui.skip")) { onFinish() }
                    .font(.dsCaption(12)).foregroundStyle(DS.Palette.paper.opacity(0.5))
                    .buttonStyle(.plain)
            }
        }
    }

    // MARK: - Цель разбираемого уровня

    @ViewBuilder
    private var goalBanner: some View {
        HStack(spacing: 8) {
            Image(systemName: "target").font(.system(size: 11))
            Text(level?.goalText ?? "").font(.dsBody(14))
        }
        .foregroundStyle(DS.Palette.gold)
    }

    // MARK: - Доска: кадры собираются по эталонному решению

    private var board: some View {
        HStack(spacing: 14) {
            ForEach(Array(panels.enumerated()), id: \.offset) { pair in
                panelView(pair.element, index: pair.offset)
            }
        }
    }

    private func panelView(_ panel: Panel, index: Int) -> some View {
        let landed = index < cur.filled
        return VStack(spacing: 5) {
            // Размер кадра держит прямоугольник, а сцена и спрайты идут поверх (`overlay`) и в
            // раскладке не участвуют. Иначе `scaledToFill` сообщает размер больше предложенного,
            // кадр раздувается, и подпись со скруглениями уходит под обрез.
            Rectangle()
                .fill(DS.Palette.ink.opacity(0.3))
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .overlay {
                    if let sid = panel.sceneId {
                        Image.scene(sid).resizable().scaledToFill()
                    }
                }
                .overlay(LinearGradient(colors: [.clear, DS.Palette.ink.opacity(0.32)],
                                        startPoint: .center, endPoint: .bottom))
                .overlay(alignment: .bottom) {
                    HStack(alignment: .bottom, spacing: 2) {
                        ForEach(Array(panel.characters.enumerated()), id: \.offset) { cp in
                            Image.character(cp.element).resizable().scaledToFit()
                                .scaleEffect(landed ? 1 : 0.4, anchor: .bottom)
                                .offset(y: landed ? 0 : 120)
                                .opacity(landed ? 1 : 0)
                                .animation(.spring(response: 0.5, dampingFraction: 0.68)
                                    .delay(Double(cp.offset) * 0.18), value: landed)
                        }
                    }
                    .padding(.bottom, 4)
                }
                .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
                .overlay(RoundedRectangle(cornerRadius: 14, style: .continuous)
                    .stroke(DS.Palette.ink, lineWidth: 4))
                .overlay(  // золото — кадр собран
                    RoundedRectangle(cornerRadius: 14, style: .continuous)
                        .stroke(DS.Palette.gold, lineWidth: 3)
                        .opacity(landed ? 0.9 : 0)
                        .shadow(color: DS.Palette.gold.opacity(landed ? 0.65 : 0), radius: 9)
                        .animation(.easeOut(duration: 0.45).delay(0.25), value: landed)
                )

            // Подпись кадра — название сцены. Показываем только у собранных: до этого
            // подсказывать порядок нечестно, новичок как раз учится его выводить.
            Text(landed ? (db?.scenes[panel.sceneId ?? ""]?.name ?? "") : " ")
                .font(.dsCaption(10)).foregroundStyle(DS.Palette.paper.opacity(0.65))
                .lineLimit(1)
        }
    }

    // MARK: - Трей персонажей

    private var castTray: some View {
        HStack(spacing: 12) {
            ForEach(level?.characters ?? [], id: \.self) { cid in
                HStack(spacing: 5) {
                    Image.character(cid).resizable().scaledToFit().frame(height: 40)
                    Text(db?.characters[cid]?.name ?? cid)
                        .font(.dsCaption(11)).foregroundStyle(DS.Palette.paper)
                }
                .padding(.horizontal, 9).padding(.vertical, 3)
                .background(
                    RoundedRectangle(cornerRadius: 10, style: .continuous)
                        .fill(DS.Palette.panel.opacity(0.5))
                        .overlay(RoundedRectangle(cornerRadius: 10, style: .continuous)
                            .stroke(DS.Palette.ink.opacity(0.7), lineWidth: 2))
                )
            }
        }
        .frame(maxWidth: .infinity)
    }

    // MARK: - Факт-карточка (последний шаг)

    private func factCard(_ level: LevelDef) -> some View {
        ZStack {
            DS.Palette.backdrop.opacity(0.88)
            VStack(alignment: .leading, spacing: 9) {
                Text(L10n.s("ui.acc_\(level.factCard?.accuracy ?? "fact")").uppercased())
                    .font(.dsCaption(10)).tracking(1.6).foregroundStyle(DS.Palette.gold)
                Text(level.factCard?.text ?? "").font(.dsBody(15))
                    .foregroundStyle(DS.Palette.ink)
                    .fixedSize(horizontal: false, vertical: true)
                Text(level.factCard?.source ?? "").font(.dsCaption(11))
                    .foregroundStyle(DS.Palette.inkSoft)
            }
            .padding(18)
            .frame(maxWidth: 560)
            .background(
                RoundedRectangle(cornerRadius: 18, style: .continuous)
                    .fill(DS.Palette.paper)
                    .overlay(RoundedRectangle(cornerRadius: 18, style: .continuous)
                        .stroke(DS.Palette.ink, lineWidth: 4))
            )
            .padding(10)
        }
        .transition(.opacity)
        .allowsHitTesting(false)
    }

    // MARK: - Подпись шага и кнопки

    private var caption: some View {
        VStack(spacing: 3) {
            Text(L10n.s("ui.onb.\(cur.key).title"))
                .font(.dsSerif(19)).foregroundStyle(DS.Palette.paper)
            Text(L10n.s("ui.onb.\(cur.key).body"))
                .font(.dsBody(14)).foregroundStyle(DS.Palette.paper.opacity(0.72))
                .multilineTextAlignment(.center)
                .lineLimit(3)
                .minimumScaleFactor(0.85)
        }
        .frame(maxWidth: .infinity)
        .id(cur.key)                       // смена текста — не «перепечатка», а замена
        .transition(.opacity)
    }

    private var controls: some View {
        HStack {
            HStack(spacing: 7) {
                ForEach(Self.steps.indices, id: \.self) { i in
                    Circle()
                        .fill(i == step ? DS.Palette.gold : DS.Palette.paper.opacity(0.3))
                        .frame(width: 7, height: 7)
                }
            }
            Spacer()
            Button {
                if isLast { onFinish() }
                else { withAnimation(.easeInOut(duration: 0.3)) { step += 1 } }
            } label: {
                Text(L10n.s(isLast ? "ui.start" : "ui.next"))
                    .font(.dsBody(15)).foregroundStyle(DS.Palette.paper)
                    .padding(.horizontal, 24).padding(.vertical, 9)
                    .background(
                        Capsule().fill(DS.Palette.maroon)
                            .overlay(Capsule().stroke(DS.Palette.ink, lineWidth: 3))
                    )
            }
            .buttonStyle(.plain)
        }
    }
}
