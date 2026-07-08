plugins { id("com.android.asset-pack") }

assetPack {
    packName.set("chapter_borgia")
    dynamicDelivery { deliveryType.set("on-demand") }
}
