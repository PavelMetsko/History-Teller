plugins { id("com.android.asset-pack") }

assetPack {
    packName.set("chapter_empire")
    dynamicDelivery { deliveryType.set("on-demand") }
}
