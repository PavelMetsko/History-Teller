import SwiftUI
import Simulation
import DesignSystem
import GameContent

/// Экран загрузки главы (landscape). Пока качается арт главы, на глазах «собирается»
/// реальный демо-уровень из встроенного Рима: настоящие сцены и персонажи запрыгивают
/// в свои слоты. Снизу — прогресс-бар и сменяющиеся подсказки «как играть» (онбординг).
public struct ChapterLoadingView: View {
    private let chapterNumber: Int
    private let chapterTitle: String
    private let epoch: String
    private let demoLevel: LevelDef?
    private let db: ContentDb
    private let onReady: () -> Void
    private var sync = ContentSync.shared

    public init(chapterNumber: Int, chapterTitle: String, epoch: String,
                demoLevel: LevelDef?, db: ContentDb,
                onReady: @escaping () -> Void) {
        self.chapterNumber = chapterNumber
        self.chapterTitle = chapterTitle
        self.epoch = epoch
        self.demoLevel = demoLevel
        self.db = db
        self.onReady = onReady
    }

    @State private var retryToken = 0
    @State private var assembled = false
    @State private var bob = false
    @State private var shimmer = false
    @State private var pulse = false
    @State private var tipIndex = 0
    private static let tipCount = 8

    /// Панели демо-уровня из эталонного решения (только со сценой). Пусто на первом запуске —
    /// уровней Рима ещё нет на диске, тогда экран показывает только прогресс и подсказку.
    private var panels: [Panel] { (demoLevel?.solution ?? []).filter { $0.sceneId != nil } }

    /// Глобальный порядок «прыжков» — слева направо, кадр за кадром.
    private func stagger(panel: Int, slot: Int) -> Double {
        var idx = 0
        for p in 0..<panel { idx += panels[p].characters.count }
        return Double(idx + slot) * 0.26
    }

    public var body: some View {
        ZStack {
            DS.Palette.backdrop.ignoresSafeArea()

            GeometryReader { geo in
                VStack(spacing: 24) {
                    header
                    board
                        .frame(maxWidth: .infinity)
                        .frame(height: min(geo.size.height * 0.48, 220))
                    footer
                }
                .padding(.horizontal, 46)
                .padding(.vertical, 24)
                .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .center)
            }
        }
        .overlay {
            // Сеть отвалилась посреди докачки — не выкидываем в меню молча, даём повторить.
            if let failure = sync.failure {
                downloadFailed(failure)
            }
        }
        .task(id: retryToken) {
            await sync.ensureChapter(epoch)
            guard sync.failure == nil else { return }
            try? await Task.sleep(nanoseconds: 400_000_000)  // короткий показ «100% · Готово!» перед скрытием
            onReady()
        }
        .onAppear {
            tipIndex = Int.random(in: 0..<Self.tipCount)  // одна случайная подсказка на загрузку
            withAnimation { assembled = true }
            withAnimation(.easeInOut(duration: 1.4).repeatForever(autoreverses: true)) { bob = true }
            withAnimation(.linear(duration: 1.1).repeatForever(autoreverses: false)) { shimmer = true }
            withAnimation(.easeInOut(duration: 0.9).repeatForever(autoreverses: true)) { pulse = true }
        }
    }

    /// Загрузка не удалась: причина, «Повторить» и выход в меню — вместо молчаливого возврата.
    @ViewBuilder
    private func downloadFailed(_ message: String) -> some View {
        ZStack {
            DS.Palette.backdrop.opacity(0.94).ignoresSafeArea()
            VStack(spacing: 14) {
                // Подложка здесь — тёмный backdrop, поэтому текст бумажный: ink на нём
                // давал контраст около 1.1:1, то есть не читался вовсе.
                Text(L10n.s("ui.load_fail")).font(.dsSerif(20))
                    .foregroundStyle(DS.Palette.paper)
                Text(message).font(.dsCaption(12)).foregroundStyle(DS.Palette.paper.opacity(0.75))
                    .multilineTextAlignment(.center)
                HStack(spacing: 12) {
                    Button(L10n.s("ui.retry")) { retryToken += 1 }
                        .buttonStyle(.borderedProminent).tint(DS.Palette.maroon)
                    Button(L10n.s("ui.cancel")) { onReady() }
                        .buttonStyle(.bordered).tint(DS.Palette.paper)
                }
                .font(.dsBody(14))
            }
            .padding(28)
        }
    }

    // MARK: - Шапка (только про целевую главу)

    private var header: some View {
        VStack(spacing: 3) {
            Text(L10n.s("ui.downloading_chapter").uppercased())
                .font(.dsCaption(11)).tracking(2)
                .foregroundStyle(DS.Palette.gold)
            Text(chapterTitle)
                .font(.dsSerif(20)).foregroundStyle(DS.Palette.paper)
        }
        .frame(maxWidth: .infinity)
    }

    // MARK: - Доска (реальные сцены + персонажи)

    private var board: some View {
        HStack(spacing: 20) {
            ForEach(Array(panels.enumerated()), id: \.offset) { pair in
                panelView(pair.element, panelIndex: pair.offset)
            }
        }
    }

    private func panelView(_ panel: Panel, panelIndex: Int) -> some View {
        let landed = panel.characters.isEmpty ? true : assembled
        return ZStack(alignment: .bottom) {
            if let sid = panel.sceneId {
                Image.scene(sid).resizable().scaledToFill()
            }
            LinearGradient(colors: [.clear, DS.Palette.ink.opacity(0.28)],
                           startPoint: .center, endPoint: .bottom)

            HStack(alignment: .bottom, spacing: 2) {
                ForEach(Array(panel.characters.enumerated()), id: \.offset) { cpair in
                    sprite(cpair.element, delay: stagger(panel: panelIndex, slot: cpair.offset))
                }
            }
            .padding(.bottom, 6)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .stroke(DS.Palette.ink, lineWidth: 4)
        )
        .overlay(  // золотое свечение, когда кадр заполнен
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .stroke(DS.Palette.gold, lineWidth: 3)
                .opacity(landed ? 0.9 : 0)
                .shadow(color: DS.Palette.gold.opacity(landed ? 0.7 : 0), radius: 10)
                .animation(.easeOut(duration: 0.5).delay(stagger(panel: panelIndex, slot: panel.characters.count)), value: assembled)
        )
    }

    private func sprite(_ id: String, delay: Double) -> some View {
        Image.character(id).resizable().scaledToFit()
            .frame(maxHeight: .infinity)
            .offset(y: assembled ? (bob ? -4 : 0) : 150)
            .scaleEffect(assembled ? 1 : 0.4, anchor: .bottom)
            .opacity(assembled ? 1 : 0)
            .animation(.spring(response: 0.55, dampingFraction: 0.6).delay(delay), value: assembled)
    }

    // MARK: - Подвал (подсказки + прогресс)

    private var footer: some View {
        HStack(alignment: .bottom, spacing: 22) {
            VStack(alignment: .leading, spacing: 5) {
                HStack(spacing: 6) {
                    Image(systemName: "lightbulb.fill").font(.system(size: 12))
                    Text(L10n.s("ui.how_to_play").uppercased()).font(.dsCaption(10)).tracking(1.4)
                }
                .foregroundStyle(DS.Palette.gold)

                Text(L10n.s("ui.tip.\(tipIndex + 1)"))
                    .font(.dsBody(15)).foregroundStyle(DS.Palette.paper)
                    .fixedSize(horizontal: false, vertical: true)
                    .transition(.opacity)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .frame(height: 46, alignment: .top)

            VStack(alignment: .trailing, spacing: 6) {
                progressBar
                HStack {
                    Text(sync.progressValue >= 1 ? L10n.s("ui.ready") : L10n.s("ui.downloading_chapter"))
                        .font(.dsCaption(10)).foregroundStyle(DS.Palette.paper.opacity(0.5))
                    Spacer()
                    Text("\(Int((sync.progressValue * 100).rounded()))%")
                        .font(.dsCaption(10)).foregroundStyle(DS.Palette.gold)
                        .monospacedDigit()
                }
            }
            .frame(width: 230)
        }
        .padding(.horizontal, 30)
    }

    private var progressBar: some View {
        GeometryReader { geo in
            let fillW = max(6, geo.size.width * CGFloat(sync.progressValue))
            ZStack(alignment: .leading) {
                RoundedRectangle(cornerRadius: 8)
                    .fill(DS.Palette.paper.opacity(0.14))
                    .overlay(RoundedRectangle(cornerRadius: 8).stroke(DS.Palette.ink, lineWidth: 2))

                RoundedRectangle(cornerRadius: 6)
                    .fill(DS.Palette.gold)
                    .frame(width: fillW)
                    .overlay(  // бегущий блик — видно, что загрузка идёт
                        GeometryReader { g in
                            let band = max(22, g.size.width * 0.3)
                            LinearGradient(colors: [.clear, DS.Palette.paper.opacity(0.65), .clear],
                                           startPoint: .leading, endPoint: .trailing)
                                .frame(width: band)
                                .offset(x: -band + (shimmer ? 1 : 0) * (g.size.width + band))
                        }
                        .clipShape(RoundedRectangle(cornerRadius: 6))
                        .allowsHitTesting(false)
                    )
                    .shadow(color: DS.Palette.gold.opacity(pulse ? 0.8 : 0.25),  // пульсирующее свечение
                            radius: pulse ? 7 : 2)
                    .animation(.easeOut(duration: 0.35), value: sync.progressValue)
            }
        }
        .frame(height: 12)
    }
}
