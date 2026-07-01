import Foundation

@MainActor
final class TokenStore: ObservableObject {
    static let shared = TokenStore()

    @Published private(set) var accessToken: String?
    @Published private(set) var refreshToken: String?

    private let accessKey = "carmarket.access_token"
    private let refreshKey = "carmarket.refresh_token"

    var isLoggedIn: Bool { accessToken != nil }

    private init() {
        accessToken = UserDefaults.standard.string(forKey: accessKey)
        refreshToken = UserDefaults.standard.string(forKey: refreshKey)
    }

    func save(access: String, refresh: String) {
        accessToken = access
        refreshToken = refresh
        UserDefaults.standard.set(access, forKey: accessKey)
        UserDefaults.standard.set(refresh, forKey: refreshKey)
    }

    func clear() {
        accessToken = nil
        refreshToken = nil
        UserDefaults.standard.removeObject(forKey: accessKey)
        UserDefaults.standard.removeObject(forKey: refreshKey)
    }
}
