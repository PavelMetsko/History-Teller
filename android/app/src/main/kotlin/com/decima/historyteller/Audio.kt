package com.decima.historyteller

import android.content.Context
import android.media.AudioAttributes
import android.media.AudioFormat
import android.media.AudioTrack
import android.media.MediaCodec
import android.media.MediaExtractor
import android.media.MediaFormat
import android.media.SoundPool
import android.util.Log
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import java.io.File
import java.nio.ByteOrder
import kotlin.concurrent.thread
import kotlin.random.Random

/**
 * Звук: SFX через SoundPool (наложение, низкая задержка) + фоновая музыка своим микшером.
 *
 * Музыку раньше крутил MediaPlayer с `isLooping = true`. У AAC в начале файла лежит priming-пакет,
 * который MediaPlayer не срезает, — на каждом витке лупа был слышен щелчок (у нас луп ~75 с).
 * Теперь трек декодируется в PCM один раз, обрезается по метаданным `audio/loops.json`
 * (skip = priming, frames = истинная длина) и играется через AudioTrack: стык сэмпл-в-сэмпл.
 *
 * Побочно это дало кроссфейд между треками (два дека в одном микшере) и приседание музыки
 * под сюжетные удары. Порт iOS Audio (AVAudioEngine).
 */
object Audio {
    private val SFX = listOf("place", "select", "accent", "win", "error")

    /** Громкие удары: под них музыка приседает, чтобы не спорить с ними. */
    private val DUCKING = setOf("win", "accent")

    private var pool: SoundPool? = null
    private val ids = HashMap<String, Int>()
    private var appCtx: Context? = null
    private var settings: Settings? = null

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
        Music.reload()
    }

    fun sfx(name: String) {
        if (settings?.sfx != true) return
        val sp = pool ?: return
        val id = ids[name] ?: return
        // Микро-разброс высоты: один и тот же сэмпл на каждый тап слышится как долбёжка.
        sp.play(id, 1f, 1f, 1, 0, 0.97f + Random.nextFloat() * 0.06f)
        if (name in DUCKING) Music.duck()
    }

    /** Запустить фоновую тему (по имени из level.music или "theme"). Та же тема не перезапускается. */
    fun startMusic(name: String = "theme") = Music.start(name, settings?.music == true)

    fun stopMusic() = Music.stop()

    /** Реакция на переключатель музыки в настройках. */
    fun onMusicToggle(on: Boolean) = if (on) Music.start(Music.desired, true) else Music.stop()

    fun pause() = Music.pause()

    fun resume() = Music.resume(settings?.music == true)

    // ───────────────────────────────────────────────────────── микшер музыки

    /**
     * Два дека в одном потоке-питателе: активный подтягивается к 1, остальные к 0 —
     * отсюда кроссфейд. Он же применяет ducking, поэтому громкость меняется без щелчков.
     */
    private object Music {
        // ───────────────────────────────────────────────────────── PCM-кеш

        // Потокобезопасные: декод идёт в фоне, а читают их и главный поток, и питатель.
        private val decoded = java.util.concurrent.ConcurrentHashMap<String, ShortArray>()
        @Volatile private var loopMeta: Map<String, Pair<Int, Int>>? = null   // name -> (skip, frames)

        /** Метаданные склейки лупа кладёт `tools/build_audio.py`; 1024 — priming нашего кодера. */
        private fun meta(name: String): Pair<Int, Int>? {
            if (loopMeta == null) {
                loopMeta = runCatching {
                    val txt = ContentSync.text("audio/loops.json") ?: return@runCatching emptyMap()
                    Json.parseToJsonElement(txt).jsonObject.mapValues { (_, v) ->
                        val o = v.jsonObject
                        (o["skip"]?.jsonPrimitive?.content?.toInt() ?: 1024) to
                            (o["frames"]?.jsonPrimitive?.content?.toInt() ?: 0)
                    }
                }.getOrDefault(emptyMap())
            }
            return loopMeta?.get(name)
        }

        /** Полный декод трека в PCM 16-bit stereo. Луп ~75 с ≈ 13 МБ — держим не больше двух. */
        private fun pcm(name: String): ShortArray? {
            decoded[name]?.let { return it }
            val src = ContentSync.fileFor("audio/$name.m4a") ?: return rawPcm(name)
            val raw = runCatching { decodeFile(src) }.getOrElse {
                Log.w("Audio", "decode $name failed: $it"); return null
            } ?: return null
            val trimmed = trim(raw, name)
            if (decoded.size > 2) decoded.clear()
            decoded[name] = trimmed
            return trimmed
        }

        private fun rawPcm(name: String): ShortArray? {
            val ctx = appCtx ?: return null
            val resId = ctx.resources.getIdentifier(name, "raw", ctx.packageName)
            if (resId == 0) return null
            return runCatching {
                ctx.resources.openRawResourceFd(resId).use { fd ->
                    val ex = MediaExtractor()
                    ex.setDataSource(fd.fileDescriptor, fd.startOffset, fd.length)
                    decode(ex)
                }
            }.getOrNull()?.let { trim(it, name) }
        }

        private fun trim(raw: ShortArray, name: String): ShortArray {
            val (skip, frames) = meta(name) ?: (1024 to 0)
            val from = (skip * 2).coerceAtMost(raw.size)
            val to = if (frames > 0) (from + frames * 2).coerceAtMost(raw.size) else raw.size
            return if (from == 0 && to == raw.size) raw else raw.copyOfRange(from, to)
        }

        private fun decodeFile(f: File): ShortArray? {
            val ex = MediaExtractor()
            ex.setDataSource(f.absolutePath)
            return decode(ex)
        }

        /** MediaCodec-декод целиком в память. Синхронный режим — проще и предсказуемее асинхронного. */
        private fun decode(ex: MediaExtractor): ShortArray? {
            var trackIndex = -1
            var format: MediaFormat? = null
            for (i in 0 until ex.trackCount) {
                val fmt = ex.getTrackFormat(i)
                if (fmt.getString(MediaFormat.KEY_MIME)?.startsWith("audio/") == true) {
                    trackIndex = i; format = fmt; break
                }
            }
            val fmt = format ?: return null
            ex.selectTrack(trackIndex)
            val codec = MediaCodec.createDecoderByType(fmt.getString(MediaFormat.KEY_MIME)!!)
            codec.configure(fmt, null, null, 0)
            codec.start()

            val out = ArrayList<ShortArray>()
            val info = MediaCodec.BufferInfo()
            var inputDone = false
            var total = 0
            try {
                while (true) {
                    if (!inputDone) {
                        val ii = codec.dequeueInputBuffer(10_000)
                        if (ii >= 0) {
                            val buf = codec.getInputBuffer(ii)!!
                            val n = ex.readSampleData(buf, 0)
                            if (n < 0) {
                                codec.queueInputBuffer(ii, 0, 0, 0, MediaCodec.BUFFER_FLAG_END_OF_STREAM)
                                inputDone = true
                            } else {
                                codec.queueInputBuffer(ii, 0, n, ex.sampleTime, 0)
                                ex.advance()
                            }
                        }
                    }
                    val oi = codec.dequeueOutputBuffer(info, 10_000)
                    if (oi >= 0) {
                        if (info.size > 0) {
                            val bb = codec.getOutputBuffer(oi)!!.order(ByteOrder.nativeOrder())
                            val chunk = ShortArray(info.size / 2)
                            bb.position(info.offset)
                            bb.asShortBuffer().get(chunk)
                            out.add(chunk); total += chunk.size
                        }
                        codec.releaseOutputBuffer(oi, false)
                        if (info.flags and MediaCodec.BUFFER_FLAG_END_OF_STREAM != 0) break
                    }
                }
            } finally {
                runCatching { codec.stop() }; codec.release(); ex.release()
            }

            val pcm = ShortArray(total)
            var p = 0
            for (c in out) { c.copyInto(pcm, p); p += c.size }
            return pcm
        }

        private const val SR = 44100
        private const val FRAMES = 1024          // блок микширования (~23 мс)
        private const val CROSSFADE_S = 1.1f
        private const val BASE = 0.5f            // треки нормализованы в −20 LUFS

        var desired: String = "theme"; private set

        private class Deck(val name: String, val pcm: ShortArray) {
            var pos = 0
            var gain = 0f
        }

        private var a: Deck? = null              // активный
        private var b: Deck? = null              // уходящий
        private var track: AudioTrack? = null
        private var worker: Thread? = null
        @Volatile private var running = false
        @Volatile private var paused = false
        @Volatile private var duckUntil = 0L

        fun start(name: String, enabled: Boolean) {
            synchronized(this) {
                desired = name
                if (!enabled) return
                if (a?.name == name && running) { paused = false; return }
            }
            // Декод целого трека — сотни миллисекунд (75 с звука ≈ 13 МБ PCM). Раньше он шёл
            // прямо здесь, а зовут start() с главного потока при входе в уровень — отсюда и был
            // фриз доски на пару секунд. Готовим в фоне и подменяем деки, когда PCM готов.
            thread(name = "ht-music-decode", isDaemon = true) {
                val samples = pcm(name) ?: return@thread
                synchronized(this) {
                    if (desired != name) return@synchronized   // пока декодировали, попросили другой
                    b = a?.takeIf { it.gain > 0f }
                    a = Deck(name, samples)
                    paused = false
                    ensureThread()
                }
            }
        }

        @Synchronized fun stop() {
            running = false
            worker?.join(300)
            worker = null
            runCatching { track?.pause(); track?.flush(); track?.release() }
            track = null
            a = null; b = null
        }

        /** После синка контента PCM-кеш и метаданные лупа устарели — перечитать и продолжить. */
        @Synchronized fun reload() {
            val wasPlaying = a != null
            stop()
            decoded.clear()
            loopMeta = null
            if (wasPlaying) start(desired, true)
        }

        fun pause() { paused = true }

        fun resume(enabled: Boolean) {
            if (!enabled) return
            if (a == null) start(desired, true) else paused = false
        }

        fun duck() { duckUntil = System.currentTimeMillis() + 1100 }

        private fun ensureThread() {
            if (running) return
            running = true
            worker = thread(name = "ht-music", isDaemon = true) { loop() }
        }

        private fun loop() {
            val min = AudioTrack.getMinBufferSize(
                SR, AudioFormat.CHANNEL_OUT_STEREO, AudioFormat.ENCODING_PCM_16BIT)
            val t = AudioTrack.Builder()
                .setAudioAttributes(AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_MEDIA)
                    .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC).build())
                .setAudioFormat(AudioFormat.Builder()
                    .setSampleRate(SR)
                    .setEncoding(AudioFormat.ENCODING_PCM_16BIT)
                    .setChannelMask(AudioFormat.CHANNEL_OUT_STEREO).build())
                .setBufferSizeInBytes(maxOf(min, FRAMES * 2 * 2 * 4))
                .setTransferMode(AudioTrack.MODE_STREAM)
                .build()
            track = t
            t.play()

            val mix = ShortArray(FRAMES * 2)
            val step = (FRAMES.toFloat() / SR) / CROSSFADE_S
            while (running) {
                if (paused) { Thread.sleep(60); continue }
                val duck = if (System.currentTimeMillis() < duckUntil) 0.56f else 1f
                java.util.Arrays.fill(mix, 0)
                val cur = a
                val old = b
                for (d in listOfNotNull(cur, old)) {
                    val target = if (d === cur) 1f else 0f
                    d.gain += if (target > d.gain) step else -step
                    d.gain = d.gain.coerceIn(0f, 1f)
                    val g = d.gain * BASE * duck
                    var p = d.pos
                    for (i in mix.indices) {
                        if (p >= d.pcm.size) p = 0              // бесшовный виток
                        mix[i] = (mix[i] + d.pcm[p] * g).toInt()
                            .coerceIn(Short.MIN_VALUE.toInt(), Short.MAX_VALUE.toInt()).toShort()
                        p++
                    }
                    d.pos = p
                }
                if (old != null && old.gain <= 0f) b = null
                if (cur == null && old == null) { Thread.sleep(40); continue }
                t.write(mix, 0, mix.size)
            }
            runCatching { t.pause(); t.flush(); t.release() }
            if (track === t) track = null
        }
    }
}
