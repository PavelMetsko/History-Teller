import SwiftUI

/// Эмблема уровня игрока: сургучная печать с номером в металлическом кольце. Металл растёт со
/// званием — бронза, серебро, золото, — чтобы прогресс было видно издалека, без чтения цифр.
public struct RankBadge: View {
    let level: Int
    var size: CGFloat

    public init(level: Int, size: CGFloat = 44) {
        self.level = level
        self.size = size
    }

    public static func metal(_ level: Int) -> Color {
        switch level {
        case ..<6: return Color(red: 0.72, green: 0.47, blue: 0.27)    // бронза
        case ..<11: return Color(red: 0.70, green: 0.72, blue: 0.75)   // серебро
        default: return DS.Palette.gold
        }
    }

    public var body: some View {
        ZStack {
            Circle().fill(Self.metal(level))
            Circle().strokeBorder(DS.Palette.ink.opacity(0.55), lineWidth: max(1.5, size * 0.04))
            Circle().fill(DS.Palette.maroon).padding(size * 0.13)
                .overlay(Circle().strokeBorder(.black.opacity(0.25), lineWidth: 1).padding(size * 0.13))
            Text("\(level)")
                .font(.system(size: size * (level >= 10 ? 0.36 : 0.44), weight: .heavy, design: .serif))
                .foregroundStyle(DS.Palette.paper)
                .minimumScaleFactor(0.5)
        }
        .frame(width: size, height: size)
        .shadow(color: .black.opacity(0.25), radius: 2, y: 1)
    }
}

/// Полоса опыта до следующего уровня.
public struct XPBar: View {
    let progress: Double
    var height: CGFloat

    public init(progress: Double, height: CGFloat = 8) {
        self.progress = progress
        self.height = height
    }

    public var body: some View {
        GeometryReader { g in
            ZStack(alignment: .leading) {
                Capsule().fill(DS.Palette.ink.opacity(0.14))
                Capsule()
                    .fill(LinearGradient(colors: [DS.Palette.gold, Color(red: 0.95, green: 0.80, blue: 0.40)],
                                         startPoint: .leading, endPoint: .trailing))
                    .frame(width: max(height, g.size.width * min(1, max(0, progress))))
                    .opacity(progress > 0 ? 1 : 0)
            }
        }
        .frame(height: height)
        .overlay(Capsule().strokeBorder(DS.Palette.ink.opacity(0.35), lineWidth: 1))
    }
}

/// Счётчик с иконкой: 🔥 серия, 💡 подсказки.
public struct StatChip: View {
    let systemImage: String
    let text: String
    let tint: Color
    var dimmed: Bool

    public init(systemImage: String, text: String, tint: Color, dimmed: Bool = false) {
        self.systemImage = systemImage
        self.text = text
        self.tint = tint
        self.dimmed = dimmed
    }

    public var body: some View {
        HStack(spacing: 4) {
            Image(systemName: systemImage).font(.system(size: 13, weight: .bold))
                .foregroundStyle(dimmed ? DS.Palette.inkSoft : tint)
            Text(text).font(.dsBody(14)).monospacedDigit().foregroundStyle(DS.Palette.ink)
        }
        .padding(.horizontal, 10).padding(.vertical, 5)
        .background(Capsule().fill(DS.Palette.panel))
        .overlay(Capsule().strokeBorder(DS.Palette.ink.opacity(0.3), lineWidth: 1.2))
    }
}

/// Золотые искры вокруг точки — для повышения уровня и подарков.
public struct SparkBurst: View {
    @State private var go = false
    private let count = 14

    public init() {}

    public var body: some View {
        ZStack {
            ForEach(0..<count, id: \.self) { i in
                let a = Double(i) / Double(count) * 2 * .pi
                Image(systemName: i.isMultiple(of: 3) ? "star.fill" : "sparkle")
                    .font(.system(size: i.isMultiple(of: 2) ? 12 : 9, weight: .bold))
                    .foregroundStyle(DS.Palette.gold)
                    .offset(x: go ? cos(a) * 90 : 0, y: go ? sin(a) * 70 : 0)
                    .opacity(go ? 0 : 1)
                    .scaleEffect(go ? 1.2 : 0.3)
            }
        }
        .allowsHitTesting(false)
        .onAppear { withAnimation(.easeOut(duration: 1.1)) { go = true } }
    }
}

/// Пламя серии: растёт и меняет цвет со стадией (0 — погасло, 1 Искра … 6 Вечный огонь).
/// Живое — подрагивает; с Костра появляется ореол, с Маяка — искры вокруг.
public struct FlameBadge: View {
    let tier: Int
    var size: CGFloat
    var animated: Bool

    @State private var flicker = false
    @State private var spin = false

    public init(tier: Int, size: CGFloat = 28, animated: Bool = true) {
        self.tier = tier
        self.size = size
        self.animated = animated
    }

    /// Цвета стадии: низ → верх пламени.
    public static func colors(_ tier: Int) -> (Color, Color) {
        switch tier {
        case 0: return (Color.gray.opacity(0.5), Color.gray.opacity(0.3))
        case 1: return (Color(red: 1.0, green: 0.62, blue: 0.20), Color(red: 1.0, green: 0.86, blue: 0.40))
        case 2: return (Color(red: 1.0, green: 0.50, blue: 0.10), Color(red: 1.0, green: 0.80, blue: 0.30))
        case 3: return (Color(red: 0.95, green: 0.30, blue: 0.08), Color(red: 1.0, green: 0.70, blue: 0.20))
        case 4: return (Color(red: 0.80, green: 0.10, blue: 0.10), Color(red: 1.0, green: 0.55, blue: 0.15))
        case 5: return (Color(red: 0.10, green: 0.40, blue: 0.95), Color(red: 0.45, green: 0.85, blue: 1.0))
        default: return (Color(red: 0.55, green: 0.15, blue: 0.85), Color(red: 1.0, green: 0.75, blue: 0.95))
        }
    }

    /// Пламя крупнеет со стадией — от 70% до 100% размера.
    private var scale: CGFloat { 0.7 + 0.3 * CGFloat(min(tier, 6)) / 6 }

    public var body: some View {
        let (bottom, top) = Self.colors(tier)
        ZStack {
            if tier >= 4 {
                Circle()
                    .fill(RadialGradient(colors: [top.opacity(0.55), .clear], center: .center,
                                         startRadius: 0, endRadius: size * 0.7))
                    .frame(width: size * 1.5, height: size * 1.5)
                    .scaleEffect(flicker ? 1.08 : 0.94)
            }
            Image(systemName: "flame.fill")
                .resizable().scaledToFit()
                .foregroundStyle(LinearGradient(colors: [top, bottom], startPoint: .top, endPoint: .bottom))
                .frame(width: size * scale, height: size * scale)
                .scaleEffect(x: flicker ? 0.97 : 1.03, y: flicker ? 1.05 : 0.96, anchor: .bottom)
                .shadow(color: bottom.opacity(tier >= 2 ? 0.6 : 0), radius: size * 0.12)
            if tier >= 2 {
                Image(systemName: "flame.fill")
                    .resizable().scaledToFit()
                    .foregroundStyle(Color.white.opacity(0.75))
                    .frame(width: size * scale * 0.38, height: size * scale * 0.38)
                    .offset(y: size * scale * 0.2)
                    .scaleEffect(y: flicker ? 1.1 : 0.9, anchor: .bottom)
            }
            if tier >= 5 {
                ForEach(0..<6, id: \.self) { i in
                    Image(systemName: "sparkle")
                        .font(.system(size: size * 0.16, weight: .bold))
                        .foregroundStyle(top)
                        .offset(y: -size * 0.62)
                        .rotationEffect(.degrees(Double(i) * 60 + (spin ? 360 : 0)))
                }
            }
        }
        .frame(width: size, height: size)
        .onAppear {
            guard animated, tier > 0 else { return }
            withAnimation(.easeInOut(duration: 0.55).repeatForever(autoreverses: true)) { flicker = true }
            if tier >= 5 {
                withAnimation(.linear(duration: 8).repeatForever(autoreverses: false)) { spin = true }
            }
        }
    }
}
