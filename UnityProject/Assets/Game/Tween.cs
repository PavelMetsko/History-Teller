using System.Collections;
using UnityEngine;

namespace HistoryTeller.Game
{
    /// <summary>Минимальные корутинные твины — без внешних зависимостей (DOTween и т.п.).</summary>
    public static class Tween
    {
        public static float OutCubic(float x) => 1f - Mathf.Pow(1f - x, 3f);

        public static float OutBack(float x)
        {
            const float c1 = 1.70158f, c3 = c1 + 1f;
            float t = x - 1f;
            return 1f + c3 * t * t * t + c1 * t * t;
        }

        public static IEnumerator Scale(Transform t, float from, float to, float dur,
            System.Func<float, float> ease = null)
        {
            ease = ease ?? OutBack;
            for (float e = 0; e < dur; e += Time.unscaledDeltaTime)
            {
                if (t == null) yield break;
                t.localScale = Vector3.one * Mathf.LerpUnclamped(from, to, ease(e / dur));
                yield return null;
            }
            if (t != null) t.localScale = Vector3.one * to;
        }

        public static IEnumerator Pulse(Transform t, float amp, float dur)
        {
            for (float e = 0; e < dur; e += Time.unscaledDeltaTime)
            {
                if (t == null) yield break;
                t.localScale = Vector3.one * (1f + amp * Mathf.Sin(Mathf.PI * (e / dur)));
                yield return null;
            }
            if (t != null) t.localScale = Vector3.one;
        }

        public static IEnumerator Shake(Transform t, float amp, float dur)
        {
            if (t == null) yield break;
            Vector3 basePos = t.localPosition;
            for (float e = 0; e < dur; e += Time.unscaledDeltaTime)
            {
                if (t == null) yield break;
                float damp = 1f - e / dur;
                t.localPosition = basePos + (Vector3)(Random.insideUnitCircle * amp * damp);
                yield return null;
            }
            if (t != null) t.localPosition = basePos;
        }

        public static IEnumerator Fade(CanvasGroup g, float from, float to, float dur)
        {
            for (float e = 0; e < dur; e += Time.unscaledDeltaTime)
            {
                if (g == null) yield break;
                g.alpha = Mathf.Lerp(from, to, OutCubic(e / dur));
                yield return null;
            }
            if (g != null) g.alpha = to;
        }

        /// <summary>Всплывающий и тающий текст (сердечко, кинжал и т.п.).</summary>
        public static IEnumerator FloatUp(Transform t, float distance, float dur)
        {
            if (t == null) yield break;
            Vector3 from = t.localPosition;
            var texts = t.GetComponentsInChildren<UnityEngine.UI.Text>();
            var self = t.GetComponent<UnityEngine.UI.Text>();
            for (float e = 0; e < dur; e += Time.unscaledDeltaTime)
            {
                if (t == null) yield break;
                float x = e / dur;
                t.localPosition = from + Vector3.up * (distance * OutCubic(x));
                float a = 1f - x * x;
                if (self != null) SetAlpha(self, a);
                foreach (var txt in texts) SetAlpha(txt, a);
                yield return null;
            }
            if (t != null) Object.Destroy(t.gameObject);
        }

        private static void SetAlpha(UnityEngine.UI.Text t, float a)
        {
            var c = t.color;
            c.a = a;
            t.color = c;
        }

        /// <summary>Универсальный «улетающий» элемент: сдвиг по anchoredPosition + затухание + масштаб.
        /// Используется для сердечек, искр, конфетти. По завершении уничтожает объект.</summary>
        public static IEnumerator Drift(GameObject go, Vector2 delta, float dur,
            float startScale = 1f, float endScale = 1f, float spin = 0f)
        {
            if (go == null) yield break;
            var rt = go.transform as RectTransform;
            // ВНИМАНИЕ: '??' не учитывает «уничтоженность» Unity-объектов — используем явную проверку
            var cg = go.GetComponent<CanvasGroup>();
            if (cg == null) cg = go.AddComponent<CanvasGroup>();
            Vector2 from = rt.anchoredPosition;
            float baseZ = rt.localEulerAngles.z;
            for (float e = 0; e < dur; e += Time.unscaledDeltaTime)
            {
                // объект (или его компоненты) могли быть уничтожены перерисовкой кадра
                if (go == null || rt == null || cg == null) yield break;
                float x = e / dur;
                rt.anchoredPosition = from + delta * OutCubic(x);
                rt.localScale = Vector3.one * Mathf.LerpUnclamped(startScale, endScale, OutCubic(x));
                if (spin != 0f) rt.localRotation = Quaternion.Euler(0, 0, baseZ + spin * x);
                cg.alpha = 1f - x * x;
                yield return null;
            }
            if (go != null) Object.Destroy(go);
        }
    }
}
