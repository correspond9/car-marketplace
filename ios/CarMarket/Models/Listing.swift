import Foundation

struct TokenResponse: Codable {
    let accessToken: String
    let refreshToken: String

    enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
        case refreshToken = "refresh_token"
    }
}

struct ListingImage: Codable, Identifiable {
    let id: String
    let url: String
    let isCover: Bool

    enum CodingKeys: String, CodingKey {
        case id, url
        case isCover = "is_cover"
    }
}

struct Listing: Codable, Identifiable {
    let id: String
    let make: String
    let model: String
    let variant: String?
    let manufacturingYear: Int
    let fuelType: String
    let transmission: String
    let bodyType: String
    let odometerKm: Int
    let askingPrice: Int
    let negotiable: Bool
    let city: String
    let locality: String?
    let status: String
    let registrationNumberMasked: String?
    let images: [ListingImage]

    enum CodingKeys: String, CodingKey {
        case id, make, model, variant, negotiable, city, locality, status, images, transmission
        case manufacturingYear = "manufacturing_year"
        case fuelType = "fuel_type"
        case bodyType = "body_type"
        case odometerKm = "odometer_km"
        case askingPrice = "asking_price"
        case registrationNumberMasked = "registration_number_masked"
    }
}

struct ListingListResponse: Codable {
    let items: [Listing]
    let total: Int
    let page: Int
    let limit: Int
    let pages: Int
}

struct ApiErrorResponse: Codable {
    struct Detail: Codable {
        let code: String?
        let message: String?
    }
    let error: Detail?
}

enum ApiError: LocalizedError {
    case invalidURL
    case http(Int, String?)
    case decoding
    case network(Error)

    var errorDescription: String? {
        switch self {
        case .invalidURL: return "Invalid URL"
        case let .http(code, message): return message ?? "Server error (\(code))"
        case .decoding: return "Could not read server response"
        case let .network(error): return error.localizedDescription
        }
    }
}
