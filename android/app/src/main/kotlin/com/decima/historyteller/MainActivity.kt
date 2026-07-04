package com.decima.historyteller

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        Billing.init(this)
        Audio.init(this)
        // Приоритет: сохранённый язык из настроек → debug-extra "lang" → авто (системная локаль).
        val savedLang = Settings(this).lang.ifEmpty { null }
        GameContent.load(assets, langOverride = savedLang ?: intent.getStringExtra("lang"))
        val startLevel = intent.getStringExtra("level")
        setContent { Root(startLevel) }
        Audio.startMusic("theme")
    }

    override fun onPause() { super.onPause(); Audio.pause() }
    override fun onResume() { super.onResume(); Audio.resume() }
}
