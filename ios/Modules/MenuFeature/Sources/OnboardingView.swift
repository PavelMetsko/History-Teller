import SwiftUI
import DesignSystem
import GameContent

/// Пошаговый онбординг (landscape): проводит новичка по всем правилам игры
/// с иконкой, заголовком, описанием и кнопкой «Далее». Показывается один раз.
public struct OnboardingView: View {
    private let onFinish: () -> Void
    public init(onFinish: @escaping () -> Void) { self.onFinish = onFinish }

    private struct Step { let icon: String; let title: String; let body: String }

    private var steps: [Step] {
        [
            .init(icon: "books.vertical.fill",        title: L10n.s("ui.onb.1.title"), body: L10n.s("ui.onb.1.body")),
            .init(icon: "rectangle.split.3x1.fill",   title: L10n.s("ui.onb.2.title"), body: L10n.s("ui.onb.2.body")),
            .init(icon: "hand.draw.fill",             title: L10n.s("ui.onb.3.title"), body: L10n.s("ui.onb.3.body")),
            .init(icon: "person.fill.questionmark",   title: L10n.s("ui.onb.4.title"), body: L10n.s("ui.onb.4.body")),
            .init(icon: "exclamationmark.triangle.fill", title: L10n.s("ui.onb.5.title"), body: L10n.s("ui.onb.5.body")),
            .init(icon: "scroll.fill",                title: L10n.s("ui.onb.6.title"), body: L10n.s("ui.onb.6.body")),
        ]
    }

    @State private var step = 0
    private var isLast: Bool { step >= steps.count - 1 }

    public var body: some View {
        ZStack {
            DS.Palette.backdrop.ignoresSafeArea()

            VStack(spacing: 18) {
                Text(L10n.s("ui.how_to_play").uppercased())
                    .font(.dsCaption(12)).tracking(2).foregroundStyle(DS.Palette.gold)

                card

                controls
            }
            .padding(.horizontal, 54)
            .padding(.vertical, 26)
            .frame(maxWidth: 720)
        }
    }

    private var card: some View {
        ZStack {
            RoundedRectangle(cornerRadius: 22, style: .continuous)
                .fill(DS.Palette.panel)
                .overlay(RoundedRectangle(cornerRadius: 22, style: .continuous)
                    .stroke(DS.Palette.ink, lineWidth: 4))

            TabView(selection: $step) {
                ForEach(steps.indices, id: \.self) { i in
                    stepView(steps[i]).tag(i).padding(.horizontal, 34)
                }
            }
            .tabViewStyle(.page(indexDisplayMode: .never))
        }
        .frame(maxHeight: .infinity)
    }

    private func stepView(_ s: Step) -> some View {
        HStack(spacing: 30) {
            ZStack {
                Circle().fill(DS.Palette.gold.opacity(0.16))
                Circle().stroke(DS.Palette.gold.opacity(0.5), lineWidth: 3)
                Image(systemName: s.icon).font(.system(size: 62)).foregroundStyle(DS.Palette.maroon)
            }
            .frame(width: 150, height: 150)

            VStack(alignment: .leading, spacing: 12) {
                Text(s.title).font(.dsSerif(26)).foregroundStyle(DS.Palette.ink)
                Text(s.body).font(.dsBody(17)).foregroundStyle(DS.Palette.inkSoft)
                    .fixedSize(horizontal: false, vertical: true)
                    .lineSpacing(3)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }

    private var controls: some View {
        HStack {
            HStack(spacing: 8) {
                ForEach(steps.indices, id: \.self) { i in
                    Circle()
                        .fill(i == step ? DS.Palette.gold : DS.Palette.paper.opacity(0.35))
                        .frame(width: 8, height: 8)
                }
            }

            Spacer()

            Button {
                if isLast { onFinish() }
                else { withAnimation(.easeInOut(duration: 0.25)) { step += 1 } }
            } label: {
                Text(L10n.s(isLast ? "ui.start" : "ui.next"))
                    .font(.dsBody(16)).foregroundStyle(DS.Palette.paper)
                    .padding(.horizontal, 26).padding(.vertical, 11)
                    .background(
                        Capsule().fill(DS.Palette.maroon)
                            .overlay(Capsule().stroke(DS.Palette.ink, lineWidth: 3))
                    )
            }
            .buttonStyle(.plain)
        }
    }
}
