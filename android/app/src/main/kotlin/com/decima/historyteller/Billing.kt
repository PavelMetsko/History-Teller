package com.decima.historyteller

import android.app.Activity
import android.content.Context
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Clear
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextDecoration
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.android.billingclient.api.*

/**
 * Покупки (Google Play Billing 7). Рим бесплатен; остальные главы — либо разовая **поглавная**
 * покупка (INAPP, у каждой своя цена), либо **подписка** на весь контент (SUBS, месяц/год).
 * Источник истины — Play; кэш открытых эпох в SharedPreferences для оффлайна. Порт iOS Store.
 */
object Billing {
    const val CHAPTER_PREFIX = "com.decima.historyteller.chapter."
    val PAID_EPOCHS = listOf("tudor", "revolution", "empire", "borgia", "byzantium")
    fun chapterProduct(epoch: String) = CHAPTER_PREFIX + epoch
    const val SUB_MONTHLY = "com.decima.historyteller.sub.monthly"
    const val SUB_YEARLY = "com.decima.historyteller.sub.yearly"

    var unlockedEpochs by mutableStateOf(setOf<String>()); private set
    var subscribed by mutableStateOf(false); private set
    var purchasing by mutableStateOf(false); private set
    private val prices = mutableStateMapOf<String, String>()   // productId -> formattedPrice

    private var client: BillingClient? = null
    private val details = HashMap<String, ProductDetails>()    // productId -> details
    private var settings: Settings? = null

    fun isUnlocked(epoch: String): Boolean = epoch == "rome" || subscribed || epoch in unlockedEpochs
    fun chapterPrice(epoch: String): String = prices[chapterProduct(epoch)] ?: ""
    fun subPrice(productId: String): String = prices[productId] ?: ""

    fun init(ctx: Context) {
        if (client != null) return
        settings = Settings(ctx).also {
            unlockedEpochs = it.unlockedEpochs
            subscribed = it.subscribed
        }
        val c = BillingClient.newBuilder(ctx.applicationContext)
            .setListener { result, purchases ->
                if (result.responseCode == BillingClient.BillingResponseCode.OK && purchases != null) handlePurchases(purchases)
                purchasing = false
            }
            .enablePendingPurchases(PendingPurchasesParams.newBuilder().enableOneTimeProducts().build())
            .build()
        client = c
        c.startConnection(object : BillingClientStateListener {
            override fun onBillingSetupFinished(result: BillingResult) {
                if (result.responseCode == BillingClient.BillingResponseCode.OK) { queryProducts(); refreshEntitlements() }
            }
            override fun onBillingServiceDisconnected() {}
        })
    }

    private fun queryProducts() {
        val c = client ?: return
        // INAPP — поглавные
        val inapp = PAID_EPOCHS.map {
            QueryProductDetailsParams.Product.newBuilder().setProductId(chapterProduct(it))
                .setProductType(BillingClient.ProductType.INAPP).build()
        }
        c.queryProductDetailsAsync(QueryProductDetailsParams.newBuilder().setProductList(inapp).build()) { r, list ->
            if (r.responseCode == BillingClient.BillingResponseCode.OK) for (pd in list) {
                details[pd.productId] = pd
                prices[pd.productId] = pd.oneTimePurchaseOfferDetails?.formattedPrice ?: ""
            }
        }
        // SUBS — подписка (месяц/год)
        val subs = listOf(SUB_MONTHLY, SUB_YEARLY).map {
            QueryProductDetailsParams.Product.newBuilder().setProductId(it)
                .setProductType(BillingClient.ProductType.SUBS).build()
        }
        c.queryProductDetailsAsync(QueryProductDetailsParams.newBuilder().setProductList(subs).build()) { r, list ->
            if (r.responseCode == BillingClient.BillingResponseCode.OK) for (pd in list) {
                details[pd.productId] = pd
                prices[pd.productId] = pd.subscriptionOfferDetails?.firstOrNull()
                    ?.pricingPhases?.pricingPhaseList?.firstOrNull()?.formattedPrice ?: ""
            }
        }
    }

    /** Восстановление прав: INAPP + SUBS покупки. */
    fun refreshEntitlements() {
        val c = client ?: return
        c.queryPurchasesAsync(QueryPurchasesParams.newBuilder().setProductType(BillingClient.ProductType.INAPP).build()) { _, p -> handlePurchases(p) }
        c.queryPurchasesAsync(QueryPurchasesParams.newBuilder().setProductType(BillingClient.ProductType.SUBS).build()) { _, p -> handlePurchases(p) }
    }

    fun purchaseChapter(activity: Activity, epoch: String) {
        val pd = details[chapterProduct(epoch)] ?: return
        launch(activity, BillingFlowParams.ProductDetailsParams.newBuilder().setProductDetails(pd).build())
    }

    fun purchaseSubscription(activity: Activity, productId: String) {
        val pd = details[productId] ?: return
        val offer = pd.subscriptionOfferDetails?.firstOrNull()?.offerToken ?: return
        launch(activity, BillingFlowParams.ProductDetailsParams.newBuilder()
            .setProductDetails(pd).setOfferToken(offer).build())
    }

    private fun launch(activity: Activity, param: BillingFlowParams.ProductDetailsParams) {
        val c = client ?: return
        purchasing = true
        val r = c.launchBillingFlow(activity, BillingFlowParams.newBuilder()
            .setProductDetailsParamsList(listOf(param)).build())
        if (r.responseCode != BillingClient.BillingResponseCode.OK) purchasing = false
    }

    private fun handlePurchases(purchases: List<Purchase>) {
        val epochs = unlockedEpochs.toMutableSet(); var sub = subscribed; var changed = false
        for (p in purchases) {
            if (p.purchaseState != Purchase.PurchaseState.PURCHASED) continue
            for (prod in p.products) {
                when {
                    prod.startsWith(CHAPTER_PREFIX) -> { epochs.add(prod.removePrefix(CHAPTER_PREFIX)); changed = true }
                    prod == SUB_MONTHLY || prod == SUB_YEARLY -> { sub = true; changed = true }
                }
            }
            if (!p.isAcknowledged) client?.acknowledgePurchase(
                AcknowledgePurchaseParams.newBuilder().setPurchaseToken(p.purchaseToken).build()) {}
        }
        if (changed) {
            unlockedEpochs = epochs; subscribed = sub
            settings?.unlockedEpochs = epochs; settings?.subscribed = sub
        }
    }
}

/** Пейволл главы: открыть эту главу (разовая) или подписка на всё. Порт iOS PaywallView. */
@Composable
fun PaywallScreen(epoch: String, chapterTitle: String, onClose: () -> Unit, onUnlocked: () -> Unit) {
    val ctx = LocalContext.current
    val activity = ctx as? Activity

    LaunchedEffect(Billing.isUnlocked(epoch)) { if (Billing.isUnlocked(epoch)) onUnlocked() }

    Box(Modifier.fillMaxSize().background(Color.Black.copy(alpha = 0.5f)).clickable { onClose() },
        contentAlignment = Alignment.Center) {
        Box(contentAlignment = Alignment.TopEnd) {
            BookPage(Modifier.widthIn(max = 490.dp).clickable(enabled = false) {}) {
                Column(Modifier.padding(horizontal = 32.dp, vertical = 20.dp),
                    horizontalAlignment = Alignment.CenterHorizontally) {
                    Box(Modifier.size(56.dp).clip(CircleShape).background(Palette.maroon)
                        .border(2.dp, Palette.gold, CircleShape), contentAlignment = Alignment.Center) {
                        Icon(Icons.Filled.Star, null, tint = Palette.gold, modifier = Modifier.size(26.dp))
                    }
                    Spacer(Modifier.height(10.dp))
                    Text("«$chapterTitle»", color = Palette.ink, fontSize = 22.sp, fontWeight = FontWeight.Bold,
                        fontFamily = Fonts.serif, textAlign = TextAlign.Center)
                    Box(Modifier.padding(top = 6.dp).width(70.dp).height(3.dp).clip(RoundedCornerShape(2.dp)).background(Palette.gold))
                    Spacer(Modifier.height(10.dp))
                    Text(L10n.s("ui.paywall_sub"), color = Palette.inkSoft, fontSize = 14.sp,
                        fontFamily = Fonts.rounded, textAlign = TextAlign.Center)
                    Spacer(Modifier.height(14.dp))

                    // 1) эту главу
                    val chPrice = Billing.chapterPrice(epoch)
                    Row(Modifier.widthIn(min = 260.dp).clip(RoundedCornerShape(28.dp)).background(Palette.maroon)
                        .border(2.5.dp, Palette.ink, RoundedCornerShape(28.dp))
                        .clickable(enabled = !Billing.purchasing) { activity?.let { Billing.purchaseChapter(it, epoch) } }
                        .padding(horizontal = 30.dp, vertical = 12.dp),
                        horizontalArrangement = Arrangement.Center, verticalAlignment = Alignment.CenterVertically) {
                        if (Billing.purchasing) CircularProgressIndicator(color = Palette.paper, strokeWidth = 2.dp, modifier = Modifier.size(20.dp))
                        else Text(if (chPrice.isEmpty()) L10n.s("ui.buy_chapter_cta") else "${L10n.s("ui.buy_chapter_cta")} — $chPrice",
                            color = Palette.paper, fontSize = 17.sp, fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
                    }

                    Spacer(Modifier.height(12.dp))
                    Text(L10n.s("ui.or").uppercase(), color = Palette.inkSoft, fontSize = 11.sp, fontFamily = Fonts.rounded)
                    Spacer(Modifier.height(6.dp))
                    Text(L10n.s("ui.sub_hint"), color = Palette.inkSoft, fontSize = 12.sp, fontFamily = Fonts.rounded)
                    Spacer(Modifier.height(8.dp))

                    // 2) подписка (месяц/год)
                    Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                        val m = Billing.subPrice(Billing.SUB_MONTHLY)
                        val y = Billing.subPrice(Billing.SUB_YEARLY)
                        if (m.isNotEmpty()) SubButton(L10n.s("ui.sub_month", m)) { activity?.let { Billing.purchaseSubscription(it, Billing.SUB_MONTHLY) } }
                        if (y.isNotEmpty()) SubButton(L10n.s("ui.sub_year", y)) { activity?.let { Billing.purchaseSubscription(it, Billing.SUB_YEARLY) } }
                    }

                    Spacer(Modifier.height(12.dp))
                    Text(L10n.s("ui.restore"), color = Palette.inkSoft, fontSize = 13.sp, fontFamily = Fonts.rounded,
                        textDecoration = TextDecoration.Underline, modifier = Modifier.clickable { Billing.refreshEntitlements() })
                }
            }
            Box(Modifier.padding(10.dp).size(30.dp).clip(CircleShape).background(Palette.paper)
                .border(1.dp, Palette.ink.copy(alpha = 0.25f), CircleShape).clickable { onClose() },
                contentAlignment = Alignment.Center) {
                Icon(Icons.Filled.Clear, null, tint = Palette.inkSoft, modifier = Modifier.size(16.dp))
            }
        }
    }
}

@Composable
private fun SubButton(label: String, onClick: () -> Unit) {
    Box(Modifier.clip(RoundedCornerShape(24.dp)).background(Palette.panel)
        .border(2.dp, Palette.gold, RoundedCornerShape(24.dp))
        .clickable(enabled = !Billing.purchasing) { onClick() }.padding(horizontal = 22.dp, vertical = 10.dp)) {
        Text(label, color = Palette.ink, fontSize = 15.sp, fontFamily = Fonts.rounded)
    }
}
