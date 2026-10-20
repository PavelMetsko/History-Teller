import SwiftUI
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

/// Скрытый экран: статистика всех игроков обеих платформ (как в Decima и Line Kick).
struct AdminStatsView: View {
    let password: String
    let onClose: () -> Void

    @State private var data: [String: Any]?
    @State private var error: String?
    @State private var loading = false

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    if let error { Text(error).foregroundStyle(.red) }
                    if let data { content(data) } else if loading { ProgressView().frame(maxWidth: .infinity) }
                }
                .padding()
            }
            .navigationTitle("Stats")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) { Button("Close", action: onClose) }
                ToolbarItem(placement: .primaryAction) {
                    Button { Task { await load() } } label: { Image(systemName: "arrow.clockwise") }
                }
            }
            .refreshable { await load() }
            .task { await load() }
        }
    }

    private func load() async {
        loading = true
        defer { loading = false }
        switch await AdminStatsAPI.fetch(password: password) {
        case .success(let d): data = d; error = nil
        case .failure(.unauthorized): error = "Wrong password"; AdminAccess.forget()
        case .failure(.network(let m)): error = m
        }
    }

    // MARK: - Секции

    @ViewBuilder private func content(_ d: [String: Any]) -> some View {
        let p = d["players"] as? [String: Any] ?? [:]
        section("Players") {
            grid([("Total", p["total"]), ("iOS", p["ios"]), ("Android", p["android"]),
                  ("New today", p["new1"]), ("New 7d", p["new7"]),
                  ("Active today", p["active1"]), ("Active 7d", p["active7"]), ("Active 30d", p["active30"])])
        }
        section("Chapters") {
            ForEach(rows(d["chapters"]).indices, id: \.self) { i in
                let r = rows(d["chapters"])[i]
                let id = r["chapter"] as? String ?? "?"
                row(L10n.s("chapter.\(id).title"),
                    "\(num(r["players"])) players · \(num(r["completions"]))/\(num(r["starts"])) done · ad \(num(r["ad_unlocks"]))")
            }
        }
        section("Levels (started → completed players)") {
            ForEach(rows(d["levels"]).indices, id: \.self) { i in
                let r = rows(d["levels"])[i]
                let id = r["level"] as? String ?? "?"
                let s = num(r["started"]), c = num(r["completed"])
                row(L10n.opt("level.\(id).title") ?? id,
                    "\(s) → \(c)" + (s > 0 ? "  (\(c * 100 / s)%)" : ""))
            }
        }
        section("Recent") {
            ForEach(rows(d["recent"]).indices, id: \.self) { i in
                let r = rows(d["recent"])[i]
                let ts = Date(timeIntervalSince1970: Double(num(r["ts"])) / 1000)
                let level = (r["level"] as? String).map { L10n.opt("level.\($0).title") ?? $0 } ?? ""
                row("\(r["type"] as? String ?? "") \(level)",
                    "\(r["platform"] as? String ?? "") \(r["country"] as? String ?? "") · \(ts.formatted(.relative(presentation: .numeric)))")
            }
        }
        section("Countries") { kv(d["countries"]) }
        section("Languages") { kv(d["langs"]) }
        section("Versions") { kv(d["versions"]) }
    }

    private func section<C: View>(_ title: String, @ViewBuilder _ body: () -> C) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title).font(.headline)
            body()
        }
    }

    private func grid(_ items: [(String, Any?)]) -> some View {
        LazyVGrid(columns: [GridItem(.adaptive(minimum: 110))], alignment: .leading, spacing: 8) {
            ForEach(items.indices, id: \.self) { i in
                VStack(alignment: .leading) {
                    Text("\(num(items[i].1))").font(.title2.bold())
                    Text(items[i].0).font(.caption).foregroundStyle(.secondary)
                }
            }
        }
    }

    private func kv(_ any: Any?) -> some View {
        ForEach(rows(any).indices, id: \.self) { i in
            let r = rows(any)[i]
            row(r["k"] as? String ?? "?", "\(num(r["n"]))")
        }
    }

    private func row(_ left: String, _ right: String) -> some View {
        HStack(alignment: .firstTextBaseline) {
            Text(left).lineLimit(1)
            Spacer(minLength: 8)
            Text(right).font(.callout.monospacedDigit()).foregroundStyle(.secondary)
        }
        .font(.callout)
    }

    private func rows(_ any: Any?) -> [[String: Any]] { any as? [[String: Any]] ?? [] }
    private func num(_ any: Any?) -> Int { (any as? NSNumber)?.intValue ?? 0 }
}
