package in.carmarket.app.ui.sell

import android.app.Application
import android.net.Uri
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import in.carmarket.app.CarMarketApp
import in.carmarket.app.data.remote.ListingCreateBody
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class SellListingUiState(
    val make: String = "",
    val model: String = "",
    val variant: String = "",
    val year: String = "",
    val odometerKm: String = "",
    val price: String = "",
    val city: String = "",
    val locality: String = "",
    val fuelType: String = "petrol",
    val transmission: String = "manual",
    val bodyType: String = "hatchback",
    val selectedPhotos: List<Uri> = emptyList(),
    val isSubmitting: Boolean = false,
    val error: String? = null,
    val successMessage: String? = null,
)

class SellListingViewModel(application: Application) : AndroidViewModel(application) {
    private val listingRepository = CarMarketApp.instance.listingRepository
    private val contentResolver = application.contentResolver
    private val _uiState = MutableStateFlow(SellListingUiState())
    val uiState: StateFlow<SellListingUiState> = _uiState.asStateFlow()

    fun onMakeChange(v: String) = _uiState.update { it.copy(make = v) }
    fun onModelChange(v: String) = _uiState.update { it.copy(model = v) }
    fun onVariantChange(v: String) = _uiState.update { it.copy(variant = v) }
    fun onYearChange(v: String) = _uiState.update { it.copy(year = v) }
    fun onOdometerChange(v: String) = _uiState.update { it.copy(odometerKm = v) }
    fun onPriceChange(v: String) = _uiState.update { it.copy(price = v) }
    fun onCityChange(v: String) = _uiState.update { it.copy(city = v) }
    fun onLocalityChange(v: String) = _uiState.update { it.copy(locality = v) }
    fun onFuelChange(v: String) = _uiState.update { it.copy(fuelType = v) }
    fun onTransmissionChange(v: String) = _uiState.update { it.copy(transmission = v) }
    fun onBodyTypeChange(v: String) = _uiState.update { it.copy(bodyType = v) }

    fun onPhotosSelected(uris: List<Uri>) {
        _uiState.update { it.copy(selectedPhotos = uris.take(10)) }
    }

    fun submit(onSuccess: () -> Unit) {
        val state = _uiState.value
        val year = state.year.toIntOrNull()
        val km = state.odometerKm.toIntOrNull()
        val price = state.price.toLongOrNull()
        if (state.make.isBlank() || state.model.isBlank() || year == null || km == null || price == null || state.city.isBlank()) {
            _uiState.update { it.copy(error = "Fill in make, model, year, km, price, and city") }
            return
        }

        viewModelScope.launch {
            _uiState.update { it.copy(isSubmitting = true, error = null, successMessage = null) }
            val body = ListingCreateBody(
                make = state.make.trim(),
                model = state.model.trim(),
                variant = state.variant.trim().ifBlank { null },
                manufacturingYear = year,
                bodyType = state.bodyType,
                fuelType = state.fuelType,
                transmission = state.transmission,
                odometerKm = km,
                askingPrice = price,
                city = state.city.trim(),
                locality = state.locality.trim().ifBlank { null },
            )
            listingRepository.create(body).fold(
                onSuccess = { listing ->
                    var uploadError: String? = null
                    state.selectedPhotos.forEachIndexed { index, uri ->
                        listingRepository.uploadImage(
                            listingId = listing.id,
                            uri = uri,
                            contentResolver = contentResolver,
                            isCover = index == 0,
                            sortOrder = index,
                        ).onFailure { e ->
                            uploadError = e.message
                        }
                    }
                    listingRepository.publish(listing.id).fold(
                        onSuccess = {
                            _uiState.update {
                                it.copy(
                                    isSubmitting = false,
                                    successMessage = uploadError?.let { err ->
                                        "Listing created but some photos failed: $err"
                                    } ?: "Listing created and submitted!",
                                    make = "",
                                    model = "",
                                    variant = "",
                                    year = "",
                                    odometerKm = "",
                                    price = "",
                                    city = "",
                                    locality = "",
                                    selectedPhotos = emptyList(),
                                )
                            }
                            onSuccess()
                        },
                        onFailure = { e ->
                            _uiState.update {
                                it.copy(
                                    isSubmitting = false,
                                    successMessage = "Listing created but publish failed: ${e.message}",
                                )
                            }
                        },
                    )
                },
                onFailure = { e ->
                    _uiState.update { it.copy(isSubmitting = false, error = e.message) }
                },
            )
        }
    }
}
