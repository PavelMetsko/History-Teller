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
            val file = ContentSync.fileFor("audio/$name.m4a")
            if (file != null) { ids[name] = sp.load(file.absolutePath, 1); continue }
            val resId = ctx.resources.getIdentifier(name, "raw", ctx.packageName)
            if (resId != 0) ids[name] = sp.load(ctx, resId, 1)
        }
    }

    /**
     * Перечитать SFX. Зовётся после синхронизации контента: пул набивается один раз на старте,
     * и без перезагрузки звук, приехавший из облака, молчал бы до перезапуска.
     */
    fun reloadSfx(ctx: Context) {
        pool?.release()
        pool = null
        ids.clear()
        init(ctx)
        if (currentMusic != null) { val m = desired; stopMusic(); startMusic(m) }
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
        val mp = openMusic(ctx, name) ?: return
        mp.isLooping = true
        mp.setVolume(0.3f, 0.3f)
        mp.start()
        music = mp
        currentMusic = name
    }

    /** Скачанный трек перекрывает вшитый — звук тоже приезжает из облака. */
    private fun openMusic(ctx: Context, name: String): MediaPlayer? {
        ContentSync.fileFor("audio/$name.m4a")?.let { file ->
            return runCatching {
                MediaPlayer().apply { setDataSource(file.absolutePath); prepare() }
            }.getOrNull()
        }
        val resId = ctx.resources.getIdentifier(name, "raw", ctx.packageName)
        return if (resId != 0) MediaPlayer.create(ctx, resId) else null
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
