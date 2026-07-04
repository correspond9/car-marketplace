package `in`.carmarket.app.ui.auth

import android.net.Uri
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.media3.common.MediaItem
import androidx.media3.common.Player
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.ui.AspectRatioFrameLayout
import androidx.media3.ui.PlayerView
import `in`.carmarket.app.R
import `in`.carmarket.app.ui.components.BrandLogo
import `in`.carmarket.app.ui.components.MatteGlassCard
import `in`.carmarket.app.ui.theme.Slate600

@Composable
fun LoginScreen(
    onLoggedIn: () -> Unit,
    viewModel: LoginViewModel = viewModel(),
) {
    val state by viewModel.uiState.collectAsState()
    val context = LocalContext.current
    val bgOverlay = Brush.verticalGradient(
        colors = listOf(Color(0x33020617), Color(0x99020E1F), Color(0xCC020617)),
    )
    val backgroundPlayer = remember(context) {
        ExoPlayer.Builder(context).build().apply {
            repeatMode = Player.REPEAT_MODE_ALL
            volume = 0f
            playWhenReady = true
            val videoUri = Uri.parse("android.resource://${context.packageName}/${R.raw.login_background}")
            setMediaItem(MediaItem.fromUri(videoUri))
            prepare()
        }
    }

    DisposableEffect(backgroundPlayer) {
        onDispose { backgroundPlayer.release() }
    }

    Scaffold(containerColor = Color.Transparent) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding),
        ) {
            AndroidView(
                factory = { ctx ->
                    PlayerView(ctx).apply {
                        useController = false
                        resizeMode = AspectRatioFrameLayout.RESIZE_MODE_ZOOM
                        player = backgroundPlayer
                    }
                },
                modifier = Modifier.fillMaxSize(),
            )
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(bgOverlay),
            )
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(24.dp),
                verticalArrangement = Arrangement.Center,
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                BrandLogo(modifier = Modifier.height(56.dp))
                MatteGlassCard(modifier = Modifier.fillMaxWidth().padding(top = 24.dp)) {
                    Column(modifier = Modifier.padding(20.dp)) {
                        Text(
                            "Login to Auto Link Marketplace",
                            style = MaterialTheme.typography.headlineSmall,
                            modifier = Modifier.padding(bottom = 8.dp),
                        )
                        Text(
                            "Sign in with your mobile number",
                            color = Slate600,
                            modifier = Modifier.padding(bottom = 20.dp),
                        )

                        OutlinedTextField(
                            value = state.phone,
                            onValueChange = viewModel::onPhoneChange,
                            label = { Text("Mobile number") },
                            prefix = { Text("+91 ") },
                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone),
                            singleLine = true,
                            modifier = Modifier.fillMaxWidth(),
                            enabled = !state.otpSent && !state.isLoading,
                        )

                        if (state.otpSent) {
                            Spacer(modifier = Modifier.height(16.dp))
                            OutlinedTextField(
                                value = state.otp,
                                onValueChange = viewModel::onOtpChange,
                                label = { Text("OTP") },
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.NumberPassword),
                                singleLine = true,
                                modifier = Modifier.fillMaxWidth(),
                                enabled = !state.isLoading,
                            )
                            Text(
                                "Test OTP: 123456",
                                style = MaterialTheme.typography.bodySmall,
                                color = Slate600,
                                modifier = Modifier.padding(top = 8.dp),
                            )
                        }

                        state.error?.let {
                            Text(
                                it,
                                color = MaterialTheme.colorScheme.error,
                                modifier = Modifier.padding(top = 12.dp),
                            )
                        }

                        Spacer(modifier = Modifier.height(20.dp))

                        if (state.isLoading) {
                            CircularProgressIndicator(modifier = Modifier.align(Alignment.CenterHorizontally))
                        } else if (state.otpSent) {
                            Button(
                                onClick = { viewModel.verifyOtp(onLoggedIn) },
                                modifier = Modifier.fillMaxWidth(),
                            ) {
                                Text("Verify & continue")
                            }
                        } else {
                            Button(
                                onClick = viewModel::requestOtp,
                                modifier = Modifier.fillMaxWidth(),
                            ) {
                                Text("Send OTP")
                            }
                        }
                    }
                }
            }
        }
    }
}
