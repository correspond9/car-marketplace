# CarMarket — iOS App

Native **Swift + SwiftUI** app. Not a WebView wrapper.

## Location

```
ios/
├── CarMarket.xcodeproj/     ← Open this in Xcode
├── CarMarket/
│   ├── Views/               # Login, Home, Search, Listing detail
│   ├── ViewModels/
│   ├── Services/            # API client
│   ├── Models/
│   └── Storage/             # Token persistence
└── CarMarketTests/
```

## Open in Xcode (requires macOS)

1. Install **Xcode 16+** from the Mac App Store.
2. Open `ios/CarMarket.xcodeproj`.
3. Select an **iPhone simulator** (iOS 17+).
4. Start the **API** on your Mac (`uvicorn` on port 8000) and **Docker**.
5. Press **Run** (⌘R).

### API URL

| Build | URL |
|-------|-----|
| Debug | `http://127.0.0.1:8000/api/v1/` |
| Release | `https://api.carmarket.in/api/v1/` |

For a **physical iPhone** on the same Wi‑Fi, change `ApiConfig.swift` to your Mac’s LAN IP (e.g. `http://192.168.1.5:8000/api/v1/`).

### Dev login

- Any 10-digit mobile number
- OTP: **`123456`**

## Features implemented

- Phone OTP login (tokens in UserDefaults — Keychain upgrade planned)
- Home feed with pull-to-refresh
- Search by keyword and city
- Listing detail screen
- Structured error handling from API

## Architecture

- **SwiftUI + MVVM** — `@MainActor` view models
- **URLSession + Codable** — REST client
- **Async/await** throughout

## Tests

In Xcode: **Product → Test** (⌘U), or:

```bash
xcodebuild test -project CarMarket.xcodeproj -scheme CarMarket -destination 'platform=iOS Simulator,name=iPhone 16'
```

## App Store notes (future)

- Replace UserDefaults token storage with **Keychain**
- Add Sign in with Apple if social login is added
- Privacy manifest & photo/camera usage strings when listing upload is added
