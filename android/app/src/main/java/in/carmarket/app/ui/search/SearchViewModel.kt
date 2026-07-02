package `in`.carmarket.app.ui.search

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import `in`.carmarket.app.CarMarketApp
import `in`.carmarket.app.data.remote.ListingDto
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class SearchUiState(
    val query: String = "",
    val city: String = "",
    val listings: List<ListingDto> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null,
    val hasSearched: Boolean = false,
)

class SearchViewModel : ViewModel() {
    private val listingRepository = CarMarketApp.instance.listingRepository
    private val _uiState = MutableStateFlow(SearchUiState())
    val uiState: StateFlow<SearchUiState> = _uiState.asStateFlow()

    fun onQueryChange(value: String) {
        _uiState.update { it.copy(query = value) }
    }

    fun onCityChange(value: String) {
        _uiState.update { it.copy(city = value) }
    }

    fun search() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null, hasSearched = true) }
            val state = _uiState.value
            listingRepository.search(
                query = state.query,
                city = state.city,
                limit = 30,
            ).fold(
                onSuccess = { items ->
                    _uiState.update { it.copy(listings = items, isLoading = false) }
                },
                onFailure = { e ->
                    _uiState.update { it.copy(isLoading = false, error = e.message) }
                },
            )
        }
    }
}
