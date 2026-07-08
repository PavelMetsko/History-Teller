import SwiftUI
import DesignSystem
import GameContent

/// Первый экран при первом запуске: выбор языка (нативными названиями).
/// Выбор применяется сразу — дальнейший онбординг и весь UI идут на нём.
public struct LanguagePickerView: View {
    private let onSelect: (String) -> Void
    public init(onSelect: @escaping (String) -> Void) { self.onSelect = onSelect }

    /// code → нативное имя языка.
    private let languages: [(code: String, name: String)] = [
        ("en", "English"), ("ru", "Русский"), ("es", "Español"),
        ("de", "Deutsch"), ("fr", "Français"), ("it", "Italiano"),
        ("pt", "Português"), ("pl", "Polski"), ("nl", "Nederlands"),
    ]

    private let columns = [GridItem(.flexible(), spacing: 14),
                           GridItem(.flexible(), spacing: 14),
                           GridItem(.flexible(), spacing: 14)]

    public var body: some View {
        ZStack {
            DS.Palette.backdrop.ignoresSafeArea()

            VStack(spacing: 18) {
                Image(systemName: "globe").font(.system(size: 34)).foregroundStyle(DS.Palette.gold)
                Text("History Teller").font(.dsSerif(24)).foregroundStyle(DS.Palette.paper)
                Text("Language · Язык · Sprache")
                    .font(.dsCaption(11)).tracking(1).foregroundStyle(DS.Palette.paper.opacity(0.5))

                LazyVGrid(columns: columns, spacing: 14) {
                    ForEach(languages, id: \.code) { lang in
                        Button { onSelect(lang.code) } label: {
                            Text(lang.name)
                                .font(.dsBody(17)).foregroundStyle(DS.Palette.ink)
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 14)
                                .background(
                                    RoundedRectangle(cornerRadius: 14, style: .continuous)
                                        .fill(DS.Palette.panel)
                                        .overlay(RoundedRectangle(cornerRadius: 14, style: .continuous)
                                            .stroke(DS.Palette.ink, lineWidth: 3))
                                )
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding(.top, 4)
            }
            .padding(.horizontal, 54)
            .padding(.vertical, 26)
            .frame(maxWidth: 660)
        }
    }
}
