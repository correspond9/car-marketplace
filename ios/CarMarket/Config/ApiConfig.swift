import Foundation

enum ApiConfig {
    #if DEBUG
    static let baseURL = URL(string: "http://127.0.0.1:8000/api/v1/")!
    #else
    static let baseURL = URL(string: "https://api.auto.linkpc.net/api/v1/")!
    #endif
}
