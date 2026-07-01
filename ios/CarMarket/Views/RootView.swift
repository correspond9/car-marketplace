import SwiftUI

struct RootView: View {
    @ObservedObject private var tokens = TokenStore.shared
    @State private var selectedTab = 0
    @State private var homePath = NavigationPath()
    @State private var searchPath = NavigationPath()
    @State private var sellPath = NavigationPath()
    @State private var favoritesPath = NavigationPath()
    @State private var profilePath = NavigationPath()

    var body: some View {
        Group {
            if tokens.isLoggedIn {
                TabView(selection: $selectedTab) {
                    tabStack(path: $homePath, tab: 0) {
                        HomeView { id in homePath.append(AppRoute.listing(id)) }
                    }
                    .tabItem { Label("Home", systemImage: "house") }

                    tabStack(path: $searchPath, tab: 1) {
                        SearchView { id in searchPath.append(AppRoute.listing(id)) }
                    }
                    .tabItem { Label("Search", systemImage: "magnifyingglass") }

                    tabStack(path: $sellPath, tab: 2) {
                        SellListingView()
                    }
                    .tabItem { Label("Sell", systemImage: "plus.circle") }

                    tabStack(path: $favoritesPath, tab: 3) {
                        FavoritesView { id in favoritesPath.append(AppRoute.listing(id)) }
                    }
                    .tabItem { Label("Favorites", systemImage: "heart") }

                    tabStack(path: $profilePath, tab: 4) {
                        ProfileView(
                            onLoggedOut: { tokens.clear() },
                            onMyListings: { profilePath.append(AppRoute.myListings) },
                        )
                    }
                    .tabItem { Label("Profile", systemImage: "person") }
                }
            } else {
                LoginView {}
            }
        }
    }

    @ViewBuilder
    private func tabStack<Content: View>(
        path: Binding<NavigationPath>,
        tab: Int,
        @ViewBuilder content: () -> Content,
    ) -> some View {
        NavigationStack(path: path) {
            content()
                .navigationDestination(for: AppRoute.self) { route in
                    switch route {
                    case .listing(let id):
                        ListingDetailView(listingId: id)
                    case .myListings:
                        MyListingsView { id in path.wrappedValue.append(AppRoute.listing(id)) }
                    }
                }
        }
        .tag(tab)
    }
}

enum AppRoute: Hashable {
    case listing(String)
    case myListings
}
