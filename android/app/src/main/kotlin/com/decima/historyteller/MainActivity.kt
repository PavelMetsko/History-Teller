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
        // Контент грузится в Root после ContentSync.syncCore — здесь его ещё нет.
        val startLevel = intent.getStringExtra("level")
        setContent { Root(startLevel) }
        Audio.startMusic("theme")
    }

    override fun onPause() { super.onPause(); Audio.pause() }
    override fun onResume() { super.onResume(); Audio.resume() }
}
