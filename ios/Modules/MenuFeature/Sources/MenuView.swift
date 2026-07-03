import SwiftUI
import DesignSystem
import GameContent

/// Главное меню — титульная страница книги.
public struct MenuView: View {
    private let onPlay: () -> Void
    private let onReset: () -> Void
    @State private var showResetConfirm = false
    @State private var showSettings = false

    public init(onPlay: @escaping () -> Void, onReset: @escaping () -> Void) {
        self.onPlay = onPlay
        self.onReset = onReset
    }

    public var body: some View {
        ZStack {
            DS.Palette.backdrop.ignoresSafeArea()

            BookPage {
                HStack(spacing: 20) {
                    titleBlock
                        .layoutPriority(1)
                    Spacer(minLength: 0)
                    heroSprites
                }
                .frame(maxWidth: 720)                       // плотная композиция, не растягиваться на iPad
                .frame(maxWidth: .infinity)                 // и центрироваться в книге
                .padding(EdgeInsets(top: 24, leading: 48, bottom: 24, trailing: 36))
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
                .font(.dsSerif(48))
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
                .font(.dsBody(15))
                .foregroundStyle(DS.Palette.inkSoft)
                .fixedSize(horizontal: false, vertical: true)
                .padding(.top, 14)

            playButton
                .padding(.top, 22)

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
            .font(.dsSerif(22))
            .foregroundStyle(DS.Palette.paper)
            .padding(.horizontal, 40).padding(.vertical, 15)
            .background(Capsule().fill(DS.Palette.maroon))
            .overlay(Capsule().strokeBorder(DS.Palette.ink, lineWidth: 3))
            .shadow(color: .black.opacity(0.25), radius: 5, y: 3)
        }
        .buttonStyle(.plain)
    }

    private var heroSprites: some View {
        ZStack(alignment: .bottom) {
            Image.character("caesar")
                .resizable().scaledToFit()
                .frame(height: 250)
                .offset(x: -60)
            Image.character("cleopatra")
                .resizable().scaledToFit()
                .frame(height: 280)
                .offset(x: 55)
        }
        .frame(width: 320)
    }
}
