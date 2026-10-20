package com.decima.historyteller

import android.content.Context
import com.android.billingclient.api.BillingClient
import com.android.billingclient.api.ProductDetails
import com.android.billingclient.api.Purchase
import com.google.android.gms.ads.AdValue
import com.google.android.gms.ads.rewarded.RewardedAd
import com.tenjin.android.TenjinSDK
import org.json.JSONObject

/**
 * Атрибуция установок и покупок через Tenjin (MMP для закупки в AppLovin). Порт iOS
 * AttributionService. Стартует только после формы согласия; в ЕЭЗ решение берётся из согласия
 * UMP (TCF, цель 1): отказ → optOut, Tenjin ничего не отправляет. Сессии считаются по connect() — повторяем на каждом onResume.
 */
object Attribution {
    private const val SDK_KEY = "Q7XO1BESYOXRFBHMQDBMSHMBC1CUCQRQ"
    private var tenjin: TenjinSDK? = null
    private var started = false

    /** Раз за процесс, из MainActivity. Само дожидается согласия. */
    fun start(context: Context) {
        if (started) return
        started = true
        val app = context.applicationContext
        Billing.onPurchase = { p, details -> trackPurchase(p, details) }
        ConsentService.onChange { tenjin?.let { applyConsent(it) } }
        ConsentService.onReady {
            tenjin = TenjinSDK.getInstance(app, SDK_KEY).also {
                it.setAppStore(TenjinSDK.AppStoreType.googleplay)
                applyConsent(it)
                it.connect()
            }
        }
    }

    fun onResume() {
        tenjin?.let { applyConsent(it); it.connect() }
    }

    /** Доход с показа ролика (ILRD) — Tenjin считает по нему ROAS закупки. */
    fun trackAdRevenue(value: AdValue, ad: RewardedAd) {
        val t = tenjin ?: return
        val info = ad.responseInfo
        t.eventAdImpressionAdMob(JSONObject().apply {
            put("ad_unit_id", ad.adUnitId)
            put("value_micros", value.valueMicros)
            put("currency_code", value.currencyCode)
            put("response_id", info.responseId)
            put("mediation_adapter_class_name", info.loadedAdapterResponseInfo?.adapterClassName)
            put("precision_type", value.precisionType)
        })
    }

    private fun applyConsent(t: TenjinSDK) {
        // Вне ЕЭЗ формы нет и TCF-строки тоже — там Tenjin работает по умолчанию.
        if (ConsentService.isConsentNotRequired) t.optIn() else t.optInOutUsingCMP()
    }

    /** Глава — разовая цена, подписка — полная цена периода (последняя фаза, после пробных). */
    private fun trackPurchase(p: Purchase, details: ProductDetails?) {
        val t = tenjin ?: return
        val d = details ?: return
        val (micros, currency) = if (d.productType == BillingClient.ProductType.INAPP) {
            val o = d.oneTimePurchaseOfferDetails ?: return
            o.priceAmountMicros to o.priceCurrencyCode
        } else {
            val phase = d.subscriptionOfferDetails?.firstOrNull()?.pricingPhases?.pricingPhaseList?.lastOrNull() ?: return
            phase.priceAmountMicros to phase.priceCurrencyCode
        }
        t.transaction(d.productId, currency, p.quantity, micros / 1_000_000.0, p.originalJson, p.signature)
    }
}
