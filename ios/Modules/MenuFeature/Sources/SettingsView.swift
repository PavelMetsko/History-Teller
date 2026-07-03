import SwiftUI
import DesignSystem
import GameContent

/// Экран настроек — книжная карточка поверх меню: музыка, звуки, вибрация, язык.
/// Значения в UserDefaults (`ht.music` / `ht.sfx` / `ht.haptics` / `ht.lang`),
/// их читают Audio, Haptics и L10n. По умолчанию звук/вибрация включены, язык — авто.
public struct SettingsView: View {
    @AppStorage("ht.music")   private var music   = true
    @AppStorage("ht.sfx")     private var sfx     = true
    @AppStorage("ht.haptics") private var haptics = true
    @AppStorage("ht.lang")    private var lang    = ""

    private let onClose: () -> Void
    public init(onClose: @escaping () -> Void) { self.onClose = onClose }

    private let langNames: [String: String] = [
        "ru": "Русский", "en": "English", "es": "Español", "de": "Deutsch",
        "fr": "Français", "it": "Italiano", "pt": "Português", "pl": "Polski", "nl": "Nederlands"
    ]

    public var body: some View {
        ZStack {
            Color.black.opacity(0.45).ignoresSafeArea()
                .onTapGesture { onClose() }

            BookPage {
                VStack(spacing: 12) {
                    Text(L10n.s("ui.settings"))
                        .font(.dsSerif(24)).foregroundStyle(DS.Palette.ink).padding(.top, 2)
                    RoundedRectangle(cornerRadius: 2).fill(DS.Palette.gold).frame(width: 90, height: 3)

                    VStack(spacing: 2) {
                        toggleRow(icon: "music.note", title: L10n.s("ui.music"), isOn: $music) { on in
                            if on { Audio.shared.startMusic() } else { Audio.shared.stopMusic() }
                        }
                        divider
                        toggleRow(icon: "speaker.wave.2.fill", title: L10n.s("ui.sound"), isOn: $sfx) { on in
                            if on { Audio.shared.play(.select) }
                        }
                        divider
                        toggleRow(icon: "iphone.radiowaves.left.and.right", title: L10n.s("ui.haptics"), isOn: $haptics) { on in
                            if on { Haptics.light() }
                        }
                        divider
                        languageRow
                    }
                    .padding(.vertical, 2)

                    Button(action: onClose) {
                        Text(L10n.s("ui.done"))
                            .font(.dsSerif(18)).foregroundStyle(DS.Palette.paper)
                            .padding(.horizontal, 44).padding(.vertical, 12)
                            .background(Capsule().fill(DS.Palette.maroon))
                            .overlay(Capsule().strokeBorder(DS.Palette.ink, lineWidth: 2.5))
                    }
                    .buttonStyle(.plain).padding(.top, 2)
                }
                .padding(EdgeInsets(top: 18, leading: 32, bottom: 20, trailing: 32))
                .frame(width: 440)
            }
            .fixedSize()
            .shadow(color: .black.opacity(0.4), radius: 18, y: 10)
        }
    }

    private func toggleRow(icon: String, title: String, isOn: Binding<Bool>,
                           onChange: @escaping (Bool) -> Void) -> some View {
        HStack(spacing: 14) {
            rowIcon(icon)
            Text(title).font(.dsBody(17)).foregroundStyle(DS.Palette.ink)
            Spacer(minLength: 20)
            Toggle("", isOn: isOn)
                .labelsHidden().tint(DS.Palette.success)
                .onChange(of: isOn.wrappedValue) { _, v in onChange(v) }
        }
        .padding(.horizontal, 8).padding(.vertical, 9)
    }

    private var languageRow: some View {
        HStack(spacing: 14) {
            rowIcon("globe")
            Text(L10n.s("ui.language")).font(.dsBody(17)).foregroundStyle(DS.Palette.ink)
            Spacer(minLength: 20)
            Menu {
                Button("Auto") { lang = "" }
                ForEach(L10n.available, id: \.self) { code in
                    Button(langNames[code] ?? code) { lang = code }
                }
            } label: {
                HStack(spacing: 5) {
                    Text(lang.isEmpty ? "Auto" : (langNames[lang] ?? lang))
                        .font(.dsBody(16))
                    Image(systemName: "chevron.up.chevron.down").font(.system(size: 11, weight: .semibold))
                }
                .foregroundStyle(DS.Palette.maroon)
            }
        }
        .padding(.horizontal, 8).padding(.vertical, 9)
    }

    private func rowIcon(_ name: String) -> some View {
        Image(systemName: name)
            .font(.system(size: 18, weight: .semibold))
            .foregroundStyle(DS.Palette.maroon).frame(width: 26)
    }

    private var divider: some View {
        Rectangle().fill(DS.Palette.ink.opacity(0.12)).frame(height: 1)
    }
}
