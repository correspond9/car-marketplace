package `in`.carmarket.app.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val LightColors = lightColorScheme(
    primary = Green700,
    onPrimary = Color.White,
    secondary = Green800,
    background = Slate50,
    onBackground = Slate900,
    surface = MatteGlassSurface,
    onSurface = Slate900,
    surfaceVariant = Slate100,
)

@Composable
fun CarMarketTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = LightColors,
        content = content,
    )
}
