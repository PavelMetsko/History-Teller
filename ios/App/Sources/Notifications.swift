import Foundation
import UserNotifications
import GameContent
import GameProgress

/// Локальные напоминания (правила — `docs/f2p-patch-4.0.md` §3): серия сгорает, эпизод дня,
/// подарок, «история ждёт». Перепланируются целиком при уходе в фон и после каждого решения,
/// поэтому всегда отражают свежее состояние, а не то, что было при прошлом запуске.
enum Notifications {
    private static let ids = ["ht.streak", "ht.daily", "ht.gift", "ht.week"]

    /// Системный запрос — один раз, после первого экрана награды: игрок уже понял, зачем возвращаться.
    static func askOnce() {
        guard !Meta.shared.pushAsked else { return }
        Meta.shared.pushAsked = true
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { _, _ in }
    }

    /// - Parameters:
    ///   - tomorrowDaily: название эпизода дня на завтра.
    ///   - lastTitle: эпизод, к которому звать вернуться.
    static func reschedule(tomorrowDaily: String?, lastTitle: String?) {
        let center = UNUserNotificationCenter.current()
        center.getNotificationSettings { settings in
            guard settings.authorizationStatus == .authorized || settings.authorizationStatus == .provisional
            else { return }
            center.removePendingNotificationRequests(withIdentifiers: ids)
            let meta = Meta.shared
            let cal = Calendar.current
            let now = Date()
            let today = cal.startOfDay(for: now)

            if meta.currentStreak >= 1 && !meta.solvedToday,
               let at = cal.date(bySettingHour: 20, minute: 0, second: 0, of: today), at > now {
                add("ht.streak", L10n.s("ui.push.streak", meta.currentStreak), at)
            }
            if let title = tomorrowDaily,
               let day = cal.date(byAdding: .day, value: 1, to: today),
               let at = cal.date(bySettingHour: 19, minute: 0, second: 0, of: day) {
                add("ht.daily", L10n.s("ui.push.daily", title), at)
            }
            if let day = cal.date(byAdding: .day, value: 3, to: today),
               let at = cal.date(bySettingHour: 18, minute: 0, second: 0, of: day) {
                add("ht.gift", L10n.s("ui.push.gift"), at)
            }
            if let title = lastTitle,
               let day = cal.date(byAdding: .day, value: 7, to: today),
               let at = cal.date(bySettingHour: 18, minute: 0, second: 0, of: day) {
                add("ht.week", L10n.s("ui.push.week", title), at)
            }
        }
    }

    private static func add(_ id: String, _ body: String, _ date: Date) {
        let content = UNMutableNotificationContent()
        content.title = "History Teller"
        content.body = body
        content.sound = .default
        let comps = Calendar.current.dateComponents([.year, .month, .day, .hour, .minute], from: date)
        let trigger = UNCalendarNotificationTrigger(dateMatching: comps, repeats: false)
        UNUserNotificationCenter.current().add(UNNotificationRequest(identifier: id, content: content, trigger: trigger))
    }
}
