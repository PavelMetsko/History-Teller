import UIKit
import Observation
import GoogleMobileAds
import GameContent

/// Реклама Google AdMob: rewarded — «ролик за подсказку» и возврат серии, интерстишел — между
/// эпизодами (когда показывать, решает приложение по правилам из манифеста). SDK стартует после
/// формы согласия UMP. Доход с показов уходит в Tenjin.
@Observable
public final class AdService: NSObject {
    public static let shared = AdService()

    /// Блоки History Teller в AdMob; в отладке — тестовые блоки Google (настоящие показы
    /// с устройства разработчика AdMob считает недействительным трафиком).
    #if DEBUG
    private static let rewardedUnitId = "ca-app-pub-3940256099942544/1712485313"
    private static let interstitialUnitId = "ca-app-pub-3940256099942544/4411468910"
    #else
    private static let rewardedUnitId = "ca-app-pub-6335946344432887/7637221863"
    private static let interstitialUnitId = "ca-app-pub-6335946344432887/1188467235"
    #endif

    /// Ролик загружен и его можно показать прямо сейчас.
    public private(set) var isReady = false
    public private(set) var isShowing = false
    /// Секунд до следующего ролика (кулдаун из манифеста). 0 — можно смотреть.
    public private(set) var cooldownLeft = 0

    /// Показывать ли кнопки «за ролик» вообще (ролики не выключены в манифесте).
    public var isEnabled: Bool { ContentSync.shared.rewardedEnabled }
    public var interstitialReady: Bool { interstitial != nil }

    /// Любая полноэкранная реклама закрыта — для паузы между показами (ставит приложение).
    public var onFullscreenShown: (() -> Void)?

    private var started = false
    private var sdkStarted = false
    private var loading = false
    private var loadingInter = false
    private var rewardedAd: RewardedAd?
    private var interstitial: InterstitialAd?
    private var retryAttempt = 0.0
    private var interRetry = 0.0
    private var rewarded = false
    private var completion: ((Bool) -> Void)?
    private var interCompletion: (() -> Void)?
    private var cooldownTimer: Timer?

    private override init() {}

    /// Раз за сессию, из приложения на старте. Само дожидается согласия.
    public func start() {
        guard !started else { return }
        started = true
        ConsentService.shared.onReady { [weak self] in self?.startSDK() }
        // Согласие дали позже, в форме из настроек, — теперь можно грузить.
        ConsentService.shared.onChange { [weak self] in self?.startSDK() }
    }

    /// Показать ролик. `completion(true)` — досмотрел и заслужил награду.
    public func show(completion: @escaping (Bool) -> Void) {
        guard isEnabled, cooldownLeft == 0, let ad = rewardedAd,
              let vc = ConsentService.topViewController() else { return completion(false) }
        rewarded = false
        self.completion = completion
        isShowing = true
        ad.present(from: vc) { [weak self] in self?.rewarded = true }
    }

    /// Показать интерстишел, если он загружен; иначе сразу `completion` — игрок не ждёт рекламу.
    public func showInterstitial(completion: @escaping () -> Void) {
        guard let ad = interstitial, let vc = ConsentService.topViewController() else { return completion() }
        interCompletion = completion
        isShowing = true
        ad.present(from: vc)
    }

    private func startSDK() {
        guard ConsentService.shared.canRequestAds else { return }
        guard !sdkStarted else { load(); loadInterstitial(); return }
        sdkStarted = true
        MobileAds.shared.start { [weak self] _ in self?.load(); self?.loadInterstitial() }
    }

    private func load() {
        guard sdkStarted, !loading, rewardedAd == nil else { return }
        loading = true
        RewardedAd.load(with: Self.rewardedUnitId, request: Request()) { [weak self] ad, error in
            guard let self else { return }
            self.loading = false
            guard let ad else {
                print("Rewarded load error: \(error?.localizedDescription ?? "?")")
                self.isReady = false
                // Экспоненциальная пауза до 64 с: no-fill не должен оставить игрока без роликов.
                self.retryAttempt += 1
                let delay = pow(2.0, min(6.0, self.retryAttempt))
                DispatchQueue.main.asyncAfter(deadline: .now() + delay) { [weak self] in self?.load() }
                return
            }
            self.retryAttempt = 0
            ad.fullScreenContentDelegate = self
            ad.paidEventHandler = { [weak ad] value in
                guard let ad else { return }
                AttributionService.shared.trackAdRevenue(value, unitId: ad.adUnitID, info: ad.responseInfo)
            }
            self.rewardedAd = ad
            self.isReady = true
        }
    }

    private func loadInterstitial() {
        guard sdkStarted, !loadingInter, interstitial == nil else { return }
        loadingInter = true
        InterstitialAd.load(with: Self.interstitialUnitId, request: Request()) { [weak self] ad, error in
            guard let self else { return }
            self.loadingInter = false
            guard let ad else {
                print("Interstitial load error: \(error?.localizedDescription ?? "?")")
                self.interRetry += 1
                let delay = pow(2.0, min(6.0, self.interRetry))
                DispatchQueue.main.asyncAfter(deadline: .now() + delay) { [weak self] in self?.loadInterstitial() }
                return
            }
            self.interRetry = 0
            ad.fullScreenContentDelegate = self
            ad.paidEventHandler = { [weak ad] value in
                guard let ad else { return }
                AttributionService.shared.trackAdRevenue(value, unitId: ad.adUnitID, info: ad.responseInfo)
            }
            self.interstitial = ad
        }
    }

    private func finishShow(_ ad: FullScreenPresentingAd) {
        isShowing = false
        onFullscreenShown?()
        if ad is InterstitialAd {
            interstitial = nil
            let done = interCompletion
            interCompletion = nil
            done?()
            loadInterstitial()
            return
        }
        isReady = false
        rewardedAd = nil
        let done = completion
        completion = nil
        if rewarded { startCooldown() }
        done?(rewarded)
        load()
    }

    private func startCooldown() {
        let total = ContentSync.shared.rewardedCooldown
        guard total > 0 else { return }
        let shownAt = Date()
        cooldownTimer?.invalidate()
        cooldownLeft = total
        cooldownTimer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { [weak self] t in
            guard let self else { return t.invalidate() }
            self.cooldownLeft = max(0, total - Int(Date().timeIntervalSince(shownAt)))
            if self.cooldownLeft == 0 { t.invalidate() }
        }
    }
}

extension AdService: FullScreenContentDelegate {
    public func adDidDismissFullScreenContent(_ ad: FullScreenPresentingAd) { finishShow(ad) }

    public func ad(_ ad: FullScreenPresentingAd, didFailToPresentFullScreenContentWithError error: Error) {
        rewarded = false
        finishShow(ad)
    }
}
