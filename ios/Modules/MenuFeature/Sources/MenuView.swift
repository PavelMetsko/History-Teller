import SwiftUI
import DesignSystem
import GameContent

/// Главное меню — титульная страница книги.
public struct MenuView: View {
    private let onPlay: () -> Void
    private let onReset: () -> Void
    @State private var showResetConfirm = false

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
                    Spacer(minLength: 0)
                    heroSprites
                }
                .padding(EdgeInsets(top: 24, leading: 48, bottom: 24, trailing: 36))
            }
            .padding(EdgeInsets(top: 16, leading: 20, bottom: 16, trailing: 20))

            if showResetConfirm {
                BookDialog(
                    title: "Сбросить прогресс?",
                    message: "Все пройденные уровни станут заново закрытыми.\nЭто действие нельзя отменить.",
                    confirmTitle: "Сбросить",
                    cancelTitle: "Отмена",
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
        }
    }

    private var titleBlock: some View {
        VStack(alignment: .leading, spacing: 0) {
            Spacer(minLength: 0)

            Text("ИСТОРИЧЕСКАЯ ГОЛОВОЛОМКА")
                .font(.dsCaption(11))
                .tracking(2)
                .foregroundStyle(DS.Palette.maroon)

            Text("History Teller")
                .font(.dsSerif(48))
                .foregroundStyle(DS.Palette.ink)
                .padding(.top, 4)

            // тонкая линия-росчерк под заголовком
            RoundedRectangle(cornerRadius: 2)
                .fill(DS.Palette.gold)
                .frame(width: 120, height: 3)
                .padding(.top, 8)

            Text("Собери историю из панелей —\nи узнай, как было на самом деле.")
                .font(.dsBody(15))
                .foregroundStyle(DS.Palette.inkSoft)
                .padding(.top, 14)

            playButton
                .padding(.top, 22)

            Button {
                withAnimation(.easeIn(duration: 0.2)) { showResetConfirm = true }
            } label: {
                Text("Сбросить прогресс")
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
                Text("Играть")
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
