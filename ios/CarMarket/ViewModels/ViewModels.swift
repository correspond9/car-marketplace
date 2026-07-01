import Foundation

@MainActor
final class AuthViewModel: ObservableObject {
    @Published var phone = ""
    @Published var otp = ""
    @Published var otpSent = false
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let auth = AuthService.shared

    func sendOtp() async {
        guard phone.filter(\.isNumber).count == 10 else {
            errorMessage = "Enter a valid 10-digit mobile number"
            return
        }
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        do {
            try await auth.requestOtp(phone: phone)
            otpSent = true
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func verify() async -> Bool {
        guard otp.count >= 4 else {
            errorMessage = "Enter the OTP"
            return false
        }
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        do {
            try await auth.verifyOtp(phone: phone, otp: otp)
            return true
        } catch {
            errorMessage = error.localizedDescription
            return false
        }
    }
}

@MainActor
final class HomeViewModel: ObservableObject {
    @Published var listings: [Listing] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let service = ListingService.shared

    func load() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        do {
            listings = try await service.search(limit: 12)
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

@MainActor
final class SearchViewModel: ObservableObject {
    @Published var query = ""
    @Published var city = ""
    @Published var listings: [Listing] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var hasSearched = false

    private let service = ListingService.shared

    func search() async {
        isLoading = true
        errorMessage = nil
        hasSearched = true
        defer { isLoading = false }
        do {
            listings = try await service.search(query: query, city: city, limit: 30)
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

@MainActor
final class ListingDetailViewModel: ObservableObject {
    @Published var listing: Listing?
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let service = ListingService.shared

    func load(id: String) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        do {
            listing = try await service.getListing(id: id)
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
