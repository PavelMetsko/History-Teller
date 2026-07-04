package com.decima.historyteller

import android.content.Context
import android.media.AudioAttributes
import android.media.MediaPlayer
import android.media.SoundPool

/**
 * Звук: SFX через SoundPool (наложение, низкая задержка) + фоновая музыка через MediaPlayer (луп).
 * Файлы — wav в `res/raw`. Учитывает переключатели [Settings]. Порт iOS Audio (AVFoundation).
 */
object Audio {
    private val SFX = listOf(
        "place", "remove", "select", "ally", "conspire", "love", "kill", "crown", "envy", "win", "error")

    private var pool: SoundPool? = null
    private val ids = HashMap<String, Int>()
    private var appCtx: Context? = null
    private var settings: Settings? = null

    private var music: MediaPlayer? = null
    private var currentMusic: String? = null
    private var desired: String = "theme"

    fun init(ctx: Context) {
        if (pool != null) return
        appCtx = ctx.applicationContext
        settings = Settings(ctx)
        val attrs = AudioAttributes.Builder()
            .setUsage(AudioAttributes.USAGE_GAME)
            .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION).build()
        val sp = SoundPool.Builder().setMaxStreams(6).setAudioAttributes(attrs).build()
        pool = sp
        for (name in SFX) {
            val resId = ctx.resources.getIdentifier(name, "raw", ctx.packageName)
            if (resId != 0) ids[name] = sp.load(ctx, resId, 1)
        }
    }

    fun sfx(name: String) {
        if (settings?.sfx != true) return
        val sp = pool ?: return
        val id = ids[name] ?: return
        sp.play(id, 1f, 1f, 1, 0, 1f)
    }

    /** Запустить фоновую тему (по имени из level.music или "theme"). Та же тема не перезапускается. */
    fun startMusic(name: String = "theme") {
        desired = name
        if (settings?.music != true) return
        if (currentMusic == name && music?.isPlaying == true) return
        stopMusic()
        val ctx = appCtx ?: return
        val resId = ctx.resources.getIdentifier(name, "raw", ctx.packageName)
        if (resId == 0) return
        val mp = MediaPlayer.create(ctx, resId) ?: return
        mp.isLooping = true
        mp.setVolume(0.3f, 0.3f)
        mp.start()
        music = mp
        currentMusic = name
    }

    fun stopMusic() {
        music?.let { runCatching { it.stop() }; it.release() }
        music = null; currentMusic = null
    }

    /** Реакция на переключатель музыки в настройках. */
    fun onMusicToggle(on: Boolean) { if (on) startMusic(desired) else stopMusic() }

    fun pause() { music?.let { runCatching { if (it.isPlaying) it.pause() } } }
    fun resume() {
        if (settings?.music == true) music?.let { runCatching { it.start() } } ?: startMusic(desired)
    }
}
