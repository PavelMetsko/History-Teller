import Foundation

/// Анонимная статистика игры для скрытого админ-экрана (сервер `server/stats`, Cloudflare).
/// Игрок — случайный ID установки; имени, почты, рекламного ID и местоположения здесь нет
/// (страну определяет сам Cloudflare по запросу). События копятся и уходят пачкой; без сети
/// очередь ждёт следующей попытки, игре это ничем не мешает.
public final class Telemetry {
    public static let shared = Telemetry()

    static let endpoint = URL(string: "https://stats.historyteller.app/e")!
    private static let iidKey = "ht.telemetry.iid"
    private static let queueKey = "ht.telemetry.queue"
    private static let maxQueue = 200

    private let iid: String
    private let lock = NSLock()
    private var queue: [[String: String]]
    private var sending = false
    private var flushScheduled = false

    private init() {
        let d = UserDefaults.standard
        if let saved = d.string(forKey: Self.iidKey) { iid = saved } else {
            iid = UUID().uuidString
            d.set(iid, forKey: Self.iidKey)
        }
        queue = (d.array(forKey: Self.queueKey) as? [[String: String]]) ?? []
    }

    /// `session` | `level_start` | `level_complete` | `ad_unlock`.
    public func track(_ type: String, level: String? = nil, chapter: String? = nil) {
        var ev = ["type": type]
        if let level { ev["level"] = level }
        if let chapter { ev["chapter"] = chapter }
        lock.lock()
        queue.append(ev)
        if queue.count > Self.maxQueue { queue.removeFirst(queue.count - Self.maxQueue) }
        persist()
        let schedule = !flushScheduled
        flushScheduled = true
        lock.unlock()
        // Небольшая пауза — события одного действия (начал уровень, открыл за ролик) уходят вместе.
        if schedule { DispatchQueue.global(qos: .utility).asyncAfter(deadline: .now() + 2) { self.flush() } }
    }

    private func flush() {
        lock.lock()
        flushScheduled = false
        guard !sending, !queue.isEmpty else { lock.unlock(); return }
        sending = true
        let batch = Array(queue.prefix(50))
        lock.unlock()

        let body: [String: Any] = [
            "iid": iid, "platform": "ios",
            "ver": Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "",
            "lang": L10n.lang, "events": batch,
        ]
        var req = URLRequest(url: Self.endpoint)
        req.httpMethod = "POST"
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.httpBody = try? JSONSerialization.data(withJSONObject: body)
        req.timeoutInterval = 15
        URLSession.shared.dataTask(with: req) { _, response, _ in
            let ok = (response as? HTTPURLResponse).map { (200..<300).contains($0.statusCode) } ?? false
            self.lock.lock()
            if ok { self.queue.removeFirst(min(batch.count, self.queue.count)); self.persist() }
            self.sending = false
            let more = ok && !self.queue.isEmpty
            self.lock.unlock()
            if more { self.flush() }
        }.resume()
    }

    private func persist() { UserDefaults.standard.set(queue, forKey: Self.queueKey) }
}

/// Запрос сводки для скрытого админ-экрана. Пароль сверяется на сервере.
public enum AdminStatsAPI {
    static let url = URL(string: "https://stats.historyteller.app/admin/stats")!

    public enum Failure: Error { case unauthorized, network(String) }

    public static func fetch(password: String) async -> Result<[String: Any], Failure> {
        var req = URLRequest(url: url)
        req.setValue("Bearer \(password)", forHTTPHeaderField: "Authorization")
        req.timeoutInterval = 20
        do {
            let (data, response) = try await URLSession.shared.data(for: req)
            let code = (response as? HTTPURLResponse)?.statusCode ?? 0
            if code == 401 { return .failure(.unauthorized) }
            guard code == 200, let obj = try JSONSerialization.jsonObject(with: data) as? [String: Any]
            else { return .failure(.network("HTTP \(code)")) }
            return .success(obj)
        } catch {
            return .failure(.network(error.localizedDescription))
        }
    }
}
