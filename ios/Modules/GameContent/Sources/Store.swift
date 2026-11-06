import Foundation
import StoreKit
import Observation

/// Покупки (StoreKit 2). С 4.0 все главы играются бесплатно с рекламой, а каждая глава по-прежнему
/// продаётся отдельно: купленная глава — без интерстишелов и с безлимитом подсказок. Общей покупки
/// нет; подписка осталась только у тех, кто оформил её раньше, — им без рекламы везде.
/// Права проверяются через `Transaction.currentEntitlements`, поэтому переносятся между устройствами.
@Observable
public final class Store {
    public static let shared = Store()

    /// Поглавные непотребляемые продукты: `com.decima.historyteller.chapter.<epoch>`.
    public static let chapterPrefix = "com.decima.historyteller.chapter."
    /// Платные главы берём из манифеста: новая глава, выложенная в облако, сама попадёт в запрос
    /// продуктов — достаточно завести IAP в App Store Connect, релиз для этого не нужен.
    public static var paidEpochs: [String] {
        let fromManifest = ContentSync.shared.availableChapters.filter { !$0.free }.map(\.id)
        return fromManifest.isEmpty ? ["tudor", "revolution", "empire", "borgia", "byzantium"] : fromManifest
    }
    public static func chapterProductID(_ epoch: String) -> String { chapterPrefix + epoch }

    /// Подписка на всё (группа `all_access`) — больше не продаётся, но действующая работает.
    public static let monthlyID = "com.decima.historyteller.sub.monthly"
    public static let yearlyID  = "com.decima.historyteller.sub.yearly"
    public static var subscriptionIDs: [String] { [monthlyID, yearlyID] }

    public private(set) var products: [String: Product] = [:]
    public private(set) var unlockedEpochs: Set<String> = []
    public private(set) var subscribed = false
    public private(set) var purchasing = false

    private var updatesTask: Task<Void, Never>?

    /// Новая подтверждённая покупка (не восстановление) — для атрибуции (Tenjin). Ставит приложение.
    /// Третий параметр — подписанный JWS транзакции (чек StoreKit 2 для серверной проверки).
    public static var onPurchase: ((Transaction, Product, String) -> Void)?

    private init() {
        updatesTask = observeTransactionUpdates()
        Task { await loadProducts(); await refreshEntitlements() }
    }

    /// Глава без рекламы и с безлимитом подсказок: куплена именно она (или действует старая подписка).
    public func adsFree(_ epoch: String) -> Bool { subscribed || unlockedEpochs.contains(epoch) }

    /// Только для скриншота ревью (env HT_DEMO_PRICES=1): подставляет демо-цены, т.к. в симуляторе
    /// StoreKit-конфиг не применяется. В проде флага нет — работают реальные цены.
    private var demoPrices: Bool { ProcessInfo.processInfo.environment["HT_DEMO_PRICES"] == "1" }
    public func chapterPrice(_ epoch: String) -> String {
        if demoPrices { return "$2.99" }
        return products[Self.chapterProductID(epoch)]?.displayPrice ?? ""
    }

    public func loadProducts() async {
        let ids = Self.paidEpochs.map { Self.chapterProductID($0) }
        let list = (try? await Product.products(for: ids)) ?? []
        var map: [String: Product] = [:]
        for p in list { map[p.id] = p }
        let final = map
        await MainActor.run { self.products = final }
    }

    public func refreshEntitlements() async {
        var epochs: Set<String> = []
        var sub = false
        for await result in Transaction.currentEntitlements {
            guard case .verified(let t) = result, t.revocationDate == nil else { continue }
            if t.productID.hasPrefix(Self.chapterPrefix) {
                epochs.insert(String(t.productID.dropFirst(Self.chapterPrefix.count)))
            } else if Self.subscriptionIDs.contains(t.productID) {
                sub = true
            }
        }
        let fe = epochs, fs = sub
        await MainActor.run { self.unlockedEpochs = fe; self.subscribed = fs }
    }

    /// Купить продукт по id (поглавный или подписку). UI обновится через entitlements.
    @discardableResult
    public func purchase(_ productID: String) async -> Bool {
        guard let product = products[productID] else { return false }
        await MainActor.run { self.purchasing = true }
        defer { Task { await MainActor.run { self.purchasing = false } } }
        do {
            switch try await product.purchase() {
            case .success(let verification):
                if case .verified(let t) = verification {
                    Self.onPurchase?(t, product, verification.jwsRepresentation)
                    await t.finish()
                    await refreshEntitlements()
                    return true
                }
            default: break
            }
        } catch { }
        return false
    }

    @discardableResult
    public func purchaseChapter(_ epoch: String) async -> Bool { await purchase(Self.chapterProductID(epoch)) }

    /// Восстановить покупки (требование Apple — отдельная кнопка).
    public func restore() async {
        try? await AppStore.sync()
        await refreshEntitlements()
    }

    private func observeTransactionUpdates() -> Task<Void, Never> {
        Task.detached { [weak self] in
            for await result in Transaction.updates {
                if case .verified(let t) = result {
                    await t.finish()
                    await self?.refreshEntitlements()
                }
            }
        }
    }
}
