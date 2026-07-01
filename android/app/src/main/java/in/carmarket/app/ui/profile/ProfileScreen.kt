package in.carmarket.app.ui.profile

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import in.carmarket.app.ui.theme.Slate600

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(
    onLoggedOut: () -> Unit,
    onMyListings: () -> Unit,
    viewModel: ProfileViewModel = viewModel(),
) {
    val state by viewModel.uiState.collectAsState()

    if (state.showDeleteConfirm) {
        AlertDialog(
            onDismissRequest = viewModel::dismissDeleteConfirm,
            title = { Text("Delete account?") },
            text = { Text("This permanently removes your account and listings. This cannot be undone.") },
            confirmButton = {
                TextButton(onClick = { viewModel.deleteAccount(onLoggedOut) }) {
                    Text("Delete", color = MaterialTheme.colorScheme.error)
                }
            },
            dismissButton = {
                TextButton(onClick = viewModel::dismissDeleteConfirm) {
                    Text("Cancel")
                }
            },
        )
    }

    Scaffold(
        topBar = {
            TopAppBar(title = { Text("Profile") })
        },
    ) { padding ->
        when {
            state.isLoading -> {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(padding),
                    verticalArrangement = Arrangement.Center,
                    horizontalAlignment = Alignment.CenterHorizontally,
                ) {
                    CircularProgressIndicator()
                }
            }
            else -> {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(padding)
                        .padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    state.user?.let { user ->
                        Text(
                            user.displayName ?: "CarMarket user",
                            style = MaterialTheme.typography.headlineSmall,
                        )
                        Text(user.phone, color = Slate600)
                        user.city?.let { Text("City: $it", color = Slate600) }
                        Text("Role: ${user.role}", color = Slate600)
                    }
                    state.error?.let {
                        Text(it, color = MaterialTheme.colorScheme.error)
                    }
                    Button(
                        onClick = onMyListings,
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Text("My listings")
                    }
                    OutlinedButton(
                        onClick = {
                            viewModel.logout()
                            onLoggedOut()
                        },
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Text("Log out")
                    }
                    OutlinedButton(
                        onClick = viewModel::confirmDelete,
                        modifier = Modifier.fillMaxWidth(),
                        enabled = !state.isDeleting,
                    ) {
                        Text("Delete account", color = MaterialTheme.colorScheme.error)
                    }
                }
            }
        }
    }
}
