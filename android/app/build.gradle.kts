import java.util.Properties
import java.io.FileInputStream

plugins {
    id("com.android.application")
    kotlin("android")
    kotlin("plugin.serialization")
    id("org.jetbrains.kotlin.plugin.compose")
}

// Релизная подпись: читаем из keystore.properties (в .gitignore). Если файла нет —
// release собирается неподписанным (для CI/дебага), это не ломает сборку.
val keystorePropsFile = rootProject.file("keystore.properties")
val hasKeystore = keystorePropsFile.exists()
val keystoreProps = Properties().apply { if (hasKeystore) load(FileInputStream(keystorePropsFile)) }

android {
    namespace = "com.decima.historyteller"
    compileSdk = 36

    // Play Asset Delivery: арт глав в on-demand asset-паках (Google Play хостит; свой сервер не нужен).

    defaultConfig {
        applicationId = "com.decima.historyteller"
        minSdk = 26
        targetSdk = 36
        versionCode = 12
        versionName = "3.0.1"
    }
    buildFeatures { compose = true; buildConfig = true }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
        // play-services-ads 24+ собран Kotlin 2.2+, проект на 2.0.21: зовём только Java-API SDK,
        // поэтому проверку версии метаданных пропускаем. Уйдёт с переходом проекта на Kotlin 2.2+.
        freeCompilerArgs += "-Xskip-metadata-version-check"
    }

    signingConfigs {
        if (hasKeystore) create("release") {
            storeFile = rootProject.file(keystoreProps["storeFile"] as String)
            storePassword = keystoreProps["storePassword"] as String
            keyAlias = keystoreProps["keyAlias"] as String
            keyPassword = keystoreProps["keyPassword"] as String
        }
    }
    buildTypes {
        getByName("debug") {
            // Адрес локального стенда контента (tools/publish_content.py --serve).
            // Пусто по умолчанию — сборка идёт на прод-CDN, как и раньше. Передаётся так:
            //   ./gradlew :app:assembleDebug -PhtContentUrl=http://127.0.0.1:8787
            val url = (project.findProperty("htContentUrl") as String?).orEmpty()
            buildConfigField("String", "CONTENT_URL", "\"$url\"")
        }
        getByName("release") {
            buildConfigField("String", "CONTENT_URL", "\"\"")
            isMinifyEnabled = false
            if (hasKeystore) signingConfig = signingConfigs.getByName("release")
        }
    }
}

dependencies {
    implementation(project(":engine"))
    implementation(platform("androidx.compose:compose-bom:2024.10.01"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-graphics")
    implementation("androidx.compose.foundation:foundation")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.material:material-icons-core")
    implementation("androidx.activity:activity-compose:1.9.3")
    implementation("androidx.datastore:datastore-preferences:1.1.1")
    implementation("com.google.android.play:review-ktx:2.0.2")
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.7.3")
    // Play Billing 8.x required by Google Play (deadline 2026-08-31). Plain (non-ktx)
    // Java artifact: code uses callback APIs only, and billing-ktx 8.x needs Kotlin 2.1
    // (project is on Kotlin 2.0.21). The Java artifact has no Kotlin metadata → no conflict.
    implementation("com.android.billingclient:billing:8.0.0")
    // Атрибуция установок и покупок (Tenjin, MMP для закупки в AppLovin) + то, что SDK читает:
    // рекламный ID, App Set ID и Install Referrer (источник установки из Google Play).
    implementation("com.tenjin:android-sdk:1.24.0")
    implementation("com.google.android.gms:play-services-ads-identifier:18.2.0")
    implementation("com.google.android.gms:play-services-appset:16.1.0")
    implementation("com.android.installreferrer:installreferrer:2.2")
    // Rewarded-реклама (Google AdMob) и согласие GDPR (Google UMP — сертифицированный CMP,
    // без него AdMob в ЕЭЗ рекламу не показывает). Форма — в AdMob → Privacy & messaging.
    implementation("com.google.android.gms:play-services-ads:24.9.0")
    implementation("com.google.android.ump:user-messaging-platform:4.0.0")
}
