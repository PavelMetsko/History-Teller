import SwiftUI

/// Книжный диалог-подтверждение: затемнение + пергаментная карточка с двумя кнопками.
public struct BookDialog: View {
    private let title: String
    private let message: String?
    private let confirmTitle: String
    private let cancelTitle: String
    private let destructive: Bool
    private let onConfirm: () -> Void
    private let onCancel: () -> Void
    @State private var appeared = false

    public init(title: String,
                message: String? = nil,
                confirmTitle: String,
                cancelTitle: String,
                destructive: Bool = false,
                onConfirm: @escaping () -> Void,
                onCancel: @escaping () -> Void) {
        self.title = title
        self.message = message
        self.confirmTitle = confirmTitle
        self.cancelTitle = cancelTitle
        self.destructive = destructive
        self.onConfirm = onConfirm
        self.onCancel = onCancel
    }

    public var body: some View {
        ZStack {
            Color.black.opacity(0.5).ignoresSafeArea()
                .opacity(appeared ? 1 : 0)
                .onTapGesture { onCancel() }

            BookPage {
                VStack(spacing: 12) {
                    Text(title)
                        .font(.dsSerif(22))
                        .foregroundStyle(DS.Palette.ink)
                        .multilineTextAlignment(.center)
                    if let message {
                        Text(message)
                            .font(.dsBody(14))
                            .foregroundStyle(DS.Palette.inkSoft)
                            .multilineTextAlignment(.center)
                    }
                    HStack(spacing: 14) {
                        dialogButton(cancelTitle, filled: false, action: onCancel)
                        dialogButton(confirmTitle, filled: true, action: onConfirm)
                    }
                    .padding(.top, 8)
                }
                .padding(26)
            }
            .frame(maxWidth: 460)
            .padding(.horizontal, 40)
            .scaleEffect(appeared ? 1 : 0.85)
            .opacity(appeared ? 1 : 0)
        }
        .onAppear {
            withAnimation(.spring(response: 0.4, dampingFraction: 0.78)) { appeared = true }
        }
    }

    private func dialogButton(_ title: String, filled: Bool, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Text(title)
                .font(.dsBody(15))
                .foregroundStyle(filled ? DS.Palette.paper : DS.Palette.ink)
                .padding(.horizontal, 26).padding(.vertical, 11)
                .background(
                    Capsule().fill(filled ? (destructive ? DS.Palette.maroon : DS.Palette.gold)
                                          : DS.Palette.paper)
                )
                .overlay(Capsule().strokeBorder(DS.Palette.ink.opacity(0.55), lineWidth: 2))
        }
        .buttonStyle(.plain)
    }
}
