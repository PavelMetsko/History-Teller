import SwiftUI
import UIKit

/// Маппинг id контента → имя ассета в Assets.xcassets и удобные SwiftUI-аксессоры.
public enum GameAssets {
    public static func characterImageName(_ id: String) -> String { "char_\(id)" }
    public static func sceneImageName(_ id: String) -> String { "scene_\(id)" }

    public static func hasCharacterArt(_ id: String) -> Bool {
        UIImage(named: characterImageName(id), in: .gameContent, compatibleWith: nil) != nil
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
}
