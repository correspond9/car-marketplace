package `in`.carmarket.app.ui.listing

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import `in`.carmarket.app.CarMarketApp
import `in`.carmarket.app.data.remote.ListingDto
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class ListingDetailUiState(
    val listing: ListingDto? = null,
    val isLoading: Boolean = true,
    val isFavorite: Boolean = false,
    val favoriteBusy: Boolean = false,
    val showInquiryDialog: Boolean = false,
    val inquiryMessage: String = "",
    val inquirySending: Boolean = false,
    val inquirySent: Boolean = false,
    val error: String? = null,
    val message: String? = null,
)

class ListingDetailViewModel(listingId: String) : ViewModel() {
    private val listingRepository = CarMarketApp.instance.listingRepository
    private val favoriteRepository = CarMarketApp.instance.favoriteRepository
    private val inquiryRepository = CarMarketApp.instance.inquiryRepository
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
                    checkFavorite(listingId)
                    trackView(listingId)
                },
                onFailure = { e ->
                    _uiState.update { it.copy(isLoading = false, error = e.message) }
                },
            )
        }
    }

    private fun checkFavorite(listingId: String) {
        viewModelScope.launch {
            favoriteRepository.list(limit = 100).onSuccess { favorites ->
                val isFav = favorites.any { it.id == listingId }
                _uiState.update { it.copy(isFavorite = isFav) }
            }
        }
    }

    private fun trackView(listingId: String) {
        viewModelScope.launch {
            listingRepository.trackView(listingId)
        }
    }

    fun toggleFavorite() {
        val listingId = _uiState.value.listing?.id ?: return
        viewModelScope.launch {
            _uiState.update { it.copy(favoriteBusy = true) }
            val result = if (_uiState.value.isFavorite) {
                favoriteRepository.remove(listingId)
            } else {
                favoriteRepository.add(listingId)
            }
            result.fold(
                onSuccess = {
                    _uiState.update { it.copy(isFavorite = !it.isFavorite, favoriteBusy = false) }
                },
                onFailure = { e ->
                    _uiState.update { it.copy(favoriteBusy = false, message = e.message) }
                },
            )
        }
    }

    fun showInquiryDialog() {
        _uiState.update { it.copy(showInquiryDialog = true, inquirySent = false, message = null) }
    }

    fun dismissInquiryDialog() {
        _uiState.update { it.copy(showInquiryDialog = false, inquiryMessage = "") }
    }

    fun onInquiryMessageChange(message: String) {
        _uiState.update { it.copy(inquiryMessage = message) }
    }

    fun sendInquiry() {
        val listingId = _uiState.value.listing?.id ?: return
        val message = _uiState.value.inquiryMessage.trim()
        if (message.length < 5) {
            _uiState.update { it.copy(message = "Message must be at least 5 characters") }
            return
        }
        viewModelScope.launch {
            _uiState.update { it.copy(inquirySending = true, message = null) }
            inquiryRepository.create(listingId, message).fold(
                onSuccess = {
                    _uiState.update {
                        it.copy(
                            inquirySending = false,
                            inquirySent = true,
                            showInquiryDialog = false,
                            inquiryMessage = "",
                            message = "Inquiry sent! Seller will respond soon.",
                        )
                    }
                },
                onFailure = { e ->
                    _uiState.update { it.copy(inquirySending = false, message = e.message) }
                },
            )
        }
    }
}
