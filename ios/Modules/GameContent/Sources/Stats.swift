import Foundation

/// Счётчики прохождения глав — «играет ли в это кто-нибудь и докуда доходит».
///
/// Наружу уходит только строка-ключ (`done:rome:sabines`). Ни идентификатора установки, ни
/// времени, ни чего-либо ещё о человеке: на сервере копится «сколько раз ключ приходил»,
/// и связать два ключа одного игрока нельзя даже теоретически. Это осознанное ограничение —
/// оно позволяет не менять обещание политики приватности.
///
/// Каждый ключ отправляется максимум один раз за установку, поэтому счётчик читается как
/// «столько установок сюда дошло», а не «столько раз запускали».
public enum Stats {
    /// Debug-сборки в счётчики не пишут: иначе своя же отладка выглядит как игроки.
    #if DEBUG
    private static let enabled = false
    #else
    private static let enabled = true
    #endif

    private static let endpoint = URL(string: "https://stats.historyteller.app/c")!
    private static let sentKey = "ht.stats.sent"
    private static let pendingKey = "ht.stats.pending"

    public static func chapterOpened(_ chapter: String) { send("open:\(chapter)") }

    public static func levelSolved(chapter: String, level: String) { send("done:\(chapter):\(level)") }

    /// Досылает то, что не ушло раньше. Зовётся на старте: эпизод могли пройти в самолёте.
    public static func flushPending() { send(nil) }

    // MARK: - Внутреннее

    /// Кладёт ключ в очередь и пытается отправить всю очередь целиком.
    ///
    /// Ключ переезжает в «отправленные» только после успеха — иначе пройденный офлайн эпизод
    /// пропал бы навсегда, а один запрос в день на пару десятков байт того не стоит.
    private static func send(_ key: String?) {
        guard enabled else { return }
        let defaults = UserDefaults.standard
        var sent = Set(defaults.stringArray(forKey: sentKey) ?? [])
        var pending = Set(defaults.stringArray(forKey: pendingKey) ?? [])

        if let key {
            guard !sent.contains(key) else { return }
            pending.insert(key)
            defaults.set(Array(pending), forKey: pendingKey)
        }
        guard !pending.isEmpty else { return }

        let batch = Array(pending.prefix(16))     // столько же принимает Worker за раз
        var request = URLRequest(url: endpoint)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.timeoutInterval = 10
        request.httpBody = try? JSONSerialization.data(withJSONObject: ["e": batch])

        URLSession.shared.dataTask(with: request) { _, response, error in
            guard error == nil,
                  let code = (response as? HTTPURLResponse)?.statusCode,
                  (200..<300).contains(code) else { return }
            sent.formUnion(batch)
            pending.subtract(batch)
            defaults.set(Array(sent), forKey: sentKey)
            defaults.set(Array(pending), forKey: pendingKey)
        }.resume()
    }
}
