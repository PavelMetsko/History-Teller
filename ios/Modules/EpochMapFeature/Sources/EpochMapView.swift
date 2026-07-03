import SwiftUI
import Simulation
import DesignSystem
import GameContent
import GameProgress

/// Карта эпохи — книжный разворот: главы-уровни на пергаментной странице.
public struct EpochMapView: View {
    private let levels: [LevelDef]
    private let db: ContentDb
    private let progress: ProgressStore
    private let onSelect: (String) -> Void
    private let onBack: () -> Void

    public init(levels: [LevelDef],
                db: ContentDb,
                progress: ProgressStore,
                onSelect: @escaping (String) -> Void,
                onBack: @escaping () -> Void) {
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
            Text("Древний Рим")
                .font(.dsSerif(26))
                .foregroundStyle(DS.Palette.ink)
            Text("Пройдено \(progress.solvedCount) из \(levels.count)")
                .font(.dsCaption(12))
                .foregroundStyle(DS.Palette.inkSoft)
        }
        .frame(maxWidth: .infinity)
        .padding(.top, 2)
    }

    private var levelsArea: some View {
        ZStack {
            // корешок книги по центру
            HStack {
                Spacer()
                LinearGradient(colors: [DS.Palette.ink.opacity(0),
                                        DS.Palette.ink.opacity(0.14),
                                        DS.Palette.ink.opacity(0)],
                               startPoint: .leading, endPoint: .trailing)
                    .frame(width: 26)
                Spacer()
            }

            ScrollView(showsIndicators: false) {
                LazyVGrid(columns: columns, spacing: 16) {
                    ForEach(Array(levels.enumerated()), id: \.element.id) { idx, level in
                        LevelCard(
                            number: idx + 1,
                            title: level.title,
                            sceneId: level.scenes.first,
                            completed: progress.isCompleted(level.id),
                            unlocked: progress.isUnlocked(levelId: level.id, orderedIds: orderedIds),
                            onTap: { onSelect(level.id) }
                        )
                    }
                }
                .padding(.vertical, 4)
            }
        }
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
