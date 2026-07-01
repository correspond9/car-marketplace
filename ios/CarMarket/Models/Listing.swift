import Foundation

struct TokenResponse: Codable {
    let accessToken: String
    let refreshToken: String

    enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
        case refreshToken = "refresh_token"
    }
}

struct UserMe: Codable {
    let id: String
    let phone: String
    let email: String?
    let displayName: String?
    let city: String?
    let role: String

    enum CodingKeys: String, CodingKey {
        case id, phone, email, city, role
        case displayName = "display_name"
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

struct ListingCreateInput: Encodable {
    let make: String
    let model: String
    let variant: String?
    let manufacturingYear: Int
    let bodyType: String
    let fuelType: String
    let transmission: String
    let odometerKm: Int
    let askingPrice: Int
    let city: String
    let locality: String?
    let negotiable: Bool

    enum CodingKeys: String, CodingKey {
        case make, model, variant, negotiable, city, locality, transmission
        case manufacturingYear = "manufacturing_year"
        case bodyType = "body_type"
        case fuelType = "fuel_type"
        case odometerKm = "odometer_km"
        case askingPrice = "asking_price"
    }
}

struct ImagePresignRequest: Encodable {
    let filename: String
    let contentType: String

    enum CodingKeys: String, CodingKey {
        case filename
        case contentType = "content_type"
    }
}

struct ImagePresignResponse: Decodable {
    let uploadUrl: String
    let storageKey: String
    let contentType: String

    enum CodingKeys: String, CodingKey {
        case uploadUrl = "upload_url"
        case storageKey = "storage_key"
        case contentType = "content_type"
    }
}

struct ImageConfirmInput: Encodable {
    let storageKey: String
    let sortOrder: Int
    let isCover: Bool

    enum CodingKeys: String, CodingKey {
        case storageKey = "storage_key"
        case sortOrder = "sort_order"
        case isCover = "is_cover"
    }
}

struct InquiryCreateInput: Encodable {
    let message: String
}

struct Inquiry: Codable, Identifiable {
    let id: String
    let listingId: String
    let message: String
    let status: String
    let sellerPhone: String?

    enum CodingKeys: String, CodingKey {
        case id, message, status
        case listingId = "listing_id"
        case sellerPhone = "seller_phone"
    }
}

struct Review: Codable, Identifiable {
    let id: String
    let rating: Int
    let text: String?

    enum CodingKeys: String, CodingKey {
        case id, rating, text
    }
}

struct ReviewListResponse: Codable {
    let items: [Review]
}

struct DealerStore: Codable, Identifiable {
    let id: String
    let name: String
    let slug: String
    let city: String?
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
