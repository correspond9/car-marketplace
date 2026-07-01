import SwiftUI

struct RootView: View {
    @ObservedObject private var tokens = TokenStore.shared
    @State private var path = NavigationPath()

    var body: some View {
        Group {
            if tokens.isLoggedIn {
                NavigationStack(path: $path) {
                    HomeView(
                        onSearch: { path.append(AppRoute.search) },
                        onSelectListing: { path.append(AppRoute.listing($0)) },
                    )
                    .navigationDestination(for: AppRoute.self) { route in
                        switch route {
                        case .search:
                            SearchView { id in path.append(AppRoute.listing(id)) }
                        case let .listing(id):
                            ListingDetailView(listingId: id)
                        }
                    }
                }
            } else {
                LoginView {
                    // TokenStore publishes login state
                }
            }
        }
    }
}

enum AppRoute: Hashable {
    case search
    case listing(String)
}
