package in.carmarket.app.ui.mylistings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import in.carmarket.app.CarMarketApp
import in.carmarket.app.data.remote.ListingDto
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class MyListingsUiState(
    val listings: List<ListingDto> = emptyList(),
    val isLoading: Boolean = true,
    val error: String? = null,
    val actionInProgress: Boolean = false,
    val actionMessage: String? = null,
)

class MyListingsViewModel : ViewModel() {
    private val listingRepository = CarMarketApp.instance.listingRepository
    private val _uiState = MutableStateFlow(MyListingsUiState())
    val uiState: StateFlow<MyListingsUiState> = _uiState.asStateFlow()

    init {
        load()
    }

    fun load() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null, actionMessage = null) }
            listingRepository.getMine().fold(
                onSuccess = { listings ->
                    _uiState.update { it.copy(listings = listings, isLoading = false) }
                },
                onFailure = { e ->
                    _uiState.update { it.copy(isLoading = false, error = e.message) }
                },
            )
        }
    }

    fun publish(id: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(actionInProgress = true, actionMessage = null) }
            listingRepository.publish(id).fold(
                onSuccess = {
                    _uiState.update { it.copy(actionInProgress = false, actionMessage = "Listing submitted") }
                    load()
                },
                onFailure = { e ->
                    _uiState.update { it.copy(actionInProgress = false, actionMessage = e.message) }
                },
            )
        }
    }

    fun markSold(id: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(actionInProgress = true, actionMessage = null) }
            listingRepository.markSold(id).fold(
                onSuccess = {
                    _uiState.update { it.copy(actionInProgress = false, actionMessage = "Marked as sold") }
                    load()
                },
                onFailure = { e ->
                    _uiState.update { it.copy(actionInProgress = false, actionMessage = e.message) }
                },
            )
        }
    }
}
