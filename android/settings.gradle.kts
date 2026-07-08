pluginManagement {
    repositories { google(); mavenCentral(); gradlePluginPortal() }
}
dependencyResolutionManagement {
    repositories { google(); mavenCentral() }
}
rootProject.name = "HistoryTeller"
include(":engine")
include(":app")
include(":chapter_byzantium")
include(":chapter_borgia")
include(":chapter_empire")
include(":chapter_revolution")
include(":chapter_tudor")
