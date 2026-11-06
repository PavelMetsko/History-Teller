import SwiftUI
import DesignSystem
import GameContent

/// Подарок дня: календарь на семь дней, сегодняшний подсвечен. Подарки растут к седьмому дню —
/// пропустил день, и календарь начинается заново.
public struct GiftView: View {
    private let step: Int
    private let gifts: [Int]
    private let onClaim: () -> Void

    @State private var claimed = false
    @State private var wobble = false

    public init(step: Int, gifts: [Int], onClaim: @escaping () -> Void) {
        self.step = step
        self.gifts = gifts
        self.onClaim = onClaim
    }

    public var body: some View {
        ZStack {
            Color.black.opacity(0.55).ignoresSafeArea()
            BookPage {
                VStack(spacing: 14) {
                    Image(systemName: "gift.fill")
                        .font(.system(size: 38))
                        .foregroundStyle(DS.Palette.maroon)
                        .rotationEffect(.degrees(wobble ? -8 : 8))
                    Text(L10n.s("ui.gift_title")).font(.dsSerif(24)).foregroundStyle(DS.Palette.ink)
                    Text(L10n.s("ui.gift_body")).font(.dsBody(13)).foregroundStyle(DS.Palette.inkSoft)
                    HStack(spacing: 8) {
                        ForEach(1...gifts.count, id: \.self) { day in cell(day) }
                    }
                    Button {
                        guard !claimed else { return }
                        claimed = true
                        Audio.shared.play(.accent)
                        Haptics.success()
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.9) { onClaim() }
                    } label: {
                        Text(claimed ? "+\(gifts[step - 1]) 💡" : L10n.s("ui.gift_claim"))
                            .font(.dsSerif(18)).foregroundStyle(DS.Palette.paper)
                            .padding(.horizontal, 40).padding(.vertical, 12)
                            .background(Capsule().fill(DS.Palette.maroon))
                            .overlay(Capsule().strokeBorder(DS.Palette.gold, lineWidth: 2))
                    }
                    .buttonStyle(.plain)
                    .overlay { if claimed { SparkBurst() } }
                }
                .padding(EdgeInsets(top: 20, leading: 30, bottom: 20, trailing: 30))
            }
            .fixedSize()
            .shadow(color: .black.opacity(0.4), radius: 18, y: 10)
        }
        .onAppear {
            withAnimation(.easeInOut(duration: 0.5).repeatForever(autoreverses: true)) { wobble = true }
        }
    }

    private func cell(_ day: Int) -> some View {
        let past = day < step, today = day == step
        return VStack(spacing: 4) {
            Text(L10n.s("ui.gift_day", day)).font(.dsCaption(10))
                .foregroundStyle(today ? DS.Palette.paper : DS.Palette.inkSoft)
            ZStack {
                if past || (today && claimed) {
                    Image(systemName: "checkmark.circle.fill").font(.system(size: 20)).foregroundStyle(DS.Palette.success)
                } else {
                    Text("\(gifts[day - 1]) 💡").font(.dsBody(13))
                        .foregroundStyle(today ? DS.Palette.paper : DS.Palette.ink)
                }
            }
            .frame(height: 24)
        }
        .frame(width: 58, height: day == gifts.count ? 70 : 62)
        .background(RoundedRectangle(cornerRadius: 10)
            .fill(today ? DS.Palette.maroon : (day == gifts.count ? DS.Palette.gold.opacity(0.35) : DS.Palette.panel)))
        .overlay(RoundedRectangle(cornerRadius: 10)
            .strokeBorder(today ? DS.Palette.gold : DS.Palette.ink.opacity(0.25), lineWidth: today ? 2.5 : 1))
        .scaleEffect(today ? 1.08 : 1)
    }
}
