using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace HistoryTeller.Game
{
    /// <summary>Процедурные UI-ресурсы: скруглённый 9-slice спрайт, арт из Resources, палитра.</summary>
    public static class UiKit
    {
        private static Sprite _rounded;
        private static readonly Dictionary<string, Sprite> _artCache =
            new Dictionary<string, Sprite>();

        /// <summary>Спрайт из Resources/Art/{name}.png (портреты char_*, фоны scene_*). null если нет.</summary>
        public static Sprite LoadArt(string name)
        {
            if (_artCache.TryGetValue(name, out var cached)) return cached;
            var tex = Resources.Load<Texture2D>("Art/" + name);
            Sprite s = null;
            if (tex != null)
                s = Sprite.Create(tex, new Rect(0, 0, tex.width, tex.height),
                    new Vector2(0.5f, 0.5f), 100f);
            _artCache[name] = s;
            return s;
        }

        /// <summary>Скруглённый прямоугольник (9-slice) — генерируется один раз.</summary>
        public static Sprite Rounded
        {
            get
            {
                if (_rounded == null) _rounded = MakeRounded(64, 20);
                return _rounded;
            }
        }

        private static Sprite MakeRounded(int size, int radius)
        {
            var tex = new Texture2D(size, size, TextureFormat.ARGB32, false)
            {
                wrapMode = TextureWrapMode.Clamp,
                filterMode = FilterMode.Bilinear
            };
            var px = new Color32[size * size];
            for (int y = 0; y < size; y++)
            for (int x = 0; x < size; x++)
            {
                // расстояние до «внутреннего» прямоугольника
                float dx = Mathf.Max(radius - x, x - (size - 1 - radius), 0);
                float dy = Mathf.Max(radius - y, y - (size - 1 - radius), 0);
                float d = Mathf.Sqrt(dx * dx + dy * dy);
                float a = Mathf.Clamp01(radius - d + 0.5f); // 1px сглаживание
                px[y * size + x] = new Color32(255, 255, 255, (byte)(a * 255));
            }
            tex.SetPixels32(px);
            tex.Apply();
            var border = Vector4.one * (radius + 2);
            return Sprite.Create(tex, new Rect(0, 0, size, size),
                new Vector2(0.5f, 0.5f), 100f, 0, SpriteMeshType.FullRect, border);
        }

        /// <summary>Image со скруглёнными углами.</summary>
        public static Image RoundedImage(GameObject go, Color color)
        {
            var img = go.AddComponent<Image>();
            img.sprite = Rounded;
            img.type = Image.Type.Sliced;
            img.color = color;
            return img;
        }

        public static Color Hex(string hex)
        {
            ColorUtility.TryParseHtmlString(hex, out var c);
            return c;
        }

        /// <summary>Детерминированный цвет из id (заглушка вместо арта персонажей/сцен).</summary>
        public static Color IdColor(string id, float s, float v)
        {
            unchecked
            {
                int h = 17;
                foreach (char c in id) h = h * 31 + c;
                return Color.HSVToRGB(Mathf.Abs(h % 360) / 360f, s, v);
            }
        }
    }
}
