import SwiftUI

struct ListingDetailView: View {
    let listingId: String
    @StateObject private var viewModel = ListingDetailViewModel()

    var body: some View {
        Group {
            if viewModel.isLoading && viewModel.listing == nil {
                ProgressView()
            } else if let error = viewModel.errorMessage, viewModel.listing == nil {
                ContentUnavailableView("Error", systemImage: "exclamationmark.triangle", description: Text(error))
            } else if let listing = viewModel.listing {
                ScrollView {
                    VStack(alignment: .leading, spacing: 0) {
                        if let url = listing.images.first?.url, let imageURL = URL(string: url) {
                            AsyncImage(url: imageURL) { phase in
                                if case .success(let image) = phase {
                                    image.resizable().scaledToFill()
                                } else {
                                    Color.gray.opacity(0.2)
                                }
                            }
                            .frame(height: 260)
                            .clipped()
                        }

                        VStack(alignment: .leading, spacing: 10) {
                            Text("\(listing.make) \(listing.model)\(listing.variant.map { " \($0)" } ?? "")")
                                .font(.title2.bold())
                            Text(PriceFormatter.format(listing.askingPrice))
                                .font(.title.bold())
                                .foregroundStyle(.green)
                            detail("Year", "\(listing.manufacturingYear)")
                            detail("Odometer", "\(PriceFormatter.km(listing.odometerKm)) km")
                            detail("Fuel", listing.fuelType.capitalized)
                            detail("Transmission", listing.transmission.capitalized)
                            detail("Body", listing.bodyType.capitalized)
                            detail("Location", listing.locality.map { "\(listing.city), \($0)" } ?? listing.city)
                            if let reg = listing.registrationNumberMasked {
                                detail("Registration", reg)
                            }
                            Button("Contact seller") {}
                                .buttonStyle(.borderedProminent)
                                .tint(.green)
                                .frame(maxWidth: .infinity)
                                .padding(.top, 12)
                        }
                        .padding(16)
                    }
                }
            }
        }
        .navigationBarTitleDisplayMode(.inline)
        .task { await viewModel.load(id: listingId) }
    }

    private func detail(_ label: String, _ value: String) -> some View {
        Text("\(label): \(value)").foregroundStyle(.secondary)
    }
}
