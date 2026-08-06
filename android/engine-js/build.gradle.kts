// Тот же движок, скомпилированный для браузера — под редактор контента.
//
// Исходники не копируются, а разделяются с :engine через srcDir: солвер в редакторе обязан быть
// тем же, что в игре, иначе «проверено в редакторе» перестанет что-либо значить.
//
// Почему не Kotlin Multiplatform: KMP-модулю нужен androidTarget(), иначе Android-приложение не
// сможет его резолвить. Это правка сборки работающей игры ради модуля, который игре не нужен.
// Здесь же :engine остаётся нетронутым, а JS собирается рядом.
plugins {
    kotlin("js")
    kotlin("plugin.serialization")
}

kotlin {
    js(IR) {
        browser()
        binaries.executable()
    }
    sourceSets {
        val main by getting {
            kotlin.srcDir("../engine/src/main/kotlin")
            // Раннер валидатора работает с файловой системой — в браузере ему нечего делать.
            kotlin.exclude("**/Audit.kt")
            dependencies {
                implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.7.3")
            }
        }
    }
}
