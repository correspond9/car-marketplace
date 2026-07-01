import SwiftUI

struct HomeView: View {
    @StateObject private var viewModel = HomeViewModel()
    var onSelectListing: (String) -> Void

    var body: some View {
        Group {
            if viewModel.isLoading && viewModel.listings.isEmpty {
                ProgressView("Loading cars…")
            } else if let error = viewModel.errorMessage, viewModel.listings.isEmpty {
                ContentUnavailableView("Could not load", systemImage: "wifi.exclamationmark", description: Text(error))
            } else {
                List(viewModel.listings) { listing in
                    Button {
                        onSelectListing(listing.id)
                    } label: {
                        ListingCardView(listing: listing)
                    }
                    .buttonStyle(.plain)
                    .listRowSeparator(.hidden)
                    .listRowInsets(EdgeInsets(top: 6, leading: 16, bottom: 6, trailing: 16))
                }
                .listStyle(.plain)
                .refreshable { await viewModel.load() }
            }
        }
        .navigationTitle("CarMarket")
        .task { await viewModel.load() }
    }
}
