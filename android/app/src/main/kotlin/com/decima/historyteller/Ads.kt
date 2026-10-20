package com.decima.historyteller

import android.app.Activity
import android.content.Context
import android.os.Handler
import android.os.Looper
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import com.applovin.mediation.MaxAd
import com.applovin.mediation.MaxError
import com.applovin.mediation.MaxReward
import com.applovin.mediation.MaxRewardedAdListener
import com.applovin.mediation.ads.MaxRewardedAd
import com.applovin.sdk.AppLovinMediationProvider
import com.applovin.sdk.AppLovinPrivacySettings
import com.applovin.sdk.AppLovinSdk
import com.applovin.sdk.AppLovinSdkInitializationConfiguration
import kotlin.math.min
import kotlin.math.pow

/**
 * Rewarded-реклама через AppLovin MAX (порт iOS AdService): «посмотри ролик — открой один уровень
 * платной главы». Интерстишелов нет. SDK стартует после окна согласия (флаги согласия — до
 * старта), выключается флагом `ads.rewarded` в облачном манифесте. Доход с показов — в Tenjin.
 */
object AdService : MaxRewardedAdListener {
    // TODO: ключи из кабинета AppLovin MAX (Account → Keys, MAX → Ad Units). Пока пусто — рекламы нет.
    private const val SDK_KEY = ""
    private const val REWARDED_UNIT_ID = ""

    /** Ролик загружен и его можно показать прямо сейчас. */
    var isReady by mutableStateOf(false); private set
    var isShowing by mutableStateOf(false); private set
    /** Секунд до следующего ролика (кулдаун из манифеста). 0 — можно смотреть. */
    var cooldownLeft by mutableIntStateOf(0); private set

    /** Показывать ли кнопку «за ролик» вообще: ключи заданы и реклама не выключена в манифесте. */
    val isEnabled: Boolean get() = SDK_KEY.isNotEmpty() && ContentSync.rewardedEnabled()

    private var started = false
    private var rewardedAd: MaxRewardedAd? = null
    private var retryAttempt = 0.0
    private var rewarded = false
    private var completion: ((Boolean) -> Unit)? = null
    private lateinit var appContext: Context
    private val main = Handler(Looper.getMainLooper())

    /** Раз за процесс, из MainActivity. Само дожидается согласия. */
    fun start(context: Context) {
        if (started) return
        started = true
        appContext = context.applicationContext
        ConsentService.onReady { initializeSdk() }
        ConsentService.onChange { applyConsent() }
    }

    /** Флаг согласия — только когда игрок отвечал (GDPR-регион): вне ЕЭЗ «нет ответа» ≠ отказ. */
    private fun applyConsent() {
        if (ConsentService.choice.value != null)
            AppLovinPrivacySettings.setHasUserConsent(ConsentService.hasUserConsent)
        AppLovinPrivacySettings.setDoNotSell(ConsentService.doNotSell)
    }

    /** Показать ролик. `completion(true)` — досмотрел и заслужил награду. */
    fun show(activity: Activity, completion: (Boolean) -> Unit) {
        val ad = rewardedAd
        if (!isEnabled || cooldownLeft > 0 || ad == null || !ad.isReady) return completion(false)
        rewarded = false
        this.completion = completion
        isShowing = true
        ad.showAd(activity)
    }

    private fun initializeSdk() {
        if (SDK_KEY.isEmpty()) return
        applyConsent()
        val config = AppLovinSdkInitializationConfiguration.builder(SDK_KEY)
            .setMediationProvider(AppLovinMediationProvider.MAX)
            .build()
        AppLovinSdk.getInstance(appContext).initialize(config) {
            if (REWARDED_UNIT_ID.isEmpty()) return@initialize
            rewardedAd = MaxRewardedAd.getInstance(REWARDED_UNIT_ID).also {
                it.setListener(this)
                it.setRevenueListener { ad -> Attribution.trackAdRevenue(ad) }
                it.loadAd()
            }
        }
    }

    private fun finishShow() {
        isShowing = false
        isReady = false
        val done = completion
        completion = null
        if (rewarded) startCooldown()
        done?.invoke(rewarded)
        rewardedAd?.loadAd()
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

    override fun onAdLoaded(ad: MaxAd) { retryAttempt = 0.0; isReady = true }

    override fun onAdLoadFailed(adUnitId: String, error: MaxError) {
        isReady = false
        // Экспоненциальная пауза до 64 с — как советует AppLovin.
        retryAttempt += 1
        val delayMs = (2.0.pow(min(6.0, retryAttempt)) * 1000).toLong()
        main.postDelayed({ rewardedAd?.loadAd() }, delayMs)
    }

    override fun onAdDisplayed(ad: MaxAd) {}
    override fun onAdClicked(ad: MaxAd) {}
    override fun onAdHidden(ad: MaxAd) = finishShow()
    override fun onAdDisplayFailed(ad: MaxAd, error: MaxError) { rewarded = false; finishShow() }
    override fun onUserRewarded(ad: MaxAd, reward: MaxReward) { rewarded = true }
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
