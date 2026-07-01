# CarMarket — Android App

Native **Kotlin + Jetpack Compose** app. Not a WebView wrapper.

## Location

```
android/
├── app/src/main/java/in/carmarket/app/
│   ├── ui/          # Screens (Login, Home, Search, Listing detail)
│   ├── data/        # API, repositories, token storage
│   └── ...
└── gradle/          # Version catalog & wrapper config
```

## Open in Android Studio

1. Install [Android Studio](https://developer.android.com/studio) (Ladybug or newer).
2. **File → Open** → select the `android/` folder.
3. Wait for Gradle sync (downloads dependencies automatically).
4. Start the **API** on your PC (`uvicorn` on port 8000) and **Docker** (Postgres + Redis).
5. Run on an **Android Emulator** (API 26+).

### API URL

| Environment | URL (built into app) |
|-------------|----------------------|
| Debug (emulator) | `http://10.0.2.2:8000/api/v1/` |
| Release | `https://api.carmarket.in/api/v1/` |

`10.0.2.2` is the emulator’s alias for your PC’s `localhost`.

### Dev login

- Any 10-digit Indian mobile number
- OTP: **`123456`**

## Features implemented

- Phone OTP login (secure token storage via DataStore)
- Home feed — latest live listings from API
- Search — filter by keyword and city
- Listing detail — price, specs, photos (when available)
- Pull-to-refresh on home
- Deep link intent filter for `https://carmarket.in/listing/*` (App Links — domain verification pending)

## Architecture

- **MVVM** — ViewModel + Compose UI
- **Retrofit + Moshi** — REST client matching OpenAPI
- **Coil** — image loading
- **Navigation Compose** — typed routes

## Build from command line

After opening once in Android Studio (generates Gradle wrapper):

```bash
cd android
./gradlew assembleDebug
```

## Tests

```bash
./gradlew test
```
