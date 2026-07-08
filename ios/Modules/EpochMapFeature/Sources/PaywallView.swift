import SwiftUI
import DesignSystem
import GameContent

/// Пейволл главы: открыть именно эту главу (разовая покупка со своей ценой)
/// ИЛИ оформить подписку на весь контент (текущий и будущий). + «Восстановить покупку».
public struct PaywallView: View {
    @State private var store = Store.shared
    private let epoch: String
    private let chapterTitle: String
    private let onClose: () -> Void
    private let onUnlocked: () -> Void

    public init(epoch: String, chapterTitle: String,
                onClose: @escaping () -> Void, onUnlocked: @escaping () -> Void) {
        self.epoch = epoch
        self.chapterTitle = chapterTitle
        self.onClose = onClose
        self.onUnlocked = onUnlocked
    }

    public var body: some View {
        ZStack {
            Color.black.opacity(0.5).ignoresSafeArea().onTapGesture { onClose() }

            BookPage {
                VStack(spacing: 12) {
                    ZStack {
                        Circle().fill(DS.Palette.maroon).frame(width: 56, height: 56)
                            .overlay(Circle().strokeBorder(DS.Palette.gold, lineWidth: 2))
                        Image(systemName: "crown.fill").font(.system(size: 24, weight: .semibold))
                            .foregroundStyle(DS.Palette.gold)
                    }
                    .shadow(color: .black.opacity(0.25), radius: 4, y: 2)

                    Text("«\(chapterTitle)»").font(.dsSerif(22)).foregroundStyle(DS.Palette.ink)
                    RoundedRectangle(cornerRadius: 2).fill(DS.Palette.gold).frame(width: 70, height: 3)
                    Text(L10n.s("ui.paywall_sub")).font(.dsBody(14)).foregroundStyle(DS.Palette.inkSoft)
                        .multilineTextAlignment(.center).fixedSize(horizontal: false, vertical: true)

                    // 1) Открыть эту главу
                    primaryButton(
                        title: store.chapterPrice(epoch).isEmpty
                            ? L10n.s("ui.buy_chapter_cta")
                            : "\(L10n.s("ui.buy_chapter_cta")) — \(store.chapterPrice(epoch))",
                        action: { Task { await store.purchaseChapter(epoch) } })
                    .padding(.top, 2)

                    // разделитель
                    HStack(spacing: 10) {
                        line; Text(L10n.s("ui.or").uppercased()).font(.dsCaption(11)).foregroundStyle(DS.Palette.inkSoft); line
                    }.padding(.vertical, 2)

                    // 2) Подписка на всё
                    Text(L10n.s("ui.sub_hint")).font(.dsCaption(12)).foregroundStyle(DS.Palette.inkSoft)
                    HStack(spacing: 10) {
                        if !store.monthlyPrice.isEmpty {
                            subButton(L10n.s("ui.sub_month", store.monthlyPrice), id: Store.monthlyID)
                        }
                        if !store.yearlyPrice.isEmpty {
                            subButton(L10n.s("ui.sub_year", store.yearlyPrice), id: Store.yearlyID)
                        }
                    }

                    Button { Task { await store.restore() } } label: {
                        Text(L10n.s("ui.restore")).font(.dsCaption(13)).foregroundStyle(DS.Palette.inkSoft).underline()
                    }.buttonStyle(.plain).padding(.top, 2)
                }
                .padding(EdgeInsets(top: 20, leading: 32, bottom: 20, trailing: 32))
                .frame(width: 480)
            }
            .fixedSize()
            .shadow(color: .black.opacity(0.4), radius: 18, y: 10)
            .overlay(alignment: .topTrailing) {
                Button(action: onClose) {
                    Image(systemName: "xmark").font(.system(size: 12, weight: .heavy))
                        .foregroundStyle(DS.Palette.inkSoft).frame(width: 30, height: 30)
                        .background(Circle().fill(DS.Palette.paper))
                        .overlay(Circle().strokeBorder(DS.Palette.ink.opacity(0.25), lineWidth: 1))
                }.buttonStyle(.plain).padding(10)
            }
        }
        .onChange(of: store.isUnlocked(epoch)) { _, unlocked in
            if unlocked { onUnlocked() }
        }
    }

    private var line: some View { RoundedRectangle(cornerRadius: 1).fill(DS.Palette.ink.opacity(0.2)).frame(height: 1) }

    private func primaryButton(title: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Group {
                if store.purchasing { ProgressView().tint(DS.Palette.paper) }
                else { Text(title) }
            }
            .font(.dsSerif(17)).foregroundStyle(DS.Palette.paper)
            .frame(minWidth: 260).padding(.horizontal, 30).padding(.vertical, 12)
            .background(Capsule().fill(DS.Palette.maroon))
            .overlay(Capsule().strokeBorder(DS.Palette.ink, lineWidth: 2.5))
            .shadow(color: .black.opacity(0.25), radius: 4, y: 2)
        }.buttonStyle(.plain).disabled(store.purchasing)
    }

    private func subButton(_ title: String, id: String) -> some View {
        Button { Task { await store.purchase(id) } } label: {
            Text(title).font(.dsBody(15)).foregroundStyle(DS.Palette.ink)
                .padding(.horizontal, 22).padding(.vertical, 10)
                .background(Capsule().fill(DS.Palette.panel))
                .overlay(Capsule().strokeBorder(DS.Palette.gold, lineWidth: 2))
        }.buttonStyle(.plain).disabled(store.purchasing)
    }
}
