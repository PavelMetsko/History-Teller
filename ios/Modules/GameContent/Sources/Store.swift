import Foundation
import StoreKit
import Observation

/// Покупки (StoreKit 2). Модель: первая глава (Рим) бесплатна; остальные — либо разовая
/// **поглавная** покупка (у каждой своя цена), либо **подписка** на весь контент (текущий и будущий).
/// Права проверяются через `Transaction.currentEntitlements`, поэтому переносятся между устройствами.
@Observable
public final class Store {
    public static let shared = Store()

    /// Поглавные непотребляемые продукты: `com.decima.historyteller.chapter.<epoch>`.
    public static let chapterPrefix = "com.decima.historyteller.chapter."
    public static let paidEpochs = ["tudor", "revolution", "empire", "borgia", "byzantium"]
    public static func chapterProductID(_ epoch: String) -> String { chapterPrefix + epoch }

    /// Подписка на всё (группа `all_access`). Месяц + год.
    public static let monthlyID = "com.decima.historyteller.sub.monthly"
    public static let yearlyID  = "com.decima.historyteller.sub.yearly"
    public static var subscriptionIDs: [String] { [monthlyID, yearlyID] }

    public private(set) var products: [String: Product] = [:]
    public private(set) var unlockedEpochs: Set<String> = []
    public private(set) var subscribed = false
    public private(set) var purchasing = false

    private var updatesTask: Task<Void, Never>?

    private init() {
        updatesTask = observeTransactionUpdates()
        Task { await loadProducts(); await refreshEntitlements() }
    }

    /// Открыта ли глава: Рим бесплатен, либо активна подписка, либо куплена именно эта глава.
    public func isUnlocked(_ epoch: String) -> Bool {
        epoch == "rome" || subscribed || unlockedEpochs.contains(epoch)
    }

    public func chapterPrice(_ epoch: String) -> String { products[Self.chapterProductID(epoch)]?.displayPrice ?? "" }
    public var monthlyPrice: String { products[Self.monthlyID]?.displayPrice ?? "" }
    public var yearlyPrice: String { products[Self.yearlyID]?.displayPrice ?? "" }

    public func loadProducts() async {
        let ids = Self.paidEpochs.map { Self.chapterProductID($0) } + Self.subscriptionIDs
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
