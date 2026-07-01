package in.carmarket.app.data.repository

import in.carmarket.app.data.remote.ApiService
import in.carmarket.app.data.remote.ListingDto

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

    suspend fun getById(id: String): Result<ListingDto> = apiCall {
        api.getListing(id)
    }
}
