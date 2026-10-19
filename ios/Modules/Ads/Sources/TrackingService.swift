import UIKit
import AppTrackingTransparency

/// Системный запрос ATT (порт из Decima). Спрашиваем один раз: если ответ уже есть, сразу дальше.
/// Без разрешения реклама и атрибуция работают, просто без IDFA.
public final class TrackingService {
    public static let shared = TrackingService()
    private init() {}

    public var status: ATTrackingManager.AuthorizationStatus { ATTrackingManager.trackingAuthorizationStatus }

    public func requestIfNeeded(completion: @escaping () -> Void) {
        guard status == .notDetermined else { return completion() }
        // Окно ATT молча не показывается, если приложение ещё не active — ждём, пока UI устоится.
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
            ATTrackingManager.requestTrackingAuthorization { _ in
                DispatchQueue.main.async { completion() }
            }
        }
    }
}
