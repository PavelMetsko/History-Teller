import UIKit

/// Тактильная отдача. На симуляторе — no-op, на устройстве добавляет «сок».
public enum Haptics {
    public static func light()  { impact(.light) }
    public static func medium() { impact(.medium) }
    public static func rigid()  { impact(.rigid) }

    public static func success() {
        let g = UINotificationFeedbackGenerator()
        g.prepare()
        g.notificationOccurred(.success)
    }

    public static func error() {
        let g = UINotificationFeedbackGenerator()
        g.prepare()
        g.notificationOccurred(.error)
    }

    private static func impact(_ style: UIImpactFeedbackGenerator.FeedbackStyle) {
        let g = UIImpactFeedbackGenerator(style: style)
        g.prepare()
        g.impactOccurred()
    }
}
