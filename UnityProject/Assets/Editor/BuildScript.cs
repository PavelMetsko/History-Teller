using System.IO;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace HistoryTeller.EditorTools
{
    /// <summary>
    /// Сборка в один клик: меню HistoryTeller → Build iOS (Xcode project).
    /// Результат — папка ios-build/ рядом с UnityProject; открыть Unity-iPhone.xcodeproj,
    /// выбрать Team в Signing и нажать Run.
    /// </summary>
    public static class BuildScript
    {
        private const string ScenePath = "Assets/Scenes/Main.unity";
        private const string BundleId = "com.pavel.historyteller";

        [MenuItem("HistoryTeller/Build iOS (Xcode project)")]
        public static void BuildIos()
        {
            EnsureScene();
            ApplyPlayerSettings();

            if (!EditorUserBuildSettings.SwitchActiveBuildTarget(
                    BuildTargetGroup.iOS, BuildTarget.iOS))
            {
                EditorUtility.DisplayDialog("History Teller",
                    "Не удалось переключиться на iOS. Установлен ли модуль iOS Build Support " +
                    "для этой версии Unity? (Unity Hub → Installs → ⚙ → Add modules)", "OK");
                return;
            }

            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = new[] { ScenePath },
                target = BuildTarget.iOS,
                locationPathName = "../ios-build"
            });

            if (report.summary.result == BuildResult.Succeeded)
                EditorUtility.RevealInFinder(
                    Path.GetFullPath("../ios-build/Unity-iPhone.xcodeproj"));
            else
                Debug.LogError("Build failed: " + report.summary.result);
        }

        [MenuItem("HistoryTeller/Apply Player Settings")]
        public static void ApplyPlayerSettings()
        {
            PlayerSettings.productName = "History Teller";
            PlayerSettings.companyName = "Pavel";
            PlayerSettings.SetApplicationIdentifier(BuildTargetGroup.iOS, BundleId);
            PlayerSettings.defaultInterfaceOrientation = UIOrientation.Portrait;
            PlayerSettings.iOS.targetDevice = iOSTargetDevice.iPhoneAndiPad;
            PlayerSettings.iOS.requiresFullScreen = true;
            Debug.Log("Player settings applied: " + BundleId);
        }

        [MenuItem("HistoryTeller/Create Main Scene")]
        public static void EnsureScene()
        {
            if (File.Exists(ScenePath)) return;
            Directory.CreateDirectory("Assets/Scenes");
            var scene = EditorSceneManager.NewScene(
                NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);
            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.Refresh();
            Debug.Log("Scene created: " + ScenePath);
        }
    }
}
