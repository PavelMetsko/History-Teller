import Foundation
import StoreKit
import Observation

/// Покупки (StoreKit 2). Фримиум: первая глава бесплатна, разовая непотребляемая покупка
/// `unlockall` открывает все остальные главы (и будущие). Права проверяются через
/// `Transaction.currentEntitlements`, так что покупка переносится между устройствами.
@Observable
public final class Store {
    public static let shared = Store()

    /// ID непотребляемой покупки. Должен совпадать с App Store Connect и Store.storekit.
    public static let unlockAllID = "com.decima.historyteller.unlockall"

    public private(set) var product: Product?
    public private(set) var isUnlocked = false
    public private(set) var purchasing = false

    private var updatesTask: Task<Void, Never>?

    private init() {
        updatesTask = observeTransactionUpdates()
        Task { await loadProducts(); await refreshEntitlements() }
    }

    /// Цена для кнопки («$4.99»). Пусто, пока продукт не загружен (нет сети / конфигурации).
    public var priceText: String { product?.displayPrice ?? "" }

    public func loadProducts() async {
        product = try? await Product.products(for: [Self.unlockAllID]).first
    }

    public func refreshEntitlements() async {
        var unlocked = false
        for await result in Transaction.currentEntitlements {
            if case .verified(let t) = result,
               t.productID == Self.unlockAllID, t.revocationDate == nil {
                unlocked = true
            }
        }
        let final = unlocked
        await MainActor.run { self.isUnlocked = final }
    }

    /// Купить. Возвращает true при успехе. UI сам обновится через `isUnlocked`.
    @discardableResult
    public func purchase() async -> Bool {
        guard let product else { return false }
        await MainActor.run { self.purchasing = true }
        defer { Task { await MainActor.run { self.purchasing = false } } }
        do {
            switch try await product.purchase() {
            case .success(let verification):
                if case .verified(let t) = verification {
                    await t.finish()
                    await MainActor.run { self.isUnlocked = true }
                    return true
                }
            default: break
            }
        } catch { }
        return false
    }

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
