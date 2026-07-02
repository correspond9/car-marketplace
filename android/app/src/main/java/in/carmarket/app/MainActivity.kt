package `in`.carmarket.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import `in`.carmarket.app.ui.navigation.AppNavHost
import `in`.carmarket.app.ui.theme.CarMarketTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            CarMarketTheme {
                AppNavHost()
            }
        }
    }
}
