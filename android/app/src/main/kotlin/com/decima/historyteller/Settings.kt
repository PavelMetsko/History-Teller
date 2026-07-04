package com.decima.historyteller

import android.content.Context
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.KeyboardArrowDown
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.Icon
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

/** Настройки (SharedPreferences `ht.settings`): язык + музыка/звук/вибрация. Порт iOS AppStorage. */
class Settings(ctx: Context) {
    private val p = ctx.getSharedPreferences("ht.settings", Context.MODE_PRIVATE)
    var lang: String
        get() = p.getString("lang", "") ?: ""
        set(v) = p.edit().putString("lang", v).apply()
    var music: Boolean
        get() = p.getBoolean("music", true)
        set(v) = p.edit().putBoolean("music", v).apply()
    var sfx: Boolean
        get() = p.getBoolean("sfx", true)
        set(v) = p.edit().putBoolean("sfx", v).apply()
    var haptics: Boolean
        get() = p.getBoolean("haptics", true)
        set(v) = p.edit().putBoolean("haptics", v).apply()
    // Кэш права на «все главы» (источник истины — Google Play; кэш для оффлайна/старта).
    var unlocked: Boolean
        get() = p.getBoolean("unlocked", false)
        set(v) = p.edit().putBoolean("unlocked", v).apply()
}

/** Лёгкая вибрация (учитывает настройку). Аудио — Фаза 5. */
object Haptics {
    fun light(ctx: Context, enabled: Boolean) {
        if (!enabled) return
        val vib = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            (ctx.getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as? VibratorManager)?.defaultVibrator
        } else {
            @Suppress("DEPRECATION") ctx.getSystemService(Context.VIBRATOR_SERVICE) as? Vibrator
        } ?: return
        vib.vibrate(VibrationEffect.createOneShot(12, VibrationEffect.DEFAULT_AMPLITUDE))
    }
}

private val langNames = linkedMapOf(
    "ru" to "Русский", "en" to "English", "es" to "Español", "de" to "Deutsch",
    "fr" to "Français", "it" to "Italiano", "pt" to "Português", "pl" to "Polski", "nl" to "Nederlands"
)

/** Экран настроек — затемнение + книжная карточка (порт SettingsView). onLangChange перезагружает контент. */
@Composable
fun SettingsScreen(settings: Settings, onLangChange: (String) -> Unit, onClose: () -> Unit) {
    val ctx = LocalContext.current
    var music by remember { mutableStateOf(settings.music) }
    var sfx by remember { mutableStateOf(settings.sfx) }
    var haptics by remember { mutableStateOf(settings.haptics) }
    var lang by remember { mutableStateOf(settings.lang) }

    Box(Modifier.fillMaxSize().background(Color.Black.copy(alpha = 0.45f)).clickable { onClose() },
        contentAlignment = Alignment.Center) {
        // Карточка — перехватывает тапы (не закрывается при клике внутрь).
        BookPage(Modifier.widthIn(max = 460.dp).clickable(enabled = false) {}) {
            Column(Modifier.padding(horizontal = 32.dp, vertical = 18.dp),
                horizontalAlignment = Alignment.CenterHorizontally) {
                Text(L10n.s("ui.settings"), color = Palette.ink, fontSize = 24.sp,
                    fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
                Box(Modifier.padding(top = 6.dp).width(90.dp).height(3.dp)
                    .clip(RoundedCornerShape(2.dp)).background(Palette.gold))
                Spacer(Modifier.height(8.dp))

                ToggleRow(L10n.s("ui.music"), music) { music = it; settings.music = it; Audio.onMusicToggle(it) }
                Divider()
                ToggleRow(L10n.s("ui.sound"), sfx) { sfx = it; settings.sfx = it; if (it) Audio.sfx("select") }
                Divider()
                ToggleRow(L10n.s("ui.haptics"), haptics) {
                    haptics = it; settings.haptics = it; if (it) Haptics.light(ctx, true)
                }
                Divider()
                LanguageRow(lang) { code ->
                    lang = code; settings.lang = code; onLangChange(code)
                }

                Spacer(Modifier.height(14.dp))
                Row(Modifier.clip(RoundedCornerShape(28.dp)).background(Palette.maroon)
                    .clickable { onClose() }.padding(horizontal = 44.dp, vertical = 11.dp)) {
                    Text(L10n.s("ui.done"), color = Palette.paper, fontSize = 18.sp,
                        fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
                }
            }
        }
    }
}

@Composable
private fun ToggleRow(title: String, checked: Boolean, onChange: (Boolean) -> Unit) {
    Row(Modifier.fillMaxWidth().padding(horizontal = 8.dp, vertical = 6.dp),
        verticalAlignment = Alignment.CenterVertically) {
        Text(title, color = Palette.ink, fontSize = 17.sp, fontFamily = Fonts.rounded)
        Spacer(Modifier.weight(1f))
        Switch(checked = checked, onCheckedChange = onChange,
            colors = SwitchDefaults.colors(
                checkedThumbColor = Palette.paper, checkedTrackColor = Palette.success,
                uncheckedThumbColor = Palette.paper, uncheckedTrackColor = Palette.ink.copy(alpha = 0.3f)))
    }
}

@Composable
private fun LanguageRow(lang: String, onPick: (String) -> Unit) {
    var open by remember { mutableStateOf(false) }
    Row(Modifier.fillMaxWidth().padding(horizontal = 8.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically) {
        Text(L10n.s("ui.language"), color = Palette.ink, fontSize = 17.sp, fontFamily = Fonts.rounded)
        Spacer(Modifier.weight(1f))
        Box {
            Row(Modifier.clip(RoundedCornerShape(8.dp)).clickable { open = true }
                .padding(horizontal = 6.dp, vertical = 4.dp), verticalAlignment = Alignment.CenterVertically) {
                Text(if (lang.isEmpty()) "Auto" else (langNames[lang] ?: lang),
                    color = Palette.maroon, fontSize = 16.sp, fontFamily = Fonts.rounded, fontWeight = FontWeight.Bold)
                Icon(Icons.Filled.KeyboardArrowDown, null, tint = Palette.maroon, modifier = Modifier.size(20.dp))
            }
            DropdownMenu(expanded = open, onDismissRequest = { open = false },
                modifier = Modifier.background(Palette.paper)) {
                LangItem("Auto", lang.isEmpty()) { onPick(""); open = false }
                for ((code, name) in langNames)
                    LangItem(name, lang == code) { onPick(code); open = false }
            }
        }
    }
}

@Composable
private fun LangItem(label: String, selected: Boolean, onClick: () -> Unit) {
    DropdownMenuItem(
        text = { Text(label, color = Palette.ink, fontSize = 15.sp, fontFamily = Fonts.rounded,
            fontWeight = if (selected) FontWeight.Bold else FontWeight.Normal) },
        onClick = onClick,
        trailingIcon = { if (selected) Icon(Icons.Filled.Check, null, tint = Palette.success, modifier = Modifier.size(18.dp)) }
    )
}

@Composable
private fun Divider() {
    Box(Modifier.fillMaxWidth().height(1.dp).background(Palette.ink.copy(alpha = 0.12f)))
}
