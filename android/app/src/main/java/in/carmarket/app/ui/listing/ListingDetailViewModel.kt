package in.carmarket.app.ui.listing

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import in.carmarket.app.CarMarketApp
import in.carmarket.app.data.remote.ListingDto
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class ListingDetailUiState(
    val listing: ListingDto? = null,
    val isLoading: Boolean = true,
    val error: String? = null,
)

class ListingDetailViewModel(listingId: String) : ViewModel() {
    private val listingRepository = CarMarketApp.instance.listingRepository
    private val _uiState = MutableStateFlow(ListingDetailUiState())
    val uiState: StateFlow<ListingDetailUiState> = _uiState.asStateFlow()

    init {
        load(listingId)
    }

    fun load(listingId: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            listingRepository.getById(listingId).fold(
                onSuccess = { listing ->
                    _uiState.update { it.copy(listing = listing, isLoading = false) }
                },
                onFailure = { e ->
                    _uiState.update { it.copy(isLoading = false, error = e.message) }
                },
            )
        }
    }
}
