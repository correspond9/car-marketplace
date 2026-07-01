import PhotosUI
import SwiftUI

struct FavoritesView: View {
    @StateObject private var viewModel = FavoritesViewModel()
    var onSelectListing: (String) -> Void

    var body: some View {
        Group {
            if viewModel.isLoading && viewModel.listings.isEmpty {
                ProgressView()
            } else if let error = viewModel.errorMessage, viewModel.listings.isEmpty {
                ContentUnavailableView("Error", systemImage: "heart.slash", description: Text(error))
            } else if viewModel.listings.isEmpty {
                ContentUnavailableView("No favorites", systemImage: "heart", description: Text("Save cars you like"))
            } else {
                List(viewModel.listings) { listing in
                    Button { onSelectListing(listing.id) } label: {
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
        .navigationTitle("Favorites")
        .task { await viewModel.load() }
    }
}

struct MyListingsView: View {
    @StateObject private var viewModel = MyListingsViewModel()
    var onSelectListing: (String) -> Void

    var body: some View {
        Group {
            if viewModel.isLoading && viewModel.listings.isEmpty {
                ProgressView()
            } else if let error = viewModel.errorMessage, viewModel.listings.isEmpty {
                ContentUnavailableView("Error", systemImage: "exclamationmark.triangle", description: Text(error))
            } else if viewModel.listings.isEmpty {
                ContentUnavailableView("No listings", systemImage: "car", description: Text("Create your first listing from Sell"))
            } else {
                List(viewModel.listings) { listing in
                    VStack(alignment: .leading, spacing: 8) {
                        Button { onSelectListing(listing.id) } label: {
                            ListingCardView(listing: listing)
                        }
                        .buttonStyle(.plain)
                        Text("Status: \(listing.status.replacingOccurrences(of: "_", with: " "))")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                        HStack {
                            if listing.status == "draft" || listing.status == "pending_review" {
                                Button("Publish") {
                                    Task { await viewModel.publish(id: listing.id) }
                                }
                                .buttonStyle(.borderedProminent)
                                .tint(.green)
                            }
                            if listing.status == "live" {
                                Button("Mark sold") {
                                    Task { await viewModel.markSold(id: listing.id) }
                                }
                                .buttonStyle(.bordered)
                            }
                        }
                    }
                    .listRowSeparator(.hidden)
                    .listRowInsets(EdgeInsets(top: 8, leading: 16, bottom: 8, trailing: 16))
                }
                .listStyle(.plain)
                .refreshable { await viewModel.load() }
            }
        }
        .navigationTitle("My listings")
        .task { await viewModel.load() }
    }
}

struct SellListingView: View {
    @StateObject private var viewModel = SellListingViewModel()

    var body: some View {
        Form {
            Section("Vehicle") {
                TextField("Make", text: $viewModel.make)
                TextField("Model", text: $viewModel.model)
                TextField("Variant (optional)", text: $viewModel.variant)
                TextField("Year", text: $viewModel.year)
                    .keyboardType(.numberPad)
                TextField("Odometer (km)", text: $viewModel.odometerKm)
                    .keyboardType(.numberPad)
            }
            Section("Price & location") {
                TextField("Asking price (₹)", text: $viewModel.price)
                    .keyboardType(.numberPad)
                TextField("City", text: $viewModel.city)
                TextField("Locality (optional)", text: $viewModel.locality)
            }
            Section("Details") {
                Picker("Fuel", selection: $viewModel.fuelType) {
                    ForEach(["petrol", "diesel", "cng", "ev", "hybrid"], id: \.self) { Text($0.capitalized).tag($0) }
                }
                Picker("Transmission", selection: $viewModel.transmission) {
                    ForEach(["manual", "automatic"], id: \.self) { Text($0.capitalized).tag($0) }
                }
                Picker("Body type", selection: $viewModel.bodyType) {
                    ForEach(["hatchback", "sedan", "suv", "muv"], id: \.self) { Text($0.capitalized).tag($0) }
                }
            }
            Section("Photos") {
                PhotosPicker(
                    selection: $viewModel.selectedPhotos,
                    maxSelectionCount: 10,
                    matching: .images,
                ) {
                    Label("Add photos (\(viewModel.selectedPhotos.count))", systemImage: "photo.on.rectangle")
                }
            }
            if let error = viewModel.errorMessage {
                Section { Text(error).foregroundStyle(.red) }
            }
            if let success = viewModel.successMessage {
                Section { Text(success).foregroundStyle(.green) }
            }
            Section {
                Button(viewModel.isSubmitting ? "Creating…" : "Create listing") {
                    Task { await viewModel.submit() }
                }
                .disabled(viewModel.isSubmitting)
            }
        }
        .navigationTitle("Sell")
    }
}

struct ProfileView: View {
    @StateObject private var viewModel = ProfileViewModel()
    var onLoggedOut: () -> Void
    var onMyListings: () -> Void

    var body: some View {
        Group {
            if viewModel.isLoading && viewModel.user == nil {
                ProgressView()
            } else {
                List {
                    if let user = viewModel.user {
                        Section {
                            Text(user.displayName ?? "CarMarket user")
                                .font(.title2.bold())
                            Text(user.phone)
                                .foregroundStyle(.secondary)
                            if let city = user.city {
                                Text("City: \(city)").foregroundStyle(.secondary)
                            }
                            Text("Role: \(user.role)").foregroundStyle(.secondary)
                        }
                    }
                    if let error = viewModel.errorMessage {
                        Section { Text(error).foregroundStyle(.red) }
                    }
                    Section {
                        Button("My listings", action: onMyListings)
                        Button("Log out", role: .destructive) {
                            viewModel.logout()
                            onLoggedOut()
                        }
                        Button("Delete account", role: .destructive) {
                            viewModel.showDeleteConfirm = true
                        }
                    }
                }
            }
        }
        .navigationTitle("Profile")
        .task { await viewModel.load() }
        .confirmationDialog(
            "Delete account?",
            isPresented: $viewModel.showDeleteConfirm,
            titleVisibility: .visible,
        ) {
            Button("Delete permanently", role: .destructive) {
                Task {
                    if await viewModel.deleteAccount() {
                        onLoggedOut()
                    }
                }
            }
            Button("Cancel", role: .cancel) {}
        } message: {
            Text("This removes your account and listings forever.")
        }
    }
}
