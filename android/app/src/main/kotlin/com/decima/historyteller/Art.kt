package com.decima.historyteller

import android.content.Context
import android.graphics.BitmapFactory
import androidx.compose.foundation.Image
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.FilterQuality
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.painter.BitmapPainter
import androidx.compose.ui.graphics.painter.Painter
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource

/**
 * Доступ к арту. Приоритет: скачанное через [ContentSync] → вшитое в res/drawable.
 *
 * Play Asset Delivery отсюда убран: доставку глав целиком взял на себя ContentSync, и это
 * единственный механизм на обе платформы вместо трёх разных (PAD, ODR, бандл).
 */
private fun artFile(name: String) = ContentSync.fileFor("art/$name.webp")

/** Есть ли арт (скачанный или вшитый) — для выбора позы без отрисовки. */
fun artExists(ctx: Context, name: String): Boolean =
    artFile(name) != null || ctx.resources.getIdentifier(name, "drawable", ctx.packageName) != 0

/** Единый загрузчик картинки по имени. */
@Composable
fun artPainter(name: String): Painter? {
    val ctx = LocalContext.current
    // Ключ по поколению: после докачки главы кадр должен перечитать файл, а не отдать промах.
    val file = remember(name, ContentSync.generation) { artFile(name) }
    if (file != null) {
        val bmp = remember(file.absolutePath) { BitmapFactory.decodeFile(file.absolutePath)?.asImageBitmap() }
        // High (бикубика), а не дефолтный Low: спрайт 768 px рисуется на доске в ~70 px, и
        // билинейная фильтрация рассыпает его в «лесенку». Заметно на плотных экранах
        // невысокого разрешения — на 720p арт выглядел откровенно шакальным.
        if (bmp != null) return BitmapPainter(bmp, filterQuality = FilterQuality.High)
    }
    val resId = remember(name) { ctx.resources.getIdentifier(name, "drawable", ctx.packageName) }
    return if (resId != 0) painterResource(resId) else null
}

/** Drop-in: рисует картинку по имени, если найдена. */
@Composable
fun ArtImage(name: String, modifier: Modifier = Modifier, contentScale: ContentScale = ContentScale.Fit) {
    val p = artPainter(name)
    if (p != null) Image(p, null, modifier, contentScale = contentScale)
}
