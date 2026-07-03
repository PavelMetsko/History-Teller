import SwiftUI

/// Карточка бумажного стиля: заливка + толстый контур цвета чернил + мягкая тень.
public struct PaperCard<Content: View>: View {
    private let cornerRadius: CGFloat
    private let fill: Color
    private let borderWidth: CGFloat
    private let content: Content

    public init(cornerRadius: CGFloat = 18,
                fill: Color = DS.Palette.panel,
                borderWidth: CGFloat = 4,
                @ViewBuilder content: () -> Content) {
        self.cornerRadius = cornerRadius
        self.fill = fill
        self.borderWidth = borderWidth
        self.content = content()
    }

    public var body: some View {
        content
            .background(
                RoundedRectangle(cornerRadius: cornerRadius, style: .continuous).fill(fill)
            )
            .overlay(
                RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
                    .strokeBorder(DS.Palette.ink, lineWidth: borderWidth)
            )
            .shadow(color: DS.Palette.ink.opacity(0.18), radius: 5, x: 0, y: 3)
    }
}

/// Капсульная плашка-лейбл (действие сцены, статус цели и т.п.).
public struct PillLabel: View {
    private let text: String
    private let systemImage: String?
    private let background: Color
    private let foreground: Color

    public init(_ text: String,
                systemImage: String? = nil,
                background: Color = DS.Palette.paper,
                foreground: Color = DS.Palette.ink) {
        self.text = text
        self.systemImage = systemImage
        self.background = background
        self.foreground = foreground
    }

    public var body: some View {
        HStack(spacing: 5) {
            if let systemImage { Image(systemName: systemImage) }
            Text(text)
        }
        .font(.dsCaption())
        .padding(.horizontal, 10)
        .padding(.vertical, 6)
        .foregroundStyle(foreground)
        .background(Capsule().fill(background))
        .overlay(Capsule().strokeBorder(DS.Palette.ink, lineWidth: 2))
    }
}
