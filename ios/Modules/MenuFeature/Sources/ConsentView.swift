import SwiftUI
import DesignSystem
import GameContent
import Ads

/// Окно согласия на рекламные данные (GDPR). Своё, в стиле книги, без стороннего CMP.
/// Кнопки «Согласен» и «Не согласен» равнозначны по виду — так требует GDPR; закрыть окно
/// мимо выбора нельзя.
public struct ConsentView: View {
    private let consent = ConsentService.shared
    public init() {}

    public var body: some View {
        ZStack {
            Color.black.opacity(0.5).ignoresSafeArea()

            BookPage {
                VStack(spacing: 12) {
                    ZStack {
                        Circle().fill(DS.Palette.maroon).frame(width: 52, height: 52)
                            .overlay(Circle().strokeBorder(DS.Palette.gold, lineWidth: 2))
                        Image(systemName: "hand.raised.fill").font(.system(size: 22, weight: .semibold))
                            .foregroundStyle(DS.Palette.gold)
                    }
                    Text(L10n.s("ui.consent_title")).font(.dsSerif(22)).foregroundStyle(DS.Palette.ink)
                    RoundedRectangle(cornerRadius: 2).fill(DS.Palette.gold).frame(width: 70, height: 3)
                    Text(L10n.s("ui.consent_body")).font(.dsBody(14)).foregroundStyle(DS.Palette.inkSoft)
                        .multilineTextAlignment(.center).fixedSize(horizontal: false, vertical: true)

                    HStack(spacing: 14) {
                        choiceButton(L10n.s("ui.consent_decline")) { consent.answer(false) }
                        choiceButton(L10n.s("ui.consent_accept")) { consent.answer(true) }
                    }
                    .padding(.top, 4)

                    Link(L10n.s("ui.privacy"), destination: Legal.privacyURL)
                        .font(.dsCaption(12)).foregroundStyle(DS.Palette.inkSoft).underline()
                }
                .padding(EdgeInsets(top: 20, leading: 32, bottom: 18, trailing: 32))
                .frame(width: 480)
            }
            .fixedSize()
            .shadow(color: .black.opacity(0.4), radius: 18, y: 10)
        }
    }

    private func choiceButton(_ title: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Text(title)
                .font(.dsSerif(17)).foregroundStyle(DS.Palette.paper)
                .frame(width: 170).padding(.vertical, 12)
                .background(Capsule().fill(DS.Palette.maroon))
                .overlay(Capsule().strokeBorder(DS.Palette.ink, lineWidth: 2.5))
        }
        .buttonStyle(.plain)
    }
}
