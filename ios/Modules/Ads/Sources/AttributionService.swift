import UIKit
import StoreKit
import TenjinSDK
import GameContent

/// Атрибуция установок и покупок через Tenjin (MMP для закупки в AppLovin).
/// Стартует только после окна согласия и ATT: в `connect()` уходит IDFA, если игрок разрешил.
/// Отказ от рекламных данных (окно согласия/настройки) → `optOut`: Tenjin ничего не отправляет.
public final class AttributionService {
    public static let shared = AttributionService()

    private static let sdkKey = "NPIA8DFXOC5W1JPGKYDHEMTMKJXAUBG3"
    private var started = false
    private var connected = false

    private init() {}

    /// Раз за сессию, из приложения на старте. Само дожидается согласия.
    public func start() {
        guard !started else { return }
        started = true
        Store.onPurchase = { [weak self] transaction, product, jws in self?.trackPurchase(transaction, product, jws) }
        ConsentService.shared.onReady { [weak self] in self?.connect() }
        // Сессии считаются по connect(): повторяем при каждом возвращении в приложение.
        NotificationCenter.default.addObserver(forName: UIApplication.didBecomeActiveNotification,
                                               object: nil, queue: .main) { [weak self] _ in
            guard let self, self.connected else { return }
            self.applyConsent()
            TenjinSDK.connect()
        }
    }

    private func connect() {
        TenjinSDK.getInstance(Self.sdkKey)
        applyConsent()
        TenjinSDK.connect()
        connected = true
    }

    private func applyConsent() {
        if ConsentService.shared.doNotSell { TenjinSDK.optOut() } else { TenjinSDK.optIn() }
    }

    /// Глава — разовая покупка (`transaction`), подписка — первое оформление (`purchasesManager`).
    /// Продления Tenjin получает с сервера App Store (ключ App Store Connect в кабинете Tenjin).
    private func trackPurchase(_ t: Transaction, _ product: Product, _ jws: String) {
        guard connected else { return }
        if t.productType == .autoRenewable {
            TenjinSDK.purchasesManager().subscription(t)
        } else {
            TenjinSDK.transaction(
                withProductName: t.productID,
                andCurrencyCode: product.priceFormatStyle.currencyCode,
                andQuantity: t.purchasedQuantity,
                andUnitPrice: NSDecimalNumber(decimal: product.price),
                andTransactionId: String(t.id),
                andBase64Receipt: jws
            )
        }
    }
}
