import Foundation

final class ApiClient {
    static let shared = ApiClient()
    private let session: URLSession
    private let decoder: JSONDecoder

    private init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        session = URLSession(configuration: config)
        decoder = JSONDecoder()
    }

    func request<T: Decodable>(
        path: String,
        method: String = "GET",
        body: Encodable? = nil,
        authenticated: Bool = false,
    ) async throws -> T {
        guard let url = URL(string: path, relativeTo: ApiConfig.baseURL) else {
            throw ApiError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        if authenticated, let token = await TokenStore.shared.accessToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        if let body {
            request.httpBody = try JSONEncoder().encode(AnyEncodable(body))
        }

        do {
            let (data, response) = try await session.data(for: request)
            guard let http = response as? HTTPURLResponse else {
                throw ApiError.network(URLError(.badServerResponse))
            }
            guard (200 ... 299).contains(http.statusCode) else {
                let message = (try? decoder.decode(ApiErrorResponse.self, from: data))?.error?.message
                throw ApiError.http(http.statusCode, message)
            }
            if http.statusCode == 204 || data.isEmpty {
                if T.self == EmptyResponse.self {
                    return EmptyResponse() as! T
                }
            }
            do {
                return try decoder.decode(T.self, from: data)
            } catch {
                throw ApiError.decoding
            }
        } catch let error as ApiError {
            throw error
        } catch {
            throw ApiError.network(error)
        }
    }

    func uploadPut(urlString: String, data: Data, contentType: String) async throws {
        guard let url = URL(string: urlString) else { throw ApiError.invalidURL }
        var request = URLRequest(url: url)
        request.httpMethod = "PUT"
        request.setValue(contentType, forHTTPHeaderField: "Content-Type")
        let (_, response) = try await session.upload(for: request, from: data)
        guard let http = response as? HTTPURLResponse, (200 ... 299).contains(http.statusCode) else {
            throw ApiError.http((response as? HTTPURLResponse)?.statusCode ?? 0, "Image upload failed")
        }
    }
}

struct EmptyResponse: Decodable {
    init() {}
}

private struct AnyEncodable: Encodable {
    private let encode: (Encoder) throws -> Void
    init(_ wrapped: Encodable) {
        encode = wrapped.encode
    }
    func encode(to encoder: Encoder) throws {
        try encode(encoder)
    }
}

private struct OtpRequest: Encodable { let phone: String }
private struct OtpVerify: Encodable { let phone: String; let otp: String }

@MainActor
final class AuthService: ObservableObject {
    static let shared = AuthService()
    private let client = ApiClient.shared
    private let tokens = TokenStore.shared

    var isLoggedIn: Bool { tokens.isLoggedIn }

    func requestOtp(phone: String) async throws {
        let normalized = normalizePhone(phone)
        let _: EmptyResponse = try await client.request(
            path: "auth/otp/request",
            method: "POST",
            body: OtpRequest(phone: normalized),
        )
    }

    func verifyOtp(phone: String, otp: String) async throws {
        let normalized = normalizePhone(phone)
        let response: TokenResponse = try await client.request(
            path: "auth/otp/verify",
            method: "POST",
            body: OtpVerify(phone: normalized, otp: otp),
        )
        tokens.save(access: response.accessToken, refresh: response.refreshToken)
    }

    func logout() {
        tokens.clear()
    }

    func deleteAccount() async throws {
        let _: EmptyResponse = try await client.request(
            path: "auth/account",
            method: "DELETE",
            authenticated: true,
        )
        tokens.clear()
    }

    func getMe() async throws -> UserMe {
        try await client.request(path: "users/me", authenticated: true)
    }

    private func normalizePhone(_ phone: String) -> String {
        let digits = phone.filter(\.isNumber)
        if digits.count == 10 { return digits }
        if digits.count == 12, digits.hasPrefix("91") {
            return String(digits.dropFirst(2))
        }
        return digits
    }
}

@MainActor
final class ListingService {
    static let shared = ListingService()
    private let client = ApiClient.shared

    func search(query: String? = nil, city: String? = nil, limit: Int = 20) async throws -> [Listing] {
        var components = URLComponents()
        components.path = "listings"
        var items: [URLQueryItem] = [
            URLQueryItem(name: "sort", value: "newest"),
            URLQueryItem(name: "limit", value: String(limit)),
        ]
        if let query, !query.isEmpty { items.append(URLQueryItem(name: "q", value: query)) }
        if let city, !city.isEmpty { items.append(URLQueryItem(name: "city", value: city)) }
        components.queryItems = items
        let path = components.string ?? "listings"
        let response: ListingListResponse = try await client.request(path: path)
        return response.items
    }

    func getListing(id: String) async throws -> Listing {
        try await client.request(path: "listings/\(id)")
    }

    func getMine(limit: Int = 20) async throws -> [Listing] {
        let response: ListingListResponse = try await client.request(
            path: "listings/me?limit=\(limit)",
            authenticated: true,
        )
        return response.items
    }

    func create(_ input: ListingCreateInput) async throws -> Listing {
        try await client.request(path: "listings", method: "POST", body: input, authenticated: true)
    }

    func publish(id: String) async throws -> Listing {
        try await client.request(path: "listings/\(id)/publish", method: "POST", authenticated: true)
    }

    func markSold(id: String) async throws -> Listing {
        try await client.request(path: "listings/\(id)/sold", method: "POST", authenticated: true)
    }

    func presignImage(listingId: String, filename: String, contentType: String) async throws -> ImagePresignResponse {
        try await client.request(
            path: "listings/\(listingId)/images/presign",
            method: "POST",
            body: ImagePresignRequest(filename: filename, contentType: contentType),
            authenticated: true,
        )
    }

    func confirmImage(listingId: String, input: ImageConfirmInput) async throws -> ListingImage {
        try await client.request(
            path: "listings/\(listingId)/images/confirm",
            method: "POST",
            body: input,
            authenticated: true,
        )
    }

    func uploadImage(listingId: String, data: Data, contentType: String, isCover: Bool, sortOrder: Int) async throws {
        let filename = "photo_\(Int(Date().timeIntervalSince1970)).jpg"
        let presign = try await presignImage(listingId: listingId, filename: filename, contentType: contentType)
        try await client.uploadPut(urlString: presign.uploadUrl, data: data, contentType: contentType)
        _ = try await confirmImage(
            listingId: listingId,
            input: ImageConfirmInput(storageKey: presign.storageKey, sortOrder: sortOrder, isCover: isCover),
        )
    }
}

@MainActor
final class FavoriteService {
    static let shared = FavoriteService()
    private let client = ApiClient.shared

    func list(limit: Int = 20) async throws -> [Listing] {
        let response: ListingListResponse = try await client.request(
            path: "favorites?limit=\(limit)",
            authenticated: true,
        )
        return response.items
    }

    func add(listingId: String) async throws {
        struct IdResponse: Decodable { let id: String }
        _ = try await client.request(
            path: "favorites/\(listingId)",
            method: "POST",
            authenticated: true,
        ) as IdResponse
    }

    func remove(listingId: String) async throws {
        let _: EmptyResponse = try await client.request(
            path: "favorites/\(listingId)",
            method: "DELETE",
            authenticated: true,
        )
    }
}

@MainActor
final class InquiryService {
    static let shared = InquiryService()
    private let client = ApiClient.shared

    func create(listingId: String, message: String) async throws -> Inquiry {
        try await client.request(
            path: "listings/\(listingId)/inquiries",
            method: "POST",
            body: InquiryCreateInput(message: message),
            authenticated: true,
        )
    }
}

@MainActor
final class DealerService {
    static let shared = DealerService()
    private let client = ApiClient.shared

    func getBySlug(_ slug: String) async throws -> DealerStore {
        try await client.request(path: "dealer-stores/\(slug)")
    }

    func getMyListings(limit: Int = 20) async throws -> [Listing] {
        let response: ListingListResponse = try await client.request(
            path: "dealer-stores/me/listings?limit=\(limit)",
            authenticated: true,
        )
        return response.items
    }
}

@MainActor
final class ReviewService {
    static let shared = ReviewService()
    private let client = ApiClient.shared

    func list(targetType: String, targetId: String) async throws -> [Review] {
        let response: ReviewListResponse = try await client.request(
            path: "reviews?target_type=\(targetType)&target_id=\(targetId)",
        )
        return response.items
    }
}
