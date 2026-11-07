package com.decima.historyteller

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Clear
import androidx.compose.material.icons.filled.Check
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
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
 * Покупки (Google Play Billing 8). С 4.0 все главы играются бесплатно, с рекламой. Каждая
 * платная глава продаётся отдельно (INAPP) как «Без рекламы» в ней: ни интерстишелов, ни
 * счёта подсказок ([Premium.adsFree]). Подписка (SUBS, месяц/год) больше не продаётся, но
 * подписчики 3.x сохраняют всё. Источник истины — Play; кэш прав для оффлайна. Порт iOS Store.
 */
object Billing {
    const val CHAPTER_PREFIX = "com.decima.historyteller.chapter."
    /**
     * Платные главы берём из манифеста: новая глава, выложенная в облако, сама попадёт в запрос
     * продуктов — достаточно завести IAP в Play Console. Вшитый список — фолбэк без манифеста.
     */
    val PAID_EPOCHS: List<String>
        get() = ContentSync.availableChapters().filterNot { it.free }.map { it.id }
            .ifEmpty { listOf("usa", "tudor", "poland", "revolution", "empire", "borgia", "byzantium") }
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

    /** Новая покупка, подтверждённая в Play (не восстановление) — для атрибуции (Tenjin). Ставит приложение. */
    var onPurchase: ((Purchase, ProductDetails?) -> Unit)? = null

    /** Цена главы из Play; пусто — продукт не загрузился (кнопку не показываем). */
    fun chapterPrice(epoch: String): String = prices[chapterProduct(epoch)] ?: ""

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

    /**
     * Перезапросить цены после загрузки манифеста: [init] идёт раньше, чем манифест прочитан,
     * и тогда в запрос попадал только вшитый список (без новых глав — Польши, США).
     */
    fun reloadProducts() = queryProducts()

    private fun queryProducts() {
        val c = client ?: return
        // INAPP — поглавные
        val inapp = PAID_EPOCHS.map {
            QueryProductDetailsParams.Product.newBuilder().setProductId(chapterProduct(it))
                .setProductType(BillingClient.ProductType.INAPP).build()
        }
        c.queryProductDetailsAsync(QueryProductDetailsParams.newBuilder().setProductList(inapp).build()) { r, res ->
            if (r.responseCode == BillingClient.BillingResponseCode.OK) for (pd in res.productDetailsList) {
                details[pd.productId] = pd
                prices[pd.productId] = pd.oneTimePurchaseOfferDetails?.formattedPrice ?: ""
            }
        }
        // SUBS — подписка (месяц/год)
        val subs = listOf(SUB_MONTHLY, SUB_YEARLY).map {
            QueryProductDetailsParams.Product.newBuilder().setProductId(it)
                .setProductType(BillingClient.ProductType.SUBS).build()
        }
        c.queryProductDetailsAsync(QueryProductDetailsParams.newBuilder().setProductList(subs).build()) { r, res ->
            if (r.responseCode == BillingClient.BillingResponseCode.OK) for (pd in res.productDetailsList) {
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
                AcknowledgePurchaseParams.newBuilder().setPurchaseToken(p.purchaseToken).build()) { r ->
                // Неподтверждённая = ещё не учтённая: так каждая покупка уходит в атрибуцию ровно один раз.
                if (r.responseCode == BillingClient.BillingResponseCode.OK) {
                    onPurchase?.invoke(p, p.products.firstOrNull()?.let { details[it] })
                    Telemetry.track("purchase", p.products.firstOrNull())
                }
            }
        }
        if (changed) {
            unlockedEpochs = epochs; subscribed = sub
            settings?.unlockedEpochs = epochs; settings?.subscribed = sub
        }
    }
}

/**
 * Окно «Глава без рекламы» — поглавная покупка 4.0. Входы: плашка на карте главы и окно
 * «Подсказки закончились» (глава текущего уровня). Порт iOS PremiumView(epoch).
 */
@Composable
fun PremiumScreen(epoch: String, onClose: () -> Unit) {
    val ctx = LocalContext.current
    val activity = ctx as? Activity
    LaunchedEffect(Unit) { Telemetry.track("premium_open", null, epoch) }

    Box(Modifier.fillMaxSize().background(Color.Black.copy(alpha = 0.5f)).clickable { onClose() },
        contentAlignment = Alignment.Center) {
        Box(contentAlignment = Alignment.TopEnd) {
            BookPage(Modifier.widthIn(max = 490.dp).clickable(enabled = false) {}) {
                Column(Modifier.padding(start = 32.dp, end = 32.dp, top = 18.dp, bottom = 22.dp)
                        .verticalScroll(rememberScrollState()),
                    horizontalAlignment = Alignment.CenterHorizontally) {
                    Box(Modifier.size(56.dp).clip(CircleShape).background(Palette.maroon)
                        .border(2.dp, Palette.gold, CircleShape), contentAlignment = Alignment.Center) {
                        Text("👑", fontSize = 26.sp)
                    }
                    Spacer(Modifier.height(8.dp))
                    Text(L10n.s("ui.chapter_noads_title"), color = Palette.ink, fontSize = 24.sp, fontWeight = FontWeight.Bold,
                        fontFamily = Fonts.serif, textAlign = TextAlign.Center)
                    Text("«${L10n.s("chapter.$epoch.title")}»", color = Palette.maroon, fontSize = 16.sp,
                        fontWeight = FontWeight.Bold, fontFamily = Fonts.serif, textAlign = TextAlign.Center)
                    Box(Modifier.padding(top = 6.dp).width(70.dp).height(3.dp).clip(RoundedCornerShape(2.dp)).background(Palette.gold))
                    Spacer(Modifier.height(10.dp))
                    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        for (b in listOf("ui.chapter_noads_b1", "ui.chapter_noads_b2", "ui.premium_b3")) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(Icons.Filled.Check, null, tint = Palette.success, modifier = Modifier.size(18.dp))
                                Spacer(Modifier.width(8.dp))
                                Text(L10n.s(b), color = Palette.ink, fontSize = 14.sp, fontFamily = Fonts.rounded)
                            }
                        }
                    }
                    Spacer(Modifier.height(14.dp))

                    if (Premium.adsFree(epoch)) {
                        Text(L10n.s("ui.premium_active"), color = Palette.success, fontSize = 16.sp,
                            fontWeight = FontWeight.Bold, fontFamily = Fonts.rounded, textAlign = TextAlign.Center)
                    } else {
                        // Цена не приехала из Play — кнопку не показываем.
                        val price = Billing.chapterPrice(epoch)
                        if (price.isNotEmpty()) {
                            Row(Modifier.widthIn(min = 260.dp).clip(RoundedCornerShape(28.dp)).background(Palette.maroon)
                                .border(2.5.dp, Palette.ink, RoundedCornerShape(28.dp))
                                .clickable(enabled = !Billing.purchasing) { activity?.let { Billing.purchaseChapter(it, epoch) } }
                                .padding(horizontal = 30.dp, vertical = 12.dp),
                                horizontalArrangement = Arrangement.Center, verticalAlignment = Alignment.CenterVertically) {
                                if (Billing.purchasing) CircularProgressIndicator(color = Palette.paper, strokeWidth = 2.dp, modifier = Modifier.size(20.dp))
                                else Text(L10n.s("ui.chapter_noads_cta", price),
                                    color = Palette.paper, fontSize = 17.sp, fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
                            }
                        }
                        Spacer(Modifier.height(10.dp))
                        Text(L10n.s("ui.restore"), color = Palette.maroon, fontSize = 13.sp, fontFamily = Fonts.rounded,
                            textDecoration = TextDecoration.Underline,
                            modifier = Modifier.clickable { Billing.refreshEntitlements() }.padding(4.dp))
                    }

                    Spacer(Modifier.height(10.dp))
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                        fun openUrl(url: String) = ctx.startActivity(
                            Intent(Intent.ACTION_VIEW, Uri.parse(url)).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
                        Text(L10n.s("ui.terms"), color = Palette.maroon, fontSize = 13.sp, fontFamily = Fonts.rounded,
                            textDecoration = TextDecoration.Underline, modifier = Modifier.clickable { openUrl(Legal.TERMS_URL) })
                        Text("·", color = Palette.inkSoft)
                        Text(L10n.s("ui.privacy"), color = Palette.maroon, fontSize = 13.sp, fontFamily = Fonts.rounded,
                            textDecoration = TextDecoration.Underline, modifier = Modifier.clickable { openUrl(Legal.PRIVACY_URL) })
                    }
                }
            }
            // Больший тап-таргет (44dp) вокруг видимого кружка 32dp — X легко нажать.
            Box(Modifier.padding(4.dp).size(44.dp).clip(CircleShape).clickable { onClose() },
                contentAlignment = Alignment.Center) {
                Box(Modifier.size(32.dp).clip(CircleShape).background(Palette.paper)
                    .border(1.dp, Palette.ink.copy(alpha = 0.25f), CircleShape),
                    contentAlignment = Alignment.Center) {
                    Icon(Icons.Filled.Clear, null, tint = Palette.inkSoft, modifier = Modifier.size(18.dp))
                }
            }
        }
    }
}

/**
 * Кнопка «▶ ролик» (подсказка, возврат серии). Ролик не загрузился или идёт кулдаун — кнопка
 * неактивна с пояснением «Ролик загружается…» / «Следующий ролик через N с».
 */
@Composable
fun AdButton(label: String, onClick: () -> Unit) {
    val available = AdService.isEnabled && AdService.isReady && AdService.cooldownLeft == 0 && !AdService.isShowing
    val title = when {
        AdService.cooldownLeft > 0 -> L10n.s("ui.ad_cooldown", AdService.cooldownLeft)
        available -> label
        else -> L10n.s("ui.video_loading")
    }
    Box(Modifier.clip(RoundedCornerShape(24.dp)).background(Palette.panel)
        .border(2.dp, Palette.ink.copy(alpha = if (available) 0.5f else 0.2f), RoundedCornerShape(24.dp))
        .clickable(enabled = available) { onClick() }.padding(horizontal = 22.dp, vertical = 10.dp)) {
        Text("▶  $title", color = if (available) Palette.ink else Palette.inkSoft, fontSize = 15.sp, fontFamily = Fonts.rounded)
    }
}
