import Foundation
import Observation

/// Согласие на рекламные данные — без стороннего CMP. AppLovin MAX и Tenjin принимают простой
/// флаг согласия, который нужно выставить до старта их SDK, поэтому спрашиваем сами:
/// в GDPR-регионе (ЕЭЗ, UK, Швейцария) — своё окно, затем ATT; в остальных — только ATT.
/// Окно рисует приложение (`promptVisible`), сервис хранит ответ и сообщает `onReady`.
@Observable
public final class ConsentService {
    public static let shared = ConsentService()

    public enum Choice: String { case granted, denied }

    /// Сохранённый ответ. nil — ещё не спрашивали.
    public private(set) var choice: Choice? {
        didSet { UserDefaults.standard.set(choice?.rawValue, forKey: Self.key) }
    }
    /// Показывать окно согласия (первый запуск в GDPR-регионе или строка в настройках).
    public private(set) var promptVisible = false

    /// В GDPR-регионе — явное согласие; в остальных реклама персональная, пока игрок не отказался
    /// в настройках (для AppLovin это «do not sell», CCPA).
    public var hasUserConsent: Bool { choice == .granted }
    public var doNotSell: Bool { choice == .denied }

    private static let key = "ht.adsConsent"
    private var started = false
    private var settled = false
    private var readyHandlers: [() -> Void] = []
    private var changeHandlers: [() -> Void] = []

    private init() {
        choice = UserDefaults.standard.string(forKey: Self.key).flatMap(Choice.init)
    }

    /// Вызвать, когда согласие и ATT отработали (сразу, если уже).
    public func onReady(_ handler: @escaping () -> Void) {
        if settled { handler() } else { readyHandlers.append(handler) }
    }

    /// Игрок поменял ответ (окно из настроек) — SDK обновляют свои флаги.
    public func onChange(_ handler: @escaping () -> Void) { changeHandlers.append(handler) }

    /// Раз за сессию, после онбординга.
    public func start() {
        guard !started else { return }
        started = true
        if choice == nil && Self.isGDPRRegion {
            promptVisible = true          // продолжим в answer(_:)
        } else {
            requestTrackingAndFinish()
        }
    }

    /// Строка «Конфиденциальность» в настройках: передумать в любую сторону.
    public func showPrompt() { promptVisible = true }

    public func answer(_ granted: Bool) {
        choice = granted ? .granted : .denied
        promptVisible = false
        if settled { changeHandlers.forEach { $0() } } else { requestTrackingAndFinish() }
    }

    private func requestTrackingAndFinish() {
        TrackingService.shared.requestIfNeeded { [weak self] in
            guard let self, !self.settled else { return }
            self.settled = true
            let handlers = self.readyHandlers
            self.readyHandlers = []
            handlers.forEach { $0() }
        }
    }

    /// ЕЭЗ + Великобритания + Швейцария. Регион устройства; если его нет — европейский часовой пояс.
    /// Лишний раз спросить безопасно, не спросить где надо — нет.
    static var isGDPRRegion: Bool {
        if let region = Locale.current.region?.identifier { return gdprRegions.contains(region) }
        return TimeZone.current.identifier.hasPrefix("Europe/")
    }

    static let gdprRegions: Set<String> = [
        "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT",
        "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE",   // ЕС
        "IS", "LI", "NO",                                                         // ЕЭЗ
        "GB", "CH",
    ]
}
