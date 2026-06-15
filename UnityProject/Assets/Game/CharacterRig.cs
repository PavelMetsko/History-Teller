using System.Collections;
using System.Collections.Generic;
using Newtonsoft.Json.Linq;
using UnityEngine;
using UnityEngine.UI;

namespace HistoryTeller.Game
{
    /// <summary>
    /// Кукольный риг персонажа: собирает фигуру из слоёв-частей (back_arm/body/front_arm/head…)
    /// по манифесту Resources/Art/rig/&lt;id&gt;/rig.json и проигрывает анимации взаимодействия,
    /// вращая части вокруг их пивотов. Арт подменяемый — движок от него не зависит.
    ///
    /// Если рига для персонажа нет (нет rig.json) — Build вернёт null, и вызывающий код
    /// должен откатиться на плоский портрет.
    /// </summary>
    public sealed class CharacterRig : MonoBehaviour
    {
        private readonly Dictionary<string, RectTransform> _parts =
            new Dictionary<string, RectTransform>();
        private float _size;
        private Coroutine _idle;

        public RectTransform Part(string name) =>
            _parts.TryGetValue(name, out var p) ? p : null;

        // ---------- сборка ----------

        /// <summary>Собирает риг под parent. size — сторона квадрата фигуры в px UI.
        /// Возвращает компонент или null, если нет арта рига.</summary>
        public static CharacterRig Build(Transform parent, string charId, float size)
        {
            var manifest = Resources.Load<TextAsset>($"Art/rig/{charId}/rig");
            if (manifest == null) return null;

            JObject obj;
            try { obj = JObject.Parse(manifest.text); }
            catch { return null; }

            var root = new GameObject("Rig_" + charId, typeof(RectTransform));
            root.transform.SetParent(parent, false);
            var rrt = (RectTransform)root.transform;
            rrt.anchorMin = rrt.anchorMax = new Vector2(0.5f, 0.5f);
            rrt.pivot = new Vector2(0.5f, 0.5f);
            rrt.sizeDelta = new Vector2(size, size);
            rrt.anchoredPosition = Vector2.zero;

            var rig = root.AddComponent<CharacterRig>();
            rig._size = size;

            var parts = (JArray)obj["parts"] ?? new JArray();
            // порядок отрисовки задаётся z (по возрастанию = сзади→вперёд = порядок в иерархии)
            var ordered = new List<JToken>(parts);
            ordered.Sort((a, b) => ((int?)a["z"] ?? 0).CompareTo((int?)b["z"] ?? 0));

            foreach (var pt in ordered)
            {
                string name = (string)pt["name"];
                if (string.IsNullOrEmpty(name)) continue;
                var tex = Resources.Load<Texture2D>($"Art/rig/{charId}/{name}");
                if (tex == null) continue;

                // пивот из манифеста (нормализованный, от левого-верха). По умолчанию центр.
                var pv = pt["pivot"] as JArray;
                float px = pv != null ? (float)pv[0] : 0.5f;
                float pyTop = pv != null ? (float)pv[1] : 0.5f;
                // UI-пивот считается от низа → инвертируем Y
                Vector2 uiPivot = new Vector2(px, 1f - pyTop);

                var go = new GameObject(name, typeof(RectTransform));
                go.transform.SetParent(root.transform, false);
                var rt = (RectTransform)go.transform;
                rt.anchorMin = rt.anchorMax = new Vector2(0.5f, 0.5f);
                rt.pivot = uiPivot;
                rt.sizeDelta = new Vector2(size, size);
                // сместить рект так, чтобы кадр (size) был отцентрован в контейнере при смещённом пивоте
                rt.anchoredPosition = new Vector2((uiPivot.x - 0.5f) * size, (uiPivot.y - 0.5f) * size);

                var img = go.AddComponent<Image>();
                img.sprite = Sprite.Create(tex, new Rect(0, 0, tex.width, tex.height),
                    new Vector2(0.5f, 0.5f), 100f);
                img.raycastTarget = false;
                img.preserveAspect = true;

                rig._parts[name] = rt;
            }

            if (rig._parts.Count == 0) { Destroy(root); return null; }
            rig._idle = rig.StartCoroutine(rig.IdleLoop());
            return rig;
        }

        // ---------- базовые анимации ----------

        private static float Ease(float x) => 1f - Mathf.Pow(1f - x, 3f);

        /// <summary>Лёгкое «дыхание» в покое: голова и корпус чуть качаются.</summary>
        private IEnumerator IdleLoop()
        {
            var head = Part("head");
            var body = Part("body");
            float t = Random.Range(0f, 6f);
            while (true)
            {
                t += Time.unscaledDeltaTime;
                float s = Mathf.Sin(t * 1.6f);
                if (head != null) head.localRotation = Quaternion.Euler(0, 0, s * 2.2f);
                if (body != null) body.localScale = new Vector3(1f, 1f + s * 0.012f, 1f);
                yield return null;
            }
        }

        public void StopIdle()
        {
            if (_idle != null) { StopCoroutine(_idle); _idle = null; }
            var head = Part("head"); if (head != null) head.localRotation = Quaternion.identity;
            var body = Part("body"); if (body != null) body.localScale = Vector3.one;
        }

        /// <summary>Повернуть часть к целевому углу за dur (с возвратом idle потом — на усмотрение вызова).</summary>
        public IEnumerator RotatePart(string name, float toDeg, float dur)
        {
            var p = Part(name);
            if (p == null) yield break;
            float from = NormAngle(p.localEulerAngles.z);
            for (float e = 0; e < dur; e += Time.unscaledDeltaTime)
            {
                if (p == null) yield break;
                p.localRotation = Quaternion.Euler(0, 0, Mathf.LerpAngle(from, toDeg, Ease(e / dur)));
                yield return null;
            }
            if (p != null) p.localRotation = Quaternion.Euler(0, 0, toDeg);
        }

        private static float NormAngle(float a) { a %= 360f; if (a > 180f) a -= 360f; return a; }

        /// <summary>Наклон всей фигуры к собеседнику. dir: -1 влево, +1 вправо.</summary>
        public IEnumerator LeanToward(float dir, float angle = 12f, float dur = 0.35f)
        {
            StopIdle();
            yield return RotatePart("body", -dir * angle, dur);
        }

        /// <summary>Кивок головой (наклон вперёд-к собеседнику и обратно).</summary>
        public IEnumerator HeadTilt(float dir, float angle = 14f, float dur = 0.3f)
        {
            StopIdle();
            yield return RotatePart("head", -dir * angle, dur);
        }

        /// <summary>Поднять ближнюю руку (потянуться/поднести). dir задаёт сторону взмаха.</summary>
        public IEnumerator RaiseFrontArm(float dir, float angle = 55f, float dur = 0.3f)
        {
            yield return RotatePart("front_arm", dir * angle, dur);
        }

        /// <summary>Вернуть всё в нейтраль и снова запустить idle.</summary>
        public IEnumerator Relax(float dur = 0.3f)
        {
            var co1 = StartCoroutine(RotatePart("body", 0f, dur));
            var co2 = StartCoroutine(RotatePart("head", 0f, dur));
            var co3 = StartCoroutine(RotatePart("front_arm", 0f, dur));
            yield return co1; yield return co2; yield return co3;
            if (_idle == null) _idle = StartCoroutine(IdleLoop());
        }

        /// <summary>Появление в кадре: подскок снизу с лёгким перелётом.</summary>
        public IEnumerator BounceIn(float dur = 0.4f)
        {
            var rt = (RectTransform)transform;
            Vector2 baseP = rt.anchoredPosition;
            rt.localScale = Vector3.one * 0.6f;
            for (float e = 0; e < dur; e += Time.unscaledDeltaTime)
            {
                float x = e / dur;
                rt.anchoredPosition = baseP + Vector2.down * (40f * (1f - Ease(x)));
                rt.localScale = Vector3.one * Mathf.LerpUnclamped(0.6f, 1f, Tween.OutBack(x));
                yield return null;
            }
            rt.anchoredPosition = baseP;
            rt.localScale = Vector3.one;
        }
    }
}
