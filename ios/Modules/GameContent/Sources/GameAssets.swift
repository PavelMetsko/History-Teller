import SwiftUI
import UIKit

/// Хранилище арта: файлы WebP, а не каталог ассетов.
///
/// Почему не `Assets.xcassets`: actool перекодирует всё в `Assets.car` без потерь, поэтому внутри
/// каталога любой lossy-формат разворачивается обратно (HEIC-исходник раздувался вчетверо).
/// Файлами тот же арт весит 24 МБ вместо 48 и совпадает байт-в-байт с Android — один набор на обе платформы.
///
/// Приоритет источников: скачанное → вшитое в бандл. `resolve` подставляет ContentSync;
/// он же зовёт `invalidate()` после установки новой версии контента.
public enum ArtStore {
    /// Логический путь (`art/char_caesar.webp`) → файл в кеше, если скачан.
    /// Пока не выставлен — работает только вшитый арт.
    public static var resolve: ((String) -> URL?)?

    private static let images = NSCache<NSString, UIImage>()
    private static let presence = NSCache<NSString, NSNumber>()   // NSCache потокобезопасен, в отличие от Dictionary

    /// Заглушка для мест, где вью требует непустой `Image`, а арта нет.
    static let blank = UIImage()

    public static func invalidate() {
        images.removeAllObjects()
        presence.removeAllObjects()
    }

    public static func url(_ name: String) -> URL? {
        if let downloaded = resolve?("art/\(name).webp") { return downloaded }
        return Bundle.gameContent.url(forResource: name, withExtension: "webp")
    }

    /// Есть ли арт. Дёргается из тел вью на каждый кадр, поэтому результат запоминаем — иначе
    /// получаем stat() на каждую позу каждого персонажа в каждой перерисовке.
    public static func exists(_ name: String) -> Bool {
        let key = name as NSString
        if let known = presence.object(forKey: key) { return known.boolValue }
        let found = url(name) != nil
        presence.setObject(NSNumber(value: found), forKey: key)
        return found
    }

    public static func image(_ name: String) -> UIImage? {
        let key = name as NSString
        if let hit = images.object(forKey: key) { return hit }
        guard let url = url(name), let img = UIImage(contentsOfFile: url.path) else { return nil }
        images.setObject(img, forKey: key)
        return img
    }
}

/// Маппинг id контента → имя файла арта и удобные SwiftUI-аксессоры.
public enum GameAssets {
    public static func characterImageName(_ id: String) -> String { "char_\(id)" }
    public static func sceneImageName(_ id: String) -> String { "scene_\(id)" }
    public static func deadImageName(_ id: String) -> String { "char_\(id)_dead" }
    public static func triumphImageName(_ id: String) -> String { "char_\(id)_triumph" }
    public static func defeatedImageName(_ id: String) -> String { "char_\(id)_defeated" }
    public static func plotImageName(_ id: String) -> String { "char_\(id)_plot" }

    public static func hasCharacterArt(_ id: String) -> Bool { ArtStore.exists(characterImageName(id)) }
    /// Есть ли отдельная поза «повержен» (слой 3). Если нет — UI откатывается на ч/б+поворот.
    public static func hasDeadPose(_ id: String) -> Bool { ArtStore.exists(deadImageName(id)) }
    /// Есть ли поза «триумф» (победные состояния). Если нет — обычный спрайт.
    public static func hasTriumphPose(_ id: String) -> Bool { ArtStore.exists(triumphImageName(id)) }
    /// Есть ли поза «разгромлен, но жив» (беглец/разбит/изгнан/отвергнут). Если нет — обычный спрайт.
    public static func hasDefeatedPose(_ id: String) -> Bool { ArtStore.exists(defeatedImageName(id)) }
    /// Есть ли поза «заговорщик» (флаг plotting). Если нет — дрожь-фолбэк.
    public static func hasPlotPose(_ id: String) -> Bool { ArtStore.exists(plotImageName(id)) }
    public static func hasSceneArt(_ id: String) -> Bool { ArtStore.exists(sceneImageName(id)) }
}

public extension Image {
    /// Картинка по готовому имени ассета (`char_caesar_dead` и т.п.) — когда имя уже выбрано
    /// вызывающим. Единственный путь к арту: `Image(name, bundle:)` ищет в каталоге ассетов,
    /// которого в проекте больше нет, и молча рисует пустоту.
    init(art name: String) {
        self.init(uiImage: ArtStore.image(name) ?? ArtStore.blank)
    }

    /// Спрайт персонажа (прозрачный фон).
    static func character(_ id: String) -> Image {
        Image(uiImage: ArtStore.image(GameAssets.characterImageName(id)) ?? ArtStore.blank)
    }
    /// Фон сцены.
    static func scene(_ id: String) -> Image {
        Image(uiImage: ArtStore.image(GameAssets.sceneImageName(id)) ?? ArtStore.blank)
    }
    /// Пропс-объект (кровь, корона, мечи, нож гильотины) — прозрачный.
    static func prop(_ id: String) -> Image {
        Image(uiImage: ArtStore.image("prop_\(id)") ?? ArtStore.blank)
    }
}
