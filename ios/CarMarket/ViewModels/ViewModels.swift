import Foundation
import PhotosUI
import SwiftUI

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
    @Published var isFavorite = false
    @Published var favoriteBusy = false
    @Published var showInquirySheet = false
    @Published var inquiryMessage = ""
    @Published var inquirySending = false
    @Published var statusMessage: String?
    @Published var errorMessage: String?

    private let listingService = ListingService.shared
    private let favoriteService = FavoriteService.shared
    private let inquiryService = InquiryService.shared

    func load(id: String) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        do {
            listing = try await listingService.getListing(id: id)
            await checkFavorite(listingId: id)
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    private func checkFavorite(listingId: String) async {
        do {
            let favorites = try await favoriteService.list(limit: 100)
            isFavorite = favorites.contains { $0.id == listingId }
        } catch {
            // ignore
        }
    }

    func toggleFavorite() async {
        guard let listingId = listing?.id else { return }
        favoriteBusy = true
        defer { favoriteBusy = false }
        do {
            if isFavorite {
                try await favoriteService.remove(listingId: listingId)
            } else {
                try await favoriteService.add(listingId: listingId)
            }
            isFavorite.toggle()
        } catch {
            statusMessage = error.localizedDescription
        }
    }

    func sendInquiry() async {
        guard let listingId = listing?.id else { return }
        let message = inquiryMessage.trimmingCharacters(in: .whitespacesAndNewlines)
        guard message.count >= 5 else {
            statusMessage = "Message must be at least 5 characters"
            return
        }
        inquirySending = true
        defer { inquirySending = false }
        do {
            _ = try await inquiryService.create(listingId: listingId, message: message)
            showInquirySheet = false
            inquiryMessage = ""
            statusMessage = "Inquiry sent! Seller will respond soon."
        } catch {
            statusMessage = error.localizedDescription
        }
    }
}

@MainActor
final class FavoritesViewModel: ObservableObject {
    @Published var listings: [Listing] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let service = FavoriteService.shared

    func load() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        do {
            listings = try await service.list()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

@MainActor
final class MyListingsViewModel: ObservableObject {
    @Published var listings: [Listing] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let service = ListingService.shared

    func load() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        do {
            listings = try await service.getMine()
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func publish(id: String) async {
        do {
            _ = try await service.publish(id: id)
            await load()
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func markSold(id: String) async {
        do {
            _ = try await service.markSold(id: id)
            await load()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

@MainActor
final class SellListingViewModel: ObservableObject {
    @Published var make = ""
    @Published var model = ""
    @Published var variant = ""
    @Published var year = ""
    @Published var odometerKm = ""
    @Published var price = ""
    @Published var city = ""
    @Published var locality = ""
    @Published var fuelType = "petrol"
    @Published var transmission = "manual"
    @Published var bodyType = "hatchback"
    @Published var selectedPhotos: [PhotosPickerItem] = []
    @Published var isSubmitting = false
    @Published var errorMessage: String?
    @Published var successMessage: String?

    private let service = ListingService.shared

    func submit() async {
        guard let yearInt = Int(year),
              let km = Int(odometerKm),
              let priceInt = Int(price),
              !make.isEmpty, !model.isEmpty, !city.isEmpty else {
            errorMessage = "Fill in make, model, year, km, price, and city"
            return
        }

        isSubmitting = true
        errorMessage = nil
        successMessage = nil
        defer { isSubmitting = false }

        do {
            let input = ListingCreateInput(
                make: make.trimmingCharacters(in: .whitespaces),
                model: model.trimmingCharacters(in: .whitespaces),
                variant: variant.isEmpty ? nil : variant,
                manufacturingYear: yearInt,
                bodyType: bodyType,
                fuelType: fuelType,
                transmission: transmission,
                odometerKm: km,
                askingPrice: priceInt,
                city: city.trimmingCharacters(in: .whitespaces),
                locality: locality.isEmpty ? nil : locality,
                negotiable: true,
            )
            let listing = try await service.create(input)
            for (index, item) in selectedPhotos.enumerated() {
                if let data = try? await item.loadTransferable(type: Data.self) {
                    try? await service.uploadImage(
                        listingId: listing.id,
                        data: data,
                        contentType: "image/jpeg",
                        isCover: index == 0,
                        sortOrder: index,
                    )
                }
            }
            _ = try await service.publish(id: listing.id)
            successMessage = "Listing created and submitted!"
            make = ""
            model = ""
            variant = ""
            year = ""
            odometerKm = ""
            price = ""
            city = ""
            locality = ""
            selectedPhotos = []
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

@MainActor
final class ProfileViewModel: ObservableObject {
    @Published var user: UserMe?
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var showDeleteConfirm = false

    private let auth = AuthService.shared

    func load() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        do {
            user = try await auth.getMe()
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func logout() {
        auth.logout()
    }

    func deleteAccount() async -> Bool {
        do {
            try await auth.deleteAccount()
            return true
        } catch {
            errorMessage = error.localizedDescription
            return false
        }
    }
}
