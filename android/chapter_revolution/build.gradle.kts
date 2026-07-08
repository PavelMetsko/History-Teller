plugins { id("com.android.asset-pack") }

assetPack {
    packName.set("chapter_revolution")
    dynamicDelivery { deliveryType.set("on-demand") }
}
