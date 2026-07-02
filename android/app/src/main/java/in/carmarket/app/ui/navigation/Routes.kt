package `in`.carmarket.app.ui.navigation

object Routes {
    const val LOGIN = "login"
    const val HOME = "home"
    const val SEARCH = "search"
    const val SELL = "sell"
    const val FAVORITES = "favorites"
    const val PROFILE = "profile"
    const val MY_LISTINGS = "my_listings"
    const val INQUIRIES = "inquiries"
    const val RECENTLY_VIEWED = "recently_viewed"
    const val LISTING = "listing/{listingId}"

    fun listing(id: String) = "listing/$id"
}
