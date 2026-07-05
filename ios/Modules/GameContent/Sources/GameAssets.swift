import SwiftUI
import UIKit

/// Маппинг id контента → имя ассета в Assets.xcassets и удобные SwiftUI-аксессоры.
public enum GameAssets {
    public static func characterImageName(_ id: String) -> String { "char_\(id)" }
    public static func sceneImageName(_ id: String) -> String { "scene_\(id)" }
    public static func deadImageName(_ id: String) -> String { "char_\(id)_dead" }
    public static func triumphImageName(_ id: String) -> String { "char_\(id)_triumph" }
    public static func defeatedImageName(_ id: String) -> String { "char_\(id)_defeated" }
    public static func plotImageName(_ id: String) -> String { "char_\(id)_plot" }

    public static func hasCharacterArt(_ id: String) -> Bool {
        UIImage(named: characterImageName(id), in: .gameContent, compatibleWith: nil) != nil
    }
    /// Есть ли отдельная поза «повержен» (слой 3). Если нет — UI откатывается на ч/б+поворот.
    public static func hasDeadPose(_ id: String) -> Bool {
        UIImage(named: deadImageName(id), in: .gameContent, compatibleWith: nil) != nil
    }
    /// Есть ли поза «триумф» (победные состояния). Если нет — обычный спрайт.
    public static func hasTriumphPose(_ id: String) -> Bool {
        UIImage(named: triumphImageName(id), in: .gameContent, compatibleWith: nil) != nil
    }
    /// Есть ли поза «разгромлен, но жив» (беглец/разбит/изгнан/отвергнут). Если нет — обычный спрайт.
    public static func hasDefeatedPose(_ id: String) -> Bool {
        UIImage(named: defeatedImageName(id), in: .gameContent, compatibleWith: nil) != nil
    }
    /// Есть ли поза «заговорщик» (флаг plotting). Если нет — дрожь-фолбэк.
    public static func hasPlotPose(_ id: String) -> Bool {
        UIImage(named: plotImageName(id), in: .gameContent, compatibleWith: nil) != nil
    }
    public static func hasSceneArt(_ id: String) -> Bool {
        UIImage(named: sceneImageName(id), in: .gameContent, compatibleWith: nil) != nil
    }
}

public extension Image {
    /// Спрайт персонажа (прозрачный фон) из контент-бандла.
    static func character(_ id: String) -> Image {
        Image(GameAssets.characterImageName(id), bundle: .gameContent)
    }
    /// Фон сцены из контент-бандла.
    static func scene(_ id: String) -> Image {
        Image(GameAssets.sceneImageName(id), bundle: .gameContent)
    }
    /// Пропс-объект (кровь, корона, мечи, нож гильотины) — прозрачный, из контент-бандла.
    static func prop(_ id: String) -> Image {
        Image("prop_\(id)", bundle: .gameContent)
    }
}
