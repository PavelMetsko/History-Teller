package com.decima.historyteller

import android.content.Context
import com.android.billingclient.api.BillingClient
import com.android.billingclient.api.ProductDetails
import com.android.billingclient.api.Purchase
import com.applovin.mediation.MaxAd
import com.tenjin.android.TenjinSDK

/**
 * Атрибуция установок и покупок через Tenjin (MMP для закупки в AppLovin). Порт iOS
 * AttributionService. Стартует только после окна согласия; отказ от рекламных данных → optOut:
 * Tenjin ничего не отправляет. Сессии считаются по connect() — повторяем на каждом onResume.
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
    fun trackAdRevenue(ad: MaxAd) {
        tenjin?.eventAdImpressionAppLovin(ad)
    }

    private fun applyConsent(t: TenjinSDK) {
        if (ConsentService.doNotSell) t.optOut() else t.optIn()
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
