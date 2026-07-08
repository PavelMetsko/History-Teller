plugins { id("com.android.asset-pack") }

assetPack {
    packName.set("chapter_byzantium")
    dynamicDelivery { deliveryType.set("on-demand") }
}
