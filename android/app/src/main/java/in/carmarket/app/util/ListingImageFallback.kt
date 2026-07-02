package `in`.carmarket.app.util

import `in`.carmarket.app.R
import `in`.carmarket.app.data.remote.ListingDto

private val CAR_IMAGE_PAIRS: Map<String, List<Int>> = mapOf(
    "maruti|swift" to listOf(R.drawable.listing_maruti_swift, R.drawable.listing_maruti_swift2),
    "hyundai|creta" to listOf(R.drawable.listing_hyundai_creta, R.drawable.listing_hyundai_creta2),
    "tata|nexon" to listOf(R.drawable.listing_tata_nexon, R.drawable.listing_tata_nexon2),
)

private fun carKey(make: String, model: String): String =
    "${make.trim().lowercase()}|${model.trim().lowercase()}"

/** First listing of a car in the feed → image 1; second → image with "2" in the name. */
fun buildListingImageSlots(listings: List<ListingDto>): Map<String, Int> {
    val seen = mutableMapOf<String, Int>()
    val slots = mutableMapOf<String, Int>()
    for (listing in listings) {
        val key = carKey(listing.make, listing.model)
        val slot = seen.getOrDefault(key, 0)
        seen[key] = slot + 1
        slots[listing.id] = slot
    }
    return slots
}

fun listingFallbackDrawable(make: String, model: String, imageSlot: Int = 0): Int? {
    val pair = CAR_IMAGE_PAIRS[carKey(make, model)] ?: return null
    return pair[imageSlot % pair.size]
}

/** Detail pages: the "2" image goes with the second variant in our sample data. */
fun listingImageSlotFromVariant(make: String, model: String, variant: String?): Int {
    val v = variant?.trim()?.lowercase().orEmpty()
    return when (carKey(make, model)) {
        "maruti|swift" -> if (v == "zxi") 1 else 0
        "hyundai|creta" -> if (v.contains("sx(o)")) 1 else 0
        "tata|nexon" -> if (v == "ev max") 1 else 0
        else -> 0
    }
}
