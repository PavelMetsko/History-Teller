using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using HistoryTeller.Simulation;

namespace HistoryTeller.Game
{
    /// <summary>
    /// Прототипный UI (uGUI, целиком из кода): панели, трей сцен/персонажей,
    /// tap-управление как в HTML-прототипе, оверлей с исторической справкой.
    /// Арт-заглушки: цветные плитки с инициалами. Шлифовка UI — следующий этап.
    /// </summary>
    public sealed class GameController : MonoBehaviour
    {
        // ---- контент/состояние ----
        private ContentDb _db;
        private List<LevelDef> _levels;
        private int _levelIdx;
        private List<Panel> _panels = new List<Panel>();
        private string _selScene, _selChar;
        private bool _solvedShown;

        // ---- UI ----
        private Font _font;
        private Text _title, _subtitle, _given, _hintText;
        private Button _prevBtn, _nextBtn;
        private Transform _panelsRow, _sceneChips, _charChips;
        private GameObject _overlay, _nextLevelBtn;
        private Text _accText, _factText, _srcText;
        private Image _accBg;
        private float _hintUntil;

        private static readonly Color ColBg = Hex("#1d1a16");
        private static readonly Color ColPanel = Hex("#2b2620");
        private static readonly Color ColPaper = Hex("#efe6d4");
        private static readonly Color ColInk = Hex("#2b2620");
        private static readonly Color ColAccent = Hex("#c8a356");
        private static readonly Color ColMuted = Hex("#8a8074");

        private void Start()
        {
            _font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            var loaded = ContentSource.LoadEpoch("rome");
            _db = loaded.Db;
            _levels = loaded.Levels;
            BuildUi();
            ResetLevel();
        }

        private void Update()
        {
            if (_hintUntil > 0f && Time.unscaledTime > _hintUntil)
            {
                _hintUntil = 0f;
                _hintText.text = "";
            }
        }

        private LevelDef Lv => _levels[_levelIdx];

        // ================= СТАТИЧНЫЙ КАРКАС =================

        private void BuildUi()
        {
            var canvasGo = new GameObject("Canvas",
                typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
            canvasGo.transform.SetParent(transform, false);
            var canvas = canvasGo.GetComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            var scaler = canvasGo.GetComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(750, 1334);
            scaler.matchWidthOrHeight = 0.5f;

            if (FindObjectOfType<EventSystem>() == null)
                new GameObject("EventSystem",
                    typeof(EventSystem), typeof(StandaloneInputModule));

            // фон
            var bg = NewUi("Bg", canvasGo.transform);
            Stretch(bg);
            bg.gameObject.AddComponent<Image>().color = ColBg;

            // корневая колонка
            var root = NewUi("Root", canvasGo.transform);
            Stretch(root);
            var rootCol = root.gameObject.AddComponent<VerticalLayoutGroup>();
            rootCol.padding = new RectOffset(16, 16, 50, 24);
            rootCol.spacing = 10;
            rootCol.childAlignment = TextAnchor.UpperCenter;
            rootCol.childControlWidth = true;
            rootCol.childControlHeight = true;
            rootCol.childForceExpandWidth = true;
            rootCol.childForceExpandHeight = false;

            // шапка: ‹ заголовок ›
            var header = Row(root, 64, 8);
            _prevBtn = AddButton(header, "‹", () => Nav(-1), ColPanel, ColPaper, 84, 64, 40);
            _title = AddText(header, "", 34, ColAccent, TextAnchor.MiddleCenter, FontStyle.BoldAndItalic);
            _title.resizeTextForBestFit = true;
            _title.resizeTextMinSize = 20;
            _title.resizeTextMaxSize = 34;
            _title.gameObject.AddComponent<LayoutElement>().flexibleWidth = 1;
            _nextBtn = AddButton(header, "›", () => Nav(+1), ColPanel, ColPaper, 84, 64, 40);

            _subtitle = AddText(root, "", 20, ColMuted, TextAnchor.MiddleCenter);
            _subtitle.gameObject.AddComponent<LayoutElement>().preferredHeight = 26;
            _given = AddText(root, "", 20, ColAccent, TextAnchor.MiddleCenter);
            _given.gameObject.AddComponent<LayoutElement>().preferredHeight = 24;

            // ряд панелей
            var panelsGo = NewUi("Panels", root);
            var panelsLe = panelsGo.gameObject.AddComponent<LayoutElement>();
            panelsLe.preferredHeight = 330;
            var panelsRow = panelsGo.gameObject.AddComponent<HorizontalLayoutGroup>();
            panelsRow.spacing = 12;
            panelsRow.childAlignment = TextAnchor.MiddleCenter;
            panelsRow.childControlWidth = false;
            panelsRow.childControlHeight = false;
            panelsRow.childForceExpandWidth = false;
            panelsRow.childForceExpandHeight = false;
            _panelsRow = panelsGo;

            // трей сцен
            AddText(root, "СЦЕНЫ", 18, ColMuted, TextAnchor.MiddleLeft)
                .gameObject.AddComponent<LayoutElement>().preferredHeight = 24;
            _sceneChips = Chips(root);

            // трей персонажей
            AddText(root, "ПЕРСОНАЖИ", 18, ColMuted, TextAnchor.MiddleLeft)
                .gameObject.AddComponent<LayoutElement>().preferredHeight = 24;
            _charChips = Chips(root);

            // кнопки
            var actions = Row(root, 66, 12);
            actions.GetComponent<HorizontalLayoutGroup>().childAlignment = TextAnchor.MiddleCenter;
            AddButton(actions, "Сбросить", ResetLevel, ColPanel, ColPaper, 220, 66, 24);
            AddButton(actions, "Подсказка", ShowSolutionHint, ColPanel, ColPaper, 220, 66, 24);

            _hintText = AddText(root, "", 22, ColAccent, TextAnchor.MiddleCenter);
            _hintText.gameObject.AddComponent<LayoutElement>().preferredHeight = 30;

            BuildOverlay(canvasGo.transform);
        }

        private void BuildOverlay(Transform canvas)
        {
            _overlay = NewUi("Overlay", canvas).gameObject;
            Stretch(_overlay.transform);
            var dim = _overlay.AddComponent<Image>();
            dim.color = new Color(0.06f, 0.05f, 0.04f, 0.84f);

            var card = NewUi("Card", _overlay.transform);
            var cardRt = (RectTransform)card;
            cardRt.sizeDelta = new Vector2(640, 0);
            card.gameObject.AddComponent<Image>().color = ColPaper;
            var col = card.gameObject.AddComponent<VerticalLayoutGroup>();
            col.padding = new RectOffset(28, 28, 26, 22);
            col.spacing = 12;
            col.childControlWidth = true;
            col.childControlHeight = true;
            col.childForceExpandWidth = true;
            col.childForceExpandHeight = false;
            card.gameObject.AddComponent<ContentSizeFitter>()
                .verticalFit = ContentSizeFitter.FitMode.PreferredSize;

            var winTitle = AddText(card, "Решено!", 34, Hex("#7a5c1e"),
                TextAnchor.MiddleLeft, FontStyle.BoldAndItalic);
            winTitle.gameObject.AddComponent<LayoutElement>().preferredHeight = 42;

            var accGo = NewUi("Acc", card);
            accGo.gameObject.AddComponent<LayoutElement>().preferredHeight = 36;
            _accBg = accGo.gameObject.AddComponent<Image>();
            _accText = AddText(accGo, "", 20, Color.white, TextAnchor.MiddleCenter, FontStyle.Bold);
            Stretch(_accText.transform);

            _factText = AddText(card, "", 24, ColInk, TextAnchor.UpperLeft);
            _srcText = AddText(card, "", 20, Hex("#6d6252"), TextAnchor.MiddleLeft, FontStyle.Italic);
            _srcText.gameObject.AddComponent<LayoutElement>().preferredHeight = 28;

            var btns = Row(card, 64, 12);
            AddButton(btns, "Ещё раз", () => { _overlay.SetActive(false); ResetLevel(); },
                Hex("#3a3122"), ColPaper, 200, 64, 24);
            _nextLevelBtn = AddButton(btns, "Дальше →", () =>
            {
                _overlay.SetActive(false);
                if (_levelIdx < _levels.Count - 1) { _levelIdx++; ResetLevel(); }
            }, Hex("#3a3122"), ColPaper, 200, 64, 24).gameObject;

            _overlay.SetActive(false);
        }

        // ================= ИГРОВАЯ ЛОГИКА =================

        private void Nav(int d)
        {
            int next = _levelIdx + d;
            if (next < 0 || next >= _levels.Count) return;
            _levelIdx = next;
            ResetLevel();
        }

        private void ResetLevel()
        {
            _panels = Enumerable.Range(0, Lv.Panels).Select(_ => new Panel()).ToList();
            _selScene = _selChar = null;
            _solvedShown = false;
            if (_overlay != null) _overlay.SetActive(false);
            Flash("");
            Render();
        }

        private void OnPanelTapped(int i)
        {
            var p = _panels[i];
            if (_selScene != null)
            {
                p.SceneId = _selScene;
                p.Characters.RemoveRange(0,
                    Mathf.Max(0, p.Characters.Count - _db.Scenes[_selScene].Slots));
                _selScene = null;
            }
            else if (_selChar != null)
            {
                if (p.SceneId == null) { Flash("Сначала поместите сцену в панель"); return; }
                if (p.Characters.Contains(_selChar)) { Flash("Этот персонаж уже здесь"); return; }
                if (p.Characters.Count >= _db.Scenes[p.SceneId].Slots)
                { Flash("В этой сцене нет места"); return; }
                p.Characters.Add(_selChar);
            }
            else return;
            Render();
        }

        private void RemoveChar(int panelIdx, string charId)
        {
            _panels[panelIdx].Characters.Remove(charId);
            Render();
        }

        private void ClearPanel(int panelIdx)
        {
            _panels[panelIdx] = new Panel();
            Render();
        }

        private void ShowSolutionHint()
        {
            List<string> sceneIds = null;
            if (Lv.Solution != null)
                sceneIds = Lv.Solution.Select(p => p.SceneId).ToList();
            else
            {
                var res = Solver.Solve(Lv, _db, 1);
                if (res.IsSolvable)
                    sceneIds = res.Solutions[0].Select(p => p.SceneId).ToList();
            }
            Flash(sceneIds == null
                ? "Решений нет — баг контента!"
                : "Порядок сцен: " + string.Join(" → ", sceneIds.Select(s => _db.Scenes[s].Name)));
        }

        private void Flash(string msg)
        {
            _hintText.text = msg;
            _hintUntil = string.IsNullOrEmpty(msg) ? 0f : Time.unscaledTime + 2.6f;
        }

        private void CheckWin(World world)
        {
            if (_solvedShown || !Lv.Goal.IsMet(world)) return;
            _solvedShown = true;
            var fc = Lv.FactCard;
            string acc = fc?.Accuracy ?? "fact";
            _accText.text = acc == "fact" ? "ФАКТ" : acc == "legend" ? "ЛЕГЕНДА" : "УПРОЩЕНИЕ";
            _accBg.color = acc == "fact" ? Hex("#4e7a3a") : acc == "legend" ? Hex("#8a4a8a") : Hex("#a07a2a");
            _factText.text = fc?.Text ?? "";
            _srcText.text = fc != null ? "— " + fc.Source : "";
            _nextLevelBtn.SetActive(_levelIdx < _levels.Count - 1);
            _overlay.SetActive(true);
        }

        // ================= РЕНДЕР =================

        private void Render()
        {
            _title.text = "«" + Lv.Title + "»";
            _subtitle.text = $"Уровень {_levelIdx + 1} из {_levels.Count} · соберите историю по заголовку";
            _given.text = Lv.InitialText ?? "";
            _prevBtn.interactable = _levelIdx > 0;
            _nextBtn.interactable = _levelIdx < _levels.Count - 1;

            var snapshots = new List<World>();
            var world = Engine.Simulate(_panels, _db, null, Lv.CreateInitialWorld(), snapshots);

            RenderPanels(snapshots);
            RenderChips();
            CheckWin(world);
        }

        private void RenderPanels(List<World> snapshots)
        {
            ClearChildren(_panelsRow);
            float w = Mathf.Min(225f, (750f - 32f - 12f * (Lv.Panels - 1)) / Lv.Panels);

            for (int i = 0; i < _panels.Count; i++)
            {
                int idx = i;
                var p = _panels[i];
                var snap = i < snapshots.Count ? snapshots[i] : new World();

                var panel = NewUi("Panel" + i, _panelsRow);
                ((RectTransform)panel).sizeDelta = new Vector2(w, 320);
                panel.gameObject.AddComponent<Image>().color = ColPaper;
                var btn = panel.gameObject.AddComponent<Button>();
                btn.onClick.AddListener(() => OnPanelTapped(idx));

                var col = panel.gameObject.AddComponent<VerticalLayoutGroup>();
                col.padding = new RectOffset(8, 8, 8, 8);
                col.spacing = 6;
                col.childControlWidth = true;
                col.childControlHeight = true;
                col.childForceExpandWidth = true;
                col.childForceExpandHeight = false;

                // шапка панели: номер + сцена + ✕
                var head = Row(panel, 44, 6);
                var num = AddText(head, (i + 1).ToString(), 22, ColAccent,
                    TextAnchor.MiddleCenter, FontStyle.Bold);
                num.gameObject.AddComponent<LayoutElement>().preferredWidth = 28;
                var sceneName = AddText(head,
                    p.SceneId != null ? _db.Scenes[p.SceneId].Name : "сцена?",
                    22, p.SceneId != null ? ColInk : Hex("#a4977e"),
                    TextAnchor.MiddleCenter,
                    p.SceneId != null ? FontStyle.Bold : FontStyle.Italic);
                sceneName.resizeTextForBestFit = true;
                sceneName.resizeTextMinSize = 14;
                sceneName.resizeTextMaxSize = 22;
                sceneName.gameObject.AddComponent<LayoutElement>().flexibleWidth = 1;
                if (p.SceneId != null || p.Characters.Count > 0)
                    AddButton(head, "×", () => ClearPanel(idx), Hex("#bb5555"), Color.white, 36, 36, 22);

                // полоса-цвет сцены
                var stripe = NewUi("Stripe", panel);
                stripe.gameObject.AddComponent<LayoutElement>().preferredHeight = 8;
                stripe.gameObject.AddComponent<Image>().color =
                    p.SceneId != null ? IdColor(p.SceneId, 0.55f, 0.65f) : Hex("#d9cdb4");

                // персонажи
                var charsGo = NewUi("Chars", panel);
                charsGo.gameObject.AddComponent<LayoutElement>().flexibleHeight = 1;
                var grid = charsGo.gameObject.AddComponent<GridLayoutGroup>();
                grid.cellSize = new Vector2((w - 24f) / 2f, 108);
                grid.spacing = new Vector2(6, 6);
                grid.childAlignment = TextAnchor.UpperCenter;

                foreach (var c in p.Characters)
                {
                    string charId = c;
                    var def = _db.Characters[c];
                    bool dead = snap.HasFlag(c, World.DeadFlag);

                    var tile = NewUi("Char_" + c, charsGo);
                    var tileImg = tile.gameObject.AddComponent<Image>();
                    tileImg.color = dead ? Hex("#9a9a92") : IdColor(c, 0.45f, 0.85f);
                    tile.gameObject.AddComponent<Button>()
                        .onClick.AddListener(() => RemoveChar(idx, charId));

                    var tcol = tile.gameObject.AddComponent<VerticalLayoutGroup>();
                    tcol.padding = new RectOffset(4, 4, 4, 4);
                    tcol.childControlWidth = true;
                    tcol.childControlHeight = true;
                    tcol.childForceExpandWidth = true;
                    tcol.childForceExpandHeight = false;

                    var badge = AddText(tile, BadgeText(snap, c, p.Characters), 15,
                        Hex("#5d2020"), TextAnchor.MiddleCenter, FontStyle.Bold);
                    badge.gameObject.AddComponent<LayoutElement>().preferredHeight = 20;

                    var init = AddText(tile, Initials(def.Name), 34, ColInk,
                        TextAnchor.MiddleCenter, FontStyle.Bold);
                    init.gameObject.AddComponent<LayoutElement>().flexibleHeight = 1;

                    var nm = AddText(tile, def.Name, 15, ColInk, TextAnchor.MiddleCenter);
                    nm.resizeTextForBestFit = true;
                    nm.resizeTextMinSize = 10;
                    nm.resizeTextMaxSize = 15;
                    nm.gameObject.AddComponent<LayoutElement>().preferredHeight = 22;
                }

                // слоты
                var slots = AddText(panel,
                    p.SceneId != null
                        ? $"{p.Characters.Count} / {_db.Scenes[p.SceneId].Slots}" : "",
                    16, Hex("#a4977e"), TextAnchor.MiddleCenter);
                slots.gameObject.AddComponent<LayoutElement>().preferredHeight = 20;
            }
        }

        private void RenderChips()
        {
            ClearChildren(_sceneChips);
            foreach (var sid in Lv.Scenes)
            {
                string id = sid;
                bool sel = _selScene == sid;
                MakeChip(_sceneChips, _db.Scenes[sid].Name, IdColor(sid, 0.55f, 0.45f), sel,
                    () => { _selScene = sel ? null : id; _selChar = null; Render(); });
            }

            ClearChildren(_charChips);
            foreach (var cid in Lv.Characters)
            {
                string id = cid;
                bool sel = _selChar == cid;
                MakeChip(_charChips, _db.Characters[cid].Name, IdColor(cid, 0.45f, 0.5f), sel,
                    () => { _selChar = sel ? null : id; _selScene = null; Render(); });
            }

            FitChips(_sceneChips, Lv.Scenes.Count);
            FitChips(_charChips, Lv.Characters.Count);
        }

        private void MakeChip(Transform parent, string label, Color baseCol, bool selected,
            UnityEngine.Events.UnityAction onClick)
        {
            var chip = NewUi("Chip_" + label, parent);
            var img = chip.gameObject.AddComponent<Image>();
            img.color = selected ? ColAccent : baseCol;
            chip.gameObject.AddComponent<Button>().onClick.AddListener(onClick);
            var t = AddText(chip, label, 22, selected ? ColInk : ColPaper,
                TextAnchor.MiddleCenter, selected ? FontStyle.Bold : FontStyle.Normal);
            Stretch(t.transform);
            t.resizeTextForBestFit = true;
            t.resizeTextMinSize = 14;
            t.resizeTextMaxSize = 22;
        }

        private string BadgeText(World snap, string c, List<string> present)
        {
            if (snap.HasFlag(c, World.DeadFlag)) return "МЁРТВ";
            var parts = new List<string>();
            if (snap.HasFlag(c, "crowned")) parts.Add("корона");
            if (snap.HasFlag(c, "plotting")) parts.Add("заговор");
            foreach (var o in present)
                if (o != c && snap.HasRelation("loves", c, o)) { parts.Add("любовь"); break; }
            foreach (var o in present)
                if (o != c && snap.HasRelation("envies", c, o)) { parts.Add("зависть"); break; }
            if (parts.Count == 0)
                foreach (var o in present)
                    if (o != c && snap.HasRelation("ally_of", c, o)) { parts.Add("союз"); break; }
            return string.Join("·", parts.Take(2));
        }

        // ================= UI-ХЕЛПЕРЫ =================

        private static Transform NewUi(string name, Transform parent)
        {
            var go = new GameObject(name, typeof(RectTransform));
            go.transform.SetParent(parent, false);
            return go.transform;
        }

        private static void Stretch(Transform t)
        {
            var rt = (RectTransform)t;
            rt.anchorMin = Vector2.zero;
            rt.anchorMax = Vector2.one;
            rt.offsetMin = Vector2.zero;
            rt.offsetMax = Vector2.zero;
        }

        private static Transform Row(Transform parent, float height, float spacing)
        {
            var go = NewUi("Row", parent);
            go.gameObject.AddComponent<LayoutElement>().preferredHeight = height;
            var row = go.gameObject.AddComponent<HorizontalLayoutGroup>();
            row.spacing = spacing;
            row.childControlWidth = false;
            row.childControlHeight = true;
            row.childForceExpandWidth = false;
            row.childForceExpandHeight = true;
            row.childAlignment = TextAnchor.MiddleCenter;
            return go;
        }

        private static Transform Chips(Transform parent)
        {
            var go = NewUi("Chips", parent);
            go.gameObject.AddComponent<LayoutElement>(); // высота задаётся в FitChips
            var grid = go.gameObject.AddComponent<GridLayoutGroup>();
            grid.cellSize = new Vector2(228, 60);
            grid.spacing = new Vector2(10, 10);
            grid.childAlignment = TextAnchor.MiddleCenter;
            return go;
        }

        /// <summary>GridLayoutGroup не сообщает высоту родителю — считаем сами (3 чипа в ряд).</summary>
        private static void FitChips(Transform chips, int count)
        {
            int rows = Mathf.Max(1, Mathf.CeilToInt(count / 3f));
            chips.GetComponent<LayoutElement>().preferredHeight = rows * 60 + (rows - 1) * 10;
        }

        private Text AddText(Transform parent, string text, int size, Color color,
            TextAnchor align, FontStyle style = FontStyle.Normal)
        {
            var go = NewUi("Text", parent);
            var t = go.gameObject.AddComponent<Text>();
            t.font = _font;
            t.text = text;
            t.fontSize = size;
            t.color = color;
            t.alignment = align;
            t.fontStyle = style;
            t.horizontalOverflow = HorizontalWrapMode.Wrap;
            t.verticalOverflow = VerticalWrapMode.Overflow;
            t.raycastTarget = false;
            return t;
        }

        private Button AddButton(Transform parent, string label,
            UnityEngine.Events.UnityAction onClick, Color bg, Color fg,
            float width, float height, int fontSize)
        {
            var go = NewUi("Btn_" + label, parent);
            var le = go.gameObject.AddComponent<LayoutElement>();
            le.preferredWidth = width;
            le.preferredHeight = height;
            var img = go.gameObject.AddComponent<Image>();
            img.color = bg;
            var btn = go.gameObject.AddComponent<Button>();
            btn.onClick.AddListener(onClick);
            var t = AddText(go, label, fontSize, fg, TextAnchor.MiddleCenter);
            Stretch(t.transform);
            return btn;
        }

        private static void ClearChildren(Transform t)
        {
            for (int i = t.childCount - 1; i >= 0; i--)
                Destroy(t.GetChild(i).gameObject);
        }

        /// <summary>Детерминированный цвет из id (заглушка вместо арта).</summary>
        private static Color IdColor(string id, float s, float v)
        {
            unchecked
            {
                int h = 17;
                foreach (char c in id) h = h * 31 + c;
                float hue = Mathf.Abs(h % 360) / 360f;
                return Color.HSVToRGB(hue, s, v);
            }
        }

        private static string Initials(string name)
        {
            var words = name.Split(' ');
            return words.Length >= 2
                ? char.ToUpper(words[0][0]).ToString() + char.ToUpper(words[words.Length - 1][0])
                : name.Substring(0, Mathf.Min(2, name.Length)).ToUpper();
        }

        private static Color Hex(string hex)
        {
            ColorUtility.TryParseHtmlString(hex, out var c);
            return c;
        }
    }
}
