package com.decima.historyteller

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        // Отладочные сборки умеют ходить на локальный стенд вместо облака (см. build.gradle.kts).
        if (BuildConfig.CONTENT_URL.isNotEmpty()) ContentSync.baseUrl = BuildConfig.CONTENT_URL
        Billing.init(this)
        Audio.init(this)
        // Контент грузится в Root после ContentSync.syncCore — здесь его ещё нет.
        val startLevel = intent.getStringExtra("level")
        setContent { Root(startLevel) }
        Audio.startMusic("theme")
    }

    override fun onPause() { super.onPause(); Audio.pause() }
    override fun onResume() { super.onResume(); Audio.resume() }
}
