import Foundation
import AVFoundation

/// Звук игры: SFX (пул плееров для наложения) и фоновая музыка. Файлы — из контент-бандла (AAC/.m4a).
///
/// Музыка играет через AVAudioEngine, а не AVAudioPlayer: у AAC в начале файла лежит priming-пакет,
/// и `numberOfLoops = -1` давал слышимый щелчок-паузу на каждом витке (у нас луп ~75 с — щёлкало
/// постоянно). AVAudioFile отдаёт уже обрезанный PCM, а `scheduleBuffer(.loops)` крутит его без шва.
///
/// Два дека вместо одного нужны для кроссфейда: раньше смена трека была `stop()` + `play()` — обрыв.
public final class Audio {
    public static let shared = Audio()

    /// Переключатели из настроек (по умолчанию вкл). Ключи общие с SettingsView.
    public var musicOn: Bool { (UserDefaults.standard.object(forKey: "ht.music") as? Bool) ?? true }
    public var sfxOn: Bool   { (UserDefaults.standard.object(forKey: "ht.sfx")   as? Bool) ?? true }

    public enum SFX: String, CaseIterable {
        case place, remove, select, ally, conspire, love, kill, crown, envy, win, error

        /// Громкие сюжетные удары — под них музыка приседает, чтобы не спорить с ними.
        var ducks: Bool { self == .kill || self == .win || self == .crown }
    }

    // MARK: - Музыка

    /// Дек = узел воспроизведения одного трека. Их два: пока один затухает, второй уже играет.
    private final class Deck {
        let node = AVAudioPlayerNode()
        var name: String?
        var buffer: AVAudioPCMBuffer?
    }

    private let engine = AVAudioEngine()
    private let decks = [Deck(), Deck()]
    private var active = 0
    private var engineReady = false
    private var buffers: [String: AVAudioPCMBuffer] = [:]

    /// База громкости музыки. Треки нормализованы в −20 LUFS, 0.5 даёт ту же громкость,
    /// что старые 0.3 на ненормализованных файлах.
    private var musicBase: Float = 0.5
    private var duck: Float = 1.0
    private var fade: [Float] = [0, 0]
    private var fadeTimer: DispatchSourceTimer?
    private var duckWork: DispatchWorkItem?

    private static let fadeStep: Float = 0.04      // 40 мс на шаг
    private static let crossfade: Float = 1.1      // с

    // MARK: - SFX

    private var pools: [SFX: [AVAudioPlayer]] = [:]
    private let poolSize = 3

    private init() {
        #if os(iOS)
        try? AVAudioSession.sharedInstance().setCategory(.ambient, options: [.mixWithOthers])
        try? AVAudioSession.sharedInstance().setActive(true)
        #endif
        NotificationCenter.default.addObserver(
            self, selector: #selector(configChanged),
            name: .AVAudioEngineConfigurationChange, object: engine)
    }

    /// Сбросить кеш. Зовётся после синхронизации контента: пулы и буферы набиваются лениво,
    /// и без сброса звук, приехавший из облака, молчал бы до перезапуска.
    public func reset() {
        pools.removeAll()
        buffers.removeAll()
        let playing = decks[active].name
        stopMusic()
        if let playing { startMusic(named: playing) }
    }

    public func preload() {
        for s in SFX.allCases { _ = pool(for: s) }
    }

    /// Скачанный трек перекрывает вшитый — звук тоже приезжает из облака.
    private static func audioURL(_ name: String) -> URL? {
        ContentSync.shared.fileURL("audio/\(name).m4a")
            ?? Bundle.gameContent.url(forResource: name, withExtension: "m4a")
    }

    // MARK: - SFX

    private func pool(for s: SFX) -> [AVAudioPlayer] {
        if let p = pools[s] { return p }
        guard let url = Self.audioURL(s.rawValue) else {
            pools[s] = []; return []
        }
        var arr: [AVAudioPlayer] = []
        for _ in 0..<poolSize {
            if let p = try? AVAudioPlayer(contentsOf: url) {
                p.enableRate = true            // нужен для рандомизации питча (см. play)
                p.prepareToPlay()
                arr.append(p)
            }
        }
        pools[s] = arr
        return arr
    }

    public func play(_ s: SFX, volume: Float = 1.0) {
        guard sfxOn else { return }
        let p = pool(for: s)
        guard let player = p.first(where: { !$0.isPlaying }) ?? p.first else { return }
        player.volume = volume
        // Микро-разброс высоты: один и тот же сэмпл на каждый тап слышится как долбёжка.
        player.rate = Float.random(in: 0.97...1.03)
        player.currentTime = 0
        player.play()
        if s.ducks { duckMusic() }
    }

    /// Приседание музыки под сюжетный удар: −5 дБ на время звука, потом обратно.
    private func duckMusic() {
        duckWork?.cancel()
        duck = 0.56
        applyVolumes()
        let work = DispatchWorkItem { [weak self] in
            self?.duck = 1.0
            self?.applyVolumes()
        }
        duckWork = work
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.1, execute: work)
    }

    // MARK: - Музыка

    /// Запустить фоновую тему по имени. Та же тема не перезапускается; другая — вводится кроссфейдом.
    public func startMusic(named name: String = "theme", volume: Float = 0.5) {
        musicBase = volume
        guard musicOn else { return }
        if decks[active].name == name, decks[active].node.isPlaying {
            applyVolumes()
            return
        }
        guard let buffer = buffer(for: name), prepareEngine(format: buffer.format) else { return }

        let next = 1 - active
        let deck = decks[next]
        deck.node.stop()
        deck.name = name
        deck.buffer = buffer
        deck.node.scheduleBuffer(buffer, at: nil, options: [.loops])
        fade[next] = 0
        applyVolumes()
        deck.node.play()
        active = next
        runFade()
    }

    public func stopMusic() {
        fadeTimer?.cancel(); fadeTimer = nil
        for (i, d) in decks.enumerated() {
            d.node.stop()
            d.name = nil
            d.buffer = nil
            fade[i] = 0
        }
    }

    /// Декодируем весь трек в PCM один раз: AVAudioFile снимает priming/padding AAC,
    /// поэтому склейка лупа получается сэмпл-в-сэмпл.
    private func buffer(for name: String) -> AVAudioPCMBuffer? {
        if let b = buffers[name] { return b }
        guard let url = Self.audioURL(name),
              let file = try? AVAudioFile(forReading: url),
              let buf = AVAudioPCMBuffer(pcmFormat: file.processingFormat,
                                         frameCapacity: AVAudioFrameCount(file.length)),
              (try? file.read(into: buf)) != nil else { return nil }
        buffers[name] = buf
        return buf
    }

    private func prepareEngine(format: AVAudioFormat) -> Bool {
        if !engineReady {
            for d in decks {
                engine.attach(d.node)
                engine.connect(d.node, to: engine.mainMixerNode, format: format)
            }
            engineReady = true
        }
        if !engine.isRunning {
            engine.prepare()
            do { try engine.start() } catch { return false }
        }
        return true
    }

    /// Один таймер ведёт оба дека: активный к 1, остальные к 0. Ушедший в 0 — останавливается.
    private func runFade() {
        fadeTimer?.cancel()
        let timer = DispatchSource.makeTimerSource(queue: .main)
        timer.schedule(deadline: .now(), repeating: .milliseconds(40))
        timer.setEventHandler { [weak self] in
            guard let self else { return }
            let step = Self.fadeStep / Self.crossfade
            var busy = false
            for i in 0..<self.decks.count {
                let target: Float = (i == self.active) ? 1 : 0
                if abs(self.fade[i] - target) > 0.001 {
                    self.fade[i] += (target > self.fade[i]) ? step : -step
                    self.fade[i] = min(1, max(0, self.fade[i]))
                    busy = true
                }
                if self.fade[i] == 0, i != self.active, self.decks[i].node.isPlaying {
                    self.decks[i].node.stop()
                    self.decks[i].name = nil
                }
            }
            self.applyVolumes()
            if !busy { self.fadeTimer?.cancel(); self.fadeTimer = nil }
        }
        fadeTimer = timer
        timer.resume()
    }

    private func applyVolumes() {
        for (i, d) in decks.enumerated() {
            d.node.volume = musicBase * duck * fade[i]
        }
    }

    /// Смена маршрута/наушников роняет граф — поднимаем и продолжаем текущий трек.
    @objc private func configChanged() {
        guard engineReady, let name = decks[active].name else { return }
        DispatchQueue.main.async { [weak self] in
            guard let self, !self.engine.isRunning else { return }
            self.stopMusic()
            self.startMusic(named: name, volume: self.musicBase)
        }
    }
}
