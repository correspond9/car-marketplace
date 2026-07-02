package `in`.carmarket.app.ui.home

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.material3.pulltorefresh.PullToRefreshBox
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import `in`.carmarket.app.ui.components.BrandLogo
import `in`.carmarket.app.ui.components.ListingCard
import `in`.carmarket.app.ui.components.MatteGlassCard
import `in`.carmarket.app.ui.theme.MatteGlassHero
import `in`.carmarket.app.ui.theme.Slate600
import `in`.carmarket.app.util.buildListingImageSlots

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    onListingClick: (String) -> Unit,
    viewModel: HomeViewModel = viewModel(),
) {
    val state by viewModel.uiState.collectAsState()
    val imageSlots = remember(state.listings) { buildListingImageSlots(state.listings) }
    val bgBrush = Brush.verticalGradient(
        colors = listOf(Color(0xFFF0FDF4), Color(0xFFEEF2F6), Color(0xFFF8FAFC)),
    )

    Scaffold(
        containerColor = Color.Transparent,
        topBar = {
            TopAppBar(
                title = {
                    BrandLogo(
                        modifier = Modifier
                            .height(44.dp)
                            .padding(horizontal = 4.dp),
                    )
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MatteGlassHero,
                ),
            )
        },
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(bgBrush)
                .padding(padding),
        ) {
            PullToRefreshBox(
                isRefreshing = state.isLoading,
                onRefresh = viewModel::load,
                modifier = Modifier.fillMaxSize(),
            ) {
                when {
                    state.isLoading && state.listings.isEmpty() -> {
                        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                            CircularProgressIndicator()
                        }
                    }
                    state.error != null && state.listings.isEmpty() -> {
                        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                            Text(state.error ?: "Error", color = MaterialTheme.colorScheme.error)
                        }
                    }
                    else -> {
                        LazyColumn(
                            contentPadding = PaddingValues(16.dp),
                            verticalArrangement = Arrangement.spacedBy(12.dp),
                        ) {
                            item {
                                MatteGlassCard(modifier = Modifier.fillMaxWidth()) {
                                    Column(modifier = Modifier.padding(16.dp)) {
                                        Text(
                                            "Find your next used car",
                                            style = MaterialTheme.typography.headlineSmall,
                                        )
                                        Text(
                                            "Browse verified listings across India",
                                            color = Slate600,
                                            modifier = Modifier.padding(top = 4.dp),
                                        )
                                    }
                                }
                            }
                            item {
                                Text(
                                    "Latest used cars",
                                    style = MaterialTheme.typography.titleLarge,
                                    modifier = Modifier.padding(top = 4.dp, bottom = 4.dp),
                                )
                            }
                            items(state.listings, key = { it.id }) { listing ->
                                ListingCard(
                                    listing = listing,
                                    imageSlot = imageSlots[listing.id] ?: 0,
                                    onClick = { onListingClick(listing.id) },
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}
