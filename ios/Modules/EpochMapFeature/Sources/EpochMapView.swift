import SwiftUI
import Simulation
import DesignSystem
import GameContent
import GameProgress

/// Карта эпохи — книжный разворот: главы-уровни на пергаментной странице.
public struct EpochMapView: View {
    private let title: String
    private let levels: [LevelDef]
    private let db: ContentDb
    private let progress: ProgressStore
    private let onSelect: (String) -> Void
    private let onBack: () -> Void

    public init(title: String = "Древний Рим",
                levels: [LevelDef],
                db: ContentDb,
                progress: ProgressStore,
                onSelect: @escaping (String) -> Void,
                onBack: @escaping () -> Void) {
        self.title = title
        self.levels = levels
        self.db = db
        self.progress = progress
        self.onSelect = onSelect
        self.onBack = onBack
    }

    private var orderedIds: [String] { levels.map(\.id) }
    private var columns: [GridItem] { Array(repeating: GridItem(.flexible(), spacing: 18), count: 4) }

    public var body: some View {
        ZStack {
            DS.Palette.backdrop.ignoresSafeArea()

            BookPage {
                VStack(spacing: 10) {
                    header
                    levelsArea
                }
                .padding(EdgeInsets(top: 14, leading: 26, bottom: 16, trailing: 26))
            }
            .padding(EdgeInsets(top: 14, leading: 18, bottom: 14, trailing: 18))
            .overlay(alignment: .topLeading) {
                RibbonButton(systemImage: "chevron.left") { onBack() }.offset(x: 42, y: -12)
            }
        }
    }

    private var header: some View {
        VStack(spacing: 2) {
            Text(title)
                .font(.dsSerif(26))
                .foregroundStyle(DS.Palette.ink)
            Text(L10n.s("ui.progress", levels.filter { progress.isCompleted($0.id) }.count, levels.count))
                .font(.dsCaption(12))
                .foregroundStyle(DS.Palette.inkSoft)
        }
        .frame(maxWidth: .infinity)
        .padding(.top, 2)
    }

    /// Уровни, сгруппированные в подглавы-акты (непрерывными сериями по полю `act`),
    /// с сохранением сквозного номера уровня (1…N) для цепочки открытия.
    private var sections: [(act: String?, items: [(index: Int, level: LevelDef)])] {
        var result: [(String?, [(index: Int, level: LevelDef)])] = []
        for (idx, level) in levels.enumerated() {
            if let last = result.last, last.0 == level.act {
                result[result.count - 1].1.append((idx, level))
            } else {
                result.append((level.act, [(idx, level)]))
            }
        }
        return result
    }

    private var levelsArea: some View {
        ScrollView(showsIndicators: false) {
            VStack(alignment: .leading, spacing: 14) {
                ForEach(Array(sections.enumerated()), id: \.offset) { _, section in
                    if let act = section.act {
                        actHeader(act)
                    }
                    LazyVGrid(columns: columns, spacing: 16) {
                        ForEach(section.items, id: \.level.id) { entry in
                            LevelCard(
                                number: entry.index + 1,
                                title: entry.level.title,
                                sceneId: entry.level.cover ?? entry.level.scenes.first,
                                completed: progress.isCompleted(entry.level.id),
                                unlocked: progress.isUnlocked(levelId: entry.level.id, orderedIds: orderedIds),
                                onTap: { onSelect(entry.level.id) }
                            )
                        }
                    }
                }
            }
            .padding(.vertical, 4)
        }
    }

    /// Заголовок акта — тиснёная строка с золотыми линиями по бокам (как разделы в книге).
    private func actHeader(_ title: String) -> some View {
        HStack(spacing: 12) {
            rule
            Text(title.uppercased())
                .font(.dsSerif(14))
                .tracking(1.5)
                .foregroundStyle(DS.Palette.maroon)
                .fixedSize()
            rule
        }
        .padding(.top, 6)
    }

    private var rule: some View {
        LinearGradient(colors: [DS.Palette.gold.opacity(0), DS.Palette.gold.opacity(0.7)],
                       startPoint: .leading, endPoint: .trailing)
            .frame(height: 1.5)
    }
}

private struct LevelCard: View {
    let number: Int
    let title: String
    let sceneId: String?
    let completed: Bool
    let unlocked: Bool
    let onTap: () -> Void

    var body: some View {
        Button(action: { if unlocked { onTap() } }) {
            VStack(spacing: 6) {
                thumbnail
                Text("\(number). \(title)")
                    .font(.dsSerif(12))
                    .foregroundStyle(unlocked ? DS.Palette.ink : DS.Palette.inkSoft)
                    .lineLimit(2)
                    .multilineTextAlignment(.center)
                    .frame(height: 30)
                    .padding(.horizontal, 4)
            }
            .padding(8)
            .background(RoundedRectangle(cornerRadius: 14, style: .continuous).fill(DS.Palette.paper))
            .overlay(RoundedRectangle(cornerRadius: 14, style: .continuous)
                .strokeBorder(DS.Palette.ink.opacity(unlocked ? 0.6 : 0.35), lineWidth: 2))
        }
        .buttonStyle(.plain)
        .disabled(!unlocked)
    }

    private var thumbnail: some View {
        ZStack {
            if let sceneId {
                Image.scene(sceneId)
                    .resizable().scaledToFill()
                    .frame(height: 74)
                    .clipped()
                    .saturation(unlocked ? 1 : 0)
            } else {
                DS.Palette.sky.opacity(0.4).frame(height: 74)
            }

            if !unlocked {
                Color.black.opacity(0.4)
                Image(systemName: "lock.fill")
                    .font(.system(size: 24, weight: .bold))
                    .foregroundStyle(.white.opacity(0.9))
            } else if completed {
                VStack {
                    HStack {
                        Spacer()
                        ZStack {
                            Image(systemName: "seal.fill")
                                .foregroundStyle(DS.Palette.success)
                            Image(systemName: "checkmark")
                                .font(.system(size: 11, weight: .heavy))
                                .foregroundStyle(.white)
                        }
                        .font(.system(size: 26))
                        .shadow(color: .black.opacity(0.25), radius: 2, y: 1)
                    }
                    Spacer()
                }
                .padding(6)
            }
        }
        .frame(height: 74)
        .frame(maxWidth: .infinity)
        .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
        .overlay(RoundedRectangle(cornerRadius: 10, style: .continuous)
            .strokeBorder(DS.Palette.ink.opacity(0.5), lineWidth: 2))
    }
}
