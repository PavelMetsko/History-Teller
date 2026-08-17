package com.decima.historyteller

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.util.LruCache
import androidx.compose.foundation.Image
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.produceState
import androidx.compose.runtime.remember
import androidx.compose.ui.graphics.ImageBitmap
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
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

/**
 * Кеш распакованных картинок на весь процесс.
 *
 * Раньше каждая картинка декодировалась прямо в композиции и жила только в `remember`: заход
 * на карту главы распаковывал три десятка обложек 1024×1024 подряд на главном потоке — доска
 * пару секунд не реагировала на касания. Теперь распаковка идёт в фоне, результат переживает
 * уход с экрана, а размер ограничен: спрайт всё равно рисуется в сотню-другую точек.
 */
private const val MAX_SIDE = 640
private val bitmapCache = object : LruCache<String, ImageBitmap>(64 * 1024) {   // килобайты
    override fun sizeOf(key: String, value: ImageBitmap) = value.width * value.height * 4 / 1024
}

private fun decodeCapped(path: String): Bitmap? {
    val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
    BitmapFactory.decodeFile(path, bounds)
    var sample = 1
    while (maxOf(bounds.outWidth, bounds.outHeight) / (sample * 2) >= MAX_SIDE) sample *= 2
    return BitmapFactory.decodeFile(path, BitmapFactory.Options().apply { inSampleSize = sample })
}

/** Единый загрузчик картинки по имени. */
@Composable
fun artPainter(name: String): Painter? {
    val ctx = LocalContext.current
    // Ключ по поколению: после докачки главы кадр должен перечитать файл, а не отдать промах.
    val file = remember(name, ContentSync.generation) { artFile(name) }
    if (file != null) {
        val key = remember(file, ContentSync.generation) { "${file.absolutePath}|${ContentSync.generation}" }
        // Из кеша — сразу, без мигания; впервые — в фоне, кадр дорисуется следующим проходом.
        //
        // Присваиваем value ВСЕГДА, а не только когда оно пустое: при смене ключа produceState
        // не сбрасывает прошлое значение, и переиспользованный слот композиции продолжал
        // показывать чужую картинку — на доске Тит Таций выглядел вторым Ромулом.
        val bmp by produceState<ImageBitmap?>(initialValue = bitmapCache.get(key), key1 = key) {
            value = bitmapCache.get(key) ?: withContext(Dispatchers.IO) {
                decodeCapped(file.absolutePath)?.asImageBitmap()?.also { bitmapCache.put(key, it) }
            }
        }
        // High (бикубика), а не дефолтный Low: спрайт рисуется на доске в ~70 px, и
        // билинейная фильтрация рассыпает его в «лесенку». Заметно на плотных экранах
        // невысокого разрешения — на 720p арт выглядел откровенно шакальным.
        bmp?.let { return BitmapPainter(it, filterQuality = FilterQuality.High) }
        return null
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
