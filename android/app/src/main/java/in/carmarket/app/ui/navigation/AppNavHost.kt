package in.carmarket.app.ui.navigation

import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import in.carmarket.app.CarMarketApp
import in.carmarket.app.ui.auth.LoginScreen
import in.carmarket.app.ui.home.HomeScreen
import in.carmarket.app.ui.listing.ListingDetailScreen
import in.carmarket.app.ui.search.SearchScreen

@Composable
fun AppNavHost() {
    val navController = rememberNavController()
    val isLoggedIn by CarMarketApp.instance.authRepository.isLoggedInFlow()
        .collectAsState(initial = false)

    val startDestination = if (isLoggedIn) Routes.HOME else Routes.LOGIN

    NavHost(navController = navController, startDestination = startDestination) {
        composable(Routes.LOGIN) {
            LoginScreen(
                onLoggedIn = {
                    navController.navigate(Routes.HOME) {
                        popUpTo(Routes.LOGIN) { inclusive = true }
                    }
                },
            )
        }
        composable(Routes.HOME) {
            HomeScreen(
                onOpenSearch = { navController.navigate(Routes.SEARCH) },
                onListingClick = { id -> navController.navigate(Routes.listing(id)) },
            )
        }
        composable(Routes.SEARCH) {
            SearchScreen(
                onBack = { navController.popBackStack() },
                onListingClick = { id -> navController.navigate(Routes.listing(id)) },
            )
        }
        composable(
            route = Routes.LISTING,
            arguments = listOf(navArgument("listingId") { type = NavType.StringType }),
        ) { entry ->
            val listingId = entry.arguments?.getString("listingId") ?: return@composable
            ListingDetailScreen(
                listingId = listingId,
                onBack = { navController.popBackStack() },
            )
        }
    }
}
