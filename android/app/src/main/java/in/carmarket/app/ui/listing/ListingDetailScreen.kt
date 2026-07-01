package in.carmarket.app.ui.listing

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import coil.compose.AsyncImage
import in.carmarket.app.ui.theme.Slate600
import in.carmarket.app.util.PriceFormatter
import java.text.NumberFormat
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ListingDetailScreen(
    listingId: String,
    onBack: () -> Unit,
    viewModel: ListingDetailViewModel = viewModel(key = listingId) {
        ListingDetailViewModel(listingId)
    },
) {
    val state by viewModel.uiState.collectAsState()
    val listing = state.listing
    val kmFormatter = NumberFormat.getNumberInstance(Locale("en", "IN"))

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(listing?.let { "${it.make} ${it.model}" } ?: "Listing") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
            )
        },
    ) { padding ->
        when {
            state.isLoading -> {
                Box(
                    Modifier.fillMaxSize().padding(padding),
                    contentAlignment = Alignment.Center,
                ) {
                    CircularProgressIndicator()
                }
            }
            state.error != null -> {
                Box(
                    Modifier.fillMaxSize().padding(padding),
                    contentAlignment = Alignment.Center,
                ) {
                    Text(state.error ?: "Error", color = MaterialTheme.colorScheme.error)
                }
            }
            listing != null -> {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(padding)
                        .verticalScroll(rememberScrollState()),
                ) {
                    val image = listing.images.firstOrNull()
                    if (image != null) {
                        AsyncImage(
                            model = image.url,
                            contentDescription = null,
                            modifier = Modifier
                                .fillMaxWidth()
                                .aspectRatio(4f / 3f),
                            contentScale = ContentScale.Crop,
                        )
                    }
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(
                            buildString {
                                append(listing.make)
                                append(" ")
                                append(listing.model)
                                listing.variant?.let { append(" $it") }
                            },
                            style = MaterialTheme.typography.headlineSmall,
                        )
                        Text(
                            PriceFormatter.format(listing.askingPrice),
                            style = MaterialTheme.typography.headlineMedium,
                            color = MaterialTheme.colorScheme.primary,
                            modifier = Modifier.padding(top = 8.dp),
                        )
                        DetailRow("Year", listing.manufacturingYear.toString())
                        DetailRow("Odometer", "${kmFormatter.format(listing.odometerKm)} km")
                        DetailRow("Fuel", listing.fuelType.replaceFirstChar { it.uppercase() })
                        DetailRow("Transmission", listing.transmission.replaceFirstChar { it.uppercase() })
                        DetailRow("Body", listing.bodyType.replaceFirstChar { it.uppercase() })
                        DetailRow(
                            "Location",
                            buildString {
                                append(listing.city)
                                listing.locality?.let { append(", $it") }
                            },
                        )
                        listing.registrationNumberMasked?.let {
                            DetailRow("Registration", it)
                        }
                        Button(
                            onClick = { },
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(top = 24.dp),
                        ) {
                            Text("Contact seller")
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun DetailRow(label: String, value: String) {
    Text(
        "$label: $value",
        color = Slate600,
        modifier = Modifier.padding(top = 8.dp),
    )
}
