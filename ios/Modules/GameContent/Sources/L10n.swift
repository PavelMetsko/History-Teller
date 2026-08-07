import Foundation

/// Локализация: единый каталог `i18n_<lang>.json` в контент-бандле (и UI, и контент).
/// Активный язык = оверрайд из настроек (`ht.lang`) → язык устройства → EN → RU-база.
/// UI-строки берутся через `L10n.s(...)`, контент локализуется на загрузке пака.
public enum L10n {
    public static let available = ["ru", "en", "es", "de", "fr", "it", "pt", "pl", "nl"]

    private static var base: [String: String] = read("ru")   // фолбэк
    private static var table: [String: String] = read("ru")
    public private(set) static var lang: String = "ru"

    /// Вызвать на старте (и при смене языка). База перечитывается здесь, а не только при
    /// первом обращении: каталог приезжает из облака, и статик мог инициализироваться пустым.
    public static func configure() {
        base = read("ru")
        setLanguage(resolvedLanguage())
    }

    public static func setLanguage(_ code: String) {
        lang = available.contains(code) ? code : "en"
        table = (lang == "ru") ? base : read(lang)
    }

    /// Язык: оверрайд из настроек → предпочтения устройства → EN.
    public static func resolvedLanguage() -> String {
        if let o = UserDefaults.standard.string(forKey: "ht.lang"),
           !o.isEmpty, available.contains(o) { return o }
        for pref in Locale.preferredLanguages {
            let code = String(pref.prefix(2)).lowercased()
            if available.contains(code) { return code }
        }
        return "en"
    }

    /// Строки, которые нужны ДО того, как каталог скачан: их показывает экран первого запуска,
    /// а каталог в этот момент ещё едет. Без них на экране висел бы голый ключ.
    private static let builtin: [String: [String: String]] = [
        "ui.downloading_content": [
            "ru": "Загрузка контента…", "en": "Downloading content…", "es": "Descargando contenido…",
            "de": "Inhalte werden geladen…", "fr": "Téléchargement du contenu…",
            "it": "Download dei contenuti…", "pt": "Baixando conteúdo…",
            "pl": "Pobieranie zawartości…", "nl": "Inhoud downloaden…",
        ],
        "ui.load_fail": [
            "ru": "Не удалось загрузить контент", "en": "Failed to load content",
            "es": "No se pudo cargar el contenido", "de": "Inhalte konnten nicht geladen werden",
            "fr": "Échec du chargement du contenu", "it": "Impossibile caricare i contenuti",
            "pt": "Falha ao carregar o conteúdo", "pl": "Nie udało się pobrać zawartości",
            "nl": "Laden van inhoud mislukt",
        ],
        "ui.retry": [
            "ru": "Повторить", "en": "Retry", "es": "Reintentar", "de": "Erneut versuchen",
            "fr": "Réessayer", "it": "Riprova", "pt": "Tentar novamente",
            "pl": "Ponów", "nl": "Opnieuw",
        ],
    ]

    /// Строка по ключу (фолбэк: база → встроенная → сам ключ).
    public static func s(_ key: String) -> String {
        table[key] ?? base[key] ?? builtin[key]?[lang] ?? builtin[key]?["en"] ?? key
    }

    /// Форматированная строка (для `%d`, `%@`).
    public static func s(_ key: String, _ args: CVarArg...) -> String {
        String(format: s(key), locale: Locale(identifier: "en_US_POSIX"), arguments: args)
    }

    /// Опционально (для локализации контента: если ключа нет — nil, оставляем исходник).
    public static func opt(_ key: String) -> String? { table[key] }

    /// Русское (базовое) значение ключа — для обратного соответствия (напр. локализация акт-заголовков).
    public static func ruBase(_ key: String) -> String? { base[key] }

    /// Все ключи базы с данным префиксом. Нужно, чтобы не держать списки ключей в коде:
    /// новая глава приносит свои `act.<epoch>.N` вместе с каталогом и подхватывается сама.
    public static func keys(prefix: String) -> [String] {
        base.keys.filter { $0.hasPrefix(prefix) }.sorted()
    }

    private static func read(_ code: String) -> [String: String] {
        // Скачанный каталог перекрывает вшитый — правки переводов приезжают без релиза.
        let url = ContentSync.shared.fileURL("content/i18n/\(code).json")
            ?? Bundle.gameContent.url(forResource: "i18n_\(code)", withExtension: "json")
        guard let url,
              let data = try? Data(contentsOf: url),
              let dict = try? JSONDecoder().decode([String: String].self, from: data)
        else { return [:] }
        return dict
    }
}
