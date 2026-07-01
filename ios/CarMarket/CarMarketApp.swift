import SwiftUI

@main
struct CarMarketApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

struct ContentView: View {
    var body: some View {
        NavigationStack {
            VStack(spacing: 16) {
                Image(systemName: "car.fill")
                    .font(.system(size: 48))
                    .foregroundStyle(.green)
                Text("CarMarket")
                    .font(.title.bold())
                Text("Used cars in India")
                    .foregroundStyle(.secondary)
            }
            .navigationTitle("Home")
        }
    }
}

#Preview {
    ContentView()
}
