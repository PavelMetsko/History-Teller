import UIKit

/// Тактильная отдача. На симуляторе — no-op, на устройстве добавляет «сок».
/// Уважает переключатель «Вибрация» в настройках (ключ `ht.haptics`, по умолчанию вкл).
public enum Haptics {
    public static var enabled: Bool {
        (UserDefaults.standard.object(forKey: "ht.haptics") as? Bool) ?? true
    }

    public static func light()  { impact(.light) }
    public static func medium() { impact(.medium) }
    public static func rigid()  { impact(.rigid) }

    public static func success() {
        guard enabled else { return }
        let g = UINotificationFeedbackGenerator()
        g.prepare()
        g.notificationOccurred(.success)
    }

    public static func error() {
        guard enabled else { return }
        let g = UINotificationFeedbackGenerator()
        g.prepare()
        g.notificationOccurred(.error)
    }

    private static func impact(_ style: UIImpactFeedbackGenerator.FeedbackStyle) {
        guard enabled else { return }
        let g = UIImpactFeedbackGenerator(style: style)
        g.prepare()
        g.impactOccurred()
    }
}
