import UIKit
import Observation
import AppLovinSDK
import GameContent

/// Rewarded-реклама через AppLovin MAX: «посмотри ролик — открой один уровень платной главы».
/// Интерстишелов нет. SDK стартует после окна согласия (флаги согласия ставятся до старта),
/// выключается флагом `ads.rewarded` в облачном манифесте. Доход с показов уходит в Tenjin.
@Observable
public final class AdService: NSObject {
    public static let shared = AdService()

    // TODO: ключи из кабинета AppLovin MAX (Account → Keys, MAX → Ad Units). Пока пусто — рекламы нет.
    private static let sdkKey = ""
    private static let rewardedUnitId = ""

    /// Ролик загружен и его можно показать прямо сейчас.
    public private(set) var isReady = false
    public private(set) var isShowing = false
    /// Секунд до следующего ролика (кулдаун из манифеста). 0 — можно смотреть.
    public private(set) var cooldownLeft = 0

    /// Показывать ли кнопку «за ролик» вообще: ключи заданы и реклама не выключена в манифесте.
    public var isEnabled: Bool { !Self.sdkKey.isEmpty && ContentSync.shared.rewardedEnabled }

    private var started = false
    private var rewardedAd: MARewardedAd?
    private var retryAttempt = 0.0
    private var rewarded = false
    private var completion: ((Bool) -> Void)?
    private var lastShown: Date?
    private var cooldownTimer: Timer?

    private override init() {}

    /// Раз за сессию, из приложения на старте. Само дожидается согласия.
    public func start() {
        guard !started else { return }
        started = true
        ConsentService.shared.onReady { [weak self] in self?.initializeSDK() }
        ConsentService.shared.onChange { [weak self] in self?.applyConsent() }
    }

    /// Согласие поменяли в настройках — обновить флаги для следующих запросов.
    public func applyConsent() {
        let consent = ConsentService.shared
        // Флаг согласия — только когда игрок отвечал (в GDPR-регионе): вне ЕЭЗ «нет ответа» ≠ отказ.
        if consent.choice != nil { ALPrivacySettings.setHasUserConsent(consent.hasUserConsent) }
        ALPrivacySettings.setDoNotSell(consent.doNotSell)
    }

    /// Показать ролик. `completion(true)` — досмотрел и заслужил награду.
    public func show(completion: @escaping (Bool) -> Void) {
        guard isEnabled, cooldownLeft == 0, let ad = rewardedAd, ad.isReady else { return completion(false) }
        rewarded = false
        self.completion = completion
        isShowing = true
        ad.show()
    }

    private func initializeSDK() {
        guard !Self.sdkKey.isEmpty else { return }
        applyConsent()
        let config = ALSdkInitializationConfiguration(sdkKey: Self.sdkKey) { builder in
            builder.mediationProvider = ALMediationProviderMAX
        }
        ALSdk.shared().initialize(with: config) { [weak self] _ in
            guard let self, !Self.rewardedUnitId.isEmpty else { return }
            let ad = MARewardedAd.shared(withAdUnitIdentifier: Self.rewardedUnitId)
            ad.delegate = self
            ad.revenueDelegate = self
            self.rewardedAd = ad
            ad.load()
        }
    }

    private func finishShow() {
        isShowing = false
        isReady = false
        let done = completion
        completion = nil
        if rewarded { lastShown = Date(); startCooldown() }
        done?(rewarded)
        rewardedAd?.load()
    }

    private func startCooldown() {
        let total = ContentSync.shared.rewardedCooldown
        guard total > 0, let lastShown else { return }
        cooldownTimer?.invalidate()
        cooldownLeft = total
        cooldownTimer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { [weak self] t in
            guard let self else { return t.invalidate() }
            self.cooldownLeft = max(0, total - Int(Date().timeIntervalSince(lastShown)))
            if self.cooldownLeft == 0 { t.invalidate() }
        }
    }
}

extension AdService: MARewardedAdDelegate, MAAdRevenueDelegate {
    public func didLoad(_ ad: MAAd) {
        retryAttempt = 0
        isReady = true
    }

    public func didFailToLoadAd(forAdUnitIdentifier adUnitIdentifier: String, withError error: MAError) {
        isReady = false
        // Экспоненциальная пауза до 64 с — как советует AppLovin.
        retryAttempt += 1
        let delay = pow(2.0, min(6.0, retryAttempt))
        DispatchQueue.main.asyncAfter(deadline: .now() + delay) { [weak self] in self?.rewardedAd?.load() }
    }

    public func didDisplay(_ ad: MAAd) {}
    public func didClick(_ ad: MAAd) {}
    public func didHide(_ ad: MAAd) { finishShow() }

    public func didFail(toDisplay ad: MAAd, withError error: MAError) {
        rewarded = false
        finishShow()
    }

    public func didRewardUser(for ad: MAAd, with reward: MAReward) { rewarded = true }

    public func didPayRevenue(for ad: MAAd) {
        AttributionService.shared.trackAdRevenue(ad)
    }
}

/// Уровни платных глав, открытые за ролик. Хранятся на устройстве; уровень «сгорает», когда
/// пройден, — дальше его открывает сам прогресс (пройденные переигрываются бесплатно).
public enum RewardedUnlocks {
    private static let key = "ht.rewardedLevels"

    public static func contains(_ levelId: String) -> Bool { ids.contains(levelId) }

    public static func add(_ levelId: String) { ids.insert(levelId) }

    public static func consume(_ levelId: String) { ids.remove(levelId) }

    private static var ids: Set<String> {
        get { Set(UserDefaults.standard.stringArray(forKey: key) ?? []) }
        set { UserDefaults.standard.set(Array(newValue), forKey: key) }
    }
}
