import SwiftUI
import DesignSystem
import GameContent

/// Пейволл: книжная карточка «Открой все главы». Первая глава бесплатна,
/// разовая покупка (`Store`) открывает остальные. Есть «Восстановить покупку».
public struct PaywallView: View {
    @State private var store = Store.shared
    private let onClose: () -> Void
    private let onUnlocked: () -> Void

    public init(onClose: @escaping () -> Void, onUnlocked: @escaping () -> Void) {
        self.onClose = onClose
        self.onUnlocked = onUnlocked
    }

    public var body: some View {
        ZStack {
            Color.black.opacity(0.5).ignoresSafeArea()
                .onTapGesture { onClose() }

            BookPage {
                VStack(spacing: 14) {
                    ZStack {
                        Circle().fill(DS.Palette.maroon).frame(width: 62, height: 62)
                            .overlay(Circle().strokeBorder(DS.Palette.gold, lineWidth: 2))
                        Image(systemName: "crown.fill")
                            .font(.system(size: 26, weight: .semibold))
                            .foregroundStyle(DS.Palette.gold)
                    }
                    .shadow(color: .black.opacity(0.25), radius: 4, y: 2)

                    Text(L10n.s("ui.unlock_title"))
                        .font(.dsSerif(24)).foregroundStyle(DS.Palette.ink)
                    RoundedRectangle(cornerRadius: 2).fill(DS.Palette.gold).frame(width: 80, height: 3)

                    Text(L10n.s("ui.unlock_body"))
                        .font(.dsBody(15)).foregroundStyle(DS.Palette.inkSoft)
                        .multilineTextAlignment(.center)
                        .fixedSize(horizontal: false, vertical: true)
                        .padding(.horizontal, 8)

                    buyButton.padding(.top, 4)

                    Button {
                        Task { await store.restore() }
                    } label: {
                        Text(L10n.s("ui.restore"))
                            .font(.dsCaption(13)).foregroundStyle(DS.Palette.inkSoft)
                            .underline()
                    }
                    .buttonStyle(.plain)
                }
                .padding(EdgeInsets(top: 22, leading: 34, bottom: 22, trailing: 34))
                .frame(width: 470)
            }
            .fixedSize()
            .shadow(color: .black.opacity(0.4), radius: 18, y: 10)
            .overlay(alignment: .topTrailing) {
                Button(action: onClose) {
                    Image(systemName: "xmark")
                        .font(.system(size: 12, weight: .heavy))
                        .foregroundStyle(DS.Palette.inkSoft)
                        .frame(width: 30, height: 30)
                        .background(Circle().fill(DS.Palette.paper))
                        .overlay(Circle().strokeBorder(DS.Palette.ink.opacity(0.25), lineWidth: 1))
                }
                .buttonStyle(.plain).padding(10)
            }
        }
        .onChange(of: store.isUnlocked) { _, unlocked in
            if unlocked { onUnlocked() }
        }
    }

    private var buyButton: some View {
        Button {
            Task { await store.purchase() }
        } label: {
            Group {
                if store.purchasing {
                    ProgressView().tint(DS.Palette.paper)
                } else {
                    Text(store.priceText.isEmpty
                         ? L10n.s("ui.unlock_cta")
                         : L10n.s("ui.unlock_cta_price", store.priceText))
                }
            }
            .font(.dsSerif(18)).foregroundStyle(DS.Palette.paper)
            .frame(minWidth: 240)
            .padding(.horizontal, 32).padding(.vertical, 13)
            .background(Capsule().fill(DS.Palette.maroon))
            .overlay(Capsule().strokeBorder(DS.Palette.ink, lineWidth: 2.5))
            .shadow(color: .black.opacity(0.25), radius: 4, y: 2)
        }
        .buttonStyle(.plain)
        .disabled(store.purchasing)
    }
}
