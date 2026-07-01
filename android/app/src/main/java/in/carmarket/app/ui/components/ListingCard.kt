package in.carmarket.app.ui.components

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import in.carmarket.app.data.remote.ListingDto
import in.carmarket.app.ui.theme.Slate600
import in.carmarket.app.util.PriceFormatter
import java.text.NumberFormat
import java.util.Locale

@Composable
fun ListingCard(
    listing: ListingDto,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val cover = listing.images.firstOrNull { it.isCover } ?: listing.images.firstOrNull()
    val km = NumberFormat.getNumberInstance(Locale("en", "IN")).format(listing.odometerKm)

    Card(
        modifier = modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
    ) {
        if (cover != null) {
            AsyncImage(
                model = cover.url,
                contentDescription = "${listing.make} ${listing.model}",
                modifier = Modifier
                    .fillMaxWidth()
                    .aspectRatio(16f / 10f),
                contentScale = ContentScale.Crop,
            )
        }
        Column(modifier = Modifier.padding(12.dp)) {
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
                modifier = Modifier.padding(top = 8.dp),
            )
        }
    }
}
