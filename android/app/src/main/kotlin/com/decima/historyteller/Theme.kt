package com.decima.historyteller

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.translate
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Outline
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.unit.Density
import androidx.compose.ui.unit.LayoutDirection

/** Бумажная палитра History Teller (порт DS.Palette из iOS). */
object Palette {
    val backdrop = Color(0xFF34222E)
    val paperEdge = Color(0xFFDECBA3)
    val ribbon = Color(0xFF982F34)
    val paper = Color(0xFFF1E4C7)
    val panel = Color(0xFFF7EFDC)
    val ink = Color(0xFF2B2419)
    val inkSoft = Color(0xFF2B2419).copy(alpha = 0.55f)
    val gold = Color(0xFFC9A24B)
    val maroon = Color(0xFF8A3B4A)
    val sky = Color(0xFFBFE0E0)
    val love = Color(0xFFCD4444)
    val success = Color(0xFF4C8B51)
}

object Fonts {
    val serif = FontFamily.Serif        // заголовки уровней/глав
    val rounded = FontFamily.SansSerif  // тело (округлого нет в стоке — sans)
}

/** Пергаментная «страница книги»: заливка + контур + золотые уголки + тень. */
@Composable
fun BookPage(modifier: Modifier = Modifier, content: @Composable BoxScope.() -> Unit) {
    Box(
        modifier
            .shadow(14.dp, RoundedCornerShape(22.dp))
            .clip(RoundedCornerShape(22.dp))
            .drawBehind {
                drawRoundRect(Palette.paper, cornerRadius = androidx.compose.ui.geometry.CornerRadius(22.dp.toPx()))
                drawRoundRect(
                    Palette.paperEdge, cornerRadius = androidx.compose.ui.geometry.CornerRadius(22.dp.toPx()),
                    style = Stroke(width = 6.dp.toPx())
                )
                drawRoundRect(
                    Palette.ink.copy(alpha = 0.45f),
                    cornerRadius = androidx.compose.ui.geometry.CornerRadius(22.dp.toPx()),
                    style = Stroke(width = 2.dp.toPx())
                )
                goldCorners(inset = 10.dp.toPx(), length = 16.dp.toPx(), thickness = 5.dp.toPx())
            },
        content = content
    )
}

/** L-образные золотые скобки по углам (порт GoldCorners). */
private fun androidx.compose.ui.graphics.drawscope.DrawScope.goldCorners(inset: Float, length: Float, thickness: Float) {
    val w = size.width; val h = size.height; val i = inset; val l = length
    val g = Palette.gold
    fun line(a: Offset, b: Offset) = drawLine(g, a, b, strokeWidth = thickness, cap = StrokeCap.Round)
    // TL
    line(Offset(i, i + l), Offset(i, i)); line(Offset(i, i), Offset(i + l, i))
    // TR
    line(Offset(w - i - l, i), Offset(w - i, i)); line(Offset(w - i, i), Offset(w - i, i + l))
    // BL
    line(Offset(i, h - i - l), Offset(i, h - i)); line(Offset(i, h - i), Offset(i + l, h - i))
    // BR
    line(Offset(w - i - l, h - i), Offset(w - i, h - i)); line(Offset(w - i, h - i), Offset(w - i, h - i - l))
}


/**
 * Лента-закладка: прямоугольник с треугольным вырезом снизу («рыбий хвост»).
 * Порт RibbonShape из iOS — на Android «назад» была простой скруглённой плашкой.
 */
object RibbonShape : Shape {
    override fun createOutline(size: Size, layoutDirection: LayoutDirection, density: Density): Outline {
        val notch = with(density) { 12.dp.toPx() }
        return Outline.Generic(Path().apply {
            moveTo(0f, 0f)
            lineTo(size.width, 0f)
            lineTo(size.width, size.height)
            lineTo(size.width / 2f, size.height - notch)
            lineTo(0f, size.height)
            close()
        })
    }
}
