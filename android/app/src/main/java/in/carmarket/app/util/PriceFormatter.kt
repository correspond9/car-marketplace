package in.carmarket.app.util

import java.text.NumberFormat
import java.util.Locale

object PriceFormatter {
    private val formatter = NumberFormat.getCurrencyInstance(Locale("en", "IN"))

    fun format(amount: Long): String = formatter.format(amount)
}
