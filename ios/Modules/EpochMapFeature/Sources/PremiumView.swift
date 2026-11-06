import SwiftUI
import DesignSystem
import GameContent
import Ads

/// «Глава без рекламы»: покупка одной главы (своя цена у каждой). Играть главу можно и так —
/// покупка убирает интерстишелы и даёт безлимит подсказок в этой главе. + «Восстановить покупку».
public struct PremiumView: View {
    @State private var store = Store.shared
    private let epoch: String
    private let chapterTitle: String
    private let onClose: () -> Void

    public init(epoch: String, chapterTitle: String, onClose: @escaping () -> Void) {
        self.epoch = epoch
        self.chapterTitle = chapterTitle
        self.onClose = onClose
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

                    Text(L10n.s("ui.chapter_noads_title")).font(.dsSerif(22)).foregroundStyle(DS.Palette.ink)
                    Text("«\(chapterTitle)»").font(.dsBody(15)).foregroundStyle(DS.Palette.inkSoft)
                    RoundedRectangle(cornerRadius: 2).fill(DS.Palette.gold).frame(width: 70, height: 3)

                    if store.adsFree(epoch) {
                        Text(L10n.s("ui.premium_active")).font(.dsBody(16)).foregroundStyle(DS.Palette.success)
                            .multilineTextAlignment(.center).padding(.vertical, 14)
                    } else {
                        VStack(alignment: .leading, spacing: 6) {
                            bullet("nosign", L10n.s("ui.chapter_noads_b1"))
                            bullet("lightbulb.fill", L10n.s("ui.chapter_noads_b2"))
                            bullet("heart.fill", L10n.s("ui.premium_b3"))
                        }
                        .padding(.vertical, 4)

                        let price = store.chapterPrice(epoch)
                        if !price.isEmpty {
                            primaryButton(title: L10n.s("ui.chapter_noads_cta", price)) {
                                Task { await store.purchaseChapter(epoch) }
                            }
                        }
                    }

                    Button { Task { await store.restore() } } label: {
                        Text(L10n.s("ui.restore")).font(.dsCaption(13)).foregroundStyle(DS.Palette.inkSoft).underline()
                    }.buttonStyle(.plain).padding(.top, 2)

                    HStack(spacing: 6) {
                        Link(L10n.s("ui.terms"), destination: Legal.termsURL)
                        Text("·").foregroundStyle(DS.Palette.inkSoft.opacity(0.6))
                        Link(L10n.s("ui.privacy"), destination: Legal.privacyURL)
                    }
                    .font(.dsCaption(12)).foregroundStyle(DS.Palette.inkSoft).underline()
                }
                .padding(EdgeInsets(top: 20, leading: 32, bottom: 20, trailing: 32))
                .frame(width: 460)
            }
            .fixedSize()
            .shadow(color: .black.opacity(0.4), radius: 18, y: 10)
            .overlay(alignment: .topTrailing) { CloseButton(action: onClose) }
        }
    }

    private func bullet(_ icon: String, _ text: String) -> some View {
        HStack(spacing: 10) {
            Image(systemName: icon).font(.system(size: 14, weight: .bold)).foregroundStyle(DS.Palette.maroon)
                .frame(width: 20)
            Text(text).font(.dsBody(15)).foregroundStyle(DS.Palette.ink)
        }
    }

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
}

/// Окно «подсказки закончились»: ролик за подсказку, Premium или отмена.
public struct HintsOutView: View {
    @State private var ads = AdService.shared
    private let onWatch: () -> Void
    private let onPremium: () -> Void
    private let onClose: () -> Void

    public init(onWatch: @escaping () -> Void, onPremium: @escaping () -> Void, onClose: @escaping () -> Void) {
        self.onWatch = onWatch
        self.onPremium = onPremium
        self.onClose = onClose
    }

    public var body: some View {
        ZStack {
            Color.black.opacity(0.5).ignoresSafeArea().onTapGesture { onClose() }
            BookPage {
                VStack(spacing: 12) {
                    Image(systemName: "lightbulb.fill").font(.system(size: 30)).foregroundStyle(DS.Palette.gold)
                    Text(L10n.s("ui.hints_out_title")).font(.dsSerif(22)).foregroundStyle(DS.Palette.ink)
                    Text(L10n.s("ui.hints_out_body")).font(.dsBody(14)).foregroundStyle(DS.Palette.inkSoft)
                        .multilineTextAlignment(.center)
                    VideoButton(title: L10n.s("ui.watch_video"), action: onWatch)
                    Button(action: onPremium) {
                        Label(L10n.s("ui.no_ads"), systemImage: "crown.fill")
                            .font(.dsBody(15)).foregroundStyle(DS.Palette.ink)
                            .padding(.horizontal, 22).padding(.vertical, 10)
                            .background(Capsule().fill(DS.Palette.panel))
                            .overlay(Capsule().strokeBorder(DS.Palette.gold, lineWidth: 2))
                    }.buttonStyle(.plain)
                    Button(action: onClose) {
                        Text(L10n.s("ui.cancel")).font(.dsCaption(13)).foregroundStyle(DS.Palette.inkSoft)
                    }.buttonStyle(.plain)
                }
                .padding(EdgeInsets(top: 20, leading: 36, bottom: 18, trailing: 36))
                .frame(width: 400)
            }
            .fixedSize()
            .shadow(color: .black.opacity(0.4), radius: 18, y: 10)
        }
    }
}

/// Кнопка «за ролик»: неактивна с пояснением, пока ролик не загрузился или идёт показ.
public struct VideoButton: View {
    @State private var ads = AdService.shared
    let title: String
    let action: () -> Void

    public init(title: String, action: @escaping () -> Void) {
        self.title = title
        self.action = action
    }

    public var body: some View {
        let available = ads.isEnabled && ads.isReady && ads.cooldownLeft == 0 && !ads.isShowing
        Button(action: action) {
            HStack(spacing: 8) {
                Image(systemName: "play.rectangle.fill").font(.system(size: 15, weight: .semibold))
                Text(available ? title : L10n.s("ui.video_loading")).font(.dsBody(15))
            }
            .foregroundStyle(available ? DS.Palette.paper : DS.Palette.paper.opacity(0.7))
            .padding(.horizontal, 24).padding(.vertical, 11)
            .background(Capsule().fill(available ? DS.Palette.maroon : DS.Palette.inkSoft))
            .overlay(Capsule().strokeBorder(DS.Palette.gold.opacity(available ? 0.8 : 0.3), lineWidth: 2))
        }
        .buttonStyle(.plain).disabled(!available)
    }
}

struct CloseButton: View {
    let action: () -> Void
    var body: some View {
        Button(action: action) {
            Image(systemName: "xmark").font(.system(size: 12, weight: .heavy))
                .foregroundStyle(DS.Palette.inkSoft).frame(width: 30, height: 30)
                .background(Circle().fill(DS.Palette.paper))
                .overlay(Circle().strokeBorder(DS.Palette.ink.opacity(0.25), lineWidth: 1))
        }.buttonStyle(.plain).padding(10)
    }
}
