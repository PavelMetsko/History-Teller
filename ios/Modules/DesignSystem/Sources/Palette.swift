import SwiftUI

/// Бумажная палитра History Teller (стиль-референс Storyteller: тёплый пергамент,
/// толстый тёмно-коричневый контур #2b2419).
public enum DS {
    public enum Palette {
        public static let backdrop = Color(red: 0.204, green: 0.133, blue: 0.180) // тёмный баклажан за страницей
        public static let paperEdge = Color(red: 0.870, green: 0.796, blue: 0.639) // тень/край пергамента
        public static let ribbon   = Color(red: 0.596, green: 0.184, blue: 0.204) // красная закладка
        public static let paper   = Color(red: 0.945, green: 0.894, blue: 0.780) // #F1E4C7 фон
        public static let panel   = Color(red: 0.969, green: 0.937, blue: 0.863) // #F7EFDC карточки
        public static let ink     = Color(red: 0.169, green: 0.141, blue: 0.098) // #2B2419 контур/текст
        public static let inkSoft = Color(red: 0.169, green: 0.141, blue: 0.098).opacity(0.55)
        public static let gold    = Color(red: 0.788, green: 0.635, blue: 0.294) // #C9A24B
        public static let maroon  = Color(red: 0.541, green: 0.231, blue: 0.290) // #8A3B4A пурпур тоги
        public static let sky     = Color(red: 0.749, green: 0.878, blue: 0.878) // #BFE0E0
        public static let love    = Color(red: 0.804, green: 0.267, blue: 0.267) // сердечки
        public static let success = Color(red: 0.298, green: 0.545, blue: 0.318) // цель достигнута
    }
}
