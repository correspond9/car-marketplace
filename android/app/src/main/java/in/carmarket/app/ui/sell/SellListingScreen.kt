package `in`.carmarket.app.ui.sell

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
fun SellListingScreen(
    onSubmitted: () -> Unit,
    viewModel: SellListingViewModel = viewModel(),
) {
    val state by viewModel.uiState.collectAsState()
    val photoPicker = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetMultipleContents(),
    ) { uris: List<Uri> ->
        viewModel.onPhotosSelected(uris)
    }

    Scaffold(
        topBar = {
            TopAppBar(title = { Text("Sell your car") })
        },
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            OutlinedTextField(
                value = state.make,
                onValueChange = viewModel::onMakeChange,
                label = { Text("Make") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
            )
            OutlinedTextField(
                value = state.model,
                onValueChange = viewModel::onModelChange,
                label = { Text("Model") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
            )
            OutlinedTextField(
                value = state.variant,
                onValueChange = viewModel::onVariantChange,
                label = { Text("Variant (optional)") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
            )
            OutlinedTextField(
                value = state.year,
                onValueChange = viewModel::onYearChange,
                label = { Text("Manufacturing year") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
            )
            OutlinedTextField(
                value = state.odometerKm,
                onValueChange = viewModel::onOdometerChange,
                label = { Text("Odometer (km)") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
            )
            OutlinedTextField(
                value = state.price,
                onValueChange = viewModel::onPriceChange,
                label = { Text("Asking price (₹)") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
            )
            OutlinedTextField(
                value = state.city,
                onValueChange = viewModel::onCityChange,
                label = { Text("City") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
            )
            OutlinedTextField(
                value = state.locality,
                onValueChange = viewModel::onLocalityChange,
                label = { Text("Locality (optional)") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
            )

            Text("Fuel type", style = MaterialTheme.typography.labelLarge)
            FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                listOf("petrol", "diesel", "cng", "ev", "hybrid").forEach { fuel ->
                    AssistChip(
                        onClick = { viewModel.onFuelChange(fuel) },
                        label = { Text(fuel.replaceFirstChar { it.uppercase() }) },
                        modifier = Modifier.padding(bottom = 4.dp),
                    )
                }
            }
            Text("Selected: ${state.fuelType}", style = MaterialTheme.typography.bodySmall)

            Text("Transmission", style = MaterialTheme.typography.labelLarge)
            FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                listOf("manual", "automatic").forEach { tx ->
                    AssistChip(
                        onClick = { viewModel.onTransmissionChange(tx) },
                        label = { Text(tx.replaceFirstChar { it.uppercase() }) },
                    )
                }
            }
            Text("Selected: ${state.transmission}", style = MaterialTheme.typography.bodySmall)

            Text("Body type", style = MaterialTheme.typography.labelLarge)
            FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                listOf("hatchback", "sedan", "suv", "muv").forEach { body ->
                    AssistChip(
                        onClick = { viewModel.onBodyTypeChange(body) },
                        label = { Text(body.replaceFirstChar { it.uppercase() }) },
                    )
                }
            }
            Text("Selected: ${state.bodyType}", style = MaterialTheme.typography.bodySmall)

            Button(
                onClick = { photoPicker.launch("image/*") },
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text("Add photos (${state.selectedPhotos.size})")
            }

            state.error?.let {
                Text(it, color = MaterialTheme.colorScheme.error)
            }
            state.successMessage?.let {
                Text(it, color = MaterialTheme.colorScheme.primary)
            }

            Button(
                onClick = { viewModel.submit(onSubmitted) },
                modifier = Modifier.fillMaxWidth(),
                enabled = !state.isSubmitting,
            ) {
                if (state.isSubmitting) {
                    CircularProgressIndicator(modifier = Modifier.padding(4.dp))
                } else {
                    Text("Create listing")
                }
            }
        }
    }
}
