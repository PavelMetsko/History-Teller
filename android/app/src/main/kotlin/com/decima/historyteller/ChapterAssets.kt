package com.decima.historyteller

import android.content.Context
import android.graphics.BitmapFactory
import androidx.compose.foundation.Image
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.painter.BitmapPainter
import androidx.compose.ui.graphics.painter.Painter
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import com.google.android.play.core.assetpacks.AssetPackManagerFactory
import com.google.android.play.core.assetpacks.AssetPackState
import com.google.android.play.core.assetpacks.AssetPackStateUpdateListener
import com.google.android.play.core.assetpacks.model.AssetPackStatus
import kotlinx.coroutines.suspendCancellableCoroutine
import java.io.File
import kotlin.coroutines.resume

/**
 * Play Asset Delivery: арт глав живёт в on-demand asset-паках (Google Play хостит), а не в res.
 * Пак содержит файлы-ассеты, поэтому картинки грузятся по файловому пути, а не через painterResource.
 * Установочный арт (Рим + общий) остаётся в res/drawable.
 */
object ChapterAssets {
    /** Эпохи, доставляемые on-demand паком. Rome + общий арт — в установке (res).  */
    private val packEpochs = setOf("tudor", "revolution", "empire", "borgia", "byzantium")
    fun packFor(epoch: String): String? = if (epoch in packEpochs) "chapter_$epoch" else null

    private val fileCache = HashMap<String, File?>()

    /** Файл ассета из скачанного пака (или null, если это не пак-ассет или пак не скачан). */
    fun packFile(ctx: Context, name: String): File? = fileCache.getOrPut(name) {
        val mgr = AssetPackManagerFactory.getInstance(ctx)
        for (epoch in packEpochs) {
            val loc = mgr.getPackLocation("chapter_$epoch") ?: continue
            val dir = loc.assetsPath() ?: continue
            val f = File(dir, "$name.png")
            if (f.exists()) return@getOrPut f
        }
        null
    }

    /** Скачать пак главы с прогрессом. Если это не пак-эпоха или пак уже установлен — сразу готово. */
    suspend fun fetch(ctx: Context, epoch: String, onProgress: (Float) -> Unit) {
        val pack = packFor(epoch) ?: return
        val mgr = AssetPackManagerFactory.getInstance(ctx)
        if (mgr.getPackLocation(pack) != null) { onProgress(1f); return }
        suspendCancellableCoroutine<Unit> { cont ->
            lateinit var listener: AssetPackStateUpdateListener
            listener = AssetPackStateUpdateListener { state: AssetPackState ->
                if (state.name() != pack) return@AssetPackStateUpdateListener
                when (state.status()) {
                    AssetPackStatus.DOWNLOADING -> {
                        val total = state.totalBytesToDownload()
                        if (total > 0) onProgress((state.bytesDownloaded().toFloat() / total).coerceIn(0f, 0.99f))
                    }
                    AssetPackStatus.COMPLETED -> {
                        mgr.unregisterListener(listener); fileCache.clear(); onProgress(1f)
                        if (cont.isActive) cont.resume(Unit)
                    }
                    AssetPackStatus.FAILED, AssetPackStatus.CANCELED -> {
                        mgr.unregisterListener(listener)
                        if (cont.isActive) cont.resume(Unit)   // не блокируем — фолбэк на симуляцию
                    }
                    else -> {}
                }
            }
            mgr.registerListener(listener)
            mgr.fetch(listOf(pack))
            cont.invokeOnCancellation { mgr.unregisterListener(listener) }
        }
    }
}

/** Есть ли арт (в res или в скачанном паке) — для выбора позы без отрисовки. */
fun artExists(ctx: Context, name: String): Boolean =
    ctx.resources.getIdentifier(name, "drawable", ctx.packageName) != 0 || ChapterAssets.packFile(ctx, name) != null

/** Единый загрузчик картинки: сначала res (установка), потом файл из скачанного пака. */
@Composable
fun artPainter(name: String): Painter? {
    val ctx = LocalContext.current
    val resId = remember(name) { ctx.resources.getIdentifier(name, "drawable", ctx.packageName) }
    if (resId != 0) return painterResource(resId)
    val file = remember(name) { ChapterAssets.packFile(ctx, name) }
    if (file != null) {
        val bmp = remember(file.absolutePath) { BitmapFactory.decodeFile(file.absolutePath)?.asImageBitmap() }
        if (bmp != null) return BitmapPainter(bmp)
    }
    return null
}

/** Drop-in: рисует картинку по имени (res или пак), если найдена. */
@Composable
fun ArtImage(name: String, modifier: Modifier = Modifier, contentScale: ContentScale = ContentScale.Fit) {
    val p = artPainter(name)
    if (p != null) Image(p, null, modifier, contentScale = contentScale)
}
