package in.carmarket.app.ui.navigation

object Routes {
    const val LOGIN = "login"
    const val HOME = "home"
    const val SEARCH = "search"
    const val LISTING = "listing/{listingId}"

    fun listing(id: String) = "listing/$id"
}
