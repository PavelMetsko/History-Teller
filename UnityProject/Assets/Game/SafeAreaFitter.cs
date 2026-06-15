using UnityEngine;

namespace HistoryTeller.Game
{
    /// <summary>Вписывает RectTransform в Screen.safeArea (чёлка iPhone в landscape).</summary>
    public sealed class SafeAreaFitter : MonoBehaviour
    {
        private Rect _last = Rect.zero;

        private void Update()
        {
            var sa = Screen.safeArea;
            if (sa == _last) return;
            _last = sa;

            var rt = (RectTransform)transform;
            var min = sa.position;
            var max = sa.position + sa.size;
            min.x /= Screen.width;
            min.y /= Screen.height;
            max.x /= Screen.width;
            max.y /= Screen.height;
            rt.anchorMin = min;
            rt.anchorMax = max;
            rt.offsetMin = Vector2.zero;
            rt.offsetMax = Vector2.zero;
        }
    }
}
