package `in`.carmarket.app.ui.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import `in`.carmarket.app.CarMarketApp
import `in`.carmarket.app.data.repository.ApiException
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class LoginUiState(
    val phone: String = "",
    val otp: String = "",
    val otpSent: Boolean = false,
    val isLoading: Boolean = false,
    val error: String? = null,
)

class LoginViewModel : ViewModel() {
    private val authRepository = CarMarketApp.instance.authRepository
    private val _uiState = MutableStateFlow(LoginUiState())
    val uiState: StateFlow<LoginUiState> = _uiState.asStateFlow()

    fun onPhoneChange(value: String) {
        _uiState.update { it.copy(phone = value.filter { c -> c.isDigit() }.take(10), error = null) }
    }

    fun onOtpChange(value: String) {
        _uiState.update { it.copy(otp = value.filter { c -> c.isDigit() }.take(6), error = null) }
    }

    fun requestOtp() {
        val phone = _uiState.value.phone
        if (phone.length != 10) {
            _uiState.update { it.copy(error = "Enter a valid 10-digit mobile number") }
            return
        }
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            try {
                authRepository.requestOtp(phone)
                _uiState.update { it.copy(isLoading = false, otpSent = true) }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(isLoading = false, error = e.message ?: "Could not send OTP")
                }
            }
        }
    }

    fun verifyOtp(onSuccess: () -> Unit) {
        val state = _uiState.value
        if (state.otp.length < 4) {
            _uiState.update { it.copy(error = "Enter the OTP") }
            return
        }
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            try {
                authRepository.verifyOtp(state.phone, state.otp)
                _uiState.update { it.copy(isLoading = false) }
                onSuccess()
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        error = (e as? ApiException)?.message ?: "Invalid OTP",
                    )
                }
            }
        }
    }
}
