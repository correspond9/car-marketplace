package `in`.carmarket.app.ui.recentlyviewed

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.lifecycle.viewmodel.compose.viewModel
import `in`.carmarket.app.CarMarketApp
import `in`.carmarket.app.data.remote.ListingDto
import `in`.carmarket.app.ui.components.ListingCard
import `in`.carmarket.app.util.buildListingImageSlots
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class RecentlyViewedUiState(
    val listings: List<ListingDto> = emptyList(),
    val isLoading: Boolean = true,
    val error: String? = null,
)

class RecentlyViewedViewModel : ViewModel() {
    private val listingRepository = CarMarketApp.instance.listingRepository
    private val _uiState = MutableStateFlow(RecentlyViewedUiState())
    val uiState: StateFlow<RecentlyViewedUiState> = _uiState.asStateFlow()

    init {
        load()
    }

    fun load() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            listingRepository.getRecentlyViewed().fold(
                onSuccess = { listings -> _uiState.update { it.copy(listings = listings, isLoading = false) } },
                onFailure = { e -> _uiState.update { it.copy(isLoading = false, error = e.message) } },
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RecentlyViewedScreen(
    onListingClick: (String) -> Unit,
    viewModel: RecentlyViewedViewModel = viewModel(),
) {
    val state by viewModel.uiState.collectAsState()
    val imageSlots = remember(state.listings) { buildListingImageSlots(state.listings) }

    Scaffold(topBar = { TopAppBar(title = { Text("Recently viewed") }) }) { padding ->
        when {
            state.isLoading -> {
                Box(Modifier.fillMaxSize().padding(padding), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator()
                }
            }
            state.error != null && state.listings.isEmpty() -> {
                Box(Modifier.fillMaxSize().padding(padding), contentAlignment = Alignment.Center) {
                    Text(state.error ?: "Error", color = MaterialTheme.colorScheme.error)
                }
            }
            state.listings.isEmpty() -> {
                Box(Modifier.fillMaxSize().padding(padding), contentAlignment = Alignment.Center) {
                    Text("No recently viewed cars", color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }
            else -> {
                LazyColumn(
                    modifier = Modifier.fillMaxSize().padding(padding),
                    contentPadding = PaddingValues(
                        start = 12.dp,
                        end = 12.dp,
                        top = 4.dp,
                        bottom = 12.dp,
                    ),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
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
