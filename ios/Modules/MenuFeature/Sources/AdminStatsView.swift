import SwiftUI
import Charts
import DesignSystem
import GameContent

/// Доступ к скрытому экрану статистики: пароль вводится один раз, дальше устройство помнит его.
/// Проверяет пароль сервер (`server/stats`), в приложении его нет.
enum AdminAccess {
    private static let key = "ht.admin.password"
    static var savedPassword: String? { UserDefaults.standard.string(forKey: key) }
    static func save(_ password: String) { UserDefaults.standard.set(password, forKey: key) }
    static func forget() { UserDefaults.standard.removeObject(forKey: key) }
}

/// Скрытый экран: статистика всех игроков обеих платформ — для себя, поэтому по-русски.
/// Четыре вкладки: обзор, главы (с воронкой по эпизодам), страны, живая лента.
struct AdminStatsView: View {
    let password: String
    let onClose: () -> Void

    @State private var stats: AdminStats?
    @State private var error: String?
    @State private var loading = false

    var body: some View {
        TabView {
            tab("Обзор", "chart.bar.xaxis") { OverviewTab(s: $0) }
            tab("Главы", "books.vertical") { ChaptersTab(s: $0) }
            tab("Возвраты", "arrow.uturn.backward.circle") { RetentionTab(s: $0) }
            tab("Страны", "globe.europe.africa") { CountriesTab(s: $0) }
            tab("Лента", "list.bullet.rectangle") { FeedTab(s: $0) }
        }
        .environment(\.locale, Locale(identifier: "ru"))
        .task { await load() }
    }

    private func tab<C: View>(_ title: String, _ icon: String,
                              @ViewBuilder _ content: @escaping (AdminStats) -> C) -> some View {
        NavigationStack {
            Group {
                if let stats { content(stats) }
                else if let error { ContentUnavailableView("Не загрузилось", systemImage: "wifi.exclamationmark",
                                                           description: Text(error)) }
                else { ProgressView("Загружаю…") }
            }
            .navigationTitle(title)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) { Button("Закрыть", action: onClose) }
                ToolbarItem(placement: .primaryAction) {
                    if loading { ProgressView() }
                    else { Button { Task { await load() } } label: { Image(systemName: "arrow.clockwise") } }
                }
            }
            .refreshable { await load() }
        }
        .tabItem { Label(title, systemImage: icon) }
    }

    private func load() async {
        loading = true
        defer { loading = false }
        switch await AdminStatsAPI.fetch(password: password) {
        case .success(let d): stats = AdminStats(d); error = nil
        case .failure(.unauthorized): error = "Неверный пароль"; AdminAccess.forget()
        case .failure(.network(let m)): error = m
        }
    }
}

// MARK: - Модель

/// Ответ сервера, разобранный в понятные структуры. Порядок глав и эпизодов — из манифеста
/// контента, как в игре: сервер знает только id.
struct AdminStats {
    struct Players { var total = 0, ios = 0, android = 0, new1 = 0, new7 = 0, active1 = 0, active7 = 0, active30 = 0 }
    struct Level: Identifiable { let id: String; let number: Int; let started: Int; let completed: Int }
    struct Chapter: Identifiable {
        let id: String
        let number: Int
        let icon: String
        let players: Int        // начали хоть один эпизод
        let finished: Int       // прошли последний эпизод главы
        let completions: Int
        let adUnlocks: Int
        let levels: [Level]
    }
    struct Count: Identifiable { var id: String { key }; let key: String; let n: Int }
    /// Игроки, пришедшие в один день, и сколько из них заходило ровно через N дней.
    struct Cohort: Identifiable {
        var id: Int { day }
        let day: Int
        let n: Int
        let back: Int
        let returned: [Int: Int]
        var date: Date { Date(timeIntervalSince1970: Double(day) * 86_400) }
    }
    struct Day: Identifiable { var id: Date { date }; let date: Date; let active: Int; let new: Int }
    struct Event: Identifiable {
        let id: Int
        let date: Date
        let type: String
        let level: String?
        let chapter: String?
        let platform: String?
        let country: String?
    }

    var generatedAt = Date()
    var players = Players()
    var chapters: [Chapter] = []
    var countries: [Count] = []
    var langs: [Count] = []
    var versions: [Count] = []
    var days: [Day] = []
    var recent: [Event] = []
    var cohorts: [Cohort] = []
    /// Сколько разных дней игрок заходил → сколько таких игроков.
    var activeDays: [(days: Int, n: Int)] = []
    /// Реклама и мета (4.0): тип события → всего, игроков, за 7 дней.
    var eventTypes: [(type: String, n: Int, players: Int, n7: Int)] = []
    var today: Int { Int(generatedAt.timeIntervalSince1970 / 86_400) }
    var hasRetention: Bool { !cohorts.isEmpty }

    /// Доля вернувшихся на день N — только по когортам, у которых этот день уже целиком прошёл.
    func retention(_ k: Int) -> (back: Int, of: Int) {
        cohorts.filter { $0.day + k < today }.reduce((0, 0)) { ($0.0 + ($1.returned[k] ?? 0), $0.1 + $1.n) }
    }
    /// Пусто, пока сервер не обновлён до версии с разбивкой по странам.
    var chapterCountries: [String: [Count]] = [:]
    var levelCountries: [String: [(country: String, started: Int, completed: Int)]] = [:]
    var hasCountryBreakdown: Bool { !chapterCountries.isEmpty }
    static let retentionDays = [1, 3, 7, 14, 30]

    init(_ d: [String: Any]) {
        func rows(_ k: String) -> [[String: Any]] { d[k] as? [[String: Any]] ?? [] }
        func counts(_ k: String) -> [Count] { rows(k).map { Count(key: str($0["k"]) ?? "?", n: num($0["n"])) } }

        generatedAt = Date(timeIntervalSince1970: Double(num(d["generatedAt"])) / 1000)
        let p = d["players"] as? [String: Any] ?? [:]
        players = Players(total: num(p["total"]), ios: num(p["ios"]), android: num(p["android"]),
                          new1: num(p["new1"]), new7: num(p["new7"]),
                          active1: num(p["active1"]), active7: num(p["active7"]), active30: num(p["active30"]))
        countries = counts("countries")
        langs = counts("langs")
        versions = counts("versions")

        var levelRows: [String: (Int, Int)] = [:]
        for r in rows("levels") { if let id = str(r["level"]) { levelRows[id] = (num(r["started"]), num(r["completed"])) } }
        let chapterRows = Dictionary(rows("chapters").compactMap { r in str(r["chapter"]).map { ($0, r) } },
                                     uniquingKeysWith: { a, _ in a })
        let manifest = ContentSync.shared.availableChapters
        let ids = manifest.map(\.id) + chapterRows.keys.filter { id in !manifest.contains { $0.id == id } }.sorted()
        chapters = ids.enumerated().map { i, id in
            let m = manifest.first { $0.id == id }
            let r = chapterRows[id] ?? [:]
            let levels = (m?.levels ?? []).enumerated().map { j, lid in
                Level(id: lid, number: j + 1, started: levelRows[lid]?.0 ?? 0, completed: levelRows[lid]?.1 ?? 0)
            }
            return Chapter(id: id, number: m?.number ?? 100 + i, icon: m?.icon ?? "book.closed",
                           players: num(r["players"]), finished: levels.last?.completed ?? 0,
                           completions: num(r["completions"]), adUnlocks: num(r["ad_unlocks"]), levels: levels)
        }

        let day = 86_400.0
        let active = Dictionary(rows("daily").map { (num($0["d"]), num($0["n"])) }, uniquingKeysWith: +)
        let fresh = Dictionary(rows("dailyNew").map { (num($0["d"]), num($0["n"])) }, uniquingKeysWith: +)
        if !active.isEmpty || !fresh.isEmpty {
            let today = Int(generatedAt.timeIntervalSince1970 / day)
            days = (today - 29...today).map {
                Day(date: Date(timeIntervalSince1970: Double($0) * day), active: active[$0] ?? 0, new: fresh[$0] ?? 0)
            }
        }

        recent = rows("recent").enumerated().map { i, r in
            Event(id: i, date: Date(timeIntervalSince1970: Double(num(r["ts"])) / 1000), type: str(r["type"]) ?? "",
                  level: str(r["level"]), chapter: str(r["chapter"]), platform: str(r["platform"]), country: str(r["country"]))
        }
        cohorts = rows("cohorts").map { r in
            Cohort(day: num(r["c"]), n: num(r["n"]), back: num(r["back"]),
                   returned: Dictionary(uniqueKeysWithValues: AdminStats.retentionDays.map { ($0, num(r["d\($0)"])) }))
        }
        activeDays = rows("activeDays").map { (num($0["days"]), num($0["n"])) }
        eventTypes = rows("eventTypes").map { (str($0["type"]) ?? "?", num($0["n"]), num($0["players"]), num($0["n7"])) }
        for r in rows("chapterCountries") {
            guard let ch = str(r["chapter"]) else { continue }
            chapterCountries[ch, default: []].append(Count(key: str(r["k"]) ?? "?", n: num(r["n"])))
        }
        for r in rows("levelCountries") {
            guard let lv = str(r["level"]) else { continue }
            levelCountries[lv, default: []].append((str(r["k"]) ?? "?", num(r["started"]), num(r["completed"])))
        }
    }
}

private func num(_ any: Any?) -> Int { (any as? NSNumber)?.intValue ?? 0 }
private func str(_ any: Any?) -> String? { any as? String }

// MARK: - Подписи

private enum Names {
    static func chapter(_ id: String) -> String { L10n.opt("chapter.\(id).title") ?? id }
    static func level(_ id: String) -> String { L10n.opt("level.\(id).title") ?? id }

    static func country(_ code: String) -> String {
        guard code.count == 2, code != "XX", code != "T1" else { return "Неизвестно" }
        return Locale(identifier: "ru").localizedString(forRegionCode: code) ?? code
    }
    static func flag(_ code: String) -> String {
        guard code.count == 2, code.allSatisfy(\.isLetter) else { return "🏳️" }
        return code.uppercased().unicodeScalars
            .compactMap { UnicodeScalar(127397 + $0.value) }.map(String.init).joined()
    }
    static func lang(_ code: String) -> String {
        Locale(identifier: "ru").localizedString(forLanguageCode: code)?.capitalized ?? code
    }

    /// 1 игрок, 2 игрока, 5 игроков.
    static func players(_ n: Int) -> String { "\(n) " + plural(n, "игрок", "игрока", "игроков") }
    static func times(_ n: Int) -> String { "\(n) " + plural(n, "раз", "раза", "раз") }
    static func plural(_ n: Int, _ one: String, _ few: String, _ many: String) -> String {
        let a = n % 100, b = n % 10
        if (11...14).contains(a) { return many }
        if b == 1 { return one }
        if (2...4).contains(b) { return few }
        return many
    }
    static func percent(_ part: Int, of whole: Int) -> String {
        whole > 0 ? "\(Int((Double(part) / Double(whole) * 100).rounded()))%" : "—"
    }
}

// MARK: - Общие кирпичики

private struct StatTile: View {
    let value: Int
    let title: String
    var icon: String? = nil
    var tint: Color = .accentColor

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            if let icon { Image(systemName: icon).font(.subheadline).foregroundStyle(tint) }
            Text("\(value)").font(.title.bold()).monospacedDigit()
            Text(title).font(.caption).foregroundStyle(.secondary).lineLimit(2, reservesSpace: true)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .background(.background.secondary, in: RoundedRectangle(cornerRadius: 14))
    }
}

/// Полоска «сколько из скольки» — читается быстрее цифр.
private struct ShareBar: View {
    let value: Int
    let total: Int
    var tint: Color = .accentColor

    var body: some View {
        GeometryReader { g in
            ZStack(alignment: .leading) {
                Capsule().fill(tint.opacity(0.15))
                Capsule().fill(tint)
                    .frame(width: total > 0 ? max(4, g.size.width * CGFloat(value) / CGFloat(total)) : 0)
            }
        }
        .frame(height: 8)
    }
}

private struct CountryRow: View {
    let code: String
    let n: Int
    let total: Int

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                Text(Names.flag(code))
                Text(Names.country(code)).lineLimit(1)
                Spacer()
                Text("\(n)").monospacedDigit().bold()
                Text(Names.percent(n, of: total)).monospacedDigit().foregroundStyle(.secondary)
                    .frame(width: 44, alignment: .trailing)
            }
            ShareBar(value: n, total: total, tint: .teal)
        }
        .padding(.vertical, 2)
    }
}

private struct Updated: View {
    let date: Date
    var body: some View {
        Text("Обновлено \(date.formatted(.relative(presentation: .named)))")
            .font(.footnote).foregroundStyle(.secondary).frame(maxWidth: .infinity)
    }
}

// MARK: - Обзор

private struct OverviewTab: View {
    let s: AdminStats

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                hero
                tiles
                if !s.days.isEmpty { chart }
                if !s.eventTypes.isEmpty { monetization }
                topChapters
                topCountries
                Updated(date: s.generatedAt)
            }
            .padding()
        }
    }

    private var hero: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Всего игроков").font(.subheadline).foregroundStyle(.secondary)
            Text("\(s.players.total)").font(.system(size: 52, weight: .bold, design: .rounded)).monospacedDigit()
            HStack(spacing: 16) {
                Label("iPhone \(s.players.ios)", systemImage: "apple.logo")
                Label("Android \(s.players.android)", systemImage: "smartphone")
            }
            .font(.subheadline)
            ShareBar(value: s.players.ios, total: s.players.total, tint: .blue)
                .background(Capsule().fill(.green.opacity(0.6)))
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(.background.secondary, in: RoundedRectangle(cornerRadius: 18))
    }

    private var tiles: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Новые игроки").font(.headline)
            HStack {
                StatTile(value: s.players.new1, title: "за сутки", icon: "person.badge.plus", tint: .green)
                StatTile(value: s.players.new7, title: "за неделю", icon: "person.2.badge.plus", tint: .green)
            }
            Text("Заходили в игру").font(.headline).padding(.top, 6)
            HStack {
                StatTile(value: s.players.active1, title: "за сутки", icon: "flame", tint: .orange)
                StatTile(value: s.players.active7, title: "за неделю", icon: "calendar", tint: .orange)
                StatTile(value: s.players.active30, title: "за месяц", icon: "calendar.badge.clock", tint: .orange)
            }
        }
    }

    private var chart: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Последние 30 дней").font(.headline)
            HStack(spacing: 14) {
                Label("играли", systemImage: "circle.fill").foregroundStyle(.orange)
                Label("новые", systemImage: "circle.fill").foregroundStyle(.green)
            }
            .font(.caption)
            Chart(s.days) { d in
                BarMark(x: .value("День", d.date, unit: .day), y: .value("Играли", d.active))
                    .foregroundStyle(.orange.opacity(0.35))
                BarMark(x: .value("День", d.date, unit: .day), y: .value("Новые", d.new))
                    .foregroundStyle(.green)
            }
            .chartXAxis { AxisMarks(values: .stride(by: .day, count: 7)) { _ in
                AxisGridLine(); AxisValueLabel(format: .dateTime.day().month(.abbreviated))
            } }
            .frame(height: 180)
        }
        .padding()
        .background(.background.secondary, in: RoundedRectangle(cornerRadius: 18))
    }

    /// Человеческие подписи событий рекламы и меты.
    private static let eventNames: [String: (String, String)] = [
        "inter_show": ("Реклама между эпизодами", "rectangle.on.rectangle"),
        "hint_ad": ("Ролик за подсказку", "play.rectangle.fill"),
        "hint_use": ("Подсказка из запаса", "lightbulb.fill"),
        "ad_unlock": ("Эпизод за ролик (до 4.0)", "lock.open.fill"),
        "gift_claim": ("Забрали подарок дня", "gift.fill"),
        "daily_open": ("Открыли эпизод дня", "calendar"),
        "daily_done": ("Решили эпизод дня", "calendar.badge.checkmark"),
        "streak_restore": ("Вернули серию", "flame.fill"),
        "rank_up": ("Новое звание", "rosette"),
        "premium_open": ("Открыли «Без рекламы»", "crown"),
        "purchase": ("Покупки", "creditcard.fill"),
    ]

    private var monetization: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Реклама и мета").font(.headline)
            ForEach(s.eventTypes, id: \.type) { e in
                let name = Self.eventNames[e.type] ?? (e.type, "circle")
                HStack {
                    Image(systemName: name.1).foregroundStyle(.tint).frame(width: 22)
                    Text(name.0).lineLimit(1)
                    Spacer()
                    VStack(alignment: .trailing, spacing: 0) {
                        Text("\(e.n)").monospacedDigit().bold()
                        Text("\(Names.players(e.players)) · 7 дн: \(e.n7)").font(.caption2).foregroundStyle(.secondary)
                    }
                }
            }
        }
        .padding()
        .background(.background.secondary, in: RoundedRectangle(cornerRadius: 18))
    }

    private var topChapters: some View {
        let top = s.chapters.filter { $0.players > 0 }.sorted { $0.players > $1.players }.prefix(5)
        return VStack(alignment: .leading, spacing: 10) {
            Text("Самые популярные главы").font(.headline)
            if top.isEmpty { Text("Пока никто не играл").foregroundStyle(.secondary) }
            ForEach(Array(top)) { ch in
                VStack(alignment: .leading, spacing: 4) {
                    HStack {
                        Image(systemName: ch.icon).foregroundStyle(.tint).frame(width: 22)
                        Text(Names.chapter(ch.id)).lineLimit(1)
                        Spacer()
                        Text(Names.players(ch.players)).monospacedDigit().foregroundStyle(.secondary)
                    }
                    ShareBar(value: ch.players, total: top.first?.players ?? 1)
                }
            }
        }
    }

    private var topCountries: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Откуда игроки").font(.headline)
            ForEach(s.countries.prefix(5)) { c in CountryRow(code: c.key, n: c.n, total: s.players.total) }
        }
    }
}

// MARK: - Возвраты

private struct RetentionTab: View {
    let s: AdminStats

    var body: some View {
        if !s.hasRetention {
            ContentUnavailableView("Нужно обновить сервер", systemImage: "arrow.uturn.backward.circle",
                                   description: Text("Возвраты появятся после деплоя сервера статистики."))
        } else {
            List {
                Section {
                    summary
                } footer: {
                    Text("Из тех, кто впервые открыл игру за последние 60 дней. День считается по UTC; учитываются только дни, которые уже наступили.")
                }
                Section("Сколько дней игроки заходили") { frequency }
                Section {
                    cohortTable
                } header: {
                    Text("По дням прихода")
                } footer: {
                    Text("Сколько процентов игроков, пришедших в этот день, открыли игру через 1, 3, 7, 14 и 30 дней.")
                }
                Updated(date: s.generatedAt).listRowBackground(Color.clear)
            }
        }
    }

    private var summary: some View {
        VStack(alignment: .leading, spacing: 12) {
            row("На следующий день", s.retention(1), tint: .green)
            row("Через 3 дня", s.retention(3), tint: .teal)
            row("Через неделю", s.retention(7), tint: .blue)
            row("Через месяц", s.retention(30), tint: .purple)
            let n = s.cohorts.reduce(0) { $0 + $1.n }, back = s.cohorts.reduce(0) { $0 + $1.back }
            row("Вернулись хоть раз", (back, n), tint: .orange)
        }
        .padding(.vertical, 4)
    }

    private func row(_ title: String, _ r: (back: Int, of: Int), tint: Color) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(alignment: .firstTextBaseline) {
                Text(title)
                Spacer()
                if r.of > 0 {
                    Text(Names.percent(r.back, of: r.of)).font(.title3.bold()).monospacedDigit()
                    Text("\(r.back) из \(r.of)").font(.caption).monospacedDigit().foregroundStyle(.secondary)
                } else {
                    Text("ещё рано").foregroundStyle(.secondary)
                }
            }
            ShareBar(value: r.back, total: r.of, tint: tint)
        }
    }

    private var frequency: some View {
        let buckets: [(String, ClosedRange<Int>)] = [("1 день — больше не вернулись", 1...1), ("2 дня", 2...2),
                                                    ("3–4 дня", 3...4), ("5–7 дней", 5...7),
                                                    ("8–14 дней", 8...14), ("15 дней и больше", 15...Int.max)]
        let total = s.activeDays.reduce(0) { $0 + $1.n }
        let avg = total > 0 ? Double(s.activeDays.reduce(0) { $0 + $1.days * $1.n }) / Double(total) : 0
        return Group {
            ForEach(buckets, id: \.0) { title, range in
                let n = s.activeDays.filter { range.contains($0.days) }.reduce(0) { $0 + $1.n }
                VStack(alignment: .leading, spacing: 6) {
                    HStack {
                        Text(title)
                        Spacer()
                        Text("\(n)").monospacedDigit().bold()
                        Text(Names.percent(n, of: total)).monospacedDigit().foregroundStyle(.secondary)
                            .frame(width: 44, alignment: .trailing)
                    }
                    ShareBar(value: n, total: total, tint: range.lowerBound == 1 ? .red : .indigo)
                }
                .padding(.vertical, 2)
            }
            HStack {
                Text("В среднем")
                Spacer()
                Text(String(format: "%.1f", avg) + " " + Names.plural(Int(avg.rounded()), "день", "дня", "дней"))
                    .monospacedDigit().bold()
            }
        }
    }

    private var cohortTable: some View {
        Group {
            HStack(spacing: 0) {
                Text("Пришли").frame(maxWidth: .infinity, alignment: .leading)
                ForEach(AdminStats.retentionDays, id: \.self) { k in
                    Text("\(k) д").frame(width: 46)
                }
            }
            .font(.caption.bold()).foregroundStyle(.secondary)
            ForEach(s.cohorts.reversed()) { c in
                HStack(spacing: 0) {
                    VStack(alignment: .leading, spacing: 0) {
                        Text(c.date.formatted(.dateTime.day().month(.abbreviated))).font(.subheadline)
                        Text(Names.players(c.n)).font(.caption2).foregroundStyle(.secondary)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    ForEach(AdminStats.retentionDays, id: \.self) { k in cell(c, k) }
                }
            }
        }
    }

    private func cell(_ c: AdminStats.Cohort, _ k: Int) -> some View {
        let ready = c.day + k < s.today
        let share = c.n > 0 ? Double(c.returned[k] ?? 0) / Double(c.n) : 0
        return Text(ready ? Names.percent(c.returned[k] ?? 0, of: c.n) : "")
            .font(.caption.monospacedDigit())
            .frame(width: 44, height: 30)
            .background(ready ? Color.green.opacity(0.08 + share * 0.8) : Color.clear,
                        in: RoundedRectangle(cornerRadius: 6))
            .frame(width: 46)
    }
}

// MARK: - Главы

private struct ChaptersTab: View {
    let s: AdminStats

    var body: some View {
        List {
            Section {
                ForEach(s.chapters) { ch in
                    NavigationLink { ChapterDetail(s: s, ch: ch) } label: { ChapterRow(ch: ch) }
                }
            } footer: {
                Text("«Начали» — игроки, открывшие хотя бы один эпизод. «Прошли» — дошли до последнего эпизода главы и решили его.")
            }
        }
    }
}

private struct ChapterRow: View {
    let ch: AdminStats.Chapter

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: ch.icon).foregroundStyle(.tint).frame(width: 24)
                Text(Names.chapter(ch.id)).font(.headline).lineLimit(1)
            }
            HStack(spacing: 18) {
                metric("\(ch.players)", "начали")
                metric("\(ch.finished)", "прошли")
                metric(Names.percent(ch.finished, of: ch.players), "дошли до конца")
            }
            ShareBar(value: ch.finished, total: ch.players, tint: .green)
        }
        .padding(.vertical, 4)
    }

    private func metric(_ v: String, _ t: String) -> some View {
        VStack(alignment: .leading, spacing: 0) {
            Text(v).font(.title3.bold()).monospacedDigit()
            Text(t).font(.caption).foregroundStyle(.secondary)
        }
    }
}

private struct ChapterDetail: View {
    let s: AdminStats
    let ch: AdminStats.Chapter

    /// Эпизод, на котором теряется больше всего игроков (между ним и следующим).
    private var worstDrop: (level: AdminStats.Level, lost: Int)? {
        let lv = ch.levels
        guard lv.count > 1 else { return nil }
        return zip(lv, lv.dropFirst())
            .map { ($0, $0.started - $1.started) }
            .filter { $0.1 > 0 }
            .max { $0.1 < $1.1 }
    }

    var body: some View {
        List {
            Section {
                HStack {
                    StatTile(value: ch.players, title: "начали главу", icon: "play.fill")
                    StatTile(value: ch.finished, title: "прошли до конца", icon: "flag.checkered", tint: .green)
                }
                HStack {
                    StatTile(value: ch.completions, title: "решений эпизодов всего", icon: "checkmark.seal", tint: .purple)
                    StatTile(value: ch.adUnlocks, title: "эпизодов открыто за рекламу", icon: "play.rectangle", tint: .orange)
                }
            }
            .listRowInsets(EdgeInsets(top: 4, leading: 0, bottom: 4, trailing: 0))
            .listRowBackground(Color.clear)

            if let w = worstDrop {
                Section {
                    Label {
                        Text("Больше всего уходят после эпизода №\(w.level.number) «\(Names.level(w.level.id))»: дальше не пошли \(Names.players(w.lost)).")
                    } icon: { Image(systemName: "exclamationmark.triangle.fill").foregroundStyle(.orange) }
                }
            }

            if let cs = s.chapterCountries[ch.id], !cs.isEmpty {
                Section("Откуда игроки этой главы") {
                    ForEach(cs.prefix(10)) { c in CountryRow(code: c.key, n: c.n, total: ch.players) }
                }
            }

            Section {
                ForEach(ch.levels) { lv in
                    NavigationLink { LevelDetail(s: s, ch: ch, lv: lv) } label: {
                        LevelRow(lv: lv, top: ch.levels.first?.started ?? 0)
                    }
                }
            } header: {
                Text("Эпизоды по порядку")
            } footer: {
                Text("Синяя полоса — сколько игроков дошли до эпизода (от числа начавших первый), зелёная — сколько его решили.")
            }
        }
        .navigationTitle(Names.chapter(ch.id))
        .navigationBarTitleDisplayMode(.inline)
    }
}

private struct LevelRow: View {
    let lv: AdminStats.Level
    let top: Int

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(alignment: .firstTextBaseline) {
                Text("\(lv.number)").font(.caption.bold()).monospacedDigit().foregroundStyle(.secondary)
                    .frame(width: 26, alignment: .leading)
                Text(Names.level(lv.id)).lineLimit(1)
                Spacer()
                Text("\(lv.started) → \(lv.completed)").font(.callout).monospacedDigit().foregroundStyle(.secondary)
            }
            ZStack(alignment: .leading) {
                ShareBar(value: lv.started, total: max(top, 1), tint: .blue)
                ShareBar(value: lv.completed, total: max(top, 1), tint: .green)
                    .opacity(lv.completed > 0 ? 1 : 0)
            }
        }
        .padding(.vertical, 2)
    }
}

private struct LevelDetail: View {
    let s: AdminStats
    let ch: AdminStats.Chapter
    let lv: AdminStats.Level

    var body: some View {
        List {
            Section {
                Text(Names.chapter(ch.id) + " · эпизод №\(lv.number)").foregroundStyle(.secondary)
                HStack {
                    StatTile(value: lv.started, title: "начали", icon: "play.fill")
                    StatTile(value: lv.completed, title: "решили", icon: "checkmark", tint: .green)
                    StatTile(value: max(0, lv.started - lv.completed), title: "пока не решили", icon: "hourglass", tint: .orange)
                }
                Text("Решили \(Names.percent(lv.completed, of: lv.started)) из начавших.")
            }
            .listRowSeparator(.hidden)

            Section("Страны") {
                if let cs = s.levelCountries[lv.id], !cs.isEmpty {
                    ForEach(cs.indices, id: \.self) { i in
                        let c = cs[i]
                        HStack {
                            Text(Names.flag(c.country))
                            Text(Names.country(c.country)).lineLimit(1)
                            Spacer()
                            Text("\(c.started) → \(c.completed)").monospacedDigit().foregroundStyle(.secondary)
                        }
                    }
                } else if !s.hasCountryBreakdown {
                    Text("Разбивка по странам появится после обновления сервера статистики.").foregroundStyle(.secondary)
                } else {
                    Text("Пока никто не играл").foregroundStyle(.secondary)
                }
            }
        }
        .navigationTitle(Names.level(lv.id))
        .navigationBarTitleDisplayMode(.inline)
    }
}

// MARK: - Страны

private struct CountriesTab: View {
    let s: AdminStats

    var body: some View {
        List {
            Section("Страны · \(Names.players(s.players.total))") {
                ForEach(s.countries) { c in CountryRow(code: c.key, n: c.n, total: s.players.total) }
            }
            Section("Язык игры") {
                ForEach(s.langs) { l in
                    HStack { Text(Names.lang(l.key)); Spacer(); Text("\(l.n)").monospacedDigit().foregroundStyle(.secondary) }
                }
            }
            Section("Версии приложения") {
                ForEach(s.versions) { v in
                    HStack {
                        Image(systemName: v.key.hasPrefix("ios") ? "apple.logo" : "smartphone").frame(width: 22)
                        Text(v.key.replacingOccurrences(of: "ios ", with: "iPhone ")
                                  .replacingOccurrences(of: "android ", with: "Android "))
                        Spacer()
                        Text("\(v.n)").monospacedDigit().foregroundStyle(.secondary)
                    }
                }
            }
        }
    }
}

// MARK: - Лента

private struct FeedTab: View {
    let s: AdminStats

    var body: some View {
        List {
            if s.recent.isEmpty { Text("Событий пока нет").foregroundStyle(.secondary) }
            ForEach(s.recent) { e in
                HStack(alignment: .top, spacing: 12) {
                    Image(systemName: icon(e.type))
                        .foregroundStyle(tint(e.type))
                        .frame(width: 28, height: 28)
                        .background(tint(e.type).opacity(0.15), in: Circle())
                    VStack(alignment: .leading, spacing: 3) {
                        Text(action(e)).lineLimit(2)
                        HStack(spacing: 6) {
                            if let c = e.country { Text("\(Names.flag(c)) \(Names.country(c))") }
                            if let p = e.platform { Text(p == "ios" ? "· iPhone" : "· Android") }
                            Text("· " + e.date.formatted(.relative(presentation: .named)))
                        }
                        .font(.caption).foregroundStyle(.secondary).lineLimit(1)
                    }
                }
                .padding(.vertical, 2)
            }
        }
    }

    private func action(_ e: AdminStats.Event) -> String {
        let level = e.level.map { "«\(Names.level($0))»" } ?? ""
        let chapter = e.chapter.map { " · \(Names.chapter($0))" } ?? ""
        switch e.type {
        case "level_start": return "Начал эпизод \(level)\(chapter)"
        case "level_complete": return "Решил эпизод \(level)\(chapter)"
        case "ad_unlock": return "Открыл за рекламу \(level)\(chapter)"
        default: return e.type
        }
    }
    private func icon(_ t: String) -> String {
        switch t {
        case "level_start": return "play.fill"
        case "level_complete": return "checkmark"
        case "ad_unlock": return "play.rectangle.fill"
        default: return "circle"
        }
    }
    private func tint(_ t: String) -> Color {
        switch t {
        case "level_start": return .blue
        case "level_complete": return .green
        case "ad_unlock": return .orange
        default: return .gray
        }
    }
}
