# CarMarket iOS

Native iOS app (Swift + SwiftUI).

## Requirements

- Xcode 16+
- macOS
- iOS 17+ deployment target

## Setup

1. Open `ios/CarMarket.xcodeproj` in Xcode (create project from sources if needed)
2. Set API URL in `CarMarket/Config/ApiConfig.swift`
3. Run on simulator or device

## Architecture (planned)

- SwiftUI views + Observable ViewModels
- URLSession / OpenAPI-generated client
- Keychain for auth tokens
- AsyncImage / Kingfisher for photos

## Status

Scaffold only — API integration in Phase 1.
