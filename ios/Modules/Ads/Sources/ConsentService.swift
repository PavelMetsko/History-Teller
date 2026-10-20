import UIKit
import Observation
import UserMessagingPlatform

/// Согласие на данные: GDPR-форма Google UMP (сертифицированный CMP — без него AdMob в ЕЭЗ
/// рекламу не показывает), затем системный запрос ATT. Как в Decima. Запускается раз за сессию —
/// после онбординга, чтобы новичок сначала увидел игру. Форма и языки настраиваются в AdMob →
/// Privacy & messaging («History Teller GDPR consent»). Реклама и Tenjin ждут `onReady`.
@Observable
public final class ConsentService {
    public static let shared = ConsentService()

    /// Можно запрашивать рекламу (согласие получено или не требуется).
    public private(set) var canRequestAds = false
    /// Строка «Конфиденциальность» в настройках — только там, где форма обязательна (ЕЭЗ/UK/CH).
    public private(set) var privacyOptionsRequired = false
    /// Форма в этом регионе не нужна (вне ЕЭЗ) — Tenjin тогда не ждёт TCF-строку.
    public var isConsentNotRequired: Bool { ConsentInformation.shared.consentStatus == .notRequired }

    private var started = false
    private var settled = false
    private var readyHandlers: [() -> Void] = []
    private var changeHandlers: [() -> Void] = []

    private init() {}

    /// Вызвать, когда согласие и ATT отработали (сразу, если уже).
    public func onReady(_ handler: @escaping () -> Void) {
        if settled { handler() } else { readyHandlers.append(handler) }
    }

    /// Игрок поменял выбор в форме из настроек — SDK обновляют свои флаги.
    public func onChange(_ handler: @escaping () -> Void) { changeHandlers.append(handler) }

    /// Раз за сессию, после онбординга.
    public func start() {
        guard !started else { return }
        started = true

        let parameters = RequestParameters()
        #if DEBUG
        // Форма показывается как в ЕЭЗ — иначе вне Европы её не проверить.
        let debug = DebugSettings()
        debug.geography = .EEA
        parameters.debugSettings = debug
        #endif

        ConsentInformation.shared.requestConsentInfoUpdate(with: parameters) { [weak self] error in
            guard let self else { return }
            if let error { print("Consent info update error: \(error.localizedDescription)") }
            DispatchQueue.main.async {
                // Не обновилось (офлайн) — работаем на сохранённом согласии.
                guard error == nil, let vc = Self.topViewController() else { return self.finish() }
                ConsentForm.loadAndPresentIfRequired(from: vc) { formError in
                    if let formError { print("Consent form error: \(formError.localizedDescription)") }
                    self.finish()
                }
            }
        }
    }

    /// Строка «Конфиденциальность» в настройках: форма Google с выбором заново.
    public func presentPrivacyOptionsForm() {
        ConsentForm.presentPrivacyOptionsForm(from: Self.topViewController()) { [weak self] error in
            if let error { print("Privacy options form error: \(error.localizedDescription)") }
            guard let self else { return }
            self.refresh()
            self.changeHandlers.forEach { $0() }
        }
    }

    private func finish() {
        refresh()
        // ATT после GDPR-формы, как рекомендует Google: два окна не наслаиваются.
        TrackingService.shared.requestIfNeeded { [weak self] in
            guard let self, !self.settled else { return }
            self.settled = true
            let handlers = self.readyHandlers
            self.readyHandlers = []
            handlers.forEach { $0() }
        }
    }

    private func refresh() {
        canRequestAds = ConsentInformation.shared.canRequestAds
        privacyOptionsRequired = ConsentInformation.shared.privacyOptionsRequirementStatus == .required
    }

    static func topViewController() -> UIViewController? {
        let scene = UIApplication.shared.connectedScenes.first { $0.activationState == .foregroundActive } as? UIWindowScene
            ?? UIApplication.shared.connectedScenes.first as? UIWindowScene
        guard let window = scene?.windows.first(where: \.isKeyWindow) ?? scene?.windows.first,
              var top = window.rootViewController else { return nil }
        while let presented = top.presentedViewController { top = presented }
        return top
    }
}
