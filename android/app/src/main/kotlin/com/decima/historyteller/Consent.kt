package com.decima.historyteller

import android.content.Context
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalUriHandler
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextDecoration
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.util.Locale
import java.util.TimeZone

/**
 * Согласие на рекламные данные — без стороннего CMP (порт ConsentService с iOS). AppLovin MAX
 * и Tenjin принимают простой флаг согласия, выставляемый до старта их SDK, поэтому спрашиваем
 * сами: в GDPR-регионе (ЕЭЗ, UK, Швейцария) — своё окно [ConsentDialog], в остальных — ничего.
 * ATT на Android нет — рекламный ID регулируется настройками системы.
 */
object ConsentService {
    enum class Choice { GRANTED, DENIED }

    private const val PREFS = "ht.ads"
    private const val KEY = "consent"

    private val _choice = MutableStateFlow<Choice?>(null)
    val choice: StateFlow<Choice?> = _choice.asStateFlow()

    /** Показывать окно согласия (первый запуск в GDPR-регионе или строка в настройках). */
    private val _promptVisible = MutableStateFlow(false)
    val promptVisible: StateFlow<Boolean> = _promptVisible.asStateFlow()

    /** В GDPR-регионе — явное согласие; в остальных реклама персональная, пока не отказался (CCPA). */
    val hasUserConsent get() = _choice.value == Choice.GRANTED
    val doNotSell get() = _choice.value == Choice.DENIED

    private var started = false
    private var settled = false
    private val readyHandlers = mutableListOf<() -> Unit>()
    private val changeHandlers = mutableListOf<() -> Unit>()

    /** Игрок поменял ответ (окно из настроек) — SDK обновляют свои флаги. */
    fun onChange(handler: () -> Unit) { changeHandlers += handler }
    private lateinit var appContext: Context

    /** Вызвать, когда согласие отработало (сразу, если уже). */
    fun onReady(handler: () -> Unit) {
        if (settled) handler() else readyHandlers += handler
    }

    /** Раз за сессию, после онбординга. */
    fun start(context: Context) {
        if (started) return
        started = true
        appContext = context.applicationContext
        _choice.value = appContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .getString(KEY, null)?.let { runCatching { Choice.valueOf(it) }.getOrNull() }
        if (_choice.value == null && isGdprRegion()) _promptVisible.value = true else finish()
    }

    /** Строка «Конфиденциальность» в настройках: передумать в любую сторону. */
    fun showPrompt() { _promptVisible.value = true }

    fun answer(context: Context, granted: Boolean) {
        val c = if (granted) Choice.GRANTED else Choice.DENIED
        _choice.value = c
        context.applicationContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .edit().putString(KEY, c.name).apply()
        _promptVisible.value = false
        if (settled) changeHandlers.forEach { it() } else finish()
    }

    private fun finish() {
        if (settled) return
        settled = true
        val handlers = readyHandlers.toList()
        readyHandlers.clear()
        handlers.forEach { it() }
    }

    /** Регион устройства; если его нет — европейский часовой пояс. Лишний раз спросить безопасно. */
    private fun isGdprRegion(): Boolean {
        val region = Locale.getDefault().country
        if (region.isNotEmpty()) return region in GDPR_REGIONS
        return TimeZone.getDefault().id.startsWith("Europe/")
    }

    private val GDPR_REGIONS = setOf(
        "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT",
        "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE",   // ЕС
        "IS", "LI", "NO",                                                         // ЕЭЗ
        "GB", "CH",
    )
}

/** Окно согласия в стиле книги. Кнопки равнозначны (требование GDPR), закрыть мимо выбора нельзя. */
@Composable
fun ConsentDialog(context: Context) {
    val uri = LocalUriHandler.current
    Box(Modifier.fillMaxSize().background(Color.Black.copy(alpha = 0.5f)).clickable(enabled = false) {},
        contentAlignment = Alignment.Center) {
        BookPage(Modifier.widthIn(max = 480.dp)) {
            Column(Modifier.padding(horizontal = 32.dp, vertical = 18.dp),
                horizontalAlignment = Alignment.CenterHorizontally) {
                Box(Modifier.size(48.dp).clip(CircleShape).background(Palette.maroon)
                    .border(2.dp, Palette.gold, CircleShape), contentAlignment = Alignment.Center) {
                    Text("✋", fontSize = 22.sp)
                }
                Spacer(Modifier.height(8.dp))
                Text(L10n.s("ui.consent_title"), color = Palette.ink, fontSize = 22.sp,
                    fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
                Box(Modifier.padding(top = 6.dp).width(70.dp).height(3.dp)
                    .clip(RoundedCornerShape(2.dp)).background(Palette.gold))
                Spacer(Modifier.height(10.dp))
                Text(L10n.s("ui.consent_body"), color = Palette.inkSoft, fontSize = 14.sp,
                    fontFamily = Fonts.rounded, textAlign = TextAlign.Center)
                Spacer(Modifier.height(14.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(14.dp)) {
                    ConsentButton(L10n.s("ui.consent_decline")) { ConsentService.answer(context, false) }
                    ConsentButton(L10n.s("ui.consent_accept")) { ConsentService.answer(context, true) }
                }
                Spacer(Modifier.height(10.dp))
                Text(L10n.s("ui.privacy"), color = Palette.inkSoft, fontSize = 12.sp,
                    fontFamily = Fonts.rounded, textDecoration = TextDecoration.Underline,
                    modifier = Modifier.clickable { uri.openUri(Legal.PRIVACY_URL) })
            }
        }
    }
}

@Composable
private fun ConsentButton(title: String, onClick: () -> Unit) {
    Box(Modifier.width(170.dp).clip(RoundedCornerShape(28.dp)).background(Palette.maroon)
        .border(2.5.dp, Palette.ink, RoundedCornerShape(28.dp))
        .clickable(onClick = onClick).padding(vertical = 11.dp),
        contentAlignment = Alignment.Center) {
        Text(title, color = Palette.paper, fontSize = 17.sp,
            fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
    }
}
