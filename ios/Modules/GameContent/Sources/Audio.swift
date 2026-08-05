import Foundation
import AVFoundation

/// Проигрывание SFX (пул плееров для наложения) и фоновой музыки. Файлы — из контент-бандла (AAC/.m4a).
public final class Audio {
    public static let shared = Audio()

    /// Переключатели из настроек (по умолчанию вкл). Ключи общие с SettingsView.
    public var musicOn: Bool { (UserDefaults.standard.object(forKey: "ht.music") as? Bool) ?? true }
    public var sfxOn: Bool   { (UserDefaults.standard.object(forKey: "ht.sfx")   as? Bool) ?? true }

    public enum SFX: String, CaseIterable {
        case place, remove, select, ally, conspire, love, kill, crown, envy, win, error
    }

    private var pools: [SFX: [AVAudioPlayer]] = [:]
    private var music: AVAudioPlayer?
    private let poolSize = 3

    private init() {
        #if os(iOS)
        try? AVAudioSession.sharedInstance().setCategory(.ambient, options: [.mixWithOthers])
        try? AVAudioSession.sharedInstance().setActive(true)
        #endif
    }

    /// Сбросить кеш плееров. Зовётся после синхронизации контента: пулы набиваются лениво,
    /// и без сброса звук, приехавший из облака, молчал бы до перезапуска.
    public func reset() {
        pools.removeAll()
        currentMusicName = nil
    }

    public func preload() {
        for s in SFX.allCases { _ = pool(for: s) }
    }

    /// Скачанный трек перекрывает вшитый — звук тоже приезжает из облака.
    private static func audioURL(_ name: String) -> URL? {
        ContentSync.shared.fileURL("audio/\(name).m4a")
            ?? Bundle.gameContent.url(forResource: name, withExtension: "m4a")
    }

    private func pool(for s: SFX) -> [AVAudioPlayer] {
        if let p = pools[s] { return p }
        guard let url = Self.audioURL(s.rawValue) else {
            pools[s] = []; return []
        }
        var arr: [AVAudioPlayer] = []
        for _ in 0..<poolSize {
            if let p = try? AVAudioPlayer(contentsOf: url) { p.prepareToPlay(); arr.append(p) }
        }
        pools[s] = arr
        return arr
    }

    public func play(_ s: SFX, volume: Float = 1.0) {
        guard sfxOn else { return }
        let p = pool(for: s)
        guard let player = p.first(where: { !$0.isPlaying }) ?? p.first else { return }
        player.volume = volume
        player.currentTime = 0
        player.play()
    }

    private var currentMusicName: String?

    /// Запустить фоновую тему по имени. Если та же тема уже играет — не перезапускаем (сквозняк).
    public func startMusic(named name: String = "theme", volume: Float = 0.3) {
        guard musicOn else { return }
        if currentMusicName == name, music?.isPlaying == true {
            music?.volume = volume
            return
        }
        music?.stop()
        guard let url = Self.audioURL(name) else { return }
        let player = try? AVAudioPlayer(contentsOf: url)
        player?.numberOfLoops = -1
        player?.volume = volume
        player?.prepareToPlay()
        player?.play()
        music = player
        currentMusicName = name
    }

    public func stopMusic() {
        music?.stop()
        currentMusicName = nil
    }
}
