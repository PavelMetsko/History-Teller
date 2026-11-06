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
import com.google.android.gms.ads.interstitial.InterstitialAd
import com.google.android.gms.ads.interstitial.InterstitialAdLoadCallback
import com.google.android.gms.ads.rewarded.RewardedAd
import com.google.android.gms.ads.rewarded.RewardedAdLoadCallback

/**
 * Реклама через Google AdMob (порт iOS AdService). Два формата:
 * - **ролик** (rewarded) — подсказка, когда свои кончились, и возврат прерванной серии;
 *   выключается флагом `ads.rewarded` в облачном манифесте;
 * - **интерстишел** — при уходе с экрана награды, по правилам `docs/f2p-patch-4.0.md` §1
 *   (`ads.interstitial`, `interAfter`, `interEvery`, `interGapSec`). В купленной главе его нет.
 * SDK стартует после формы согласия UMP. Доход с показов уходит в Tenjin.
 */
object AdService {
    /** Rewarded-блок History Teller; в отладке — тестовый блок Google (свои показы = недействительный трафик). */
    private val REWARDED_UNIT_ID =
        if (BuildConfig.DEBUG) "ca-app-pub-3940256099942544/5224354917"
        else "ca-app-pub-6335946344432887/7885293016"

    /** Интерстишел History Teller; в отладке — тестовый блок Google. */
    private val INTERSTITIAL_UNIT_ID =
        if (BuildConfig.DEBUG) "ca-app-pub-3940256099942544/1033173712"
        else "ca-app-pub-6335946344432887/5661084774"

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
    private var interAd: InterstitialAd? = null
    private var interLoading = false
    private var interRetry = 0
    private var interDone: (() -> Unit)? = null
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
        Meta.noteFullscreenShown()
        ad.show(activity) { rewarded = true }
    }

    /**
     * Интерстишел при уходе с экрана награды. [solvedTotal] — эпизодов решено за всю жизнь.
     * Любое «нельзя» (Premium, выключен, рано, не загружен) — `then` сразу, без ожидания.
     */
    fun showInterstitialIfDue(activity: Activity?, solvedTotal: Int, level: String?, chapter: String?, then: () -> Unit) {
        val ad = interAd
        val gapOk = System.currentTimeMillis() / 1000.0 - Meta.lastFullscreen >= ContentSync.interGapSec()
        val due = !Premium.adsFree(chapter) && ContentSync.interstitialEnabled() &&
            solvedTotal >= ContentSync.interAfter() &&
            Meta.sinceInterstitial >= ContentSync.interEvery() && gapOk
        if (!due || ad == null || activity == null || isShowing) return then()
        interDone = then
        isShowing = true
        Meta.noteInterstitialShown()
        Telemetry.track("inter_show", level, chapter)
        ad.show(activity)
    }

    private fun startSdk() {
        if (!ConsentService.canRequestAds.value) return
        if (sdkStarted) return load()
        sdkStarted = true
        // initialize() — до любых запросов; грузим только после его завершения.
        MobileAds.initialize(appContext) { load() }
    }

    private fun load() {
        loadInterstitial()
        loadRewarded()
    }

    private fun loadInterstitial() {
        if (!sdkStarted || interLoading || interAd != null) return
        interLoading = true
        InterstitialAd.load(appContext, INTERSTITIAL_UNIT_ID, AdRequest.Builder().build(),
            object : InterstitialAdLoadCallback() {
                override fun onAdLoaded(ad: InterstitialAd) {
                    interLoading = false
                    interRetry = 0
                    ad.fullScreenContentCallback = object : FullScreenContentCallback() {
                        override fun onAdDismissedFullScreenContent() = finishInterstitial()
                        override fun onAdFailedToShowFullScreenContent(error: AdError) = finishInterstitial()
                    }
                    ad.setOnPaidEventListener { value -> Attribution.trackAdRevenue(value, ad.adUnitId, ad.responseInfo) }
                    interAd = ad
                }

                override fun onAdFailedToLoad(error: LoadAdError) {
                    interLoading = false
                    // Та же пауза, что у роликов, но длиннее потолок: интерстишел не срочен.
                    interRetry++
                    main.postDelayed({ loadInterstitial() }, 1000L shl minOf(interRetry, 7))
                }
            })
    }

    private fun finishInterstitial() {
        isShowing = false
        interAd = null
        val done = interDone
        interDone = null
        done?.invoke()
        loadInterstitial()
    }

    private fun loadRewarded() {
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
                    ad.setOnPaidEventListener { value -> Attribution.trackAdRevenue(value, ad.adUnitId, ad.responseInfo) }
                    rewardedAd = ad
                    isReady = true
                }

                override fun onAdFailedToLoad(error: LoadAdError) {
                    loading = false
                    isReady = false
                    // Экспоненциальная пауза до 64 с: no-fill не должен оставить игрока без роликов.
                    retryAttempt++
                    main.postDelayed({ loadRewarded() }, 1000L shl minOf(retryAttempt, 6))
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
        loadRewarded()
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
