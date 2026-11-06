import SwiftUI
import DesignSystem
import GameContent

/// Что показывает меню о прогрессе игрока: звание, серия, подсказки, эпизод дня.
public struct MenuMeta {
    public struct Daily {
        public let title: String
        public let chapterTitle: String
        public let coverSceneId: String?
        public let done: Bool

        public init(title: String, chapterTitle: String, coverSceneId: String?, done: Bool) {
            self.title = title
            self.chapterTitle = chapterTitle
            self.coverSceneId = coverSceneId
            self.done = done
        }
    }

    public let level: Int
    public let rankName: String
    public let xpProgress: Double
    public let streak: Int
    /// Стадия пламени серии (0 — погасло).
    public let flameTier: Int
    public let hintsBadge: String
    /// Серию можно вернуть без ролика (старая подписка).
    public let freeRestore: Bool
    public let daily: Daily?
    /// Серия прервалась вчера — её можно вернуть (ролик или бесплатно для Premium).
    public let brokenStreak: Int?

    public init(level: Int, rankName: String, xpProgress: Double, streak: Int, flameTier: Int, hintsBadge: String,
                freeRestore: Bool, daily: Daily?, brokenStreak: Int?) {
        self.level = level
        self.rankName = rankName
        self.xpProgress = xpProgress
        self.streak = streak
        self.flameTier = flameTier
        self.hintsBadge = hintsBadge
        self.freeRestore = freeRestore
        self.daily = daily
        self.brokenStreak = brokenStreak
    }
}

/// Главное меню — титульная страница книги: звание и серия сверху, «Играть» и «Альбом»,
/// справа — эпизод дня.
public struct MenuView: View {
    private let meta: MenuMeta
    private let onPlay: () -> Void
    private let onReset: () -> Void
    private let onAlbum: () -> Void
    private let onDaily: () -> Void
    private let onStreak: () -> Void
    private let onRestoreStreak: () -> Void
    @State private var showResetConfirm = false
    @State private var showSettings = false
    @State private var dailyPulse = false

    public init(meta: MenuMeta,
                onPlay: @escaping () -> Void,
                onReset: @escaping () -> Void,
                onAlbum: @escaping () -> Void,
                onDaily: @escaping () -> Void,
                onStreak: @escaping () -> Void,
                onRestoreStreak: @escaping () -> Void) {
        self.meta = meta
        self.onPlay = onPlay
        self.onReset = onReset
        self.onAlbum = onAlbum
        self.onDaily = onDaily
        self.onStreak = onStreak
        self.onRestoreStreak = onRestoreStreak
    }

    public var body: some View {
        ZStack {
            DS.Palette.backdrop.ignoresSafeArea()

            BookPage {
                VStack(spacing: 0) {
                    statsBar
                    HStack(spacing: 18) {
                        titleBlock
                            .layoutPriority(1)
                        Spacer(minLength: 0)
                        rightColumn
                    }
                }
                .frame(maxWidth: 760)                       // плотная композиция, не растягиваться на iPad
                .frame(maxWidth: .infinity)                 // и центрироваться в книге
                .padding(EdgeInsets(top: 18, leading: 34, bottom: 16, trailing: 28))
            }
            .padding(EdgeInsets(top: 16, leading: 20, bottom: 16, trailing: 20))
            .overlay(alignment: .topTrailing) {
                Button { withAnimation(.easeIn(duration: 0.2)) { showSettings = true } } label: {
                    Image(systemName: "gearshape.fill")
                        .font(.system(size: 20, weight: .semibold))
                        .foregroundStyle(DS.Palette.ink.opacity(0.7))
                        .frame(width: 44, height: 44)
                        .background(Circle().fill(DS.Palette.paper))
                        .overlay(Circle().strokeBorder(DS.Palette.ink.opacity(0.3), lineWidth: 1.5))
                        .shadow(color: .black.opacity(0.2), radius: 3, y: 1)
                }
                .buttonStyle(.plain)
                .padding(.top, 30).padding(.trailing, 40)
            }

            if showSettings {
                SettingsView(onClose: { withAnimation(.easeOut(duration: 0.2)) { showSettings = false } })
                    .transition(.opacity)
                    .zIndex(20)
            }

            if showResetConfirm {
                BookDialog(
                    title: L10n.s("ui.reset_title"),
                    message: L10n.s("ui.reset_msg"),
                    confirmTitle: L10n.s("ui.reset_confirm"),
                    cancelTitle: L10n.s("ui.cancel"),
                    destructive: true,
                    onConfirm: { onReset(); withAnimation(.easeOut(duration: 0.2)) { showResetConfirm = false } },
                    onCancel: { withAnimation(.easeOut(duration: 0.2)) { showResetConfirm = false } }
                )
                .transition(.opacity)
                .zIndex(10)
            }
        }
        .onAppear {
            if ProcessInfo.processInfo.environment["HT_RESETDLG"] == "1" { showResetConfirm = true }
            if ProcessInfo.processInfo.environment["HT_SETTINGS"] == "1" { showSettings = true }
        }
    }

    private var titleBlock: some View {
        VStack(alignment: .leading, spacing: 0) {
            Spacer(minLength: 0)

            Text(L10n.s("ui.tagline_caps"))
                .font(.dsCaption(11))
                .tracking(2)
                .foregroundStyle(DS.Palette.maroon)

            Text("History Teller")
                .font(.dsSerif(38))
                .foregroundStyle(DS.Palette.ink)
                .lineLimit(1)
                .minimumScaleFactor(0.5)
                .padding(.top, 4)

            // тонкая линия-росчерк под заголовком
            RoundedRectangle(cornerRadius: 2)
                .fill(DS.Palette.gold)
                .frame(width: 120, height: 3)
                .padding(.top, 8)

            Text(L10n.s("ui.menu_sub"))
                .font(.dsBody(14))
                .foregroundStyle(DS.Palette.inkSoft)
                .lineLimit(2)
                .minimumScaleFactor(0.8)
                .padding(.top, 10)

            // Кнопки не ужимаются: текст на них не должен уходить в многоточие ни на одном языке.
            HStack(spacing: 10) {
                playButton
                albumButton
            }
            .fixedSize()
            .padding(.top, 16)

            Button {
                withAnimation(.easeIn(duration: 0.2)) { showResetConfirm = true }
            } label: {
                Text(L10n.s("ui.reset"))
                    .font(.dsCaption())
                    .foregroundStyle(DS.Palette.inkSoft)
            }
            .padding(.top, 14)

            Spacer(minLength: 0)
        }
    }

    private var playButton: some View {
        Button(action: onPlay) {
            HStack(spacing: 10) {
                Image(systemName: "play.fill")
                Text(L10n.s("ui.play"))
            }
            .font(.dsSerif(20))
            .lineLimit(1)
            .foregroundStyle(DS.Palette.paper)
            .padding(.horizontal, 26).padding(.vertical, 12)
            .background(Capsule().fill(DS.Palette.maroon))
            .overlay(Capsule().strokeBorder(DS.Palette.ink, lineWidth: 3))
            .shadow(color: .black.opacity(0.25), radius: 5, y: 3)
        }
        .buttonStyle(.plain)
    }

    private var albumButton: some View {
        Button(action: onAlbum) {
            HStack(spacing: 8) {
                Image(systemName: "rectangle.stack.fill")
                Text(L10n.s("ui.album"))
            }
            .font(.dsSerif(17))
            .lineLimit(1)
            .foregroundStyle(DS.Palette.ink)
            .padding(.horizontal, 18).padding(.vertical, 12)
            .background(Capsule().fill(DS.Palette.panel))
            .overlay(Capsule().strokeBorder(DS.Palette.ink, lineWidth: 2.5))
            .shadow(color: .black.opacity(0.18), radius: 4, y: 2)
        }
        .buttonStyle(.plain)
    }

    /// Звание, опыт, серия, подсказки — сверху страницы, на одной строке.
    private var statsBar: some View {
        HStack(spacing: 10) {
            RankBadge(level: meta.level, size: 40)
            VStack(alignment: .leading, spacing: 4) {
                Text("\(L10n.s("ui.lvl_short", meta.level)) · \(meta.rankName)")
                    .font(.dsBody(14)).foregroundStyle(DS.Palette.ink).lineLimit(1)
                XPBar(progress: meta.xpProgress).frame(width: 170)
            }
            Spacer(minLength: 8)
            // Пламя серии — вход в «Путь огня».
            Button(action: onStreak) {
                HStack(spacing: 4) {
                    FlameBadge(tier: meta.flameTier, size: 22)
                    Text("\(meta.streak)").font(.dsBody(14)).monospacedDigit().foregroundStyle(DS.Palette.ink)
                }
                .padding(.leading, 6).padding(.trailing, 10).padding(.vertical, 2)
                .background(Capsule().fill(DS.Palette.panel))
                .overlay(Capsule().strokeBorder(FlameBadge.colors(meta.flameTier).0.opacity(0.8), lineWidth: 1.5))
            }
            .buttonStyle(.plain)
            StatChip(systemImage: "lightbulb.fill", text: meta.hintsBadge, tint: DS.Palette.gold)
            Color.clear.frame(width: 50, height: 1)   // место под шестерёнку настроек
        }
        .padding(.bottom, 6)
    }

    @ViewBuilder private var rightColumn: some View {
        VStack(spacing: 10) {
            if let broken = meta.brokenStreak { streakRescue(broken) }
            if let daily = meta.daily { dailyCard(daily) }
        }
        .frame(width: 230)
    }

    private func dailyCard(_ d: MenuMeta.Daily) -> some View {
        Button(action: onDaily) {
            VStack(spacing: 0) {
                ZStack(alignment: .topLeading) {
                    Group {
                        if let sid = d.coverSceneId {
                            Image.scene(sid).resizable().scaledToFill()
                        } else {
                            LinearGradient(colors: [DS.Palette.panel, DS.Palette.paperEdge], startPoint: .top, endPoint: .bottom)
                        }
                    }
                    .frame(width: 230, height: 100).clipped()
                    .overlay(d.done ? Color.black.opacity(0.35) : Color.clear)
                    HStack(spacing: 5) {
                        Image(systemName: "calendar.badge.clock")
                        Text(L10n.s("ui.daily_title"))
                    }
                    .font(.dsCaption(11)).foregroundStyle(.white)
                    .padding(.horizontal, 9).padding(.vertical, 5)
                    .background(Capsule().fill(DS.Palette.ribbon))
                    .padding(8)
                    if d.done {
                        Image(systemName: "checkmark.seal.fill").font(.system(size: 40))
                            .foregroundStyle(DS.Palette.gold)
                            .frame(width: 230, height: 100)
                    }
                }
                VStack(spacing: 3) {
                    Text(d.title).font(.dsSerif(16)).foregroundStyle(DS.Palette.ink).lineLimit(1)
                    Text(d.chapterTitle).font(.dsCaption(10)).foregroundStyle(DS.Palette.inkSoft).lineLimit(1)
                    Text(d.done ? L10n.s("ui.daily_done") : "×2 XP · +1 💡")
                        .font(.dsCaption(11))
                        .foregroundStyle(d.done ? DS.Palette.success : DS.Palette.maroon)
                }
                .padding(.vertical, 8).frame(maxWidth: .infinity)
                .background(DS.Palette.paper)
            }
            .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
            .overlay(RoundedRectangle(cornerRadius: 14, style: .continuous)
                .strokeBorder(d.done ? DS.Palette.ink.opacity(0.4) : DS.Palette.gold, lineWidth: 2.5))
            .shadow(color: d.done ? .black.opacity(0.2) : DS.Palette.gold.opacity(dailyPulse ? 0.6 : 0.2),
                    radius: dailyPulse ? 12 : 5)
        }
        .buttonStyle(.plain)
        .onAppear {
            guard !d.done else { return }
            withAnimation(.easeInOut(duration: 1.3).repeatForever(autoreverses: true)) { dailyPulse = true }
        }
    }

    private func streakRescue(_ n: Int) -> some View {
        VStack(spacing: 6) {
            HStack(spacing: 6) {
                Image(systemName: "flame").foregroundStyle(.orange)
                Text(L10n.s("ui.streak_lost", n)).font(.dsBody(13)).foregroundStyle(DS.Palette.ink)
                    .lineLimit(2).minimumScaleFactor(0.8)
            }
            Button(action: onRestoreStreak) {
                HStack(spacing: 6) {
                    if !meta.freeRestore { Image(systemName: "play.rectangle.fill") }
                    Text(L10n.s("ui.streak_restore"))
                }
                .font(.dsBody(13)).foregroundStyle(DS.Palette.paper)
                .padding(.horizontal, 16).padding(.vertical, 7)
                .background(Capsule().fill(.orange))
            }
            .buttonStyle(.plain)
        }
        .padding(10)
        .frame(maxWidth: .infinity)
        .background(RoundedRectangle(cornerRadius: 12).fill(DS.Palette.panel))
        .overlay(RoundedRectangle(cornerRadius: 12).strokeBorder(.orange.opacity(0.7), lineWidth: 1.5))
    }
}
