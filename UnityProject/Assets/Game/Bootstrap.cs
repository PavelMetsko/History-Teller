using UnityEngine;

namespace HistoryTeller.Game
{
    /// <summary>
    /// Вся игра поднимается из кода — сцену настраивать не нужно.
    /// Достаточно любой (в т.ч. пустой) сцены в Build Settings.
    /// </summary>
    public static class Bootstrap
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Boot()
        {
            if (Object.FindObjectOfType<GameController>() != null) return;
            Application.targetFrameRate = 60;

            // игра — только в landscape
            Screen.autorotateToPortrait = false;
            Screen.autorotateToPortraitUpsideDown = false;
            Screen.autorotateToLandscapeLeft = true;
            Screen.autorotateToLandscapeRight = true;
            Screen.orientation = ScreenOrientation.AutoRotation;

            var go = new GameObject("HistoryTeller");
            Object.DontDestroyOnLoad(go);
            go.AddComponent<GameController>();
        }
    }
}
