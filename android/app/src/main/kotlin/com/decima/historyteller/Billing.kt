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
 * Покупки (Google Play Billing 7). Фримиум: первая глава бесплатна, разовая непотребляемая
 * покупка `unlockall` открывает все главы. Источник истины — Play; кэш в [Settings.unlocked]
 * для оффлайна/старта. Порт iOS Store (StoreKit 2).
 */
object Billing {
    const val PRODUCT = "com.decima.historyteller.unlockall"

    var isUnlocked by mutableStateOf(false); private set
    var priceText by mutableStateOf(""); private set
    var purchasing by mutableStateOf(false); private set

    private var client: BillingClient? = null
    private var details: ProductDetails? = null
    private var settings: Settings? = null

    fun init(ctx: Context) {
        if (client != null) return
        settings = Settings(ctx).also { isUnlocked = it.unlocked }  // из кэша сразу
        val c = BillingClient.newBuilder(ctx.applicationContext)
            .setListener { result, purchases ->
                if (result.responseCode == BillingClient.BillingResponseCode.OK && purchases != null)
                    handlePurchases(purchases)
                purchasing = false
            }
            .enablePendingPurchases(
                PendingPurchasesParams.newBuilder().enableOneTimeProducts().build())
            .build()
        client = c
        c.startConnection(object : BillingClientStateListener {
            override fun onBillingSetupFinished(result: BillingResult) {
                if (result.responseCode == BillingClient.BillingResponseCode.OK) {
                    queryProduct()
                    refreshEntitlements()
                }
            }
            override fun onBillingServiceDisconnected() {}
        })
    }

    private fun queryProduct() {
        val c = client ?: return
        val params = QueryProductDetailsParams.newBuilder().setProductList(listOf(
            QueryProductDetailsParams.Product.newBuilder()
                .setProductId(PRODUCT)
                .setProductType(BillingClient.ProductType.INAPP).build()
        )).build()
        c.queryProductDetailsAsync(params) { result, list ->
            if (result.responseCode == BillingClient.BillingResponseCode.OK) {
                details = list.firstOrNull()
                priceText = details?.oneTimePurchaseOfferDetails?.formattedPrice ?: ""
            }
        }
    }

    /** Восстановление прав/покупок (queryPurchases). */
    fun refreshEntitlements() {
        val c = client ?: return
        c.queryPurchasesAsync(
            QueryPurchasesParams.newBuilder().setProductType(BillingClient.ProductType.INAPP).build()
        ) { _, purchases -> handlePurchases(purchases) }
    }

    fun purchase(activity: Activity) {
        val c = client ?: return
        val pd = details ?: return
        purchasing = true
        val params = BillingFlowParams.newBuilder().setProductDetailsParamsList(listOf(
            BillingFlowParams.ProductDetailsParams.newBuilder().setProductDetails(pd).build()
        )).build()
        val r = c.launchBillingFlow(activity, params)
        if (r.responseCode != BillingClient.BillingResponseCode.OK) purchasing = false
    }

    private fun handlePurchases(purchases: List<Purchase>) {
        for (p in purchases) {
            if (PRODUCT !in p.products) continue
            if (p.purchaseState == Purchase.PurchaseState.PURCHASED) {
                unlock()
                if (!p.isAcknowledged) {
                    client?.acknowledgePurchase(
                        AcknowledgePurchaseParams.newBuilder().setPurchaseToken(p.purchaseToken).build()
                    ) {}
                }
            }
        }
    }

    private fun unlock() {
        isUnlocked = true
        settings?.unlocked = true
    }
}

/** Пейволл «Открой все главы» (порт PaywallView). onUnlocked вызывается при успешной покупке. */
@Composable
fun PaywallScreen(onClose: () -> Unit, onUnlocked: () -> Unit) {
    val ctx = LocalContext.current
    val activity = ctx as? Activity

    LaunchedEffect(Billing.isUnlocked) { if (Billing.isUnlocked) onUnlocked() }

    Box(Modifier.fillMaxSize().background(Color.Black.copy(alpha = 0.5f)).clickable { onClose() },
        contentAlignment = Alignment.Center) {
        Box(contentAlignment = Alignment.TopEnd) {
            BookPage(Modifier.widthIn(max = 480.dp).clickable(enabled = false) {}) {
                Column(Modifier.padding(horizontal = 34.dp, vertical = 22.dp),
                    horizontalAlignment = Alignment.CenterHorizontally) {
                    Box(Modifier.size(62.dp).clip(CircleShape).background(Palette.maroon)
                        .border(2.dp, Palette.gold, CircleShape), contentAlignment = Alignment.Center) {
                        Icon(Icons.Filled.Star, null, tint = Palette.gold, modifier = Modifier.size(28.dp))
                    }
                    Spacer(Modifier.height(12.dp))
                    Text(L10n.s("ui.unlock_title"), color = Palette.ink, fontSize = 24.sp,
                        fontWeight = FontWeight.Bold, fontFamily = Fonts.serif, textAlign = TextAlign.Center)
                    Box(Modifier.padding(top = 6.dp).width(80.dp).height(3.dp)
                        .clip(RoundedCornerShape(2.dp)).background(Palette.gold))
                    Spacer(Modifier.height(12.dp))
                    Text(L10n.s("ui.unlock_body"), color = Palette.inkSoft, fontSize = 15.sp,
                        fontFamily = Fonts.rounded, textAlign = TextAlign.Center,
                        modifier = Modifier.padding(horizontal = 8.dp))
                    Spacer(Modifier.height(18.dp))

                    Row(Modifier.widthIn(min = 240.dp).clip(RoundedCornerShape(28.dp))
                        .background(Palette.maroon).border(2.5.dp, Palette.ink, RoundedCornerShape(28.dp))
                        .clickable(enabled = !Billing.purchasing) { activity?.let { Billing.purchase(it) } }
                        .padding(horizontal = 32.dp, vertical = 13.dp),
                        horizontalArrangement = Arrangement.Center, verticalAlignment = Alignment.CenterVertically) {
                        if (Billing.purchasing) {
                            CircularProgressIndicator(color = Palette.paper, strokeWidth = 2.dp,
                                modifier = Modifier.size(20.dp))
                        } else {
                            Text(
                                if (Billing.priceText.isEmpty()) L10n.s("ui.unlock_cta")
                                else L10n.s("ui.unlock_cta_price", Billing.priceText),
                                color = Palette.paper, fontSize = 18.sp,
                                fontWeight = FontWeight.Bold, fontFamily = Fonts.serif)
                        }
                    }
                    Spacer(Modifier.height(12.dp))
                    Text(L10n.s("ui.restore"), color = Palette.inkSoft, fontSize = 13.sp,
                        fontFamily = Fonts.rounded, textDecoration = TextDecoration.Underline,
                        modifier = Modifier.clickable { Billing.refreshEntitlements() })
                }
            }
            // Крестик
            Box(Modifier.padding(10.dp).size(30.dp).clip(CircleShape).background(Palette.paper)
                .border(1.dp, Palette.ink.copy(alpha = 0.25f), CircleShape)
                .clickable { onClose() }, contentAlignment = Alignment.Center) {
                Icon(Icons.Filled.Clear, null, tint = Palette.inkSoft, modifier = Modifier.size(16.dp))
            }
        }
    }
}
