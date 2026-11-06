import SwiftUI
import DesignSystem
import GameContent
import GameProgress

/// «Путь огня»: серия дней как дорога с вехами. Слева — нынешнее пламя, его стадия и бонус к опыту,
/// справа — дорога от Искры до Вечного огня: пройденные вехи золотые, следующая пульсирует,
/// на каждой видно, что за неё дают. Игрок видит, куда растёт и сколько осталось.
public struct StreakRoadView: View {
    let streak: Int
    let best: Int
    let solvedToday: Bool
    let brokenStreak: Int?
    let freeRestore: Bool
    let onRestore: () -> Void
    let onClose: () -> Void

    @State private var pulse = false

    public init(streak: Int, best: Int, solvedToday: Bool, brokenStreak: Int?, freeRestore: Bool,
                onRestore: @escaping () -> Void, onClose: @escaping () -> Void) {
        self.streak = streak
        self.best = best
        self.solvedToday = solvedToday
        self.brokenStreak = brokenStreak
        self.freeRestore = freeRestore
        self.onRestore = onRestore
        self.onClose = onClose
    }

    /// Станции дороги: начала стадий пламени и вехи с подсказками.
    private static let stations: [Int] =
        Array(Set(Meta.flameTiers.map(\.from) + Meta.milestones.map(\.day))).sorted()

    private var tier: Int { Meta.flameTier(streak) }

    public var body: some View {
        ZStack {
            DS.Palette.backdrop.ignoresSafeArea()
            BookPage {
                HStack(spacing: 18) {
                    header.frame(width: 210)
                    road
                }
                .padding(EdgeInsets(top: 16, leading: 26, bottom: 14, trailing: 22))
            }
            .padding(EdgeInsets(top: 14, leading: 18, bottom: 14, trailing: 18))
            .overlay(alignment: .topLeading) {
                RibbonButton(systemImage: "chevron.left") { onClose() }.offset(x: 42, y: -12)
            }
        }
        .onAppear {
            withAnimation(.easeInOut(duration: 0.9).repeatForever(autoreverses: true)) { pulse = true }
        }
    }

    // MARK: Пламя сейчас

    private var header: some View {
        VStack(spacing: 6) {
            Text(L10n.s("ui.flame_road")).font(.dsSerif(20)).foregroundStyle(DS.Palette.ink)
            FlameBadge(tier: tier, size: 86)
                .padding(.vertical, 4)
            Text(tier > 0 ? L10n.s("ui.flame.\(tier)") : "—")
                .font(.dsSerif(18)).foregroundStyle(DS.Palette.ink)
            Text(L10n.s("ui.streak_days", streak)).font(.dsBody(15)).foregroundStyle(DS.Palette.ink)
            if Meta.flameBonus(streak) > 0 {
                Text(L10n.s("ui.flame_bonus", Meta.flameBonus(streak)))
                    .font(.dsCaption(12)).foregroundStyle(DS.Palette.paper)
                    .padding(.horizontal, 10).padding(.vertical, 4)
                    .background(Capsule().fill(FlameBadge.colors(tier).0))
            }
            if let next = nextTier {
                Text(L10n.s("ui.flame_next", L10n.s("ui.flame.\(next.tier)"), next.days))
                    .font(.dsCaption(11)).foregroundStyle(DS.Palette.inkSoft)
                    .multilineTextAlignment(.center)
            }
            Text(L10n.s("ui.flame_best", max(best, streak))).font(.dsCaption(11)).foregroundStyle(DS.Palette.inkSoft)
            Spacer(minLength: 2)
            if let broken = brokenStreak {
                Button(action: onRestore) {
                    HStack(spacing: 6) {
                        if !freeRestore { Image(systemName: "play.rectangle.fill") }
                        Text(L10n.s("ui.streak_restore"))
                    }
                    .font(.dsBody(13)).foregroundStyle(DS.Palette.paper)
                    .padding(.horizontal, 14).padding(.vertical, 7)
                    .background(Capsule().fill(.orange))
                }
                .buttonStyle(.plain)
                Text(L10n.s("ui.streak_lost", broken)).font(.dsCaption(10)).foregroundStyle(DS.Palette.inkSoft)
            } else {
                Label(L10n.s(solvedToday ? "ui.flame_today" : "ui.flame_todo"),
                      systemImage: solvedToday ? "checkmark.circle.fill" : "exclamationmark.circle.fill")
                    .font(.dsCaption(11))
                    .foregroundStyle(solvedToday ? DS.Palette.success : DS.Palette.maroon)
                    .multilineTextAlignment(.center)
            }
        }
    }

    /// Следующая стадия пламени и сколько до неё дней.
    private var nextTier: (tier: Int, days: Int)? {
        guard tier < Meta.flameTiers.count else { return nil }
        return (tier + 1, Meta.flameTiers[tier].from - streak)
    }

    // MARK: Дорога

    private var road: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(L10n.s("ui.flame_rule")).font(.dsCaption(11)).foregroundStyle(DS.Palette.inkSoft)
                .lineLimit(2)
            ScrollViewReader { proxy in
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 0) {
                        ForEach(Array(Self.stations.enumerated()), id: \.element) { i, day in
                            station(day).id(day)
                            if i + 1 < Self.stations.count { segment(from: day, to: Self.stations[i + 1]) }
                        }
                    }
                    .padding(.horizontal, 10)
                    .frame(maxHeight: .infinity)
                }
                .onAppear {
                    let target = Self.stations.first { $0 > streak } ?? Self.stations.last ?? 1
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) {
                        withAnimation(.easeOut(duration: 0.6)) { proxy.scrollTo(target, anchor: .center) }
                    }
                }
            }
        }
    }

    private func station(_ day: Int) -> some View {
        let reached = streak >= day
        let isNext = !reached && Self.stations.first { $0 > streak } == day
        let tierHere = Meta.flameTiers.firstIndex { $0.from == day }.map { $0 + 1 }
        let hints = Meta.milestoneHints(day)
        return VStack(spacing: 5) {
            ZStack {
                if let t = tierHere {
                    FlameBadge(tier: reached || isNext ? t : 0, size: 34, animated: reached)
                }
            }
            .frame(height: 38)
            Text(tierHere.map { L10n.s("ui.flame.\($0)") } ?? " ")
                .font(.dsCaption(10)).foregroundStyle(reached ? DS.Palette.ink : DS.Palette.inkSoft)
                .lineLimit(1).fixedSize()
            ZStack {
                Circle()
                    .fill(reached ? DS.Palette.gold : DS.Palette.panel)
                    .frame(width: 46, height: 46)
                    .overlay(Circle().strokeBorder(isNext ? .orange : DS.Palette.ink.opacity(reached ? 0.6 : 0.3),
                                                   lineWidth: isNext ? 3 : 2))
                    .scaleEffect(isNext && pulse ? 1.08 : 1)
                    .shadow(color: isNext ? Color.orange.opacity(pulse ? 0.6 : 0.2) : .clear, radius: 8)
                if reached {
                    Image(systemName: "checkmark").font(.system(size: 16, weight: .heavy)).foregroundStyle(DS.Palette.ink)
                } else {
                    Text("\(day)").font(.dsBody(15)).monospacedDigit().foregroundStyle(DS.Palette.ink)
                }
            }
            Text(L10n.s("ui.gift_day", day)).font(.dsCaption(10)).foregroundStyle(DS.Palette.inkSoft)
                .lineLimit(1).fixedSize()
            VStack(spacing: 2) {
                if hints > 0 { rewardPill("+\(hints) 💡", on: reached) }
                if let t = tierHere, Meta.flameTiers[t - 1].bonus > 0 {
                    rewardPill(L10n.s("ui.flame_bonus", Meta.flameTiers[t - 1].bonus), on: reached)
                }
            }
            .frame(height: 40, alignment: .top)
        }
        .frame(width: 84)
    }

    private func rewardPill(_ text: String, on: Bool) -> some View {
        Text(text).font(.dsCaption(10)).lineLimit(1).fixedSize()
            .foregroundStyle(on ? DS.Palette.ink : DS.Palette.inkSoft)
            .padding(.horizontal, 7).padding(.vertical, 2)
            .background(Capsule().fill(on ? DS.Palette.gold.opacity(0.4) : DS.Palette.ink.opacity(0.07)))
    }

    /// Отрезок между вехами: залит на пройденную долю, на текущем — маркер-огонёк.
    private func segment(from a: Int, to b: Int) -> some View {
        let frac = min(1, max(0, Double(streak - a) / Double(b - a)))
        let width: CGFloat = 54
        return ZStack(alignment: .leading) {
            Capsule().fill(DS.Palette.ink.opacity(0.12)).frame(width: width, height: 6)
            Capsule().fill(DS.Palette.gold).frame(width: width * frac, height: 6)
            if streak > a && streak < b {
                FlameBadge(tier: tier, size: 22)
                    .offset(x: width * frac - 11, y: -14)
            }
        }
        .frame(width: width)
    }
}
