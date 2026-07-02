package `in`.carmarket.app.ui.mylistings

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.pulltorefresh.PullToRefreshBox
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import `in`.carmarket.app.ui.components.ListingCard
import `in`.carmarket.app.ui.theme.Slate600
import `in`.carmarket.app.util.buildListingImageSlots

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MyListingsScreen(
    onBack: () -> Unit,
    onListingClick: (String) -> Unit,
    viewModel: MyListingsViewModel = viewModel(),
) {
    val state by viewModel.uiState.collectAsState()
    val imageSlots = remember(state.listings) { buildListingImageSlots(state.listings) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("My listings") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
            )
        },
    ) { padding ->
        Box(modifier = Modifier.fillMaxSize().padding(padding)) {
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
                state.listings.isEmpty() -> {
                    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        Text("You have no listings yet", color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
                else -> {
                    LazyColumn(
                        contentPadding = PaddingValues(
                            start = 12.dp,
                            end = 12.dp,
                            top = 4.dp,
                            bottom = 12.dp,
                        ),
                        verticalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        items(state.listings, key = { it.id }) { listing ->
                            Column {
                                ListingCard(
                                    listing = listing,
                                    imageSlot = imageSlots[listing.id] ?: 0,
                                    onClick = { onListingClick(listing.id) },
                                )
                                Text(
                                    "Status: ${listing.status.replace('_', ' ')}",
                                    color = Slate600,
                                    modifier = Modifier.padding(start = 4.dp, top = 4.dp),
                                )
                                Row(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(top = 8.dp),
                                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                                ) {
                                    if (listing.status == "draft" || listing.status == "pending_review") {
                                        Button(
                                            onClick = { viewModel.publish(listing.id) },
                                            enabled = !state.actionInProgress,
                                        ) {
                                            Text("Publish")
                                        }
                                    }
                                    if (listing.status == "live") {
                                        OutlinedButton(
                                            onClick = { viewModel.markSold(listing.id) },
                                            enabled = !state.actionInProgress,
                                        ) {
                                            Text("Mark sold")
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            }
            state.actionMessage?.let { msg ->
                Text(
                    msg,
                    color = MaterialTheme.colorScheme.primary,
                    modifier = Modifier
                        .align(Alignment.BottomCenter)
                        .padding(16.dp),
                )
            }
        }
    }
}
