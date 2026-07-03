import Foundation

/// Локализация: единый каталог `i18n_<lang>.json` в контент-бандле (и UI, и контент).
/// Активный язык = оверрайд из настроек (`ht.lang`) → язык устройства → EN → RU-база.
/// UI-строки берутся через `L10n.s(...)`, контент локализуется на загрузке пака.
public enum L10n {
    public static let available = ["ru", "en", "es", "de", "fr", "it", "pt", "pl", "nl"]

    private static var base: [String: String] = read("ru")   // фолбэк
    private static var table: [String: String] = read("ru")
    public private(set) static var lang: String = "ru"

    /// Вызвать один раз на старте (и при смене языка в настройках).
    public static func configure() { setLanguage(resolvedLanguage()) }

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

    /// Строка по ключу (фолбэк: база → сам ключ).
    public static func s(_ key: String) -> String { table[key] ?? base[key] ?? key }

    /// Форматированная строка (для `%d`, `%@`).
    public static func s(_ key: String, _ args: CVarArg...) -> String {
        String(format: s(key), locale: Locale(identifier: "en_US_POSIX"), arguments: args)
    }

    /// Опционально (для локализации контента: если ключа нет — nil, оставляем исходник).
    public static func opt(_ key: String) -> String? { table[key] }

    /// Русское (базовое) значение ключа — для обратного соответствия (напр. локализация акт-заголовков).
    public static func ruBase(_ key: String) -> String? { base[key] }

    private static func read(_ code: String) -> [String: String] {
        guard let url = Bundle.gameContent.url(forResource: "i18n_\(code)", withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let dict = try? JSONDecoder().decode([String: String].self, from: data)
        else { return [:] }
        return dict
    }
}
