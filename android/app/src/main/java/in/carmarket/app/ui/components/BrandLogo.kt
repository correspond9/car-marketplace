package `in`.carmarket.app.ui.components

import androidx.compose.foundation.Image
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import `in`.carmarket.app.R

@Composable
fun BrandLogo(
    modifier: Modifier = Modifier,
    contentDescription: String = "Car-Market",
) {
    Image(
        painter = painterResource(R.drawable.logo),
        contentDescription = contentDescription,
        modifier = modifier,
        contentScale = ContentScale.Fit,
    )
}
