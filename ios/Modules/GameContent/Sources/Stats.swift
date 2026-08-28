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
    /// Базовый адрес счётчиков. Переопределяется `HTStatsBaseURL` в Info.plist (Debug там
    /// указывает на локальный `wrangler dev`) — тем же способом, что и адрес контента.
    static var baseURL: URL {
        if let s = ProcessInfo.processInfo.environment["HT_STATS_URL"], let u = URL(string: s) { return u }
        if let s = Bundle.main.object(forInfoDictionaryKey: "HTStatsBaseURL") as? String,
           let u = URL(string: s), !s.isEmpty { return u }
        return URL(string: "https://stats.historyteller.app")!
    }

    /// Debug-сборки в счётчики не пишут: иначе своя же отладка выглядит как игроки.
    #if DEBUG
    private static let enabled = false
    #else
    private static let enabled = true
    #endif

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
        var request = URLRequest(url: Stats.baseURL.appendingPathComponent("c"))
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

/// Доли прохождения эпизодов: «этот прошли 68% из тех, кто до него добрался».
///
/// Считает их сервер, сюда приезжают только проценты — абсолютных чисел клиент не видит
/// и показать не может. Эпизоды, по которым выборки мало, сервер просто не присылает,
/// поэтому на пустой статистике карточки молчат сами, без порогов в UI.
@Observable
public final class SolveRates {
    public static let shared = SolveRates()

    private struct Payload: Codable { let v: Int; let p: [String: [String: Int]] }

    private var table: [String: [String: Int]] = [:]
    private let cacheFile: URL

    private init() {
        let base = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
        cacheFile = base.appendingPathComponent("solve-rates.json")
        // С диска — чтобы карта не «доливала» проценты через секунду после открытия
        // и чтобы они были видны офлайн.
        if let data = try? Data(contentsOf: cacheFile),
           let cached = try? JSONDecoder().decode(Payload.self, from: data) {
            table = cached.p
        }
    }

    /// Процент для карточки. `nil` — сервер по этому эпизоду промолчал, показывать нечего.
    public func percent(chapter: String, level: String) -> Int? { table[chapter]?[level] }

    /// Обновить в фоне. Зовём просто на старте: ответ едет с `max-age=600`, поэтому запуски
    /// чаще раза в десять минут разбирает `URLCache` и до сети дело не доходит вовсе.
    /// (Отсюда же и грабли при отладке: пока не истёк кеш, приложение показывает прежние
    /// числа и запроса в логе стенда не видно — надо переставить приложение.)
    public func refresh() {
        URLSession.shared.dataTask(with: Stats.baseURL.appendingPathComponent("p")) { [weak self] data, response, error in
            guard let self, error == nil,
                  let code = (response as? HTTPURLResponse)?.statusCode, (200..<300).contains(code),
                  let data, let fresh = try? JSONDecoder().decode(Payload.self, from: data)
            else { return }
            DispatchQueue.main.async {
                self.table = fresh.p
                try? data.write(to: self.cacheFile, options: .atomic)
            }
        }.resume()
    }
}
