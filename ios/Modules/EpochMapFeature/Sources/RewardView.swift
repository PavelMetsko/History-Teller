import SwiftUI
import DesignSystem
import GameContent
import GameProgress

/// Экран награды после первого решения эпизода: опыт со счётчиком и полосой (через порог уровня,
/// если звание выросло), карточка в альбом, кольцо главы, серия и бонусы. Вся «дофаминовая»
/// часть цикла — здесь: игрок видит, что каждый эпизод двигает его вперёд.
public struct RewardView: View {
    let reward: Meta.SolveReward
    let levelTitle: String
    let coverSceneId: String?
    let chapterTitle: String
    let chapterDone: Int
    let chapterTotal: Int
    let hasNext: Bool
    let onNext: () -> Void
    let onMap: () -> Void

    @State private var shownXP: Int
    @State private var barProgress: Double
    @State private var barLevel: Int
    @State private var cardFlip = 90.0
    @State private var ring = 0.0
    @State private var showRankUp = false
    @State private var flameBump = false
    @State private var showExtras = false

    public init(reward: Meta.SolveReward, levelTitle: String, coverSceneId: String?,
                chapterTitle: String, chapterDone: Int, chapterTotal: Int, hasNext: Bool,
                onNext: @escaping () -> Void, onMap: @escaping () -> Void) {
        self.reward = reward
        self.levelTitle = levelTitle
        self.coverSceneId = coverSceneId
        self.chapterTitle = chapterTitle
        self.chapterDone = chapterDone
        self.chapterTotal = chapterTotal
        self.hasNext = hasNext
        self.onNext = onNext
        self.onMap = onMap
        _shownXP = State(initialValue: 0)
        _barProgress = State(initialValue: Meta.levelProgress(reward.xpBefore))
        _barLevel = State(initialValue: reward.levelBefore)
    }

    private var chapterComplete: Bool { chapterTotal > 0 && chapterDone >= chapterTotal }

    public var body: some View {
        ZStack {
            Color.black.opacity(0.55).ignoresSafeArea()
            BookPage {
                HStack(alignment: .center, spacing: 26) {
                    cardColumn.frame(width: 210)
                    VStack(alignment: .leading, spacing: 12) {
                        xpBlock
                        streakRow
                        bonuses
                        Spacer(minLength: 0)
                        buttons
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                }
                .padding(EdgeInsets(top: 22, leading: 30, bottom: 20, trailing: 30))
            }
            .frame(maxWidth: 660, maxHeight: 360)
            .padding(.horizontal, 30)
            .transition(.scale(scale: 0.85).combined(with: .opacity))

            if showRankUp { rankUpBanner.transition(.scale(scale: 0.5).combined(with: .opacity)).zIndex(5) }
        }
        .onAppear(perform: play)
    }

    // MARK: Карточка

    private var cardColumn: some View {
        VStack(spacing: 10) {
            ZStack(alignment: .bottom) {
                Group {
                    if let sid = coverSceneId {
                        Image.scene(sid).resizable().scaledToFill()
                    } else {
                        LinearGradient(colors: [DS.Palette.panel, DS.Palette.paperEdge], startPoint: .top, endPoint: .bottom)
                    }
                }
                .frame(width: 190, height: 140).clipped()
                Text(levelTitle)
                    .font(.dsSerif(13)).foregroundStyle(DS.Palette.paper)
                    .lineLimit(2).multilineTextAlignment(.center)
                    .padding(.horizontal, 8).padding(.vertical, 5)
                    .frame(maxWidth: .infinity)
                    .background(LinearGradient(colors: [.clear, .black.opacity(0.75)], startPoint: .top, endPoint: .bottom))
            }
            .frame(width: 190, height: 140)
            .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
            .overlay(RoundedRectangle(cornerRadius: 10, style: .continuous).strokeBorder(DS.Palette.gold, lineWidth: 3))
            .shadow(color: DS.Palette.gold.opacity(0.5), radius: 10)
            .rotation3DEffect(.degrees(cardFlip), axis: (x: 0, y: 1, z: 0), perspective: 0.6)

            Label(L10n.s("ui.card_added"), systemImage: "rectangle.stack.badge.plus")
                .font(.dsCaption(11)).foregroundStyle(DS.Palette.success)

            HStack(spacing: 10) {
                ZStack {
                    Circle().stroke(DS.Palette.ink.opacity(0.14), lineWidth: 5)
                    Circle().trim(from: 0, to: ring)
                        .stroke(chapterComplete ? DS.Palette.gold : DS.Palette.success,
                                style: StrokeStyle(lineWidth: 5, lineCap: .round))
                        .rotationEffect(.degrees(-90))
                    if chapterComplete {
                        Image(systemName: "seal.fill").font(.system(size: 16)).foregroundStyle(DS.Palette.gold)
                    }
                }
                .frame(width: 36, height: 36)
                VStack(alignment: .leading, spacing: 1) {
                    Text(chapterTitle).font(.dsCaption(11)).foregroundStyle(DS.Palette.inkSoft).lineLimit(1)
                    Text("\(chapterDone) / \(chapterTotal)").font(.dsBody(15)).monospacedDigit()
                        .foregroundStyle(DS.Palette.ink)
                }
            }
        }
    }

    // MARK: Опыт

    private var xpBlock: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(alignment: .firstTextBaseline, spacing: 8) {
                Text("+\(shownXP) XP")
                    .font(.system(size: 34, weight: .heavy, design: .rounded))
                    .monospacedDigit()
                    .foregroundStyle(DS.Palette.gold)
                    .shadow(color: .black.opacity(0.2), radius: 1, y: 1)
                    .contentTransition(.numericText())
                if reward.noHint {
                    Image(systemName: "lightbulb.slash.fill").font(.system(size: 14)).foregroundStyle(DS.Palette.success)
                }
            }
            HStack(spacing: 10) {
                RankBadge(level: barLevel, size: 40)
                VStack(alignment: .leading, spacing: 4) {
                    Text("\(L10n.s("ui.lvl_short", barLevel)) · \(L10n.s(Meta.rankKey(barLevel)))")
                        .font(.dsBody(14)).foregroundStyle(DS.Palette.ink).lineLimit(1)
                    XPBar(progress: barProgress, height: 10)
                }
            }
        }
    }

    private var streakRow: some View {
        HStack(spacing: 8) {
            FlameBadge(tier: Meta.flameTier(reward.streakAfter), size: 26)
                .scaleEffect(flameBump ? 1.35 : 1)
            Text(L10n.s("ui.streak_days", reward.streakAfter))
                .font(.dsBody(15)).foregroundStyle(DS.Palette.ink)
            if reward.flameBonus > 0 {
                Text(L10n.s("ui.flame_bonus", reward.flameBonus)).font(.dsCaption(11))
                    .foregroundStyle(FlameBadge.colors(Meta.flameTier(reward.streakAfter)).0)
            }
            if reward.milestoneHints > 0 && showExtras {
                bonusPill("\(L10n.s("ui.streak_milestone")) +\(reward.milestoneHints) 💡")
            }
        }
    }

    @ViewBuilder private var bonuses: some View {
        if showExtras {
            HStack(spacing: 8) {
                if reward.flameGrew && reward.tierAfter > 1 {
                    bonusPill("\(L10n.s("ui.flame_new")) \(L10n.s("ui.flame.\(reward.tierAfter)"))", gold: true)
                }
                if reward.isDaily { bonusPill("\(L10n.s("ui.daily_bonus")) · +\(reward.dailyHints) 💡") }
                if chapterComplete { bonusPill(L10n.s("ui.chapter_master", chapterTitle), gold: true) }
            }
            .transition(.move(edge: .leading).combined(with: .opacity))
        }
    }

    private func bonusPill(_ text: String, gold: Bool = false) -> some View {
        Text(text)
            .font(.dsCaption(11))
            .foregroundStyle(gold ? DS.Palette.ink : DS.Palette.paper)
            .padding(.horizontal, 10).padding(.vertical, 5)
            .background(Capsule().fill(gold ? DS.Palette.gold : DS.Palette.maroon))
            .lineLimit(1)
    }

    private var buttons: some View {
        HStack(spacing: 12) {
            Button {
                Audio.shared.play(.select); onMap()
            } label: {
                Text(L10n.s("ui.to_map")).font(.dsBody())
                    .foregroundStyle(DS.Palette.maroon)
                    .padding(.horizontal, 20).padding(.vertical, 11)
                    .background(Capsule().fill(DS.Palette.paper))
                    .overlay(Capsule().strokeBorder(DS.Palette.maroon.opacity(0.5), lineWidth: 1.5))
            }
            .buttonStyle(.plain)
            if hasNext {
                Button {
                    Audio.shared.play(.select); onNext()
                } label: {
                    HStack(spacing: 8) {
                        Text(L10n.s("ui.next_episode"))
                        Image(systemName: "play.fill")
                    }
                    .font(.dsBody())
                    .foregroundStyle(DS.Palette.paper)
                    .padding(.horizontal, 22).padding(.vertical, 11)
                    .background(Capsule().fill(DS.Palette.maroon))
                    .overlay(Capsule().strokeBorder(DS.Palette.gold.opacity(0.7), lineWidth: 2))
                }
                .buttonStyle(.plain)
            }
        }
    }

    private var rankUpBanner: some View {
        ZStack {
            SparkBurst()
            VStack(spacing: 8) {
                RankBadge(level: reward.levelAfter, size: 76)
                Text(L10n.s("ui.new_rank")).font(.dsCaption(13)).tracking(1.5).foregroundStyle(DS.Palette.maroon)
                Text(L10n.s(Meta.rankKey(reward.levelAfter))).font(.dsSerif(26)).foregroundStyle(DS.Palette.ink)
                if reward.rankHints > 0 {
                    Text("+\(reward.rankHints) 💡").font(.dsBody(16)).foregroundStyle(DS.Palette.ink)
                }
            }
            .padding(.horizontal, 34).padding(.vertical, 20)
            .background(RoundedRectangle(cornerRadius: 18).fill(DS.Palette.paper))
            .overlay(RoundedRectangle(cornerRadius: 18).strokeBorder(DS.Palette.gold, lineWidth: 3))
            .shadow(color: DS.Palette.gold.opacity(0.6), radius: 18)
        }
        .onTapGesture { withAnimation { showRankUp = false } }
    }

    // MARK: Анимация

    private func play() {
        Haptics.success()
        withAnimation(.spring(response: 0.6, dampingFraction: 0.65).delay(0.15)) { cardFlip = 0 }
        withAnimation(.easeOut(duration: 0.9).delay(0.4)) {
            ring = Double(chapterDone) / Double(max(1, chapterTotal))
        }
        countXP()
        if reward.streakGrew {
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.2) {
                withAnimation(.spring(response: 0.25, dampingFraction: 0.4)) { flameBump = true }
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                    withAnimation(.spring(response: 0.3, dampingFraction: 0.6)) { flameBump = false }
                }
            }
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
            withAnimation(.spring(response: 0.45, dampingFraction: 0.75)) { showExtras = true }
            if reward.totalHints > 0 || chapterComplete { Audio.shared.play(.accent) }
        }
    }

    /// Счётчик опыта и полоса: при повышении полоса доливается до конца, звание меняется,
    /// и уже с нуля растёт остаток.
    private func countXP() {
        let total = reward.xpGained
        guard total > 0 else { return }
        let steps = 20
        for k in 1...steps {
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.35 + Double(k) * 0.04) {
                withAnimation(.easeOut(duration: 0.05)) { shownXP = total * k / steps }
                if k % 4 == 0 { Haptics.light() }
            }
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) {
            if reward.rankedUp {
                withAnimation(.easeIn(duration: 0.6)) { barProgress = 1 }
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.65) {
                    barLevel = reward.levelAfter
                    barProgress = 0
                    withAnimation(.easeOut(duration: 0.5)) { barProgress = Meta.levelProgress(reward.xpAfter) }
                    Audio.shared.play(.win)
                    Haptics.success()
                    withAnimation(.spring(response: 0.5, dampingFraction: 0.6)) { showRankUp = true }
                    DispatchQueue.main.asyncAfter(deadline: .now() + 2.6) {
                        withAnimation(.easeOut(duration: 0.3)) { showRankUp = false }
                    }
                }
            } else {
                withAnimation(.easeOut(duration: 0.8)) { barProgress = Meta.levelProgress(reward.xpAfter) }
            }
        }
    }
}
