package in.carmarket.app.ui.profile

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import in.carmarket.app.CarMarketApp
import in.carmarket.app.data.remote.UserMeDto
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class ProfileUiState(
    val user: UserMeDto? = null,
    val isLoading: Boolean = true,
    val isDeleting: Boolean = false,
    val showDeleteConfirm: Boolean = false,
    val error: String? = null,
)

class ProfileViewModel : ViewModel() {
    private val authRepository = CarMarketApp.instance.authRepository
    private val _uiState = MutableStateFlow(ProfileUiState())
    val uiState: StateFlow<ProfileUiState> = _uiState.asStateFlow()

    init {
        load()
    }

    fun load() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            authRepository.getMe().fold(
                onSuccess = { user ->
                    _uiState.update { it.copy(user = user, isLoading = false) }
                },
                onFailure = { e ->
                    _uiState.update { it.copy(isLoading = false, error = e.message) }
                },
            )
        }
    }

    fun logout() {
        viewModelScope.launch {
            authRepository.logout()
        }
    }

    fun confirmDelete() {
        _uiState.update { it.copy(showDeleteConfirm = true) }
    }

    fun dismissDeleteConfirm() {
        _uiState.update { it.copy(showDeleteConfirm = false) }
    }

    fun deleteAccount(onLoggedOut: () -> Unit) {
        viewModelScope.launch {
            _uiState.update { it.copy(isDeleting = true, showDeleteConfirm = false) }
            authRepository.deleteAccount().fold(
                onSuccess = {
                    _uiState.update { it.copy(isDeleting = false) }
                    onLoggedOut()
                },
                onFailure = { e ->
                    _uiState.update { it.copy(isDeleting = false, error = e.message) }
                },
            )
        }
    }
}
