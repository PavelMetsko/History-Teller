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
    compileSdk = 35

    // Play Asset Delivery: арт глав в on-demand asset-паках (Google Play хостит; свой сервер не нужен).
    assetPacks += listOf(":chapter_tudor", ":chapter_revolution", ":chapter_empire", ":chapter_borgia", ":chapter_byzantium")

    defaultConfig {
        applicationId = "com.decima.historyteller"
        minSdk = 26
        targetSdk = 35
        versionCode = 2
        versionName = "1.0"
    }
    buildFeatures { compose = true; buildConfig = true }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }

    signingConfigs {
        if (hasKeystore) create("release") {
            storeFile = rootProject.file(keystoreProps["storeFile"] as String)
            storePassword = keystoreProps["storePassword"] as String
            keyAlias = keystoreProps["keyAlias"] as String
            keyPassword = keystoreProps["keyPassword"] as String
        }
    }
    buildTypes {
        getByName("release") {
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
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.7.3")
    implementation("com.android.billingclient:billing-ktx:7.1.1")
    implementation("com.google.android.play:asset-delivery-ktx:2.2.0")
}
