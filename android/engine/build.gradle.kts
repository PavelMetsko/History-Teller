plugins {
    kotlin("jvm")
    kotlin("plugin.serialization")
    application
}
dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.7.3")
}
application { mainClass.set("teller.engine.AuditKt") }
