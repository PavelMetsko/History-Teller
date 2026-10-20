package com.decima.historyteller

import android.app.Activity
import android.content.Context
import android.os.Handler
import android.os.Looper
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import com.google.android.gms.ads.AdError
import com.google.android.gms.ads.AdRequest
import com.google.android.gms.ads.FullScreenContentCallback
import com.google.android.gms.ads.LoadAdError
import com.google.android.gms.ads.MobileAds
import com.google.android.gms.ads.rewarded.RewardedAd
import com.google.android.gms.ads.rewarded.RewardedAdLoadCallback

/**
 * Rewarded-реклама через Google AdMob (порт iOS AdService): «посмотри ролик — открой один уровень
 * платной главы». Интерстишелов нет. SDK стартует после формы согласия UMP, выключается флагом
 * `ads.rewarded` в облачном манифесте. Доход с показов уходит в Tenjin.
 */
object AdService {
    /** Rewarded-блок History Teller; в отладке — тестовый блок Google (свои показы = недействительный трафик). */
    private val REWARDED_UNIT_ID =
        if (BuildConfig.DEBUG) "ca-app-pub-3940256099942544/5224354917"
        else "ca-app-pub-6335946344432887/7885293016"

    /** Ролик загружен и его можно показать прямо сейчас. */
    var isReady by mutableStateOf(false); private set
    var isShowing by mutableStateOf(false); private set
    /** Секунд до следующего ролика (кулдаун из манифеста). 0 — можно смотреть. */
    var cooldownLeft by mutableIntStateOf(0); private set

    /** Показывать ли кнопку «за ролик» вообще (реклама не выключена в манифесте). */
    val isEnabled: Boolean get() = ContentSync.rewardedEnabled()

    private var started = false
    private var sdkStarted = false
    private var loading = false
    private var rewardedAd: RewardedAd? = null
    private var retryAttempt = 0
    private var rewarded = false
    private var completion: ((Boolean) -> Unit)? = null
    private lateinit var appContext: Context
    private val main = Handler(Looper.getMainLooper())

    /** Раз за процесс, из MainActivity. Само дожидается согласия. */
    fun start(context: Context) {
        if (started) return
        started = true
        appContext = context.applicationContext
        ConsentService.onReady { startSdk() }
        // Согласие дали позже, в форме из настроек, — теперь можно грузить.
        ConsentService.onChange { startSdk() }
    }

    /** Показать ролик. `completion(true)` — досмотрел и заслужил награду. */
    fun show(activity: Activity, completion: (Boolean) -> Unit) {
        val ad = rewardedAd
        if (!isEnabled || cooldownLeft > 0 || ad == null) return completion(false)
        rewarded = false
        this.completion = completion
        isShowing = true
        ad.show(activity) { rewarded = true }
    }

    private fun startSdk() {
        if (!ConsentService.canRequestAds.value) return
        if (sdkStarted) return load()
        sdkStarted = true
        // initialize() — до любых запросов; грузим только после его завершения.
        MobileAds.initialize(appContext) { load() }
    }

    private fun load() {
        if (!sdkStarted || loading || rewardedAd != null) return
        loading = true
        RewardedAd.load(appContext, REWARDED_UNIT_ID, AdRequest.Builder().build(),
            object : RewardedAdLoadCallback() {
                override fun onAdLoaded(ad: RewardedAd) {
                    loading = false
                    retryAttempt = 0
                    ad.fullScreenContentCallback = object : FullScreenContentCallback() {
                        override fun onAdDismissedFullScreenContent() = finishShow()
                        override fun onAdFailedToShowFullScreenContent(error: AdError) {
                            rewarded = false; finishShow()
                        }
                    }
                    ad.setOnPaidEventListener { value -> Attribution.trackAdRevenue(value, ad) }
                    rewardedAd = ad
                    isReady = true
                }

                override fun onAdFailedToLoad(error: LoadAdError) {
                    loading = false
                    isReady = false
                    // Экспоненциальная пауза до 64 с: no-fill не должен оставить игрока без роликов.
                    retryAttempt++
                    main.postDelayed({ load() }, 1000L shl minOf(retryAttempt, 6))
                }
            })
    }

    private fun finishShow() {
        isShowing = false
        isReady = false
        rewardedAd = null
        val done = completion
        completion = null
        if (rewarded) startCooldown()
        done?.invoke(rewarded)
        load()
    }

    private fun startCooldown() {
        val total = ContentSync.rewardedCooldown()
        if (total <= 0) return
        val shownAt = System.currentTimeMillis()
        cooldownLeft = total
        main.post(object : Runnable {
            override fun run() {
                cooldownLeft = maxOf(0, total - ((System.currentTimeMillis() - shownAt) / 1000).toInt())
                if (cooldownLeft > 0) main.postDelayed(this, 1000)
            }
        })
    }
}

/**
 * Уровни платных глав, открытые за ролик. Хранятся на устройстве; уровень «сгорает», когда
 * пройден, — дальше его открывает сам прогресс (пройденные переигрываются бесплатно).
 */
object RewardedUnlocks {
    private const val PREFS = "ht.ads"
    private const val KEY = "rewardedLevels"

    fun contains(ctx: Context, levelId: String) = levelId in ids(ctx)
    fun add(ctx: Context, levelId: String) = save(ctx, ids(ctx) + levelId)
    fun consume(ctx: Context, levelId: String) = save(ctx, ids(ctx) - levelId)

    private fun ids(ctx: Context): Set<String> =
        ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getStringSet(KEY, emptySet()) ?: emptySet()

    private fun save(ctx: Context, ids: Set<String>) =
        ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().putStringSet(KEY, ids).apply()
}
