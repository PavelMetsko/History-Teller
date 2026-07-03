import SwiftUI

public extension Font {
    /// Округлый «книжный» шрифт под бумажный стиль.
    static func dsTitle(_ size: CGFloat = 26) -> Font { .system(size: size, weight: .heavy,     design: .rounded) }
    static func dsBody(_ size: CGFloat = 16)  -> Font { .system(size: size, weight: .semibold,  design: .rounded) }
    static func dsCaption(_ size: CGFloat = 12) -> Font { .system(size: size, weight: .bold,     design: .rounded) }
    /// Книжный шрифт с засечками (заголовки уровней/глав).
    static func dsSerif(_ size: CGFloat = 22) -> Font { .system(size: size, weight: .bold,     design: .serif) }
}
