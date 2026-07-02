package `in`.carmarket.app.util

import org.junit.Assert.assertTrue
import org.junit.Test

class PriceFormatterTest {
    @Test
    fun formatIndianCurrency() {
        val result = PriceFormatter.format(575_000L)
        assertTrue(result.contains("575") || result.contains("5,75,000"))
    }
}
