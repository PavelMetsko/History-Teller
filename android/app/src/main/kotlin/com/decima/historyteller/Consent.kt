package com.decima.historyteller

import android.app.Activity
import android.content.Context
import android.content.pm.ApplicationInfo
import com.google.android.ump.ConsentDebugSettings
import com.google.android.ump.ConsentInformation
import com.google.android.ump.ConsentRequestParameters
import com.google.android.ump.UserMessagingPlatform
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * Согласие на данные через Google UMP (сертифицированный CMP — без него AdMob в ЕЭЗ рекламу не
 * показывает), как в Decima. Порт iOS ConsentService. Запускается раз за сессию — после
 * онбординга. Форма и языки — в AdMob → Privacy & messaging («History Teller GDPR consent»).
 * Реклама и Tenjin ждут [onReady]. ATT на Android нет — рекламный ID регулирует система.
 */
object ConsentService {

    private val _canRequestAds = MutableStateFlow(false)
    val canRequestAds: StateFlow<Boolean> = _canRequestAds.asStateFlow()

    /** Строка «Конфиденциальность» в настройках — только там, где форма обязательна (ЕЭЗ/UK/CH). */
    private val _privacyOptionsRequired = MutableStateFlow(false)
    val privacyOptionsRequired: StateFlow<Boolean> = _privacyOptionsRequired.asStateFlow()

    /** Форма в этом регионе не нужна (вне ЕЭЗ) — Tenjin тогда не ждёт TCF-строку. */
    var isConsentNotRequired = false; private set

    private var started = false
    private var settled = false
    private val readyHandlers = mutableListOf<() -> Unit>()
    private val changeHandlers = mutableListOf<() -> Unit>()

    /** Вызвать, когда согласие отработало (сразу, если уже). */
    fun onReady(handler: () -> Unit) {
        if (settled) handler() else readyHandlers += handler
    }

    /** Игрок поменял выбор в форме из настроек — SDK обновляют свои флаги. */
    fun onChange(handler: () -> Unit) { changeHandlers += handler }

    /** Раз за сессию, после онбординга. */
    fun start(activity: Activity) {
        if (started) return
        started = true
        val info = UserMessagingPlatform.getConsentInformation(activity)
        val params = ConsentRequestParameters.Builder()
            .apply { debugSettings(activity)?.let { setConsentDebugSettings(it) } }
            .build()
        info.requestConsentInfoUpdate(activity, params,
            { UserMessagingPlatform.loadAndShowConsentFormIfRequired(activity) { finish(activity) } },
            { finish(activity) })   // не обновилось (офлайн) — работаем на сохранённом согласии
    }

    /** Строка «Конфиденциальность» в настройках: форма Google с выбором заново. */
    fun presentPrivacyOptionsForm(activity: Activity) {
        UserMessagingPlatform.showPrivacyOptionsForm(activity) {
            refresh(activity)
            changeHandlers.forEach { it() }
        }
    }

    private fun finish(context: Context) {
        refresh(context)
        if (settled) return
        settled = true
        val handlers = readyHandlers.toList()
        readyHandlers.clear()
        handlers.forEach { it() }
    }

    private fun refresh(context: Context) {
        val info = UserMessagingPlatform.getConsentInformation(context)
        _canRequestAds.value = info.canRequestAds()
        _privacyOptionsRequired.value = info.privacyOptionsRequirementStatus ==
            ConsentInformation.PrivacyOptionsRequirementStatus.REQUIRED
        isConsentNotRequired = info.consentStatus == ConsentInformation.ConsentStatus.NOT_REQUIRED
    }

    /** В отладочной сборке форма показывается как в ЕЭЗ — иначе вне Европы её не проверить. */
    private fun debugSettings(context: Context): ConsentDebugSettings? {
        val debuggable = (context.applicationInfo.flags and ApplicationInfo.FLAG_DEBUGGABLE) != 0
        if (!debuggable) return null
        return ConsentDebugSettings.Builder(context)
            .setDebugGeography(ConsentDebugSettings.DebugGeography.DEBUG_GEOGRAPHY_EEA)
            .build()
    }
}
