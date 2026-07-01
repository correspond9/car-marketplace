package in.carmarket.app.data.remote

import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.POST
import retrofit2.http.Path
import retrofit2.http.Query

interface ApiService {
    @POST("auth/otp/request")
    suspend fun requestOtp(@Body body: OtpRequestBody)

    @POST("auth/otp/verify")
    suspend fun verifyOtp(@Body body: OtpVerifyBody): TokenResponse

    @GET("listings")
    suspend fun searchListings(
        @Query("q") query: String? = null,
        @Query("city") city: String? = null,
        @Query("make") make: String? = null,
        @Query("sort") sort: String = "newest",
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 20,
    ): ListingListResponse

    @GET("listings/{id}")
    suspend fun getListing(@Path("id") id: String): ListingDto

    @GET("users/me")
    suspend fun getMe(@Header("Authorization") authorization: String): Map<String, Any?>
}
