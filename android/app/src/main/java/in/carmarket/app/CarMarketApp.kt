package in.carmarket.app

import android.app.Application
import in.carmarket.app.data.local.TokenStore
import in.carmarket.app.data.remote.NetworkModule
import in.carmarket.app.data.repository.AuthRepository
import in.carmarket.app.data.repository.FavoriteRepository
import in.carmarket.app.data.repository.InquiryRepository
import in.carmarket.app.data.repository.ListingRepository

class CarMarketApp : Application() {
    lateinit var tokenStore: TokenStore
        private set
    lateinit var authRepository: AuthRepository
        private set
    lateinit var listingRepository: ListingRepository
        private set
    lateinit var favoriteRepository: FavoriteRepository
        private set
    lateinit var inquiryRepository: InquiryRepository
        private set

    override fun onCreate() {
        super.onCreate()
        instance = this
        tokenStore = TokenStore(this)
        val api = NetworkModule.createApi(tokenStore)
        authRepository = AuthRepository(api, tokenStore)
        listingRepository = ListingRepository(api)
        favoriteRepository = FavoriteRepository(api)
        inquiryRepository = InquiryRepository(api)
    }

    companion object {
        lateinit var instance: CarMarketApp
            private set
    }
}
