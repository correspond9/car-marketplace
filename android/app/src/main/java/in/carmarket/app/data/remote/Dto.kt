package in.carmarket.app.data.remote

import com.squareup.moshi.Json
import com.squareup.moshi.JsonClass

@JsonClass(generateAdapter = true)
data class OtpRequestBody(val phone: String)

@JsonClass(generateAdapter = true)
data class OtpVerifyBody(val phone: String, val otp: String)

@JsonClass(generateAdapter = true)
data class TokenResponse(
    @Json(name = "access_token") val accessToken: String,
    @Json(name = "refresh_token") val refreshToken: String,
    @Json(name = "token_type") val tokenType: String = "bearer",
)

@JsonClass(generateAdapter = true)
data class ListingImageDto(
    val id: String,
    val url: String,
    @Json(name = "is_cover") val isCover: Boolean = false,
)

@JsonClass(generateAdapter = true)
data class ListingDto(
    val id: String,
    val make: String,
    val model: String,
    val variant: String?,
    @Json(name = "manufacturing_year") val manufacturingYear: Int,
    @Json(name = "fuel_type") val fuelType: String,
    val transmission: String,
    @Json(name = "body_type") val bodyType: String,
    @Json(name = "odometer_km") val odometerKm: Int,
    @Json(name = "asking_price") val askingPrice: Long,
    val negotiable: Boolean,
    val city: String,
    val locality: String?,
    val status: String,
    @Json(name = "registration_number_masked") val registrationNumberMasked: String?,
    val images: List<ListingImageDto> = emptyList(),
)

@JsonClass(generateAdapter = true)
data class ListingListResponse(
    val items: List<ListingDto>,
    val total: Int,
    val page: Int,
    val limit: Int,
    val pages: Int,
)

@JsonClass(generateAdapter = true)
data class ApiErrorBody(
    val error: ApiErrorDetail?,
)

@JsonClass(generateAdapter = true)
data class ApiErrorDetail(
    val code: String?,
    val message: String?,
)
