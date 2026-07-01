package in.carmarket.app.data.repository

import android.content.ContentResolver
import android.net.Uri
import in.carmarket.app.data.remote.ApiService
import in.carmarket.app.data.remote.ImageConfirmBody
import in.carmarket.app.data.remote.ImagePresignRequestBody
import in.carmarket.app.data.remote.ImageUploadHelper
import in.carmarket.app.data.remote.ListingCreateBody
import in.carmarket.app.data.remote.ListingDto
import in.carmarket.app.data.remote.ListingImageDto
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class ListingRepository(private val api: ApiService) {
    suspend fun search(
        query: String? = null,
        city: String? = null,
        make: String? = null,
        page: Int = 1,
        limit: Int = 20,
    ): Result<List<ListingDto>> = apiCall {
        api.searchListings(
            query = query?.ifBlank { null },
            city = city?.ifBlank { null },
            make = make?.ifBlank { null },
            page = page,
            limit = limit,
        ).items
    }

    suspend fun getMine(page: Int = 1, limit: Int = 20): Result<List<ListingDto>> = apiCall {
        api.getMyListings(page = page, limit = limit).items
    }

    suspend fun getById(id: String): Result<ListingDto> = apiCall {
        api.getListing(id)
    }

    suspend fun create(body: ListingCreateBody): Result<ListingDto> = apiCall {
        api.createListing(body)
    }

    suspend fun publish(id: String): Result<ListingDto> = apiCall {
        api.publishListing(id)
    }

    suspend fun markSold(id: String): Result<ListingDto> = apiCall {
        api.markListingSold(id)
    }

    suspend fun delete(id: String): Result<Unit> = apiCall {
        api.deleteListing(id)
    }

    suspend fun uploadImage(
        listingId: String,
        uri: Uri,
        contentResolver: ContentResolver,
        isCover: Boolean,
        sortOrder: Int,
    ): Result<ListingImageDto> = apiCall {
        withContext(Dispatchers.IO) {
            val mimeType = contentResolver.getType(uri) ?: "image/jpeg"
            val filename = "photo_${System.currentTimeMillis()}.jpg"
            val presign = api.presignListingImage(
                listingId,
                ImagePresignRequestBody(filename = filename, contentType = mimeType),
            )
            val bytes = contentResolver.openInputStream(uri)?.use { it.readBytes() }
                ?: throw IllegalStateException("Could not read photo")
            ImageUploadHelper.uploadPut(presign.uploadUrl, bytes, presign.contentType)
            api.confirmListingImage(
                listingId,
                ImageConfirmBody(
                    storageKey = presign.storageKey,
                    sortOrder = sortOrder,
                    isCover = isCover,
                ),
            )
        }
    }
}
