package `in`.carmarket.app.data.remote

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
data class UserMeDto(
    val id: String,
    val phone: String,
    val email: String?,
    @Json(name = "display_name") val displayName: String?,
    val city: String?,
    val role: String,
    @Json(name = "phone_verified") val phoneVerified: Boolean = false,
    @Json(name = "email_verified") val emailVerified: Boolean = false,
    @Json(name = "profile_photo_url") val profilePhotoUrl: String?,
    @Json(name = "created_at") val createdAt: String?,
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
data class ListingCreateBody(
    val make: String,
    val model: String,
    val variant: String? = null,
    @Json(name = "manufacturing_year") val manufacturingYear: Int,
    @Json(name = "body_type") val bodyType: String,
    @Json(name = "fuel_type") val fuelType: String,
    val transmission: String,
    @Json(name = "odometer_km") val odometerKm: Int,
    @Json(name = "asking_price") val askingPrice: Long,
    val city: String,
    val locality: String? = null,
    val negotiable: Boolean = true,
)

@JsonClass(generateAdapter = true)
data class ImagePresignRequestBody(
    val filename: String,
    @Json(name = "content_type") val contentType: String,
)

@JsonClass(generateAdapter = true)
data class ImagePresignResponseDto(
    @Json(name = "upload_url") val uploadUrl: String,
    @Json(name = "storage_key") val storageKey: String,
    @Json(name = "content_type") val contentType: String,
    @Json(name = "expires_in") val expiresIn: Int,
)

@JsonClass(generateAdapter = true)
data class ImageConfirmBody(
    @Json(name = "storage_key") val storageKey: String,
    @Json(name = "sort_order") val sortOrder: Int = 0,
    @Json(name = "is_cover") val isCover: Boolean = false,
)

@JsonClass(generateAdapter = true)
data class InquiryCreateBody(val message: String)

@JsonClass(generateAdapter = true)
data class InquiryDto(
    val id: String,
    @Json(name = "listing_id") val listingId: String,
    @Json(name = "buyer_id") val buyerId: String,
    @Json(name = "seller_id") val sellerId: String,
    val message: String,
    val status: String,
    @Json(name = "created_at") val createdAt: String?,
    @Json(name = "seller_phone") val sellerPhone: String? = null,
    @Json(name = "buyer_phone") val buyerPhone: String? = null,
)

@JsonClass(generateAdapter = true)
data class InquiryListResponse(
    val items: List<InquiryDto>,
    val total: Int,
    val page: Int,
    val limit: Int,
)

@JsonClass(generateAdapter = true)
data class ReviewDto(
    val id: String,
    @Json(name = "reviewer_id") val reviewerId: String,
    @Json(name = "target_type") val targetType: String,
    @Json(name = "target_id") val targetId: String,
    val rating: Int,
    val text: String?,
    @Json(name = "seller_reply") val sellerReply: String?,
    val status: String,
    @Json(name = "created_at") val createdAt: String?,
)

@JsonClass(generateAdapter = true)
data class ReviewListResponse(
    val items: List<ReviewDto>,
    val total: Int,
    val page: Int,
    val limit: Int,
)

@JsonClass(generateAdapter = true)
data class ReviewCreateBody(
    @Json(name = "target_type") val targetType: String,
    @Json(name = "target_id") val targetId: String,
    val rating: Int,
    val text: String? = null,
)

@JsonClass(generateAdapter = true)
data class DealerStoreDto(
    val id: String,
    @Json(name = "owner_id") val ownerId: String,
    val name: String,
    val slug: String,
    val description: String?,
    val city: String?,
    val state: String?,
    @Json(name = "rating_avg") val ratingAvg: Double = 0.0,
    @Json(name = "rating_count") val ratingCount: Int = 0,
    @Json(name = "verification_status") val verificationStatus: String?,
)

@JsonClass(generateAdapter = true)
data class DealerStoreCreateBody(
    val name: String,
    val slug: String? = null,
    val description: String? = null,
    val city: String? = null,
    val state: String? = null,
)

@JsonClass(generateAdapter = true)
data class IdResponse(val id: String)

@JsonClass(generateAdapter = true)
data class ApiErrorBody(
    val error: ApiErrorDetail?,
)

@JsonClass(generateAdapter = true)
data class ApiErrorDetail(
    val code: String?,
    val message: String?,
)

@JsonClass(generateAdapter = true)
data class RecentlyViewedItemDto(
    @Json(name = "listing_id") val listingId: String,
    @Json(name = "viewed_at") val viewedAt: String,
    val listing: ListingDto?,
)

@JsonClass(generateAdapter = true)
data class RecentlyViewedListResponse(
    val items: List<RecentlyViewedItemDto>,
    val total: Int,
)
