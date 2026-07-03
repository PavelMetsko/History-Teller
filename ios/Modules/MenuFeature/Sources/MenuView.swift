import SwiftUI
import DesignSystem
import GameContent

/// Главное меню.
public struct MenuView: View {
    private let onPlay: () -> Void
    private let onReset: () -> Void

    public init(onPlay: @escaping () -> Void, onReset: @escaping () -> Void) {
        self.onPlay = onPlay
        self.onReset = onReset
    }

    public var body: some View {
        ZStack {
            DS.Palette.paper.ignoresSafeArea()

            HStack(spacing: 24) {
                VStack(alignment: .leading, spacing: 18) {
                    Spacer(minLength: 0)

                    Text("History Teller")
                        .font(.dsTitle(46))
                        .foregroundStyle(DS.Palette.ink)
                    Text("Собирай историю из панелей —\nи узнавай, как было на самом деле.")
                        .font(.dsBody(16))
                        .foregroundStyle(DS.Palette.inkSoft)

                    Button(action: onPlay) {
                        HStack(spacing: 8) {
                            Image(systemName: "play.fill")
                            Text("Играть")
                        }
                        .font(.dsTitle(20))
                        .foregroundStyle(DS.Palette.paper)
                        .padding(.horizontal, 34).padding(.vertical, 14)
                        .background(Capsule().fill(DS.Palette.maroon))
                        .overlay(Capsule().strokeBorder(DS.Palette.ink, lineWidth: 3))
                    }
                    .padding(.top, 4)

                    Button(action: onReset) {
                        Text("Сбросить прогресс")
                            .font(.dsCaption())
                            .foregroundStyle(DS.Palette.inkSoft)
                    }

                    Spacer(minLength: 0)
                }
                .frame(maxWidth: .infinity, alignment: .leading)

                heroSprites
            }
            .padding(.horizontal, 44)
            .padding(.vertical, 24)
        }
    }

    private var heroSprites: some View {
        ZStack(alignment: .bottom) {
            Image.character("caesar")
                .resizable().scaledToFit()
                .frame(height: 230)
                .offset(x: -70)
            Image.character("cleopatra")
                .resizable().scaledToFit()
                .frame(height: 260)
                .offset(x: 40)
        }
        .frame(width: 320)
    }
}
