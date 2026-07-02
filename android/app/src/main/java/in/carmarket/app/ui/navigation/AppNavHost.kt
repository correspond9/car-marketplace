package `in`.carmarket.app.ui.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import `in`.carmarket.app.CarMarketApp
import `in`.carmarket.app.ui.auth.LoginScreen
import `in`.carmarket.app.ui.favorites.FavoritesScreen
import `in`.carmarket.app.ui.home.HomeScreen
import `in`.carmarket.app.ui.inquiries.InquiriesScreen
import `in`.carmarket.app.ui.listing.ListingDetailScreen
import `in`.carmarket.app.ui.mylistings.MyListingsScreen
import `in`.carmarket.app.ui.profile.ProfileScreen
import `in`.carmarket.app.ui.recentlyviewed.RecentlyViewedScreen
import `in`.carmarket.app.ui.search.SearchScreen
import `in`.carmarket.app.ui.sell.SellListingScreen

private data class BottomNavItem(
    val route: String,
    val label: String,
    val icon: ImageVector,
)

private val bottomNavItems = listOf(
    BottomNavItem(Routes.HOME, "Home", Icons.Default.Home),
    BottomNavItem(Routes.SEARCH, "Search", Icons.Default.Search),
    BottomNavItem(Routes.SELL, "Sell", Icons.Default.Add),
    BottomNavItem(Routes.FAVORITES, "Favorites", Icons.Default.Favorite),
    BottomNavItem(Routes.PROFILE, "Profile", Icons.Default.Person),
)

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
            MainTabs(
                onLoggedOut = {
                    navController.navigate(Routes.LOGIN) {
                        popUpTo(0) { inclusive = true }
                    }
                },
            )
        }
    }
}

@Composable
private fun MainTabs(onLoggedOut: () -> Unit) {
    val navController = rememberNavController()
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route
    val showBottomBar = currentRoute in bottomNavItems.map { it.route }

    Scaffold(
        bottomBar = {
            if (showBottomBar) {
                NavigationBar {
                    bottomNavItems.forEach { item ->
                        NavigationBarItem(
                            selected = currentRoute == item.route,
                            onClick = {
                                navController.navigate(item.route) {
                                    popUpTo(navController.graph.findStartDestination().id) {
                                        saveState = true
                                    }
                                    launchSingleTop = true
                                    restoreState = true
                                }
                            },
                            icon = { Icon(item.icon, contentDescription = item.label) },
                            label = { Text(item.label) },
                        )
                    }
                }
            }
        },
    ) { padding ->
        NavHost(
            navController = navController,
            startDestination = Routes.HOME,
            modifier = Modifier.padding(padding),
        ) {
            composable(Routes.HOME) {
                HomeScreen(
                    onListingClick = { id -> navController.navigate(Routes.listing(id)) },
                )
            }
            composable(Routes.SEARCH) {
                SearchScreen(
                    onListingClick = { id -> navController.navigate(Routes.listing(id)) },
                )
            }
            composable(Routes.SELL) {
                SellListingScreen(onSubmitted = { })
            }
            composable(Routes.FAVORITES) {
                FavoritesScreen(
                    onListingClick = { id -> navController.navigate(Routes.listing(id)) },
                )
            }
            composable(Routes.PROFILE) {
                ProfileScreen(
                    onLoggedOut = onLoggedOut,
                    onMyListings = { navController.navigate(Routes.MY_LISTINGS) },
                    onInquiries = { navController.navigate(Routes.INQUIRIES) },
                    onRecentlyViewed = { navController.navigate(Routes.RECENTLY_VIEWED) },
                )
            }
            composable(Routes.MY_LISTINGS) {
                MyListingsScreen(
                    onBack = { navController.popBackStack() },
                    onListingClick = { id -> navController.navigate(Routes.listing(id)) },
                )
            }
            composable(Routes.INQUIRIES) {
                InquiriesScreen(onBack = { navController.popBackStack() })
            }
            composable(Routes.RECENTLY_VIEWED) {
                RecentlyViewedScreen(
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
}
