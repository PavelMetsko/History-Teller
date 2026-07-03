import SwiftUI

/// Золотые уголки-скобки по углам страницы (как в книжном развороте).
public struct GoldCorners: View {
    private let inset: CGFloat
    private let length: CGFloat
    private let thickness: CGFloat

    public init(inset: CGFloat = 10, length: CGFloat = 26, thickness: CGFloat = 5) {
        self.inset = inset; self.length = length; self.thickness = thickness
    }

    public var body: some View {
        GeometryReader { g in
            let w = g.size.width, h = g.size.height, i = inset, l = length
            Path { p in
                p.move(to: CGPoint(x: i, y: i + l)); p.addLine(to: CGPoint(x: i, y: i)); p.addLine(to: CGPoint(x: i + l, y: i))
                p.move(to: CGPoint(x: w - i - l, y: i)); p.addLine(to: CGPoint(x: w - i, y: i)); p.addLine(to: CGPoint(x: w - i, y: i + l))
                p.move(to: CGPoint(x: i, y: h - i - l)); p.addLine(to: CGPoint(x: i, y: h - i)); p.addLine(to: CGPoint(x: i + l, y: h - i))
                p.move(to: CGPoint(x: w - i - l, y: h - i)); p.addLine(to: CGPoint(x: w - i, y: h - i)); p.addLine(to: CGPoint(x: w - i, y: h - i - l))
            }
            .stroke(DS.Palette.gold, style: StrokeStyle(lineWidth: thickness, lineCap: .round, lineJoin: .round))
        }
        .allowsHitTesting(false)
    }
}

/// Пергаментная «страница книги»: заливка + контур + золотые уголки + тень.
public struct BookPage<Content: View>: View {
    private let content: Content
    public init(@ViewBuilder content: () -> Content) { self.content = content() }

    public var body: some View {
        content
            .background(
                RoundedRectangle(cornerRadius: 22, style: .continuous)
                    .fill(DS.Palette.paper)
                    .overlay(
                        RoundedRectangle(cornerRadius: 22, style: .continuous)
                            .strokeBorder(DS.Palette.paperEdge, lineWidth: 6)
                    )
            )
            .overlay(
                RoundedRectangle(cornerRadius: 22, style: .continuous)
                    .strokeBorder(DS.Palette.ink.opacity(0.45), lineWidth: 2)
            )
            .overlay(GoldCorners(inset: 4, length: 20).padding(6))
            .shadow(color: .black.opacity(0.45), radius: 14, x: 0, y: 8)
    }
}

/// Красная закладка-лента (настройки / назад).
public struct RibbonButton: View {
    private let systemImage: String
    private let action: () -> Void

    public init(systemImage: String, action: @escaping () -> Void) {
        self.systemImage = systemImage; self.action = action
    }

    public var body: some View {
        Button(action: action) {
            Image(systemName: systemImage)
                .font(.system(size: 16, weight: .bold))
                .foregroundStyle(.white)
                .frame(width: 40, height: 52)
                .background(
                    RibbonShape().fill(DS.Palette.ribbon)
                        .overlay(RibbonShape().stroke(DS.Palette.ink.opacity(0.35), lineWidth: 1.5))
                        .shadow(color: .black.opacity(0.3), radius: 3, y: 2)
                )
        }
        .buttonStyle(.plain)
    }
}

/// Форма ленты: прямоугольник с треугольным вырезом снизу (рыбий хвост).
public struct RibbonShape: Shape {
    public init() {}
    public func path(in r: CGRect) -> Path {
        var p = Path()
        let notch: CGFloat = 12
        p.move(to: CGPoint(x: r.minX, y: r.minY))
        p.addLine(to: CGPoint(x: r.maxX, y: r.minY))
        p.addLine(to: CGPoint(x: r.maxX, y: r.maxY))
        p.addLine(to: CGPoint(x: r.midX, y: r.maxY - notch))
        p.addLine(to: CGPoint(x: r.minX, y: r.maxY))
        p.closeSubpath()
        return p
    }
}
