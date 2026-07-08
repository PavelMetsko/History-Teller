import SwiftUI
import DesignSystem
import GameContent

/// Глава/эпоха для экрана выбора. Доступные — играбельны, остальные — «Скоро».
public struct Chapter: Identifiable {
    public let id: String
    public let number: Int
    public let title: String
    public let subtitle: String
    public let coverSceneId: String?   // арт обложки (сцена из эпохи)
    public let icon: String            // SF Symbol для заглушки
    public let available: Bool         // контент существует
    public let free: Bool              // бесплатная (иначе — за покупкой)
    public let progressText: String?

    public init(id: String, number: Int, title: String, subtitle: String,
                coverSceneId: String?, icon: String, available: Bool,
                free: Bool = false, progressText: String?) {
        self.id = id; self.number = number; self.title = title; self.subtitle = subtitle
        self.coverSceneId = coverSceneId; self.icon = icon
        self.available = available; self.free = free; self.progressText = progressText
    }

    /// Заблокирована пейволлом: контент есть, не бесплатна и покупка не сделана.
    public func locked(unlocked: Bool) -> Bool { available && !free && !unlocked }
}

public struct ChapterSelectView: View {
    private let chapters: [Chapter]
    private let isUnlocked: (Chapter) -> Bool
    private let priceText: (Chapter) -> String
    private let onSelect: (Chapter) -> Void
    private let onBack: () -> Void

    public init(chapters: [Chapter],
                isUnlocked: @escaping (Chapter) -> Bool = { _ in true },
                priceText: @escaping (Chapter) -> String = { _ in "" },
                onSelect: @escaping (Chapter) -> Void,
                onBack: @escaping () -> Void) {
        self.chapters = chapters
        self.isUnlocked = isUnlocked
        self.priceText = priceText
        self.onSelect = onSelect
        self.onBack = onBack
    }

    public var body: some View {
        ZStack {
            DS.Palette.backdrop.ignoresSafeArea()

            BookPage {
                VStack(spacing: 12) {
                    VStack(spacing: 2) {
                        Text("History Teller").font(.dsSerif(26)).foregroundStyle(DS.Palette.ink)
                        Text(L10n.s("ui.choose_epoch")).font(.dsCaption(12)).foregroundStyle(DS.Palette.inkSoft)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.top, 2)

                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 20) {
                            ForEach(chapters) { ch in
                                ChapterCard(chapter: ch,
                                            locked: ch.locked(unlocked: isUnlocked(ch)),
                                            priceText: priceText(ch)) {
                                    if ch.available { onSelect(ch) }
                                }
                            }
                        }
                        .padding(.horizontal, 6)
                        .frame(maxHeight: .infinity)
                    }
                    .frame(maxHeight: .infinity)
                    .padding(.bottom, 6)
                }
                .padding(EdgeInsets(top: 14, leading: 26, bottom: 14, trailing: 26))
            }
            .padding(EdgeInsets(top: 14, leading: 18, bottom: 14, trailing: 18))
            .overlay(alignment: .topLeading) {
                RibbonButton(systemImage: "chevron.left") { onBack() }.offset(x: 42, y: -12)
            }
        }
    }
}

private struct ChapterCard: View {
    let chapter: Chapter
    var locked: Bool = false
    var priceText: String = ""
    let onTap: () -> Void

    var body: some View {
        Button(action: onTap) {
            VStack(spacing: 0) {
                cover.frame(height: 168)
                footer
            }
            .frame(width: 210)
            .background(RoundedRectangle(cornerRadius: 16, style: .continuous).fill(DS.Palette.paper))
            .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
            .overlay(RoundedRectangle(cornerRadius: 16, style: .continuous)
                .strokeBorder(DS.Palette.ink.opacity(chapter.available ? 0.6 : 0.35), lineWidth: 2.5))
            .shadow(color: .black.opacity(0.25), radius: 6, y: 4)
        }
        .buttonStyle(.plain)
        .disabled(!chapter.available)
    }

    private var cover: some View {
        ZStack {
            if let sid = chapter.coverSceneId, chapter.available {
                Image.scene(sid).resizable().scaledToFill()
                    .frame(width: 210, height: 168).clipped()
            } else {
                LinearGradient(colors: [DS.Palette.panel, DS.Palette.paperEdge],
                               startPoint: .top, endPoint: .bottom)
                Image(systemName: chapter.icon)
                    .font(.system(size: 54, weight: .regular))
                    .foregroundStyle(DS.Palette.ink.opacity(0.18))
            }

            // плашка «Глава N» сверху
            VStack {
                HStack {
                    Text(L10n.s("ui.chapter_n", chapter.number))
                        .font(.dsCaption(10))
                        .foregroundStyle(.white)
                        .padding(.horizontal, 8).padding(.vertical, 4)
                        .background(Capsule().fill(DS.Palette.ribbon))
                    Spacer()
                }
                Spacer()
            }
            .padding(8)

            if !chapter.available {
                Color.black.opacity(0.15)
                VStack(spacing: 4) {
                    Image(systemName: "lock.fill").font(.system(size: 26, weight: .bold))
                        .foregroundStyle(DS.Palette.ink.opacity(0.5))
                }
            } else if locked {
                // платная глава: золотой замок в углу поверх обложки
                VStack {
                    Spacer()
                    HStack {
                        Spacer()
                        Image(systemName: "lock.fill")
                            .font(.system(size: 14, weight: .bold))
                            .foregroundStyle(.white)
                            .padding(7)
                            .background(Circle().fill(DS.Palette.maroon))
                            .overlay(Circle().strokeBorder(DS.Palette.gold, lineWidth: 1.5))
                            .shadow(color: .black.opacity(0.3), radius: 2, y: 1)
                    }
                }
                .padding(8)
            }
        }
        .frame(width: 210, height: 168)
    }

    private var footer: some View {
        VStack(spacing: 3) {
            Text(chapter.title)
                .font(.dsSerif(17))
                .foregroundStyle(chapter.available ? DS.Palette.ink : DS.Palette.inkSoft)
                .lineLimit(1)
            Text(chapter.subtitle)
                .font(.dsCaption(10))
                .foregroundStyle(DS.Palette.inkSoft)
                .lineLimit(1)
            if locked {
                HStack(spacing: 4) {
                    Image(systemName: "lock.fill").font(.system(size: 9, weight: .bold))
                    Text(priceText.isEmpty ? L10n.s("ui.locked_hint") : priceText).font(.dsCaption(11))
                }
                .foregroundStyle(DS.Palette.maroon)
            } else if chapter.available, let p = chapter.progressText {
                Text(p).font(.dsCaption(10)).foregroundStyle(DS.Palette.success)
            } else if !chapter.available {
                Text(L10n.s("ui.soon")).font(.dsCaption(11)).foregroundStyle(DS.Palette.maroon)
            }
        }
        .frame(maxWidth: .infinity)
        .frame(height: 78)
        .background(DS.Palette.paper)
    }
}
