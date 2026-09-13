import Foundation
import CryptoKit
import Observation

/// Манифест облачного контента (собирается `tools/publish_content.py`).
public struct ContentManifest: Codable, Sendable {
    public struct FileRef: Codable, Sendable {
        public let h: String        // sha256
        public let s: Int           // байт
    }
    public struct Chapter: Codable, Sendable {
        public let id: String
        public let number: Int
        public let cover: String
        public let icon: String
        public let free: Bool
        public let minAppVersion: String
        public let levels: [String]
    }
    public let version: Int
    public let minAppVersion: String
    public let chapters: [Chapter]
    public let disabled: [String]
    /// Показательный уровень: на нём построены онбординг и экран загрузки главы. Лежит в core.
    public let demo: String?
    public let core: [String]
    /// Описания уровней главы — всё, что нужно, чтобы открыть её карту. Килобайты.
    public let chapterIndex: [String: [String]]?
    /// Обложки карточек в порядке прохождения — качаются фоном, уже на открытой карте.
    public let chapterCovers: [String: [String]]?
    /// Файлы одного уровня: гейт при входе в него и единица фоновой докачки.
    public let levelFiles: [String: [String]]?
    /// Глава целиком. Осталось ради манифестов, сохранённых до поуровневой загрузки.
    public let chapterFiles: [String: [String]]
    public let files: [String: FileRef]
}

/// Доставка контента из облака.
///
/// Файлы лежат в кеше **по хешу** (`objects/<sha256>`), а не по имени: при смене версии контента
/// не бывает устаревших файлов, одинаковый арт разных глав хранится один раз, а прерванная
/// докачка не оставляет главу в полуготовом виде — готовность считается по наличию всех объектов.
///
/// Кеш — в Application Support, не в Caches: система вычищает Caches под давлением памяти,
/// и игра осталась бы без арта посреди сессии.
@Observable
public final class ContentSync {
    public static let shared = ContentSync()

    public enum Phase: Equatable {
        case idle
        case syncing(Double)
        case ready
        case failed(String)
    }

    public private(set) var phase: Phase = .idle
    public private(set) var manifest: ContentManifest?

    /// Растёт после каждого приехавшего файла. Экраны, которые читают его в `body`, сами
    /// перерисовываются, когда фоновая докачка приносит обложку или спрайт.
    public private(set) var generation = 0

    /// Базовый URL раздачи. Переопределяется переменной окружения `HT_CONTENT_URL` (локальный стенд
    /// `tools/publish_content.py --serve`) или ключом `HTContentBaseURL` в Info.plist.
    public static var baseURL: URL = {
        if let s = ProcessInfo.processInfo.environment["HT_CONTENT_URL"], let u = URL(string: s) { return u }
        if let s = Bundle.main.object(forInfoDictionaryKey: "HTContentBaseURL") as? String,
           let u = URL(string: s) { return u }
        // Свой домен, подключённый к бакету R2. Публичный `*.r2.dev` Cloudflare троттлит
        // и для продакшена не рекомендует — на нём мы жили только до покупки домена.
        return URL(string: "https://cdn.historyteller.app")!
    }()

    private let root: URL
    private let objects: URL
    private let session = URLSession(configuration: .ephemeral)

    private init() {
        let base = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
        root = base.appendingPathComponent("Content", isDirectory: true)
        objects = root.appendingPathComponent("objects", isDirectory: true)
        try? FileManager.default.createDirectory(at: objects, withIntermediateDirectories: true)
        manifest = loadCachedManifest()
        wireResolvers()
    }

    // MARK: - Доступ к файлам

    /// Логический путь (`art/char_caesar.webp`) → файл на диске, если он скачан.
    public func fileURL(_ logical: String) -> URL? {
        guard let ref = manifest?.files[logical] else { return nil }
        let url = objects.appendingPathComponent(ref.h)
        return FileManager.default.fileExists(atPath: url.path) ? url : nil
    }

    /// Содержимое скачанного текстового файла (JSON контента), если он есть.
    public func text(_ logical: String) -> String? {
        guard let url = fileURL(logical) else { return nil }
        return try? String(contentsOf: url, encoding: .utf8)
    }

    /// Порядок уровней по всем доступным главам, с учётом `disabled`.
    /// `nil` — манифеста ещё нет, вызывающий откатывается на вшитый список.
    public var levelIds: [String]? {
        guard manifest != nil else { return nil }
        return availableChapters.flatMap(\.levels).filter { !isLevelDisabled($0) }
    }

    /// Уровень для онбординга и экрана загрузки. Его файлы входят в core, поэтому он на диске
    /// с первого запуска — до того, как скачана хоть одна глава.
    public var demoLevelId: String? { manifest?.demo }

    public func isChapterReady(_ id: String) -> Bool {
        guard let files = manifest?.chapterFiles[id] else { return false }
        return files.allSatisfy { fileURL($0) != nil }
    }

    /// Описания уровней главы: без них не собрать карту. Старый манифест поуровневых списков
    /// не знает — там гейтом остаётся глава целиком.
    private func indexFiles(_ id: String) -> [String]? {
        guard let m = manifest else { return nil }
        return m.chapterIndex?[id] ?? m.chapterFiles[id]
    }

    /// Файлы одного уровня. Пусто — манифест старый, значит глава уже скачана целиком.
    private func levelFiles(_ id: String) -> [String] { manifest?.levelFiles?[id] ?? [] }

    /// Можно ли открывать карту главы.
    public func isChapterIndexReady(_ id: String) -> Bool {
        guard let files = indexFiles(id) else { return false }
        return files.allSatisfy { fileURL($0) != nil }
    }

    /// Можно ли входить в уровень, не показывая загрузку.
    public func isLevelReady(_ id: String) -> Bool {
        levelFiles(id).allSatisfy { fileURL($0) != nil }
    }

    /// Главы, доступные этой сборке: манифест может нести контент, требующий более новой версии.
    public var availableChapters: [ContentManifest.Chapter] {
        (manifest?.chapters ?? []).filter { Self.supports($0.minAppVersion) }
    }

    public func isLevelDisabled(_ id: String) -> Bool {
        manifest?.disabled.contains(id) ?? false
    }

    /// Прогресс текущей операции для полосок загрузки.
    public var progressValue: Double {
        switch phase {
        case .syncing(let p): return p
        case .ready: return 1
        default: return 0
        }
    }

    /// Текст ошибки, если последняя операция не удалась.
    public var failure: String? {
        if case .failed(let message) = phase { return message }
        return nil
    }

    /// Есть ли на устройстве всё для запуска игры (манифест + core).
    public var hasCore: Bool {
        guard let m = manifest else { return false }
        return m.core.allSatisfy { fileURL($0) != nil }
    }

    // MARK: - Синхронизация

    /// Обновить манифест и докачать core — после этого работают меню, список глав и локализация.
    public func syncCore() async {
        cancelPrefetch()     // манифест меняется под ногами, а в конце ещё и чистятся сироты
        phase = .syncing(0)
        do {
            guard let fresh = try await fetchManifest() else {
                // Контент не менялся с прошлого запуска — на диске всё, что нужно.
                phase = hasCore ? .ready : .failed("Контент не найден в кеше")
                return
            }
            guard Self.supports(fresh.minAppVersion) else {
                // Контент новее приложения целиком — работаем на том, что уже скачано.
                phase = manifest == nil ? .failed("Требуется обновление приложения") : .ready
                return
            }
            // Что уже лежало на диске — считаем по ПРЕЖНЕМУ манифесту, пока он ещё актуален.
            // По новому это не определить: правка, задевшая файл, меняет его хеш, и он
            // выглядел бы никогда не скачанным.
            let installed = downloadedPaths(in: manifest)
            manifest = fresh
            try await download(fresh.core, of: fresh)
            // Догружаем изменившееся среди уже скачанного: иначе правка уровня выкинула бы его
            // с карты — файл сменил хеш, а в кеше лежит прежний. Обновляем ровно то, что было,
            // а не главу целиком: с поуровневой загрузкой глава почти всегда скачана частично.
            try await download(installed.filter { fresh.files[$0] != nil }, of: fresh)
            saveManifest(fresh)      // манифест фиксируем только когда всё реально на диске
            pruneOrphans(fresh)
            ArtStore.invalidate()
            Audio.shared.reset()
            phase = .ready
        } catch {
            // Офлайн — не беда, если прошлый манифест и его файлы уже лежат.
            phase = manifest != nil ? .ready : .failed(Self.describe(error))
        }
    }

    /// Гейт перед картой главы: одни описания уровней, десятки килобайт. Всё остальное едет
    /// потом — обложки фоном на уже открытой карте, файлы уровня при входе в него.
    public func ensureChapterIndex(_ id: String) async {
        cancelPrefetch()
        guard let m = manifest, let files = indexFiles(id) else {
            phase = .failed("Глава \(id) не найдена в манифесте")
            return
        }
        if isChapterIndexReady(id) { phase = .ready; return }
        phase = .syncing(0)
        do {
            try await download(files, of: m)
            ArtStore.invalidate()
            phase = .ready
        } catch {
            phase = .failed(Self.describe(error))
        }
    }

    /// Гейт перед уровнем: его сцены, персонажи и музыка, ~1 МБ. Обычно к этому моменту всё уже
    /// принесла фоновая докачка, и экран загрузки не показывается вовсе.
    public func ensureLevel(_ id: String) async {
        cancelPrefetch()
        guard let m = manifest else { phase = .failed("Манифест не загружен"); return }
        if isLevelReady(id) { phase = .ready; return }
        phase = .syncing(0)
        do {
            try await download(levelFiles(id), of: m)
            ArtStore.invalidate()
            Audio.shared.reset()
            phase = .ready
        } catch {
            phase = .failed(Self.describe(error))
        }
    }

    /// Фоновая докачка главы, с которой игрок сейчас работает: сперва обложки карточек
    /// в порядке прохождения, потом уровни целиком — начиная с того, куда игрок пойдёт дальше.
    /// Ничего не блокирует и не трогает `phase`: экраны на нём не завязаны.
    public func prefetchChapter(_ id: String, startingAt levelId: String? = nil) {
        cancelPrefetch()
        guard let m = manifest else { return }
        let ids = m.chapters.first { $0.id == id }?.levels ?? []
        let start = levelId.flatMap { ids.firstIndex(of: $0) } ?? 0
        // От текущего эпизода вперёд, потом по кругу к началу: чем ближе уровень к игроку,
        // тем раньше он приезжает. Сам текущий идёт первым, до обложек, — по нему кликнут
        // с наибольшей вероятностью, и кликнут скорее, чем долистают карту.
        let order = Array(ids[start...]) + Array(ids[..<start])
        let queue = (order.first.map { levelFiles($0) } ?? []) + (m.chapterCovers?[id] ?? [])
            + order.flatMap { levelFiles($0) }

        prefetch = Task.detached(priority: .utility) { [weak self] in
            guard let self else { return }
            for path in queue {
                if Task.isCancelled { return }
                guard let ref = m.files[path] else { continue }
                if FileManager.default.fileExists(atPath: self.objects.appendingPathComponent(ref.h).path) { continue }
                guard (try? await self.fetchObject(ref, describing: path)) != nil else { continue }
                await self.noteArrived(path)
            }
        }
    }

    /// Приехавший файл докачки. Карта перерисовывается не на каждый файл, а пачкой и только
    /// когда среди приехавшего есть фон сцены — единственное, что она показывает. Раньше
    /// `generation` рос на каждый спрайт и трек, по десятку раз в секунду, и карта всё это
    /// время пересобирала сетку под пальцем — скролл дёргался и зиял пустыми ячейками.
    @MainActor
    private func noteArrived(_ path: String) {
        if path.hasPrefix("art/scene_") { arrivedScene = true }
        guard !bumpScheduled else { return }
        bumpScheduled = true
        Task { @MainActor [weak self] in
            try? await Task.sleep(for: .milliseconds(500))
            guard let self else { return }
            self.bumpScheduled = false
            // Только присутствие: уже разобранные картинки в кеше остаются, а карта
            // перерисовывается и подхватывает приехавшую обложку.
            ArtStore.invalidateMissing()
            if self.arrivedScene {
                self.arrivedScene = false
                self.generation += 1
            }
        }
    }

    public func cancelPrefetch() {
        prefetch?.cancel()
        prefetch = nil
    }

    // MARK: - Внутреннее

    private var prefetch: Task<Void, Never>?
    @ObservationIgnored private var bumpScheduled = false
    @ObservationIgnored private var arrivedScene = false

    /// Логические пути, файлы которых лежат на диске. Считается до подмены манифеста — по
    /// прежним хешам, потому что только они описывают то, что реально скачано.
    private func downloadedPaths(in m: ContentManifest?) -> [String] {
        guard let m else { return [] }
        let fm = FileManager.default
        return m.files.compactMap { path, ref in
            fm.fileExists(atPath: objects.appendingPathComponent(ref.h).path) ? path : nil
        }
    }

    /// Выкидывает объекты, на которые новый манифест больше не ссылается: после правки контента
    /// прежняя версия файла осталась бы на диске навсегда.
    private func pruneOrphans(_ m: ContentManifest) {
        let alive = Set(m.files.values.map(\.h))
        let fm = FileManager.default
        guard let names = try? fm.contentsOfDirectory(atPath: objects.path) else { return }
        for name in names where !alive.contains(name) {
            try? fm.removeItem(at: objects.appendingPathComponent(name))
        }
    }

    /// Загрузить манифест, если он изменился. `nil` — сервер ответил 304, на диске уже свежий.
    ///
    /// Манифест — единственное, что запрашивается на КАЖДОМ запуске (сам контент лежит в кеше
    /// по хешу и не перекачивается). Он весит ~100 КБ, поэтому спрашиваем условно, по ETag:
    /// когда контент не менялся, ответ — пустой 304 в пару сотен байт.
    private func fetchManifest() async throws -> ContentManifest? {
        let url = Self.baseURL.appendingPathComponent("manifest.json")
        var req = URLRequest(url: url)
        req.cachePolicy = .reloadIgnoringLocalCacheData
        if manifest != nil, let tag = UserDefaults.standard.string(forKey: Self.etagKey) {
            req.setValue(tag, forHTTPHeaderField: "If-None-Match")
        }
        let (data, response) = try await session.data(for: req)
        if let http = response as? HTTPURLResponse, http.statusCode == 304 { return nil }
        try Self.checkOK(response)
        let fresh = try JSONDecoder().decode(ContentManifest.self, from: data)
        // ETag сохраняем ПОСЛЕ разбора: на битом ответе он бы навсегда заглушил обновления.
        if let http = response as? HTTPURLResponse,
           let tag = http.value(forHTTPHeaderField: "Etag") {
            UserDefaults.standard.set(tag, forKey: Self.etagKey)
        }
        return fresh
    }

    private static let etagKey = "ht.manifest.etag" 

    /// Качает недостающие объекты. Прогресс — по байтам, чтобы полоска не скакала на мелких JSON.
    private func download(_ logical: [String], of m: ContentManifest) async throws {
        let missing = logical.compactMap { path -> (String, ContentManifest.FileRef)? in
            guard let ref = m.files[path] else { return nil }
            let dst = objects.appendingPathComponent(ref.h)
            return FileManager.default.fileExists(atPath: dst.path) ? nil : (path, ref)
        }
        guard !missing.isEmpty else { return }

        let total = missing.reduce(0) { $0 + $1.1.s }
        var done = 0
        // Последовательно: контент мелкий, а так прогресс честный и мы не забиваем канал.
        for (path, ref) in missing {
            try await fetchObject(ref, describing: path)
            done += ref.s
            phase = .syncing(Double(done) / Double(max(total, 1)))
        }
    }

    private func fetchObject(_ ref: ContentManifest.FileRef, describing path: String) async throws {
        let url = Self.baseURL.appendingPathComponent("f/\(ref.h)")
        let (data, response) = try await session.data(from: url)
        try Self.checkOK(response)

        let actual = SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
        guard actual == ref.h else {
            throw SyncError.corrupted(path)
        }
        // Пишем во временный файл и переименовываем: оборванная закачка не оставит битый объект,
        // который потом будет считаться готовым. Имя уникальное — фоновая докачка и загрузка
        // уровня могут одновременно тянуть один объект, и общий `.part` они бы затёрли друг другу.
        let tmp = objects.appendingPathComponent("\(ref.h).\(UUID().uuidString).part")
        try data.write(to: tmp, options: .atomic)
        try? FileManager.default.removeItem(at: objects.appendingPathComponent(ref.h))
        try FileManager.default.moveItem(at: tmp, to: objects.appendingPathComponent(ref.h))
    }

    private var manifestFile: URL { root.appendingPathComponent("manifest.json") }

    private func loadCachedManifest() -> ContentManifest? {
        guard let data = try? Data(contentsOf: manifestFile) else { return nil }
        return try? JSONDecoder().decode(ContentManifest.self, from: data)
    }

    private func saveManifest(_ m: ContentManifest) {
        guard let data = try? JSONEncoder().encode(m) else { return }
        try? data.write(to: manifestFile, options: .atomic)
        var url = root
        var values = URLResourceValues()
        values.isExcludedFromBackup = true      // контент восстановим из сети, в iCloud ему не место
        try? url.setResourceValues(values)
    }

    /// Подключает кеш к загрузчикам арта и контента: они спрашивают файл по логическому пути,
    /// а если его нет — откатываются на вшитое в бандл.
    private func wireResolvers() {
        ArtStore.resolve = { [weak self] logical in self?.fileURL(logical) }
    }

    enum SyncError: LocalizedError {
        case corrupted(String)
        case http(Int)

        var errorDescription: String? {
            switch self {
            case .corrupted(let p): return "Файл повреждён при загрузке: \(p)"
            case .http(let code):   return "Сервер контента ответил \(code)"
            }
        }
    }

    private static func checkOK(_ response: URLResponse) throws {
        guard let http = response as? HTTPURLResponse else { return }
        guard (200..<300).contains(http.statusCode) else { throw SyncError.http(http.statusCode) }
    }

    private static func describe(_ error: Error) -> String {
        (error as? LocalizedError)?.errorDescription ?? error.localizedDescription
    }

    /// Версия приложения для сравнения с `minAppVersion`.
    static var appVersion: String {
        Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String ?? "0"
    }

    /// Потянет ли эта сборка контент, требующий версии `required`.
    /// Сравниваем по числовым компонентам: строковое сравнение считает "1.10" старше "1.9".
    static func supports(_ required: String) -> Bool {
        let a = appVersion.split(separator: ".").map { Int($0) ?? 0 }
        let b = required.split(separator: ".").map { Int($0) ?? 0 }
        for i in 0..<max(a.count, b.count) {
            let x = i < a.count ? a[i] : 0
            let y = i < b.count ? b[i] : 0
            if x != y { return x > y }
        }
        return true
    }
}
