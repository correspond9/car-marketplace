package `in`.carmarket.app.ui.components

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import `in`.carmarket.app.data.remote.ListingDto
import `in`.carmarket.app.ui.theme.Slate600
import `in`.carmarket.app.util.PriceFormatter
import `in`.carmarket.app.util.listingFallbackDrawable
import java.text.NumberFormat
import java.util.Locale

@Composable
fun ListingCard(
    listing: ListingDto,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    imageSlot: Int = 0,
) {
    val cover = listing.images.firstOrNull { it.isCover } ?: listing.images.firstOrNull()
    val imageModel = cover?.url ?: listingFallbackDrawable(listing.make, listing.model, imageSlot)
    val km = NumberFormat.getNumberInstance(Locale("en", "IN")).format(listing.odometerKm)

    val cardShape = RoundedCornerShape(12.dp)
    val imageShape = RoundedCornerShape(topStart = 12.dp, topEnd = 12.dp)

    MatteGlassCard(
        modifier = modifier.fillMaxWidth(),
        onClick = onClick,
        shape = cardShape,
    ) {
        if (imageModel != null) {
            AsyncImage(
                model = imageModel,
                contentDescription = "${listing.make} ${listing.model}",
                modifier = Modifier
                    .fillMaxWidth()
                    .aspectRatio(16f / 10f)
                    .clip(imageShape),
                contentScale = ContentScale.Crop,
            )
        }
        Column(modifier = Modifier.padding(horizontal = 10.dp, vertical = 8.dp)) {
            Text(
                text = buildString {
                    append(listing.make)
                    append(" ")
                    append(listing.model)
                    listing.variant?.let { append(" $it") }
                },
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
            )
            Text(
                text = "${listing.manufacturingYear} · $km km · ${listing.city}",
                style = MaterialTheme.typography.bodySmall,
                color = Slate600,
                modifier = Modifier.padding(top = 4.dp),
            )
            Text(
                text = PriceFormatter.format(listing.askingPrice),
                style = MaterialTheme.typography.titleLarge,
                color = MaterialTheme.colorScheme.primary,
                modifier = Modifier.padding(top = 6.dp),
            )
        }
    }
}
