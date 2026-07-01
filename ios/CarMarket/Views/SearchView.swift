import SwiftUI

struct SearchView: View {
    @StateObject private var viewModel = SearchViewModel()
    var onSelectListing: (String) -> Void

    var body: some View {
        Form {
            Section {
                TextField("Make, model, keyword", text: $viewModel.query)
                TextField("City", text: $viewModel.city)
                Button("Search") {
                    Task { await viewModel.search() }
                }
                .disabled(viewModel.isLoading)
            }

            if viewModel.isLoading {
                Section { ProgressView() }
            }

            if let error = viewModel.errorMessage {
                Section { Text(error).foregroundStyle(.red) }
            }

            if viewModel.hasSearched && !viewModel.isLoading {
                Section("\(viewModel.listings.count) result(s)") {
                    ForEach(viewModel.listings) { listing in
                        Button {
                            onSelectListing(listing.id)
                        } label: {
                            ListingCardView(listing: listing)
                        }
                        .buttonStyle(.plain)
                    }
                }
            }
        }
        .navigationTitle("Search")
        .navigationBarTitleDisplayMode(.inline)
    }
}
