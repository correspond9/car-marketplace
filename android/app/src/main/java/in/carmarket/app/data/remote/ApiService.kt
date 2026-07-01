package in.carmarket.app.data.remote

import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.PATCH
import retrofit2.http.POST
import retrofit2.http.Path
import retrofit2.http.Query

interface ApiService {
    @POST("auth/otp/request")
    suspend fun requestOtp(@Body body: OtpRequestBody)

    @POST("auth/otp/verify")
    suspend fun verifyOtp(@Body body: OtpVerifyBody): TokenResponse

    @DELETE("auth/account")
    suspend fun deleteAccount()

    @GET("users/me")
    suspend fun getMe(): UserMeDto

    @GET("listings")
    suspend fun searchListings(
        @Query("q") query: String? = null,
        @Query("city") city: String? = null,
        @Query("make") make: String? = null,
        @Query("sort") sort: String = "newest",
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 20,
    ): ListingListResponse

    @GET("listings/me")
    suspend fun getMyListings(
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 20,
    ): ListingListResponse

    @GET("listings/{id}")
    suspend fun getListing(@Path("id") id: String): ListingDto

    @POST("listings")
    suspend fun createListing(@Body body: ListingCreateBody): ListingDto

    @POST("listings/{id}/publish")
    suspend fun publishListing(@Path("id") id: String): ListingDto

    @POST("listings/{id}/sold")
    suspend fun markListingSold(@Path("id") id: String): ListingDto

    @DELETE("listings/{id}")
    suspend fun deleteListing(@Path("id") id: String)

    @POST("listings/{id}/images/presign")
    suspend fun presignListingImage(
        @Path("id") id: String,
        @Body body: ImagePresignRequestBody,
    ): ImagePresignResponseDto

    @POST("listings/{id}/images/confirm")
    suspend fun confirmListingImage(
        @Path("id") id: String,
        @Body body: ImageConfirmBody,
    ): ListingImageDto

    @GET("favorites")
    suspend fun getFavorites(
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 20,
    ): ListingListResponse

    @POST("favorites/{listingId}")
    suspend fun addFavorite(@Path("listingId") listingId: String): IdResponse

    @DELETE("favorites/{listingId}")
    suspend fun removeFavorite(@Path("listingId") listingId: String)

    @POST("listings/{listingId}/inquiries")
    suspend fun createInquiry(
        @Path("listingId") listingId: String,
        @Body body: InquiryCreateBody,
    ): InquiryDto

    @GET("inquiries/sent")
    suspend fun getSentInquiries(
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 20,
    ): InquiryListResponse

    @GET("inquiries/inbox")
    suspend fun getInquiryInbox(
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 20,
    ): InquiryListResponse

    @PATCH("inquiries/{inquiryId}/accept")
    suspend fun acceptInquiry(@Path("inquiryId") inquiryId: String): InquiryDto

    @PATCH("inquiries/{inquiryId}/decline")
    suspend fun declineInquiry(@Path("inquiryId") inquiryId: String): InquiryDto

    @GET("reviews")
    suspend fun getReviews(
        @Query("target_type") targetType: String,
        @Query("target_id") targetId: String,
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 20,
    ): ReviewListResponse

    @POST("reviews")
    suspend fun createReview(@Body body: ReviewCreateBody): ReviewDto

    @POST("dealer-stores")
    suspend fun createDealerStore(@Body body: DealerStoreCreateBody): DealerStoreDto

    @GET("dealer-stores/{slug}")
    suspend fun getDealerStore(@Path("slug") slug: String): DealerStoreDto

    @PATCH("dealer-stores/me")
    suspend fun updateMyDealerStore(@Body body: DealerStoreCreateBody): DealerStoreDto

    @GET("dealer-stores/me/listings")
    suspend fun getDealerStoreListings(
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 20,
    ): ListingListResponse
}
