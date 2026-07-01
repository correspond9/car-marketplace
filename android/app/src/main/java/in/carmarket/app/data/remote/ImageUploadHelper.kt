package in.carmarket.app.data.remote

import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import java.util.concurrent.TimeUnit

object ImageUploadHelper {
    private val client = OkHttpClient.Builder()
        .connectTimeout(60, TimeUnit.SECONDS)
        .writeTimeout(60, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .build()

    fun uploadPut(uploadUrl: String, bytes: ByteArray, contentType: String) {
        val body = bytes.toRequestBody(contentType.toMediaType())
        val request = Request.Builder()
            .url(uploadUrl)
            .put(body)
            .build()
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                throw IllegalStateException("Image upload failed (${response.code})")
            }
        }
    }
}
