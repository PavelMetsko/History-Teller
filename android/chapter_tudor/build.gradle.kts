plugins { id("com.android.asset-pack") }

assetPack {
    packName.set("chapter_tudor")
    dynamicDelivery { deliveryType.set("on-demand") }
}
