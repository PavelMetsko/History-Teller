pluginManagement {
    repositories { google(); mavenCentral(); gradlePluginPortal() }
}
dependencyResolutionManagement {
    repositories { google(); mavenCentral() }
}
rootProject.name = "HistoryTeller"
include(":engine")
include(":app")
include(":engine-js")   // тот же движок для браузера — редактор контента
