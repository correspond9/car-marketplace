# CarMarket Android

Native Android app (Kotlin + Jetpack Compose).

## Requirements

- Android Studio Ladybug or newer
- JDK 17+
- Android SDK 35

## Setup

1. Open the `android/` folder in Android Studio
2. Sync Gradle
3. Set API URL in `app/src/main/java/in/carmarket/app/data/ApiConfig.kt`
4. Run on emulator or device

## Architecture (planned)

- MVVM with ViewModels
- Retrofit + OkHttp for API (OpenAPI-generated client)
- Coil for images
- DataStore for auth tokens

## Status

Scaffold only — API integration in Phase 1.
