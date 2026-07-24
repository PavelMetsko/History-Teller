import Foundation

/// Юридические ссылки, обязательные для подписок (App Store Guideline 3.1.2).
/// Privacy Policy — своя страница (GitHub Pages); Terms of Use — стандартный Apple EULA.
public enum Legal {
    public static let privacyURL = URL(string: "https://pavelmetsko.github.io/History-Teller/privacy.html")!
    public static let termsURL   = URL(string: "https://www.apple.com/legal/internet-services/itunes/dev/stdeula/")!
}
