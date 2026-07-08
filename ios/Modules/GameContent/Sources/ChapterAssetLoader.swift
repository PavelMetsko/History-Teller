import Foundation

/// Загрузка арта главы по требованию через On-Demand Resources.
/// App Store хостит помеченные ассеты на своём CDN — свой сервер не нужен.
///
/// Модель: каждая глава — ODR-тег `chapter_<epoch>` на её imageset'ах (задаётся в Xcode).
/// Глава Rome входит в установочный бандл (Initial install tags) → всегда `ready`.
/// Остальные качаются при первом открытии; уже скачанные держатся живыми, пока идёт сессия.
///
/// Dev-фолбэк: пока ODR-теги не настроены (или отладочный билд, где весь арт в бандле),
/// `beginAccessingResources` завершится ошибкой «тег не найден» — но арт всё равно доступен
/// из основного каталога, поэтому мы это проглатываем и просто показываем экран загрузки
/// минимальное время (чтобы анимация сборки и подсказки успели проиграться).
@MainActor
public final class ChapterAssetLoader: ObservableObject {
    public enum LoadState: Equatable { case ready, downloading, failed(String) }

    @Published public private(set) var state: LoadState = .ready
    @Published public private(set) var progress: Double = 0

    /// Главы, входящие в установочный бандл (не качаются).
    public static let bundledEpochs: Set<String> = ["rome"]

    /// Минимальная длительность показа экрана загрузки (сек) — чтобы UX был виден
    /// даже при мгновенной доступности ассетов (в dev-сборке арт встроен → «скачивание» мгновенно).
    /// Тюнинг: для прода вернуть ~2.6; сейчас 7 — чтобы разглядеть анимацию и подсказки.
    public var minimumShowSeconds: TimeInterval = 7.0

    #if os(iOS)
    /// Удерживаемые запросы: пока глава используется, её ассеты не выгружаются.
    private static var held: [String: NSBundleResourceRequest] = [:]
    #endif

    public init() {}

    public func isReady(_ epoch: String) -> Bool {
        if Self.bundledEpochs.contains(epoch) { return true }
        #if os(iOS)
        return Self.held[epoch] != nil
        #else
        return false
        #endif
    }

    /// Освобождает ассеты главы (например, при возврате в меню), возвращая место системе.
    public static func release(_ epoch: String) {
        #if os(iOS)
        held[epoch]?.endAccessingResources()
        held[epoch] = nil
        #endif
    }

    /// Гарантирует, что арт главы доступен. Прогресс идёт в `progress`, финал — `state == .ready`.
    public func ensure(_ epoch: String) async {
        if isReady(epoch) { progress = 1; state = .ready; return }

        state = .downloading
        progress = 0
        let started = Date()

        #if os(iOS)
        let request = NSBundleResourceRequest(tags: ["chapter_\(epoch)"], bundle: .gameContent)
        request.loadingPriority = NSBundleResourceRequestLoadingPriorityUrgent

        let observation = request.progress.observe(\.fractionCompleted) { [weak self] prog, _ in
            let value = prog.fractionCompleted
            Task { @MainActor in
                guard let self else { return }
                // Держим максимум 99% до самого конца — 100% ставим только перед скрытием.
                let capped = min(0.99, value)
                if capped > self.progress { self.progress = capped }
            }
        }
        do {
            try await withCheckedThrowingContinuation { (cont: CheckedContinuation<Void, Error>) in
                request.beginAccessingResources { error in
                    if let error { cont.resume(throwing: error) } else { cont.resume() }
                }
            }
            Self.held[epoch] = request  // ODR-арт скачан и удерживается
        } catch {
            // ODR-тег не настроен или арт уже в установочном бандле — не ошибка для пользователя.
        }
        observation.invalidate()
        #endif

        // Догоняем прогресс до конца с учётом минимального времени показа.
        let elapsed = Date().timeIntervalSince(started)
        if elapsed < minimumShowSeconds {
            let remaining = minimumShowSeconds - elapsed
            let steps = 24
            for step in 1...steps {
                try? await Task.sleep(nanoseconds: UInt64(remaining / Double(steps) * 1_000_000_000))
                let target = min(0.99, Double(step) / Double(steps))  // до конца таймера — не выше 99%
                if target > progress { progress = target }
            }
        }

        progress = 1   // таймер вышел — добиваем 100%, экран сейчас скроется
        state = .ready
    }
}
