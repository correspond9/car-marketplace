package `in`.carmarket.app.data.repository

import `in`.carmarket.app.data.local.TokenStore
import `in`.carmarket.app.data.remote.ApiService
import `in`.carmarket.app.data.remote.OtpRequestBody
import `in`.carmarket.app.data.remote.OtpVerifyBody
import `in`.carmarket.app.data.remote.UserMeDto
import retrofit2.HttpException

class AuthRepository(
    private val api: ApiService,
    private val tokenStore: TokenStore,
) {
    suspend fun requestOtp(phone: String) {
        api.requestOtp(OtpRequestBody(phone = normalizePhone(phone)))
    }

    suspend fun verifyOtp(phone: String, otp: String) {
        val response = api.verifyOtp(OtpVerifyBody(phone = normalizePhone(phone), otp = otp))
        tokenStore.saveTokens(response.accessToken, response.refreshToken)
    }

    suspend fun logout() {
        tokenStore.clear()
    }

    suspend fun deleteAccount(): Result<Unit> = apiCall {
        api.deleteAccount()
        tokenStore.clear()
    }

    suspend fun getMe(): Result<UserMeDto> = apiCall {
        api.getMe()
    }

    fun isLoggedInFlow() = tokenStore.isLoggedIn

    private fun normalizePhone(phone: String): String {
        val digits = phone.filter { it.isDigit() }
        return when {
            digits.length == 10 -> digits
            digits.length == 12 && digits.startsWith("91") -> digits.substring(2)
            else -> digits
        }
    }
}

class FavoriteRepository(private val api: ApiService) {
    suspend fun list(page: Int = 1, limit: Int = 20) = apiCall {
        api.getFavorites(page = page, limit = limit).items
    }

    suspend fun add(listingId: String) = apiCall {
        api.addFavorite(listingId)
    }

    suspend fun remove(listingId: String) = apiCall {
        api.removeFavorite(listingId)
    }
}

class InquiryRepository(private val api: ApiService) {
    suspend fun create(listingId: String, message: String) = apiCall {
        api.createInquiry(listingId, `in`.carmarket.app.data.remote.InquiryCreateBody(message))
    }

    suspend fun inbox() = apiCall { api.getInquiryInbox(limit = 50).items }

    suspend fun sent() = apiCall { api.getSentInquiries(limit = 50).items }

    suspend fun accept(inquiryId: String) = apiCall { api.acceptInquiry(inquiryId) }

    suspend fun decline(inquiryId: String) = apiCall { api.declineInquiry(inquiryId) }
}

class ApiException(message: String) : Exception(message)

suspend fun <T> apiCall(block: suspend () -> T): Result<T> = try {
    Result.success(block())
} catch (e: HttpException) {
    Result.failure(ApiException("Server error (${e.code()})"))
} catch (e: Exception) {
    Result.failure(ApiException(e.message ?: "Network error"))
}
