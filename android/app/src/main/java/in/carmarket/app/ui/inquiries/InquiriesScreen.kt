package `in`.carmarket.app.ui.inquiries

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Tab
import androidx.compose.material3.TabRow
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.lifecycle.viewmodel.compose.viewModel
import `in`.carmarket.app.CarMarketApp
import `in`.carmarket.app.data.remote.InquiryDto
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class InquiriesUiState(
    val tab: Int = 0,
    val items: List<InquiryDto> = emptyList(),
    val isLoading: Boolean = true,
    val error: String? = null,
    val actionId: String? = null,
)

class InquiriesViewModel : ViewModel() {
    private val inquiryRepository = CarMarketApp.instance.inquiryRepository
    private val _uiState = MutableStateFlow(InquiriesUiState())
    val uiState: StateFlow<InquiriesUiState> = _uiState.asStateFlow()

    init {
        load()
    }

    fun setTab(tab: Int) {
        _uiState.update { it.copy(tab = tab) }
        load()
    }

    fun load() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            val result = if (_uiState.value.tab == 0) {
                inquiryRepository.inbox()
            } else {
                inquiryRepository.sent()
            }
            result.fold(
                onSuccess = { items -> _uiState.update { it.copy(items = items, isLoading = false) } },
                onFailure = { e -> _uiState.update { it.copy(isLoading = false, error = e.message) } },
            )
        }
    }

    fun accept(id: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(actionId = id) }
            inquiryRepository.accept(id).fold(
                onSuccess = { updated ->
                    _uiState.update { state ->
                        state.copy(
                            items = state.items.map { if (it.id == id) updated else it },
                            actionId = null,
                        )
                    }
                },
                onFailure = { e -> _uiState.update { it.copy(actionId = null, error = e.message) } },
            )
        }
    }

    fun decline(id: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(actionId = id) }
            inquiryRepository.decline(id).fold(
                onSuccess = { updated ->
                    _uiState.update { state ->
                        state.copy(
                            items = state.items.map { if (it.id == id) updated else it },
                            actionId = null,
                        )
                    }
                },
                onFailure = { e -> _uiState.update { it.copy(actionId = null, error = e.message) } },
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun InquiriesScreen(
    onBack: () -> Unit,
    viewModel: InquiriesViewModel = viewModel(),
) {
    val state by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = { TopAppBar(title = { Text("Messages") }) },
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding),
        ) {
            TabRow(selectedTabIndex = state.tab) {
                Tab(selected = state.tab == 0, onClick = { viewModel.setTab(0) }, text = { Text("Received") })
                Tab(selected = state.tab == 1, onClick = { viewModel.setTab(1) }, text = { Text("Sent") })
            }
            when {
                state.isLoading -> {
                    Column(
                        Modifier.fillMaxSize(),
                        verticalArrangement = Arrangement.Center,
                        horizontalAlignment = Alignment.CenterHorizontally,
                    ) {
                        CircularProgressIndicator()
                    }
                }
                state.error != null && state.items.isEmpty() -> {
                    Text(
                        state.error ?: "Error",
                        color = MaterialTheme.colorScheme.error,
                        modifier = Modifier.padding(16.dp),
                    )
                }
                state.items.isEmpty() -> {
                    Text(
                        "No messages yet",
                        modifier = Modifier.padding(16.dp),
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
                else -> {
                    LazyColumn(
                        modifier = Modifier.padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp),
                    ) {
                        items(state.items, key = { it.id }) { inquiry ->
                            Column(Modifier.fillMaxWidth()) {
                                Text(inquiry.status.uppercase(), style = MaterialTheme.typography.labelSmall)
                                Text(inquiry.message, modifier = Modifier.padding(vertical = 4.dp))
                                inquiry.sellerPhone?.let {
                                    Text("Seller: $it", color = MaterialTheme.colorScheme.primary)
                                }
                                inquiry.buyerPhone?.let {
                                    Text("Buyer: $it", color = MaterialTheme.colorScheme.primary)
                                }
                                if (state.tab == 0 && inquiry.status == "open") {
                                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                        Button(
                                            onClick = { viewModel.accept(inquiry.id) },
                                            enabled = state.actionId != inquiry.id,
                                        ) { Text("Accept") }
                                        OutlinedButton(
                                            onClick = { viewModel.decline(inquiry.id) },
                                            enabled = state.actionId != inquiry.id,
                                        ) { Text("Decline") }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
