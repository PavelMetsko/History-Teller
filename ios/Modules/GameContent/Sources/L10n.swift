import Foundation

/// Локализация: единый каталог `i18n_<lang>.json` в контент-бандле (и UI, и контент).
/// Активный язык = оверрайд из настроек (`ht.lang`) → язык устройства → EN → RU-база.
/// UI-строки берутся через `L10n.s(...)`, контент локализуется на загрузке пака.
public enum L10n {
    public static let available = ["ru", "en", "es", "de", "fr", "it", "pt", "pl", "nl"]

    private static var base: [String: String] = read("ru")   // последний фолбэк
    /// Английский слой между выбранным языком и русской базой: если ключ ещё не переведён,
    /// игрок-европеец должен увидеть английский текст, а не кириллицу.
    private static var fallback: [String: String] = [:]
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
        fallback = (lang == "en" || lang == "ru") ? [:] : read("en")
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

    /// Строки, которые нужны ДО того, как каталог скачан (первый запуск), И новые UI-ключи,
    /// добавленные вместе с кодом: облачный каталог обновляется отдельной публикацией, и в окне
    /// между сборкой и публикацией такой ключ показывался игроку голым (`ui.swap_hint`).
    /// Правило: добавил ключ в код — продублируй его здесь.
    private static let builtin: [String: [String: String]] = [
        "ui.terms": [
            "ru": "Условия использования", "en": "Terms of Use", "es": "Términos de uso",
            "de": "Nutzungsbedingungen", "fr": "Conditions d'utilisation",
            "it": "Termini d'uso", "pt": "Termos de uso",
            "pl": "Warunki korzystania", "nl": "Gebruiksvoorwaarden",
        ],
        "ui.privacy": [
            "ru": "Политика конфиденциальности", "en": "Privacy Policy",
            "es": "Política de privacidad", "de": "Datenschutzerklärung",
            "fr": "Politique de confidentialité", "it": "Informativa sulla privacy",
            "pt": "Política de Privacidade", "pl": "Polityka prywatności",
            "nl": "Privacybeleid",
        ],
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
        "ui.swap_hint": [
            "ru": "Зажми кадр и перетащи на другой — кадры можно менять местами",
            "en": "Press and hold a panel, then drag it onto another — panels swap places",
            "es": "Mantén pulsado un panel y arrástralo sobre otro: los paneles se intercambian",
            "de": "Halte ein Panel gedrückt und zieh es auf ein anderes – Panels tauschen die Plätze",
            "fr": "Maintiens un cadre appuyé et fais-le glisser sur un autre — les cadres s'échangent",
            "it": "Tieni premuto un riquadro e trascinalo su un altro: i riquadri si scambiano",
            "pt": "Segure um quadro e arraste-o sobre outro — os quadros trocam de lugar",
            "pl": "Przytrzymaj kadr i przeciągnij go na inny — kadry zamienią się miejscami",
            "nl": "Houd een kader ingedrukt en sleep het op een ander — kaders wisselen van plaats",
        ],
        "ui.wrong_unused": [
            "ru": "Такой сцены в этой истории нет",
            "en": "This scene isn't part of the story",
            "es": "Esta escena no forma parte de la historia",
            "de": "Diese Szene gehört nicht zur Geschichte",
            "fr": "Cette scène ne fait pas partie de l'histoire",
            "it": "Questa scena non fa parte della storia",
            "pt": "Esta cena não faz parte da história",
            "pl": "Tej sceny nie ma w tej historii",
            "nl": "Deze scène hoort niet bij het verhaal",
        ],
        "ui.retry": [
            "ru": "Повторить", "en": "Retry", "es": "Reintentar", "de": "Erneut versuchen",
            "fr": "Réessayer", "it": "Riprova", "pt": "Tentar novamente",
            "pl": "Ponów", "nl": "Opnieuw",
        ],
        // Рядом с «Повторить» на экране загрузки: там каталог может быть ещё не скачан.
        "ui.cancel": [
            "ru": "Отмена", "en": "Cancel", "es": "Cancelar", "de": "Abbrechen",
            "fr": "Annuler", "it": "Annulla", "pt": "Cancelar",
            "pl": "Anuluj", "nl": "Annuleren",
        ],
        "ui.downloading_level": [
            "ru": "Загрузка эпизода…", "en": "Loading episode…", "es": "Cargando episodio…",
            "de": "Episode wird geladen…", "fr": "Chargement de l'épisode…",
            "it": "Caricamento dell'episodio…", "pt": "Carregando episódio…",
            "pl": "Wczytywanie epizodu…", "nl": "Aflevering laden…",
        ],
        "ui.privacy_choices": [
            "ru": "Конфиденциальность", "en": "Privacy choices", "es": "Opciones de privacidad",
            "de": "Datenschutzoptionen", "fr": "Choix de confidentialité",
            "it": "Scelte sulla privacy", "pt": "Opções de privacidade",
            "pl": "Ustawienia prywatności", "nl": "Privacykeuzes",
        ],
        "ui.level_gate_sub": [
            "ru": "Этот эпизод — из платной главы. Открой всю главу, оформи подписку или посмотри короткий ролик.",
            "en": "This episode is part of a paid chapter. Unlock the whole chapter, subscribe, or watch a short video.",
            "es": "Este episodio es de un capítulo de pago. Desbloquea el capítulo, suscríbete o mira un vídeo corto.",
            "de": "Diese Episode gehört zu einem kostenpflichtigen Kapitel. Schalte das Kapitel frei, abonniere oder sieh dir ein kurzes Video an.",
            "fr": "Cet épisode fait partie d'un chapitre payant. Débloque le chapitre, abonne-toi ou regarde une courte vidéo.",
            "it": "Questo episodio fa parte di un capitolo a pagamento. Sblocca il capitolo, abbonati o guarda un breve video.",
            "pt": "Este episódio faz parte de um capítulo pago. Desbloqueie o capítulo, assine ou assista a um vídeo curto.",
            "pl": "Ten epizod należy do płatnego rozdziału. Odblokuj rozdział, wykup subskrypcję lub obejrzyj krótki film.",
            "nl": "Deze aflevering hoort bij een betaald hoofdstuk. Ontgrendel het hoofdstuk, neem een abonnement of bekijk een korte video.",
        ],
        "ui.watch_ad": [
            "ru": "Открыть эпизод за ролик",
            "en": "Watch a video to play",
            "es": "Ver un vídeo para jugar",
            "de": "Video ansehen und spielen",
            "fr": "Regarder une vidéo pour jouer",
            "it": "Guarda un video per giocare",
            "pt": "Assistir a um vídeo para jogar",
            "pl": "Obejrzyj film, aby zagrać",
            "nl": "Bekijk een video om te spelen",
        ],
        "ui.ad_unavailable": [
            "ru": "Ролик сейчас недоступен",
            "en": "No video available right now",
            "es": "No hay vídeo disponible ahora",
            "de": "Gerade kein Video verfügbar",
            "fr": "Aucune vidéo disponible pour l'instant",
            "it": "Nessun video disponibile ora",
            "pt": "Nenhum vídeo disponível agora",
            "pl": "Film jest teraz niedostępny",
            "nl": "Er is nu geen video beschikbaar",
        ],
        "ui.ad_cooldown": [
            "ru": "Следующий ролик через %d с",
            "en": "Next video in %ds",
            "es": "Próximo vídeo en %d s",
            "de": "Nächstes Video in %d s",
            "fr": "Prochaine vidéo dans %d s",
            "it": "Prossimo video tra %d s",
            "pt": "Próximo vídeo em %d s",
            "pl": "Następny film za %d s",
            "nl": "Volgende video over %d s",
        ],
    ]

    /// Строка по ключу. Фолбэк: язык → английский → русская база → встроенная → сам ключ.
    /// Английский слой важен: каталог перевода может отставать от контента (квоты переводчика),
    /// и без него игроку показывали русский текст посреди английского экрана.
    public static func s(_ key: String) -> String {
        table[key] ?? fallback[key] ?? base[key] ?? builtin[key]?[lang] ?? builtin[key]?["en"] ?? key
    }

    /// Форматированная строка (для `%d`, `%@`).
    public static func s(_ key: String, _ args: CVarArg...) -> String {
        String(format: s(key), locale: Locale(identifier: "en_US_POSIX"), arguments: args)
    }

    /// Опционально (для локализации контента: если ключа нет — nil, оставляем исходник).
    /// Тот же английский слой: непереведённый уровень читается по-английски, а не по-русски.
    public static func opt(_ key: String) -> String? { table[key] ?? fallback[key] }

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
