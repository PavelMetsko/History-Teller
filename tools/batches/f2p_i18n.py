"""Тексты патча 4.0 (F2P + мета): добавляет ui.* ключи во все каталоги Content/i18n.
Существующие значения не трогает (каталог — источник правды). Запуск: python3 tools/batches/f2p_i18n.py"""
import json, pathlib

LANGS = ["ru", "en", "es", "pt", "pl", "de", "it", "nl", "fr"]
ROOT = pathlib.Path(__file__).resolve().parents[2] / "Content" / "i18n"

RANKS = {
    "ru": ["Ученик", "Переписчик", "Писарь", "Летописец", "Хронист", "Книжник", "Знаток", "Историк", "Архивариус", "Магистр", "Профессор", "Академик", "Мудрец", "Хранитель архива", "Хранитель времён"],
    "en": ["Apprentice", "Copyist", "Scribe", "Annalist", "Chronicler", "Bookman", "Connoisseur", "Historian", "Archivist", "Master", "Professor", "Academician", "Sage", "Keeper of Archives", "Keeper of Time"],
    "es": ["Aprendiz", "Copista", "Escriba", "Analista", "Cronista", "Erudito", "Conocedor", "Historiador", "Archivero", "Maestro", "Profesor", "Académico", "Sabio", "Guardián del archivo", "Guardián del tiempo"],
    "pt": ["Aprendiz", "Copista", "Escriba", "Analista", "Cronista", "Erudito", "Conhecedor", "Historiador", "Arquivista", "Mestre", "Professor", "Acadêmico", "Sábio", "Guardião do arquivo", "Guardião do tempo"],
    "pl": ["Uczeń", "Kopista", "Skryba", "Annalista", "Kronikarz", "Bibliofil", "Znawca", "Historyk", "Archiwista", "Magister", "Profesor", "Akademik", "Mędrzec", "Strażnik archiwum", "Strażnik czasu"],
    "de": ["Lehrling", "Kopist", "Schreiber", "Annalist", "Chronist", "Gelehrter", "Kenner", "Historiker", "Archivar", "Magister", "Professor", "Akademiker", "Weiser", "Hüter des Archivs", "Hüter der Zeit"],
    "it": ["Apprendista", "Copista", "Scriba", "Annalista", "Cronista", "Erudito", "Conoscitore", "Storico", "Archivista", "Maestro", "Professore", "Accademico", "Saggio", "Custode dell'archivio", "Custode del tempo"],
    "nl": ["Leerling", "Kopiist", "Schrijver", "Annalist", "Kroniekschrijver", "Geleerde", "Kenner", "Historicus", "Archivaris", "Magister", "Professor", "Academicus", "Wijze", "Hoeder van het archief", "Hoeder van de tijd"],
    "fr": ["Apprenti", "Copiste", "Scribe", "Annaliste", "Chroniqueur", "Lettré", "Connaisseur", "Historien", "Archiviste", "Maître", "Professeur", "Académicien", "Sage", "Gardien des archives", "Gardien du temps"],
}

# ключ → тексты в порядке LANGS
T = {
    "ui.lvl_short": ["Ур. %d", "Lv. %d", "Nv. %d", "Nv. %d", "Poz. %d", "Stufe %d", "Liv. %d", "Niv. %d", "Niv. %d"],
    "ui.new_rank": ["Новое звание!", "New rank!", "¡Nuevo rango!", "Novo título!", "Nowa ranga!", "Neuer Rang!", "Nuovo grado!", "Nieuwe rang!", "Nouveau rang !"],
    "ui.card_added": ["Карточка в альбоме", "Card added to album", "Carta añadida al álbum", "Carta adicionada ao álbum", "Karta dodana do albumu", "Karte im Album", "Carta aggiunta all'album", "Kaart in het album", "Carte ajoutée à l'album"],
    "ui.streak_days": ["Серия: %d дн.", "Streak: %d d", "Racha: %d d", "Sequência: %d d", "Seria: %d dni", "Serie: %d T.", "Serie: %d g", "Reeks: %d d", "Série : %d j"],
    "ui.streak_milestone": ["Награда за серию", "Streak reward", "Premio por racha", "Prêmio da sequência", "Nagroda za serię", "Serienbonus", "Premio serie", "Reeksbeloning", "Récompense de série"],
    "ui.daily_bonus": ["Эпизод дня ×2", "Episode of the day ×2", "Episodio del día ×2", "Episódio do dia ×2", "Epizod dnia ×2", "Episode des Tages ×2", "Episodio del giorno ×2", "Aflevering van de dag ×2", "Épisode du jour ×2"],
    "ui.chapter_master": ["Знаток: %@", "Master of %@", "Experto: %@", "Mestre: %@", "Znawca: %@", "Kenner: %@", "Esperto: %@", "Kenner: %@", "Expert : %@"],
    "ui.next_episode": ["Следующий эпизод", "Next episode", "Siguiente episodio", "Próximo episódio", "Następny epizod", "Nächste Episode", "Episodio successivo", "Volgende aflevering", "Épisode suivant"],
    "ui.to_map": ["К карте", "To map", "Al mapa", "Para o mapa", "Do mapy", "Zur Karte", "Alla mappa", "Naar kaart", "Vers la carte"],
    "ui.hints_out_title": ["Подсказки закончились", "Out of hints", "Sin pistas", "Sem dicas", "Brak podpowiedzi", "Keine Tipps mehr", "Suggerimenti finiti", "Geen hints meer", "Plus d'indices"],
    "ui.hints_out_body": ["Посмотри короткий ролик — и подсказка твоя.", "Watch a short video to get a hint.", "Mira un vídeo corto y obtén una pista.", "Assista a um vídeo curto e ganhe uma dica.", "Obejrzyj krótki film, a dostaniesz podpowiedź.", "Sieh dir ein kurzes Video an und erhalte einen Tipp.", "Guarda un breve video e ottieni un suggerimento.", "Bekijk een korte video en krijg een hint.", "Regarde une courte vidéo pour obtenir un indice."],
    "ui.watch_video": ["Смотреть ролик", "Watch video", "Ver vídeo", "Ver vídeo", "Obejrzyj film", "Video ansehen", "Guarda video", "Video bekijken", "Voir la vidéo"],
    "ui.video_loading": ["Ролик загружается…", "Video is loading…", "Cargando vídeo…", "Carregando vídeo…", "Ładowanie filmu…", "Video wird geladen…", "Caricamento video…", "Video laden…", "Chargement de la vidéo…"],
    "ui.no_ads": ["Без рекламы", "No ads", "Sin anuncios", "Sem anúncios", "Bez reklam", "Ohne Werbung", "Senza pubblicità", "Zonder advertenties", "Sans publicité"],
    "ui.premium_b1": ["Никакой рекламы между эпизодами", "No ads between episodes", "Sin anuncios entre episodios", "Sem anúncios entre episódios", "Żadnych reklam między epizodami", "Keine Werbung zwischen Episoden", "Nessuna pubblicità tra gli episodi", "Geen advertenties tussen afleveringen", "Aucune pub entre les épisodes"],
    "ui.premium_b2": ["Безлимитные подсказки", "Unlimited hints", "Pistas ilimitadas", "Dicas ilimitadas", "Nielimitowane podpowiedzi", "Unbegrenzte Tipps", "Suggerimenti illimitati", "Onbeperkte hints", "Indices illimités"],
    "ui.premium_b3": ["Поддержка автора и новых глав", "Support the author and new chapters", "Apoya al autor y nuevos capítulos", "Apoie o autor e novos capítulos", "Wsparcie autora i nowych rozdziałów", "Unterstütze den Autor und neue Kapitel", "Sostieni l'autore e nuovi capitoli", "Steun de maker en nieuwe hoofdstukken", "Soutiens l'auteur et les nouveaux chapitres"],
    "ui.premium_forever": ["Навсегда — %@", "Forever — %@", "Para siempre — %@", "Para sempre — %@", "Na zawsze — %@", "Für immer — %@", "Per sempre — %@", "Voor altijd — %@", "Pour toujours — %@"],
    "ui.premium_active": ["Реклама отключена. Спасибо! ❤️", "Ads are off. Thank you! ❤️", "Anuncios desactivados. ¡Gracias! ❤️", "Anúncios desativados. Obrigado! ❤️", "Reklamy wyłączone. Dziękujemy! ❤️", "Werbung ist aus. Danke! ❤️", "Pubblicità disattivata. Grazie! ❤️", "Advertenties uit. Bedankt! ❤️", "Publicité désactivée. Merci ! ❤️"],
    "ui.gift_title": ["Подарок дня", "Daily gift", "Regalo diario", "Presente do dia", "Prezent dnia", "Tagesgeschenk", "Regalo del giorno", "Dagcadeau", "Cadeau du jour"],
    "ui.gift_day": ["День %d", "Day %d", "Día %d", "Dia %d", "Dzień %d", "Tag %d", "Giorno %d", "Dag %d", "Jour %d"],
    "ui.gift_claim": ["Забрать", "Claim", "Recoger", "Pegar", "Odbierz", "Abholen", "Ritira", "Ophalen", "Récupérer"],
    "ui.gift_body": ["Заходи каждый день — подарки растут", "Come back every day — gifts grow", "Vuelve cada día: los regalos crecen", "Volte todo dia — os presentes crescem", "Wracaj codziennie — prezenty rosną", "Komm täglich zurück — die Geschenke wachsen", "Torna ogni giorno: i regali crescono", "Kom elke dag terug — cadeaus groeien", "Reviens chaque jour — les cadeaux grandissent"],
    "ui.daily_title": ["Эпизод дня", "Episode of the day", "Episodio del día", "Episódio do dia", "Epizod dnia", "Episode des Tages", "Episodio del giorno", "Aflevering van de dag", "Épisode du jour"],
    "ui.daily_done": ["Готово! Новый эпизод — завтра", "Done! New episode tomorrow", "¡Hecho! Nuevo episodio mañana", "Feito! Novo episódio amanhã", "Gotowe! Nowy epizod jutro", "Geschafft! Neue Episode morgen", "Fatto! Nuovo episodio domani", "Klaar! Morgen een nieuwe", "Fait ! Nouvel épisode demain"],
    "ui.streak_lost": ["Серия %d дн. прервалась", "Your %d-day streak broke", "Tu racha de %d días se rompió", "Sua sequência de %d dias acabou", "Twoja seria %d dni przerwana", "Deine %d-Tage-Serie ist gerissen", "La tua serie di %d giorni si è interrotta", "Je reeks van %d dagen is verbroken", "Ta série de %d jours est rompue"],
    "ui.streak_restore": ["Вернуть серию", "Restore streak", "Recuperar racha", "Recuperar sequência", "Przywróć serię", "Serie retten", "Recupera serie", "Reeks herstellen", "Restaurer la série"],
    "ui.album": ["Альбом", "Album", "Álbum", "Álbum", "Album", "Album", "Album", "Album", "Album"],
    "ui.album_locked": ["Ещё не открыто", "Not yet discovered", "Aún no descubierto", "Ainda não descoberto", "Jeszcze nieodkryte", "Noch nicht entdeckt", "Non ancora scoperto", "Nog niet ontdekt", "Pas encore découvert"],
    "ui.push.streak": ["🔥 Серия %d дн. сгорит в полночь — один эпизод, и она спасена", "🔥 Your %d-day streak ends at midnight — one episode saves it", "🔥 Tu racha de %d días termina a medianoche: un episodio la salva", "🔥 Sua sequência de %d dias acaba à meia-noite — um episódio salva", "🔥 Seria %d dni kończy się o północy — jeden epizod ją uratuje", "🔥 Deine %d-Tage-Serie endet um Mitternacht — eine Episode rettet sie", "🔥 La tua serie di %d giorni finisce a mezzanotte: un episodio la salva", "🔥 Je reeks van %d dagen eindigt om middernacht — één aflevering redt hem", "🔥 Ta série de %d jours s'arrête à minuit — un épisode la sauve"],
    "ui.push.daily": ["Эпизод дня: «%@»", "Episode of the day: “%@”", "Episodio del día: «%@»", "Episódio do dia: “%@”", "Epizod dnia: „%@”", "Episode des Tages: „%@“", "Episodio del giorno: «%@»", "Aflevering van de dag: ‘%@’", "Épisode du jour : « %@ »"],
    "ui.push.gift": ["Тебя ждёт подарок 🎁 Загляни за подсказками", "A gift is waiting for you 🎁 Grab your hints", "Te espera un regalo 🎁 Recoge tus pistas", "Um presente te espera 🎁 Pegue suas dicas", "Czeka na ciebie prezent 🎁 Odbierz podpowiedzi", "Ein Geschenk wartet auf dich 🎁 Hol dir Tipps", "Ti aspetta un regalo 🎁 Prendi i suggerimenti", "Er wacht een cadeau 🎁 Haal je hints", "Un cadeau t'attend 🎁 Viens chercher tes indices"],
    "ui.push.week": ["История ждёт: «%@»", "History awaits: “%@”", "La historia te espera: «%@»", "A história te espera: “%@”", "Historia czeka: „%@”", "Die Geschichte wartet: „%@“", "La storia ti aspetta: «%@»", "De geschiedenis wacht: ‘%@’", "L'histoire t'attend : « %@ »"],
    "ui.chapter_noads_title": ["Глава без рекламы", "Chapter without ads", "Capítulo sin anuncios", "Capítulo sem anúncios", "Rozdział bez reklam", "Kapitel ohne Werbung", "Capitolo senza pubblicità", "Hoofdstuk zonder advertenties", "Chapitre sans publicité"],
    "ui.chapter_noads_b1": ["Никакой рекламы в этой главе", "No ads in this chapter", "Sin anuncios en este capítulo", "Sem anúncios neste capítulo", "Żadnych reklam w tym rozdziale", "Keine Werbung in diesem Kapitel", "Nessuna pubblicità in questo capitolo", "Geen advertenties in dit hoofdstuk", "Aucune pub dans ce chapitre"],
    "ui.chapter_noads_b2": ["Безлимитные подсказки в этой главе", "Unlimited hints in this chapter", "Pistas ilimitadas en este capítulo", "Dicas ilimitadas neste capítulo", "Nielimitowane podpowiedzi w tym rozdziale", "Unbegrenzte Tipps in diesem Kapitel", "Suggerimenti illimitati in questo capitolo", "Onbeperkte hints in dit hoofdstuk", "Indices illimités dans ce chapitre"],
    "ui.chapter_noads_cta": ["Убрать рекламу — %@", "Remove ads — %@", "Quitar anuncios — %@", "Remover anúncios — %@", "Usuń reklamy — %@", "Werbung entfernen — %@", "Rimuovi pubblicità — %@", "Advertenties weg — %@", "Retirer la pub — %@"],
    "ui.flame.1": ["Искра", "Spark", "Chispa", "Faísca", "Iskra", "Funke", "Scintilla", "Vonk", "Étincelle"],
    "ui.flame.2": ["Свеча", "Candle", "Vela", "Vela", "Świeca", "Kerze", "Candela", "Kaars", "Bougie"],
    "ui.flame.3": ["Факел", "Torch", "Antorcha", "Tocha", "Pochodnia", "Fackel", "Torcia", "Fakkel", "Torche"],
    "ui.flame.4": ["Костёр", "Bonfire", "Hoguera", "Fogueira", "Ognisko", "Lagerfeuer", "Falò", "Kampvuur", "Feu de camp"],
    "ui.flame.5": ["Маяк", "Beacon", "Faro", "Farol", "Latarnia", "Leuchtfeuer", "Faro", "Baken", "Phare"],
    "ui.flame.6": ["Вечный огонь", "Eternal flame", "Llama eterna", "Chama eterna", "Wieczny ogień", "Ewige Flamme", "Fiamma eterna", "Eeuwige vlam", "Flamme éternelle"],
    "ui.flame_road": ["Путь огня", "Path of Fire", "Camino del fuego", "Caminho do fogo", "Ścieżka ognia", "Pfad des Feuers", "Via del fuoco", "Pad van vuur", "Chemin du feu"],
    "ui.flame_bonus": ["+%d%% опыта", "+%d%% XP", "+%d%% XP", "+%d%% XP", "+%d%% XP", "+%d%% EP", "+%d%% XP", "+%d%% XP", "+%d%% XP"],
    "ui.flame_new": ["Пламя разгорается!", "Your flame grows!", "¡Tu llama crece!", "Sua chama cresce!", "Płomień rośnie!", "Deine Flamme wächst!", "La tua fiamma cresce!", "Je vlam groeit!", "Ta flamme grandit !"],
    "ui.flame_best": ["Рекорд: %d дн.", "Best: %d d", "Récord: %d d", "Recorde: %d d", "Rekord: %d dni", "Rekord: %d T.", "Record: %d g", "Record: %d d", "Record : %d j"],
    "ui.flame_rule": ["Решай хотя бы один эпизод в день — пламя растёт, опыт и подсказки тоже", "Solve at least one episode a day — your flame, XP and hints grow", "Resuelve al menos un episodio al día: crecen tu llama, tu XP y tus pistas", "Resolva ao menos um episódio por dia — sua chama, XP e dicas crescem", "Rozwiązuj co najmniej jeden epizod dziennie — rośnie płomień, XP i podpowiedzi", "Löse jeden Tag mindestens eine Episode — Flamme, EP und Tipps wachsen", "Risolvi almeno un episodio al giorno: crescono fiamma, XP e suggerimenti", "Los elke dag minstens één aflevering op — je vlam, XP en hints groeien", "Résous au moins un épisode par jour — ta flamme, ton XP et tes indices grandissent"],
    "ui.flame_next": ["До «%@» — %d дн.", "“%@” in %d d", "«%@» en %d d", "“%@” em %d d", "Do „%@” — %d dni", "„%@“ in %d T.", "«%@» tra %d g", "‘%@’ over %d d", "« %@ » dans %d j"],
    "ui.flame_today": ["Сегодня уже засчитано ✓", "Today counted ✓", "Hoy ya cuenta ✓", "Hoje já contou ✓", "Dziś już zaliczone ✓", "Heute schon gezählt ✓", "Oggi già contato ✓", "Vandaag al geteld ✓", "Aujourd'hui compté ✓"],
    "ui.flame_todo": ["Реши эпизод сегодня, чтобы не погасло", "Solve an episode today to keep it lit", "Resuelve un episodio hoy para no apagarla", "Resolva um episódio hoje para não apagar", "Rozwiąż dziś epizod, żeby nie zgasł", "Löse heute eine Episode, damit sie nicht erlischt", "Risolvi un episodio oggi per non spegnerla", "Los vandaag een aflevering op om hem brandend te houden", "Résous un épisode aujourd'hui pour qu'elle ne s'éteigne pas"],
    "ui.stats_title": ["Твой путь", "Your journey", "Tu camino", "Sua jornada", "Twoja droga", "Deine Reise", "Il tuo percorso", "Jouw reis", "Ton parcours"],
}

def main():
    for i, lang in enumerate(LANGS):
        path = ROOT / f"{lang}.json"
        d = json.loads(path.read_text(encoding="utf-8"))
        added = 0
        for n, name in enumerate(RANKS[lang], 1):
            if f"ui.rank.{n}" not in d: d[f"ui.rank.{n}"] = name; added += 1
        for k, vals in T.items():
            assert len(vals) == len(LANGS), k
            if k not in d: d[k] = vals[i]; added += 1
        path.write_text(json.dumps(d, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(lang, "+", added)

if __name__ == "__main__":
    main()
