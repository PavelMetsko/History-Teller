import UIKit
import Observation
import GoogleMobileAds
import GameContent

/// Rewarded-реклама через Google AdMob: «посмотри ролик — открой один уровень платной главы».
/// Интерстишелов нет. SDK стартует после формы согласия UMP, выключается флагом `ads.rewarded`
/// в облачном манифесте. Доход с показов уходит в Tenjin.
@Observable
public final class AdService: NSObject {
    public static let shared = AdService()

    /// Rewarded-блок History Teller в AdMob; в отладке — тестовый блок Google (настоящие показы
    /// с устройства разработчика AdMob считает недействительным трафиком).
    #if DEBUG
    private static let rewardedUnitId = "ca-app-pub-3940256099942544/1712485313"
    #else
    private static let rewardedUnitId = "ca-app-pub-6335946344432887/7637221863"
    #endif

    /// Ролик загружен и его можно показать прямо сейчас.
    public private(set) var isReady = false
    public private(set) var isShowing = false
    /// Секунд до следующего ролика (кулдаун из манифеста). 0 — можно смотреть.
    public private(set) var cooldownLeft = 0

    /// Показывать ли кнопку «за ролик» вообще (реклама не выключена в манифесте).
    public var isEnabled: Bool { ContentSync.shared.rewardedEnabled }

    private var started = false
    private var sdkStarted = false
    private var loading = false
    private var rewardedAd: RewardedAd?
    private var retryAttempt = 0.0
    private var rewarded = false
    private var completion: ((Bool) -> Void)?
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

    private func startSDK() {
        guard ConsentService.shared.canRequestAds else { return }
        guard !sdkStarted else { return load() }
        sdkStarted = true
        MobileAds.shared.start { [weak self] _ in self?.load() }
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
                AttributionService.shared.trackAdRevenue(value, ad: ad)
            }
            self.rewardedAd = ad
            self.isReady = true
        }
    }

    private func finishShow() {
        isShowing = false
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
    public func adDidDismissFullScreenContent(_ ad: FullScreenPresentingAd) { finishShow() }

    public func ad(_ ad: FullScreenPresentingAd, didFailToPresentFullScreenContentWithError error: Error) {
        rewarded = false
        finishShow()
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
