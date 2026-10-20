import SwiftUI
import Ads

@main
struct HistoryTellerApp: App {
    init() {
        // Подписаться на покупки и дождаться согласия — сам SDK стартует после окна согласия/ATT.
        AttributionService.shared.start()
        AdService.shared.start()
    }

    var body: some Scene {
        WindowGroup {
            RootView()
        }
    }
}
