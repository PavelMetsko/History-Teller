using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using HistoryTeller.Simulation;

namespace HistoryTeller.Game
{
    /// <summary>
    /// «Книжный» стиль: один пергаментный лист на тёмном фоне, тонкие сепия-рамки,
    /// боковой трей с миниатюрами, выбор уровня — страница главы со списком.
    /// Меню → Глава → Игра → Победа. Всё из кода, ручные якоря.
    /// </summary>
    public sealed class GameController : MonoBehaviour
    {
        private enum AppScreen { Menu, Select, Game }

        // ---- контент/состояние ----
        private ContentDb _db;
        private List<LevelDef> _levels;
        private int _levelIdx;
        private List<Panel> _panels = new List<Panel>();
        private string _selScene, _selChar;
        private bool _solvedShown;
        private string _tutorialText = "";

        // ---- экраны ----
        private GameObject _menuRoot, _selectRoot, _gameRoot, _settingsRoot;
        private Transform _selectList;
        private Text _soundBtnLabel, _resetBtnLabel;
        private bool _resetArmed;

        // ---- игровой экран ----
        private Font _font;
        private Text _title, _info, _hintText, _goalLine;
        private Image _goalBox;
        private Transform _panelsRow, _trayScenes, _trayChars;
        private CanvasGroup _gameGroup, _overlayGroup;
        private Transform _canvasT;
        private GameObject _overlay, _nextLevelBtn;
        private Transform _card;
        private Text _accText, _factText, _srcText;
        private Image _accBg;
        private float _hintUntil;

        private readonly List<Transform> _panelViews = new List<Transform>();
        private readonly List<Dictionary<string, Transform>> _tileMap =
            new List<Dictionary<string, Transform>>();
        // риги персонажей по ключу "panelIdx:charId" (для анимаций взаимодействия)
        private readonly Dictionary<string, CharacterRig> _rigs =
            new Dictionary<string, CharacterRig>();

        // ---- палитра «старая книга» ----
        private static readonly Color ColBgDark = UiKit.Hex("#241a12");   // вокруг листа
        private static readonly Color ColPage = UiKit.Hex("#e9d9b6");     // лист
        private static readonly Color ColPanelPaper = UiKit.Hex("#f2e7ca");
        private static readonly Color ColSepia = UiKit.Hex("#8a6a48");    // линии рамок
        private static readonly Color ColInkText = UiKit.Hex("#4a3622");  // текст
        private static readonly Color ColAccent = UiKit.Hex("#a8762a");
        private static readonly Color ColMuted = UiKit.Hex("#9b8266");
        private static readonly Color ColBtn = UiKit.Hex("#6e4f33");      // кнопки
        private static readonly Color ColBtnText = UiKit.Hex("#f2e7ca");

        private static readonly Dictionary<string, string> RuleLabel =
            new Dictionary<string, string>
            {
                { "befriend", "союз" }, { "conspire", "заговор" }, { "charm", "любовь" },
                { "rivals", "зависть" }, { "betrayal_kill", "убит!" },
                { "battle_justice", "возмездие" }, { "offer_crown", "корона" },
                { "smuggle", "тайно" }, { "conquer", "разгром" },
                { "back_ruler", "поддержка Рима" }, { "enthrone", "на трон" }
            };

        private void Start()
        {
            _font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            var loaded = ContentSource.LoadEpoch("rome");
            _db = loaded.Db;
            _levels = loaded.Levels;
            Sfx.Enabled = SaveSystem.Get().SoundOn;
            BuildUi();
            ShowScreen(AppScreen.Menu);
            Music.Play();
        }

        private void Update()
        {
            if (_hintUntil > 0f && Time.unscaledTime > _hintUntil)
            {
                _hintUntil = 0f;
                _hintText.text = _tutorialText;
            }
        }

        private LevelDef Lv => _levels[_levelIdx];

        private bool IsUnlocked(int i) =>
            i == 0 || SaveSystem.IsCompleted(_levels[i - 1].Id);

        // ================= КАРКАС =================

        private void BuildUi()
        {
            var canvasGo = new GameObject("Canvas",
                typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
            canvasGo.transform.SetParent(transform, false);
            canvasGo.GetComponent<Canvas>().renderMode = RenderMode.ScreenSpaceOverlay;
            var scaler = canvasGo.GetComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1624, 750);
            scaler.matchWidthOrHeight = 1f;
            _canvasT = canvasGo.transform;

            if (FindObjectOfType<EventSystem>() == null)
                new GameObject("EventSystem",
                    typeof(EventSystem), typeof(StandaloneInputModule));

            // тьма вокруг книги
            var bg = NewUi("Bg", _canvasT);
            Stretch(bg);
            bg.gameObject.AddComponent<Image>().color = ColBgDark;

            // пергаментный лист (в safe area)
            var pageHolder = NewUi("PageHolder", _canvasT);
            Stretch(pageHolder);
            pageHolder.gameObject.AddComponent<SafeAreaFitter>();
            var page = NewUi("Page", pageHolder);
            Anchor(page, Vector2.zero, Vector2.one, new Vector2(10, 10), new Vector2(-10, -10));
            var paper = UiKit.LoadArt("paper");
            var pageImg = page.gameObject.AddComponent<Image>();
            if (paper != null) pageImg.sprite = paper;
            pageImg.color = paper != null ? Color.white : ColPage;

            BuildMenu();
            BuildSelect();
            BuildGameScreen();
            BuildWinOverlay();
            BuildSettings();
        }

        private void ShowScreen(AppScreen s)
        {
            _menuRoot.SetActive(s == AppScreen.Menu);
            _selectRoot.SetActive(s == AppScreen.Select);
            _gameRoot.SetActive(s == AppScreen.Game);
            _overlay.SetActive(false);
            _settingsRoot.SetActive(false);
            if (s == AppScreen.Select) RefreshSelect();
        }

        // ---- переходы с фейдом ----
        private GameObject _fader;
        private CanvasGroup _faderGroup;
        private bool _fading;

        private void GoTo(AppScreen s, System.Action afterSwitch = null)
        {
            if (_fading) return;
            StartCoroutine(FadeSwitch(s, afterSwitch));
        }

        private IEnumerator FadeSwitch(AppScreen s, System.Action afterSwitch)
        {
            _fading = true;
            if (_fader == null)
            {
                _fader = NewUi("Fader", _canvasT).gameObject;
                Stretch(_fader.transform);
                _fader.AddComponent<Image>().color = ColBgDark;
                _faderGroup = _fader.AddComponent<CanvasGroup>();
            }
            _fader.SetActive(true);
            _fader.transform.SetAsLastSibling();
            _faderGroup.blocksRaycasts = true;
            yield return Tween.Fade(_faderGroup, 0f, 1f, 0.18f);
            ShowScreen(s);
            afterSwitch?.Invoke();
            yield return Tween.Fade(_faderGroup, 1f, 0f, 0.25f);
            _faderGroup.blocksRaycasts = false;
            _fader.SetActive(false);
            _fading = false;
        }

        private GameObject ScreenRoot(string name)
        {
            var root = NewUi(name, _canvasT);
            Stretch(root);
            root.gameObject.AddComponent<SafeAreaFitter>();
            return root.gameObject;
        }

        // ================= ГЛАВНОЕ МЕНЮ =================

        private void BuildMenu()
        {
            _menuRoot = ScreenRoot("MenuRoot");

            var title = AddText(_menuRoot.transform, "History Teller", 92, ColInkText,
                TextAnchor.MiddleCenter, FontStyle.BoldAndItalic);
            Anchor(title.transform, new Vector2(0.5f, 1), new Vector2(0.5f, 1),
                Vector2.zero, Vector2.zero);
            ((RectTransform)title.transform).anchoredPosition = new Vector2(0, -150);
            ((RectTransform)title.transform).sizeDelta = new Vector2(1300, 110);

            var rule = NewUi("Rule", _menuRoot.transform); // декоративная линия
            var ruleRt = (RectTransform)rule;
            ruleRt.anchorMin = ruleRt.anchorMax = new Vector2(0.5f, 1);
            ruleRt.anchoredPosition = new Vector2(0, -218);
            ruleRt.sizeDelta = new Vector2(520, 4);
            rule.gameObject.AddComponent<Image>().color = ColSepia;

            var sub = AddText(_menuRoot.transform, "истории, которые сложишь сам", 26, ColMuted,
                TextAnchor.MiddleCenter, FontStyle.Italic);
            Anchor(sub.transform, new Vector2(0.5f, 1), new Vector2(0.5f, 1),
                Vector2.zero, Vector2.zero);
            ((RectTransform)sub.transform).anchoredPosition = new Vector2(0, -252);
            ((RectTransform)sub.transform).sizeDelta = new Vector2(900, 36);

            AnchoredButton(_menuRoot.transform, "Играть", () =>
            {
                Sfx.Play("select");
                GoTo(AppScreen.Select);
            }, ColBtn, ColBtnText, new Vector2(0.5f, 0.5f), new Vector2(0, -40), 380, 86, 32);

            AnchoredButton(_menuRoot.transform, "Настройки", OpenSettings,
                ColSepia, ColBtnText, new Vector2(0.5f, 0.5f), new Vector2(0, -148), 380, 70, 24);

            var ver = AddText(_menuRoot.transform, "MVP 1 · глава I «Рим»", 18, ColMuted,
                TextAnchor.MiddleCenter, FontStyle.Italic);
            Anchor(ver.transform, new Vector2(0.5f, 0), new Vector2(0.5f, 0),
                Vector2.zero, Vector2.zero);
            ((RectTransform)ver.transform).anchoredPosition = new Vector2(0, 40);
            ((RectTransform)ver.transform).sizeDelta = new Vector2(900, 28);
        }

        // ================= СТРАНИЦА ГЛАВЫ (выбор уровня) =================

        private void BuildSelect()
        {
            _selectRoot = ScreenRoot("SelectRoot");

            AnchoredButton(_selectRoot.transform, "‹",
                () => { Sfx.Play("select"); GoTo(AppScreen.Menu); },
                ColBtn, ColBtnText, new Vector2(0, 1), new Vector2(64, -56), 60, 56, 34);

            var t = AddText(_selectRoot.transform, "Глава I · Рим", 46, ColInkText,
                TextAnchor.MiddleCenter, FontStyle.BoldAndItalic);
            Anchor(t.transform, new Vector2(0.5f, 1), new Vector2(0.5f, 1),
                Vector2.zero, Vector2.zero);
            ((RectTransform)t.transform).anchoredPosition = new Vector2(0, -58);
            ((RectTransform)t.transform).sizeDelta = new Vector2(800, 56);

            var sub = AddText(_selectRoot.transform, "— выберите историю —", 20, ColMuted,
                TextAnchor.MiddleCenter, FontStyle.Italic);
            Anchor(sub.transform, new Vector2(0.5f, 1), new Vector2(0.5f, 1),
                Vector2.zero, Vector2.zero);
            ((RectTransform)sub.transform).anchoredPosition = new Vector2(0, -98);
            ((RectTransform)sub.transform).sizeDelta = new Vector2(800, 28);

            AnchoredButton(_selectRoot.transform, "Опции", OpenSettings, ColSepia, ColBtnText,
                new Vector2(1, 1), new Vector2(-92, -56), 116, 52, 20);

            var list = NewUi("List", _selectRoot.transform);
            Anchor(list, new Vector2(0.5f, 0), new Vector2(0.5f, 1),
                new Vector2(-520, 24), new Vector2(520, -126));
            _selectList = list;
        }

        private void RefreshSelect()
        {
            ClearChildren(_selectList);
            for (int i = 0; i < _levels.Count; i++)
            {
                int idx = i;
                var lv = _levels[i];
                bool done = SaveSystem.IsCompleted(lv.Id);
                bool unlocked = IsUnlocked(i);

                var row = NewUi("Lvl_" + lv.Id, _selectList);
                var rt = (RectTransform)row;
                rt.anchorMin = new Vector2(0.5f, 1);
                rt.anchorMax = new Vector2(0.5f, 1);
                rt.sizeDelta = new Vector2(1020, 84);
                rt.anchoredPosition = new Vector2(0, -10 - i * 94 - 42);

                // подложка строки — едва заметная, выбранная история выделяется при касании
                var rowBg = UiKit.RoundedImage(row.gameObject,
                    unlocked ? new Color(1f, 1f, 1f, 0.12f) : new Color(0, 0, 0, 0.03f));
                if (unlocked)
                {
                    var b = row.gameObject.AddComponent<Button>();
                    b.onClick.AddListener(() => { Sfx.Play("select"); LoadLevel(idx); });
                }

                // чекбокс
                string boxIcon = done ? "icon_box_done" : unlocked ? "icon_box" : "icon_lock";
                var box = UiKit.LoadArt(boxIcon);
                if (box != null)
                {
                    var ig = NewUi("Box", row);
                    var irt = (RectTransform)ig;
                    irt.anchorMin = irt.anchorMax = new Vector2(0, 0.5f);
                    irt.anchoredPosition = new Vector2(52, 0);
                    irt.sizeDelta = new Vector2(46, 46);
                    var img = ig.gameObject.AddComponent<Image>();
                    img.sprite = box;
                    img.preserveAspect = true;
                    img.raycastTarget = false;
                }

                var tt = AddText(row, $"{i + 1}.  «{lv.Title}»", 32,
                    unlocked ? ColInkText : ColMuted, TextAnchor.MiddleLeft,
                    unlocked ? FontStyle.BoldAndItalic : FontStyle.Italic);
                Anchor(tt.transform, new Vector2(0, 0), new Vector2(1, 1),
                    new Vector2(96, 0), new Vector2(-220, 0));

                var st = AddText(row,
                    done ? "пройдено" : unlocked ? "" : "заперто",
                    20, done ? UiKit.Hex("#7c5a1e") : ColMuted,
                    TextAnchor.MiddleRight, FontStyle.Italic);
                Anchor(st.transform, new Vector2(1, 0), new Vector2(1, 1),
                    new Vector2(-210, 0), new Vector2(-28, 0));
            }
        }

        // ================= НАСТРОЙКИ =================

        private void BuildSettings()
        {
            _settingsRoot = NewUi("Settings", _canvasT).gameObject;
            Stretch(_settingsRoot.transform);
            var dim = _settingsRoot.AddComponent<Image>();
            dim.color = new Color(0.1f, 0.07f, 0.04f, 0.8f);
            _settingsRoot.AddComponent<Button>().onClick.AddListener(CloseSettings);

            var card = NewUi("Card", _settingsRoot.transform);
            ((RectTransform)card).sizeDelta = new Vector2(560, 420);
            UiKit.RoundedImage(card.gameObject, ColPanelPaper);
            card.gameObject.AddComponent<Button>().onClick.AddListener(() => { });

            var t = AddText(card, "Настройки", 36, ColInkText,
                TextAnchor.MiddleCenter, FontStyle.BoldAndItalic);
            Anchor(t.transform, new Vector2(0, 1), new Vector2(1, 1),
                new Vector2(20, -70), new Vector2(-20, -16));

            var sndBtn = AnchoredButton(card, "", ToggleSound, ColBtn, ColBtnText,
                new Vector2(0.5f, 1), new Vector2(0, -126), 480, 66, 24);
            _soundBtnLabel = sndBtn.GetComponentInChildren<Text>();

            var rstBtn = AnchoredButton(card, "", ResetProgressTapped,
                UiKit.Hex("#8a3b3b"), ColBtnText,
                new Vector2(0.5f, 1), new Vector2(0, -210), 480, 66, 24);
            _resetBtnLabel = rstBtn.GetComponentInChildren<Text>();

            AnchoredButton(card, "Закрыть", CloseSettings, ColSepia, ColBtnText,
                new Vector2(0.5f, 1), new Vector2(0, -294), 480, 66, 24);

            _settingsRoot.SetActive(false);
        }

        private void OpenSettings()
        {
            Sfx.Play("select");
            _resetArmed = false;
            RefreshSettingsLabels();
            _settingsRoot.SetActive(true);
            _settingsRoot.transform.SetAsLastSibling();
        }

        private void CloseSettings()
        {
            _settingsRoot.SetActive(false);
            if (_selectRoot.activeSelf) RefreshSelect();
        }

        private void RefreshSettingsLabels()
        {
            _soundBtnLabel.text = SaveSystem.Get().SoundOn ? "Звук: включён" : "Звук: выключен";
            _resetBtnLabel.text = _resetArmed ? "Точно сбросить? Тап ещё раз" : "Сбросить прогресс";
        }

        private void ToggleSound()
        {
            SaveSystem.SetSound(!SaveSystem.Get().SoundOn);
            Sfx.Play("select");
            RefreshSettingsLabels();
        }

        private void ResetProgressTapped()
        {
            if (!_resetArmed)
            {
                _resetArmed = true;
                RefreshSettingsLabels();
                return;
            }
            SaveSystem.Reset();
            Sfx.Enabled = SaveSystem.Get().SoundOn;
            _resetArmed = false;
            Sfx.Play("remove");
            RefreshSettingsLabels();
        }

        // ================= ИГРОВОЙ ЭКРАН =================

        private void BuildGameScreen()
        {
            _gameRoot = ScreenRoot("GameRoot");
            _gameGroup = _gameRoot.AddComponent<CanvasGroup>();

            AnchoredButton(_gameRoot.transform, "‹",
                () => { Sfx.Play("select"); GoTo(AppScreen.Select); },
                ColBtn, ColBtnText, new Vector2(0, 1), new Vector2(64, -54), 60, 54, 34);

            // ВЕРХ: название уровня (мелко, читаемо)
            _title = AddText(_gameRoot.transform, "", 18, ColInkText,
                TextAnchor.MiddleCenter, FontStyle.Italic);
            var ttr = (RectTransform)_title.transform;
            ttr.anchorMin = ttr.anchorMax = new Vector2(0.5f, 1);
            ttr.anchoredPosition = new Vector2(0, -16);
            ttr.sizeDelta = new Vector2(660, 22);

            // строка-заголовок: [чекбокс][цель] склеены и отцентрованы как единый блок
            var titleRow = NewUi("TitleRow", _gameRoot.transform);
            var trr = (RectTransform)titleRow;
            trr.anchorMin = trr.anchorMax = new Vector2(0.5f, 1);
            trr.pivot = new Vector2(0.5f, 1);
            trr.anchoredPosition = new Vector2(0, -30);
            var hlg = titleRow.gameObject.AddComponent<HorizontalLayoutGroup>();
            hlg.spacing = 14;
            hlg.childAlignment = TextAnchor.MiddleCenter;
            hlg.childControlWidth = true; hlg.childControlHeight = true;
            hlg.childForceExpandWidth = false; hlg.childForceExpandHeight = false;
            titleRow.gameObject.AddComponent<ContentSizeFitter>().horizontalFit =
                ContentSizeFitter.FitMode.PreferredSize;

            var boxGo = NewUi("Box", titleRow);
            ((RectTransform)boxGo).sizeDelta = new Vector2(32, 32);
            var boxLE = boxGo.gameObject.AddComponent<LayoutElement>();
            boxLE.preferredWidth = 32; boxLE.preferredHeight = 32;
            _goalBox = boxGo.gameObject.AddComponent<Image>();
            _goalBox.preserveAspect = true;
            _goalBox.raycastTarget = false;

            _goalLine = AddText(titleRow, "", 30, ColInkText,
                TextAnchor.MiddleLeft, FontStyle.BoldAndItalic);
            _goalLine.horizontalOverflow = HorizontalWrapMode.Overflow;
            _goalLine.verticalOverflow = VerticalWrapMode.Overflow;
            _goalLine.gameObject.AddComponent<LayoutElement>().preferredHeight = 40;

            // короткая ремарка под заголовком (читаемо, не лезет под кнопки)
            _info = AddText(_gameRoot.transform, "", 16, ColMuted,
                TextAnchor.MiddleCenter, FontStyle.Italic);
            Anchor(_info.transform, new Vector2(0.5f, 1), new Vector2(0.5f, 1),
                Vector2.zero, Vector2.zero);
            ((RectTransform)_info.transform).anchoredPosition = new Vector2(0, -76);
            ((RectTransform)_info.transform).sizeDelta = new Vector2(820, 22);

            AnchoredButton(_gameRoot.transform, "Сброс",
                () => { Sfx.Play("remove"); ResetLevel(); },
                ColBtn, ColBtnText, new Vector2(1, 1), new Vector2(-160, -54), 116, 50, 20);
            AnchoredButton(_gameRoot.transform, "?", ShowSolutionHint, ColAccent, ColBtnText,
                new Vector2(1, 1), new Vector2(-66, -54), 50, 50, 26);

            // подсказка/туториал — одна строка под заголовком (без переноса, чтобы не лезла на заголовок)
            _hintText = AddText(_gameRoot.transform, "", 17, ColAccent,
                TextAnchor.MiddleCenter, FontStyle.BoldAndItalic);
            _hintText.horizontalOverflow = HorizontalWrapMode.Overflow;
            _hintText.verticalOverflow = VerticalWrapMode.Truncate;
            Anchor(_hintText.transform, new Vector2(0.5f, 1), new Vector2(0.5f, 1),
                Vector2.zero, Vector2.zero);
            ((RectTransform)_hintText.transform).anchoredPosition = new Vector2(0, -112);
            ((RectTransform)_hintText.transform).sizeDelta = new Vector2(1200, 22);

            // ЦЕНТР: кадры-сцены в ряд на всю ширину (между шапкой и нижним треем)
            var panelsGo = NewUi("Panels", _gameRoot.transform);
            Anchor(panelsGo, new Vector2(0, 0), new Vector2(1, 1),
                new Vector2(34, 178), new Vector2(-34, -134));
            var panelsRow = panelsGo.gameObject.AddComponent<HorizontalLayoutGroup>();
            panelsRow.spacing = 18;
            panelsRow.childAlignment = TextAnchor.MiddleCenter;
            panelsRow.childControlWidth = false;
            panelsRow.childControlHeight = false;
            panelsRow.childForceExpandWidth = false;
            panelsRow.childForceExpandHeight = false;
            _panelsRow = panelsGo;

            // НИЗ: трей одной полосой — слева сцены, справа персонажи
            var sceneLbl = AddText(_gameRoot.transform, "сцены", 19, ColInkText,
                TextAnchor.MiddleLeft, FontStyle.BoldAndItalic);
            Anchor(sceneLbl.transform, new Vector2(0, 0), new Vector2(0, 0),
                new Vector2(42, 150), new Vector2(180, 172));

            var trayS = NewUi("TrayScenes", _gameRoot.transform);
            var traySrt = (RectTransform)trayS;
            traySrt.anchorMin = traySrt.anchorMax = new Vector2(0, 0);
            traySrt.pivot = new Vector2(0, 0);
            traySrt.anchoredPosition = new Vector2(40, 12);
            traySrt.sizeDelta = new Vector2(640, 150);
            var hS = trayS.gameObject.AddComponent<HorizontalLayoutGroup>();
            hS.spacing = 10;
            hS.childAlignment = TextAnchor.LowerLeft;
            hS.childControlWidth = false; hS.childControlHeight = false;
            hS.childForceExpandWidth = false; hS.childForceExpandHeight = false;
            _trayScenes = trayS;

            var charLbl = AddText(_gameRoot.transform, "персонажи", 19, ColInkText,
                TextAnchor.MiddleRight, FontStyle.BoldAndItalic);
            Anchor(charLbl.transform, new Vector2(1, 0), new Vector2(1, 0),
                new Vector2(-180, 150), new Vector2(-42, 172));

            var trayC = NewUi("TrayChars", _gameRoot.transform);
            var trayCrt = (RectTransform)trayC;
            trayCrt.anchorMin = trayCrt.anchorMax = new Vector2(1, 0);
            trayCrt.pivot = new Vector2(1, 0);
            trayCrt.anchoredPosition = new Vector2(-40, 12);
            trayCrt.sizeDelta = new Vector2(640, 150);
            var hC = trayC.gameObject.AddComponent<HorizontalLayoutGroup>();
            hC.spacing = 10;
            hC.childAlignment = TextAnchor.LowerRight;
            hC.childControlWidth = false; hC.childControlHeight = false;
            hC.childForceExpandWidth = false; hC.childForceExpandHeight = false;
            _trayChars = trayC;
        }

        private void BuildWinOverlay()
        {
            _overlay = NewUi("Overlay", _canvasT).gameObject;
            Stretch(_overlay.transform);
            _overlay.AddComponent<Image>().color = new Color(0.1f, 0.07f, 0.04f, 0.85f);
            _overlayGroup = _overlay.AddComponent<CanvasGroup>();

            _card = NewUi("Card", _overlay.transform);
            ((RectTransform)_card).sizeDelta = new Vector2(840, 0);
            UiKit.RoundedImage(_card.gameObject, ColPanelPaper);
            var col = _card.gameObject.AddComponent<VerticalLayoutGroup>();
            col.padding = new RectOffset(32, 32, 26, 22);
            col.spacing = 12;
            col.childControlWidth = true;
            col.childControlHeight = true;
            col.childForceExpandWidth = true;
            col.childForceExpandHeight = false;
            _card.gameObject.AddComponent<ContentSizeFitter>()
                .verticalFit = ContentSizeFitter.FitMode.PreferredSize;

            var winTitle = AddText(_card, "История сложилась!", 36, ColInkText,
                TextAnchor.MiddleLeft, FontStyle.BoldAndItalic);
            winTitle.gameObject.AddComponent<LayoutElement>().preferredHeight = 44;

            var accGo = NewUi("Acc", _card);
            accGo.gameObject.AddComponent<LayoutElement>().preferredHeight = 36;
            _accBg = UiKit.RoundedImage(accGo.gameObject, Color.gray);
            _accText = AddText(accGo, "", 20, Color.white, TextAnchor.MiddleCenter, FontStyle.Bold);
            Stretch(_accText.transform);

            _factText = AddText(_card, "", 24, ColInkText, TextAnchor.UpperLeft);
            _srcText = AddText(_card, "", 20, ColMuted, TextAnchor.MiddleLeft, FontStyle.Italic);
            _srcText.gameObject.AddComponent<LayoutElement>().preferredHeight = 28;

            var btns = Row(_card, 64, 12);
            AddButton(btns, "Ещё раз", () => { _overlay.SetActive(false); ResetLevel(); },
                ColSepia, ColBtnText, 190, 64, 24);
            AddButton(btns, "К главе", () => { Sfx.Play("select"); GoTo(AppScreen.Select); },
                ColBtn, ColBtnText, 190, 64, 24);
            _nextLevelBtn = AddButton(btns, "Дальше →", () =>
            {
                if (_levelIdx < _levels.Count - 1) LoadLevel(_levelIdx + 1);
                else GoTo(AppScreen.Select);
            }, ColAccent, ColBtnText, 190, 64, 24).gameObject;

            _overlay.SetActive(false);
        }

        // ================= ИГРОВАЯ ЛОГИКА =================

        private void LoadLevel(int idx)
        {
            _levelIdx = idx;
            GoTo(AppScreen.Game, ResetLevel);
        }

        private void ResetLevel()
        {
            _panels = Enumerable.Range(0, Lv.Panels).Select(_ => new Panel()).ToList();
            _selScene = _selChar = null;
            _solvedShown = false;
            _gameGroup.interactable = true;
            _gameGroup.blocksRaycasts = true;
            if (_overlay != null) _overlay.SetActive(false);
            _hintUntil = 0f;
            Render();
        }

        private void OnPanelTapped(int i)
        {
            if (_selScene != null) { DropOnPanel(i, "scene", _selScene); _selScene = null; }
            else if (_selChar != null) DropOnPanel(i, "char", _selChar);
        }

        public void DropOnPanel(int i, string kind, string id)
        {
            var p = _panels[i];
            if (kind == "scene")
            {
                p.SceneId = id;
                while (p.Characters.Count > _db.Scenes[id].Slots)
                    p.Characters.RemoveAt(p.Characters.Count - 1);
                _selScene = null;
                Sfx.Play("place");
                Render(i, null);
            }
            else
            {
                if (p.SceneId == null) { Warn("Сначала поместите сцену в кадр"); return; }
                if (p.Characters.Contains(id)) { Warn("Этот персонаж уже здесь"); return; }
                if (p.Characters.Count >= _db.Scenes[p.SceneId].Slots)
                { Warn("В этой сцене нет места"); return; }
                p.Characters.Add(id);
                Sfx.Play("place");
                Render(i, id);
            }
        }

        public void ChipTapped(string kind, string id)
        {
            Sfx.Play("select");
            if (kind == "scene")
            {
                _selScene = _selScene == id ? null : id;
                _selChar = null;
            }
            else
            {
                _selChar = _selChar == id ? null : id;
                _selScene = null;
            }
            Render();
        }

        public Transform CreateGhost(string kind, string id)
        {
            var go = NewUi("Ghost", _canvasT);
            var rt = (RectTransform)go;
            rt.sizeDelta = new Vector2(120, 120);
            var cg = go.gameObject.AddComponent<CanvasGroup>();
            cg.blocksRaycasts = false;
            cg.alpha = 0.92f;

            var art = UiKit.LoadArt((kind == "scene" ? "scene_" : "char_") + id);
            if (art != null && kind == "char")
            {
                var img = go.gameObject.AddComponent<Image>();
                img.sprite = art;
                img.preserveAspect = true;
            }
            else if (art != null)
            {
                UiKit.RoundedImage(go.gameObject, ColSepia);
                var imgGo = NewUi("Img", go);
                Anchor(imgGo, Vector2.zero, Vector2.one, new Vector2(3, 3), new Vector2(-3, -3));
                var img = imgGo.gameObject.AddComponent<Image>();
                img.sprite = art;
            }
            else
            {
                UiKit.RoundedImage(go.gameObject, ColSepia);
                string label = kind == "scene" ? _db.Scenes[id].Name : _db.Characters[id].Name;
                var t = AddText(go, label, 20, ColBtnText, TextAnchor.MiddleCenter, FontStyle.Bold);
                Stretch(t.transform);
            }
            return go;
        }

        private void RemoveChar(int panelIdx, string charId)
        {
            _panels[panelIdx].Characters.Remove(charId);
            Sfx.Play("remove");
            Render();
        }

        private void ClearPanel(int panelIdx)
        {
            _panels[panelIdx] = new Panel();
            Sfx.Play("remove");
            Render();
        }

        private void ShowSolutionHint()
        {
            Sfx.Play("select");
            List<string> sceneIds = null;
            if (Lv.Solution != null)
                sceneIds = Lv.Solution.Select(p => p.SceneId).ToList();
            else
            {
                var res = Solver.Solve(Lv, _db, 1);
                if (res.IsSolvable)
                    sceneIds = res.Solutions[0].Select(p => p.SceneId).ToList();
            }
            Warn(sceneIds == null
                ? "Решений нет — баг контента!"
                : "Порядок сцен: " + string.Join(" → ", sceneIds.Select(s => _db.Scenes[s].Name)));
        }

        private void Warn(string msg)
        {
            Sfx.Play("error", 0.7f);
            _hintText.text = msg;
            _hintUntil = Time.unscaledTime + 2.6f;
        }

        private string TutorialStep()
        {
            if (_levelIdx != 0 || Lv.Solution == null) return "";
            if (SaveSystem.IsCompleted(Lv.Id) || _solvedShown) return "";
            for (int i = 0; i < Lv.Panels && i < Lv.Solution.Count; i++)
            {
                var sol = Lv.Solution[i];
                var p = _panels[i];
                if (p.SceneId != sol.SceneId)
                    return $"Перетащите сцену «{_db.Scenes[sol.SceneId].Name}» в кадр {i + 1}";
                foreach (var ch in p.Characters)
                    if (!sol.Characters.Contains(ch))
                        return $"В кадре {i + 1} лишний персонаж — тапните по нему, чтобы убрать";
                foreach (var ch in sol.Characters)
                    if (!p.Characters.Contains(ch))
                        return $"Перетащите «{_db.Characters[ch].Name}» в кадр {i + 1}";
                if (!p.Characters.SequenceEqual(sol.Characters))
                    return $"Роли перепутаны — поменяйте персонажей местами в кадре {i + 1} (кнопка со стрелками)";
            }
            return "";
        }

        // ================= РЕНДЕР =================

        private void Render(int changedPanel = -1, string addedChar = null)
        {
            _title.text = "";   // название уровня в шапке не показываем — только цель (топорно, как Storyteller)

            // цель с чекбоксом (отмечена, если уровень уже проходили)
            _goalLine.text = string.IsNullOrEmpty(Lv.GoalText) ? Lv.Title : Lv.GoalText;
            bool goalDone = _solvedShown || SaveSystem.IsCompleted(Lv.Id);
            _goalBox.sprite = UiKit.LoadArt(goalDone ? "icon_box_done" : "icon_box");

            // «топорный» заголовок как в Storyteller: только цель, без описаний
            _info.text = "";

            var snapshots = new List<World>();
            var events = new List<RuleEvent>();
            var world = Engine.Simulate(_panels, _db, null, Lv.CreateInitialWorld(),
                snapshots, events);

            RenderPanels(snapshots, events);
            RenderTray();

            _tutorialText = TutorialStep();
            if (_hintUntil <= 0f) _hintText.text = _tutorialText;

            if (changedPanel >= 0)
                StartCoroutine(AnimateAction(changedPanel, addedChar, events, snapshots));

            if (!_solvedShown && Lv.Goal.IsMet(world))
            {
                _solvedShown = true;
                SaveSystem.MarkCompleted(Lv.Id);
                // мгновенная «галочка» в чекбоксе цели — без всяких кнопок
                var done = UiKit.LoadArt("icon_box_done");
                if (done != null) _goalBox.sprite = done;
                StartCoroutine(Tween.Pulse(_goalBox.transform, 0.45f, 0.5f));
                Sfx.Play("win");
                StartCoroutine(WinSequence(events));
            }
        }

        private void RenderPanels(List<World> snapshots, List<RuleEvent> events)
        {
            ClearChildren(_panelsRow);
            _panelViews.Clear();
            _tileMap.Clear();
            _rigs.Clear();
            // ландшафтные кадры 4:3, ВПИСЫВАЮТСЯ в доступную область при любом числе панелей.
            // Логический размер канваса: ширина фиксирована (CanvasScaler match=width=1624), высота — по аспекту экрана.
            const float logicalW = 1624f, gap = 18f;
            float logicalH = logicalW * Screen.height / Mathf.Max(1, Screen.width);
            float availW = logicalW - 68f;                       // поля по 34 слева/справа
            float availH = Mathf.Max(240f, logicalH - 320f);     // минус шапка сверху и трей снизу
            float w = (availW - gap * (Lv.Panels - 1)) / Lv.Panels;   // точно делим ширину между кадрами
            float h = w / 1.34f;
            if (h > availH) { h = availH; w = h * 1.34f; }       // если не лезет по высоте — ограничиваем
            w = Mathf.Min(w, 760f); h = Mathf.Min(h, 470f);      // не гигантские для 1–2 кадров

            for (int i = 0; i < _panels.Count; i++)
            {
                int idx = i;
                var p = _panels[i];
                var snap = i < snapshots.Count ? snapshots[i] : new World();
                var tiles = new Dictionary<string, Transform>();

                // тёмная сепия-рамка кадра
                var frame = NewUi("Panel" + i, _panelsRow);
                ((RectTransform)frame).sizeDelta = new Vector2(w, h);
                UiKit.RoundedImage(frame.gameObject, ColSepia);
                frame.gameObject.AddComponent<PanelMarker>().Index = i;
                frame.gameObject.AddComponent<Button>()
                    .onClick.AddListener(() => OnPanelTapped(idx));

                // золотая внутренняя линия (двойная рамка как в книжной гравюре)
                var gold = NewUi("FrameLine", frame);
                Anchor(gold, Vector2.zero, Vector2.one, new Vector2(3, 3), new Vector2(-3, -3));
                UiKit.RoundedImage(gold.gameObject, ColAccent).raycastTarget = false;

                var inner = NewUi("Inner", frame);
                Anchor(inner, Vector2.zero, Vector2.one, new Vector2(6, 6), new Vector2(-6, -6));
                UiKit.RoundedImage(inner.gameObject, ColPanelPaper).raycastTarget = false;
                inner.gameObject.AddComponent<Mask>().showMaskGraphic = true;

                // фон-арт сцены, приглушённый под бумагу
                var sceneArt = p.SceneId != null ? UiKit.LoadArt("scene_" + p.SceneId) : null;
                if (sceneArt != null)
                {
                    var artGo = NewUi("SceneArt", inner);
                    Stretch(artGo);
                    var artImg = artGo.gameObject.AddComponent<Image>();
                    artImg.sprite = sceneArt;
                    artImg.color = new Color(1f, 0.97f, 0.9f, 0.9f);
                    artImg.raycastTarget = false;
                }

                // виньетка — мягкое затемнение к краям, добавляет глубину сцене
                var vig = UiKit.LoadArt("ui_vignette");
                if (vig != null)
                {
                    var vg = NewUi("Vignette", inner);
                    Stretch(vg);
                    var vim = vg.gameObject.AddComponent<Image>();
                    vim.sprite = vig;
                    vim.type = Image.Type.Simple;
                    vim.raycastTarget = false;
                }

                // пустой кадр — призрак-подсказка (стрелка вниз + «сцена»)
                if (p.SceneId == null)
                {
                    var ghost = AddText(inner, "↓", 64, new Color(0.42f, 0.31f, 0.18f, 0.32f),
                        TextAnchor.MiddleCenter, FontStyle.Bold);
                    Anchor(ghost.transform, new Vector2(0, 0.34f), new Vector2(1, 0.72f),
                        Vector2.zero, Vector2.zero);
                    var hint = AddText(inner, "сцена", 16, ColMuted,
                        TextAnchor.MiddleCenter, FontStyle.Italic);
                    Anchor(hint.transform, new Vector2(0, 0.22f), new Vector2(1, 0.34f),
                        Vector2.zero, Vector2.zero);
                }
                if (p.SceneId != null || p.Characters.Count > 0)
                {
                    var clear = AnchoredButton(inner, "×", () => ClearPanel(idx),
                        new Color(0.63f, 0.32f, 0.25f, 0.9f), ColBtnText,
                        new Vector2(1, 1), new Vector2(-24, -23), 32, 32, 19);
                    clear.GetComponentInChildren<Text>().raycastTarget = false;
                }

                // ---- постановка кадра: фигуры в слотах-ролях ----
                var stage = NewUi("Stage", inner);
                Anchor(stage, Vector2.zero, Vector2.one,
                    new Vector2(4, 24), new Vector2(-4, -10));

                var sceneDef = p.SceneId != null ? _db.Scenes[p.SceneId] : null;
                int slotCount = sceneDef != null ? sceneDef.Slots : 0;
                var roles = sceneDef != null ? sceneDef.Roles : null;
                float[] xs = slotCount <= 1 ? new[] { 0f }
                    : slotCount == 2 ? new[] { -w * 0.21f, w * 0.21f }
                    : new[] { -w * 0.24f, w * 0.24f, 0f };

                for (int s = 0; s < slotCount; s++)
                {
                    bool third = s == 2;
                    if (s < p.Characters.Count)
                    {
                        string c = p.Characters[s];
                        string charId = c;
                        bool dead = snap.HasFlag(c, World.DeadFlag);
                        string emo = "";
                        if (!dead)
                        {
                            bool inLove = p.Characters.Any(o =>
                                o != c && snap.HasRelation("loves", c, o));
                            if (inLove) emo = "_love";
                            else if (snap.HasFlag(c, "plotting")) emo = "_plot";
                        }
                        var portrait = UiKit.LoadArt("char_" + c + emo);
                        if (portrait == null) portrait = UiKit.LoadArt("char_" + c);

                        // мягкая тень под ногами — фигура «стоит» в сцене, а не висит
                        if (!dead && !third)
                        {
                            var sh = NewUi("Shadow", stage);
                            var shrt = (RectTransform)sh;
                            shrt.anchorMin = shrt.anchorMax = new Vector2(0.5f, 0f);
                            shrt.sizeDelta = new Vector2(92, 20);
                            shrt.anchoredPosition = new Vector2(xs[s], 16f);
                            var shimg = UiKit.RoundedImage(sh.gameObject, new Color(0f, 0f, 0f, 0.13f));
                            shimg.raycastTarget = false;
                        }

                        var fig = NewUi("Char_" + c, stage);
                        tiles[c] = fig;
                        var frt = (RectTransform)fig;
                        frt.anchorMin = frt.anchorMax = new Vector2(0.5f, 0f);
                        frt.anchoredPosition = new Vector2(xs[s], dead ? 54f : third ? 188f : 80f);
                        frt.sizeDelta = new Vector2(116, 154);
                        if (third) fig.localScale = Vector3.one * 0.82f;
                        if (dead) fig.localRotation = Quaternion.Euler(0, 0, 90);
                        fig.gameObject.AddComponent<Button>()
                            .onClick.AddListener(() => RemoveChar(idx, charId));
                        var hit = fig.gameObject.AddComponent<Image>(); // кликзона
                        hit.color = new Color(0, 0, 0, 0.001f);

                        var body = NewUi("Body", fig);
                        Anchor(body, new Vector2(0, 0), new Vector2(1, 1),
                            new Vector2(2, 22), new Vector2(-2, 0));
                        var bimg = body.gameObject.AddComponent<Image>();
                        if (portrait != null)
                        {
                            bimg.sprite = portrait;
                            bimg.preserveAspect = true;
                            if (dead) bimg.color = new Color(0.72f, 0.7f, 0.66f, 0.92f);
                        }
                        else bimg.color = UiKit.IdColor(c, 0.35f, 0.85f);
                        bimg.raycastTarget = false;

                        // если у персонажа есть риг-арт — собираем куклу и прячем плоский портрет
                        CharacterRig rig = dead ? null : CharacterRig.Build(body, c, 158f);
                        if (rig != null)
                        {
                            bimg.enabled = false;
                            _rigs[idx + ":" + c] = rig;
                        }
                        else if (portrait != null && s == 1)
                        {
                            body.localScale = new Vector3(-1, 1, 1); // плоский портрет — лицом к партнёру
                        }

                        // постоянная метка состояния над головой (остаётся на экране)
                        string topIcon = null;
                        if (!dead && snap.HasFlag(c, "crowned")) topIcon = "icon_crown";
                        else if (!dead && snap.HasFlag(c, "plotting")) topIcon = "icon_plotting";
                        else if (!dead && snap.HasFlag(c, "inside")) topIcon = "icon_done";   // тайно проведена — успех
                        else if (!dead && snap.HasFlag(c, "locked_out")) topIcon = "icon_lock"; // ещё не впустили
                        if (topIcon != null)
                        {
                            var ti = UiKit.LoadArt(topIcon);
                            if (ti != null)
                            {
                                var tg = NewUi("Top", fig);
                                var trt2 = (RectTransform)tg;
                                trt2.anchorMin = trt2.anchorMax = new Vector2(0.5f, 1f);
                                trt2.anchoredPosition = new Vector2(0, 8);
                                trt2.sizeDelta = new Vector2(34, 34);
                                var tim = tg.gameObject.AddComponent<Image>();
                                tim.sprite = ti;
                                tim.preserveAspect = true;
                                tim.raycastTarget = false;
                            }
                        }

                        // имя под фигурой не рисуем — как в Storyteller (имена только в трее)
                    }
                    else if (p.SceneId != null)
                    {
                        // пустой слот: призрак-подсказка (стрелка вниз) + роль, без рамки
                        var ph = NewUi("Slot" + s, stage);
                        var prt = (RectTransform)ph;
                        prt.anchorMin = prt.anchorMax = new Vector2(0.5f, 0f);
                        prt.anchoredPosition = new Vector2(xs[s], third ? 188f : 80f);
                        prt.sizeDelta = new Vector2(104, 150);
                        if (third) ph.localScale = Vector3.one * 0.82f;
                        var arrow = AddText(ph, "↓", 46, new Color(0.42f, 0.31f, 0.18f, 0.42f),
                            TextAnchor.MiddleCenter, FontStyle.Bold);
                        Anchor(arrow.transform, new Vector2(0, 0.32f), new Vector2(1, 1),
                            Vector2.zero, Vector2.zero);
                        var roleT = AddText(ph,
                            roles != null && s < roles.Count ? roles[s] : "",
                            15, ColMuted, TextAnchor.MiddleCenter, FontStyle.Italic);
                        Anchor(roleT.transform, new Vector2(0, 0), new Vector2(1, 0),
                            new Vector2(0, 2), new Vector2(0, 24));
                    }
                }

                // пиктограммы отношений между парами фигур
                int presentN = Mathf.Min(p.Characters.Count, Mathf.Max(slotCount, p.Characters.Count));
                for (int a = 0; a < presentN; a++)
                for (int b2 = a + 1; b2 < presentN; b2++)
                {
                    if (a >= xs.Length || b2 >= xs.Length) break;
                    var icons = PairIcons(snap, p.Characters[a], p.Characters[b2]);
                    if (icons.Count == 0) continue;
                    float midX = (xs[a] + xs[b2]) / 2f;
                    float midY = (b2 == 2) ? 250f : 224f;
                    for (int k = 0; k < icons.Count && k < 2; k++)
                    {
                        var sp = UiKit.LoadArt(icons[k]);
                        if (sp == null) continue;
                        // главную эмоцию (k==0) рисуем крупно и над парой — как большое сердце в Storyteller
                        float icSize = k == 0 ? 64f : 38f;
                        var pg = NewUi("Pair", stage);
                        var prt2 = (RectTransform)pg;
                        prt2.anchorMin = prt2.anchorMax = new Vector2(0.5f, 0f);
                        prt2.anchoredPosition = new Vector2(midX, midY + (k == 0 ? 0f : 56f));
                        prt2.sizeDelta = new Vector2(icSize, icSize);
                        var pim = pg.gameObject.AddComponent<Image>();
                        pim.sprite = sp;
                        pim.preserveAspect = true;
                        pim.raycastTarget = false;
                        if (k == 0) StartCoroutine(Tween.Scale(pg, 0.4f, 1f, 0.3f)); // лёгкое появление
                    }
                }

                // ПОСТОЯННАЯ подпись действия сверху кадра (пока персонажи в кадре и сработало правило)
                var acted = events
                    .Where(e => e.PanelIndex == idx)
                    .Select(e => RuleLabel.TryGetValue(e.RuleId, out var lbl) ? lbl : e.RuleId)
                    .Distinct().ToList();
                if (acted.Count > 0)
                {
                    var capGo = NewUi("ActionCap", inner);
                    var crt = (RectTransform)capGo;
                    crt.anchorMin = crt.anchorMax = new Vector2(0.5f, 1);
                    crt.anchoredPosition = new Vector2(0, -14);
                    crt.sizeDelta = new Vector2(Mathf.Min(w - 26f, 240f), 32);
                    UiKit.RoundedImage(capGo.gameObject, new Color(0.29f, 0.21f, 0.12f, 0.86f))
                        .raycastTarget = false;
                    var capT = AddText(capGo, string.Join(" · ", acted), 16,
                        UiKit.Hex("#ecd9a8"), TextAnchor.MiddleCenter, FontStyle.BoldAndItalic);
                    Stretch(capT.transform);
                }

                // нижняя подпись кадра: сцена + занятость
                var slots = AddText(inner,
                    p.SceneId != null
                        ? $"{_db.Scenes[p.SceneId].Name} · {p.Characters.Count}/{_db.Scenes[p.SceneId].Slots}"
                        : "",
                    16, ColInkText, TextAnchor.MiddleCenter, FontStyle.Italic);
                Anchor(slots.transform, new Vector2(0, 0), new Vector2(1, 0),
                    new Vector2(8, 3), new Vector2(-8, 25));

                // резные уголки кадра (поверх всего)
                AddCornerBrackets(frame, ColAccent);

                _panelViews.Add(frame);
                _tileMap.Add(tiles);
            }
        }

        /// <summary>Четыре «уголка»-кронштейна по углам кадра — книжное обрамление.</summary>
        private void AddCornerBrackets(Transform frame, Color col)
        {
            Vector2[] corners = { new Vector2(0, 1), new Vector2(1, 1), new Vector2(0, 0), new Vector2(1, 0) };
            const float inset = 9f, len = 26f, thick = 5f;
            foreach (var an in corners)
            {
                float sx = an.x == 0 ? 1f : -1f;   // к центру по X
                float sy = an.y == 1 ? -1f : 1f;    // к центру по Y
                MakeBar(frame, an, new Vector2(sx * (inset + len / 2f), sy * inset),
                    new Vector2(len, thick), col);                       // горизонтальная планка
                MakeBar(frame, an, new Vector2(sx * inset, sy * (inset + len / 2f)),
                    new Vector2(thick, len), col);                       // вертикальная планка
            }
        }

        private void MakeBar(Transform parent, Vector2 anchor, Vector2 pos, Vector2 size, Color col)
        {
            var go = NewUi("Brk", parent);
            var rt = (RectTransform)go;
            rt.anchorMin = rt.anchorMax = anchor;
            rt.pivot = new Vector2(0.5f, 0.5f);
            rt.anchoredPosition = pos;
            rt.sizeDelta = size;
            var img = UiKit.RoundedImage(go.gameObject, col);
            img.raycastTarget = false;
        }

        // ---- боковой трей с миниатюрами ----
        private void RenderTray()
        {
            ClearChildren(_trayScenes);
            for (int i = 0; i < Lv.Scenes.Count; i++)
            {
                var s = _db.Scenes[Lv.Scenes[i]];
                string lbl = string.IsNullOrEmpty(s.Action) ? s.Name : s.Name + "\n" + s.Action;
                TrayItem(_trayScenes, i, "scene", Lv.Scenes[i], lbl, _selScene == Lv.Scenes[i]);
            }

            ClearChildren(_trayChars);
            for (int i = 0; i < Lv.Characters.Count; i++)
                TrayItem(_trayChars, i, "char", Lv.Characters[i],
                    _db.Characters[Lv.Characters[i]].Name, _selChar == Lv.Characters[i]);
        }

        private void TrayItem(Transform column, int index, string kind, string id,
            string label, bool selected)
        {
            var item = NewUi("Tray_" + id, column);
            var rt = (RectTransform)item;
            rt.anchorMin = new Vector2(0.5f, 1);
            rt.anchorMax = new Vector2(0.5f, 1);
            rt.sizeDelta = new Vector2(118, 124);   // выше — портрет и подпись не наезжают
            rt.anchoredPosition = new Vector2(0, -4 - index * 116 - 56);

            // подсветка выбранного
            var backing = UiKit.RoundedImage(item.gameObject,
                selected ? new Color(0.66f, 0.46f, 0.16f, 0.35f) : new Color(0, 0, 0, 0.001f));
            backing.raycastTarget = true;
            item.gameObject.AddComponent<ChipDrag>().Init(this, kind, id);

            var art = UiKit.LoadArt((kind == "scene" ? "scene_" : "char_") + id);
            if (kind == "scene")
            {
                // мини-кадр с рамкой
                var fr = NewUi("Fr", item);
                Anchor(fr, new Vector2(0.5f, 1), new Vector2(0.5f, 1),
                    Vector2.zero, Vector2.zero);
                ((RectTransform)fr).anchoredPosition = new Vector2(0, -39);
                ((RectTransform)fr).sizeDelta = new Vector2(92, 74);
                UiKit.RoundedImage(fr.gameObject, ColSepia).raycastTarget = false;
                var inn = NewUi("In", fr);
                Anchor(inn, Vector2.zero, Vector2.one, new Vector2(2, 2), new Vector2(-2, -2));
                var innImg = inn.gameObject.AddComponent<Image>();
                if (art != null) innImg.sprite = art;
                else innImg.color = UiKit.IdColor(id, 0.4f, 0.6f);
                innImg.raycastTarget = false;
                inn.gameObject.AddComponent<Mask>().showMaskGraphic = true;
            }
            else
            {
                var pGo = NewUi("P", item);
                Anchor(pGo, new Vector2(0.5f, 1), new Vector2(0.5f, 1),
                    Vector2.zero, Vector2.zero);
                ((RectTransform)pGo).anchoredPosition = new Vector2(0, -44);
                ((RectTransform)pGo).sizeDelta = new Vector2(76, 76);   // квадрат с отступом сверху/снизу — не лезет за край и на подпись
                var img = pGo.gameObject.AddComponent<Image>();
                if (art != null) { img.sprite = art; img.preserveAspect = true; }
                else img.color = UiKit.IdColor(id, 0.4f, 0.62f);
                img.raycastTarget = false;
            }

            var t = AddText(item, label, 14, ColInkText, TextAnchor.UpperCenter, FontStyle.Italic);
            Anchor(t.transform, new Vector2(0, 0), new Vector2(1, 0),
                new Vector2(0, 0), new Vector2(0, 34));
            t.resizeTextForBestFit = true;
            t.resizeTextMinSize = 10;
            t.resizeTextMaxSize = 14;
        }

        // ================= АНИМАЦИИ =================

        private IEnumerator AnimateAction(int panelIdx, string addedChar, List<RuleEvent> events,
            List<World> snapshots)
        {
            yield return null;

            if (panelIdx >= _panelViews.Count) yield break;
            var panelView = _panelViews[panelIdx];
            if (panelView == null) yield break;

            if (addedChar != null)
            {
                // персонаж добавлен → выезжает в кадр (кукла подпрыгивает, плоский — поп)
                if (_rigs.TryGetValue(panelIdx + ":" + addedChar, out var addedRig) && addedRig != null)
                    StartCoroutine(addedRig.BounceIn(0.42f));
                else if (_tileMap[panelIdx].TryGetValue(addedChar, out var tile))
                    StartCoroutine(Tween.Scale(tile, 0.3f, 1f, 0.25f));
            }
            else
            {
                // сцена поставлена → кадр «впечатывается»
                StartCoroutine(Tween.Scale(panelView, 0.9f, 1f, 0.28f));
            }

            var seen = new HashSet<string>();
            var local = events
                .Where(e => e.PanelIndex == panelIdx)
                .Where(e => seen.Add(e.RuleId + "|" +
                    string.Join(",", e.Binding.Values.OrderBy(v => v))))
                .ToList();
            if (local.Count == 0)
            {
                // действие собрано, но ни одно правило не сработало → анимированный «промах»
                var why = MisfireReason(panelIdx, snapshots);
                if (addedChar != null && why != null)
                {
                    StartCoroutine(Tween.Pulse(panelView, 0.05f, 0.4f));
                    if (_tileMap[panelIdx].TryGetValue(addedChar, out var mt) && mt != null)
                        StartCoroutine(Tween.Shake(mt, 8f, 0.3f));
                    yield return new WaitForSecondsRealtime(0.14f);
                    SpawnFloatLabel(panelView, why,
                        UiKit.Hex("#f6ddca"), new Color(0.59f, 0.19f, 0.16f, 0.92f));
                }
                yield break;
            }
            yield return new WaitForSecondsRealtime(0.18f);

            foreach (var ev in local)
            {
                Sfx.PlayRule(ev.RuleId);
                bool lethal = ev.RuleId == "betrayal_kill" || ev.RuleId == "battle_justice";
                foreach (var charId in ev.Binding.Values.Distinct())
                {
                    if (!_tileMap[panelIdx].TryGetValue(charId, out var t) || t == null) continue;
                    if (lethal) StartCoroutine(Tween.Shake(t, 8f, 0.3f));
                    else StartCoroutine(Tween.Pulse(t, 0.12f, 0.25f));
                }
                SpawnFloatLabel(panelView, RuleLabel.TryGetValue(ev.RuleId, out var lbl)
                    ? lbl : ev.RuleId);
                if (ev.RuleId == "charm") { SpawnHearts(panelView, 5); PlayCharm(panelIdx, ev); }
                yield return new WaitForSecondsRealtime(0.30f);
            }
        }

        /// <summary>Анимация «очарования»: чародейка тянется к собеседнику, тот кивает.</summary>
        private void PlayCharm(int panelIdx, RuleEvent ev)
        {
            if (ev.Binding == null) return;
            ev.Binding.TryGetValue("A", out var charmer);   // обаятельный (tags: charming)
            ev.Binding.TryGetValue("B", out var charmed);    // тот, кого влюбляют
            if (string.IsNullOrEmpty(charmer) || string.IsNullOrEmpty(charmed)) return;
            var cast = _panels[panelIdx].Characters;
            float dir = cast.IndexOf(charmed) >= cast.IndexOf(charmer) ? 1f : -1f;

            if (_rigs.TryGetValue(panelIdx + ":" + charmer, out var ra) && ra != null)
                StartCoroutine(CharmLean(ra, dir));
            if (_rigs.TryGetValue(panelIdx + ":" + charmed, out var rb) && rb != null)
                StartCoroutine(CharmNod(rb, -dir));
        }

        private IEnumerator CharmLean(CharacterRig r, float dir)
        {
            StartCoroutine(r.RaiseFrontArm(dir, 50f, 0.3f));
            yield return r.LeanToward(dir, 13f, 0.35f);
            StartCoroutine(r.HeadTilt(dir, 12f, 0.25f));
            yield return new WaitForSecondsRealtime(0.55f);
            yield return r.Relax(0.3f);
        }

        private IEnumerator CharmNod(CharacterRig r, float dir)
        {
            yield return r.HeadTilt(dir, 12f, 0.25f);
            yield return new WaitForSecondsRealtime(0.4f);
            yield return r.Relax(0.25f);
        }

        /// <summary>Сердечки, всплывающие из центра кадра (реакция на «очарование»).</summary>
        private void SpawnHearts(Transform panelView, int count = 4)
        {
            var sprite = UiKit.LoadArt("icon_love");
            if (sprite == null) return;
            for (int i = 0; i < count; i++)
            {
                var go = NewUi("Heart", panelView);
                var rt = (RectTransform)go;
                rt.anchorMin = rt.anchorMax = new Vector2(0.5f, 0.42f);
                rt.sizeDelta = new Vector2(34, 34);
                rt.anchoredPosition = new Vector2(Random.Range(-55f, 55f), Random.Range(-10f, 25f));
                var img = go.gameObject.AddComponent<Image>();
                img.sprite = sprite; img.preserveAspect = true; img.raycastTarget = false;
                var delta = new Vector2(Random.Range(-25f, 25f), 95f + Random.Range(0f, 50f));
                StartCoroutine(DelayedDrift(go.gameObject, delta, 0.95f, i * 0.07f, 0.3f, 1f));
            }
        }

        /// <summary>Залп конфетти из центра экрана на победу.</summary>
        private void SpawnConfetti(Transform parent, int count = 18)
        {
            string[] cols = { "#c8a356", "#a8443e", "#7c9437", "#5d7a3a", "#a07a2a", "#7a4a7a" };
            for (int i = 0; i < count; i++)
            {
                var go = NewUi("Confetti", parent);
                var rt = (RectTransform)go;
                rt.anchorMin = rt.anchorMax = new Vector2(0.5f, 0.58f);
                rt.sizeDelta = new Vector2(Random.Range(10f, 18f), Random.Range(10f, 18f));
                rt.anchoredPosition = Vector2.zero;
                rt.localRotation = Quaternion.Euler(0, 0, Random.Range(0f, 360f));
                var img = UiKit.RoundedImage(go.gameObject, UiKit.Hex(cols[i % cols.Length]));
                img.raycastTarget = false;
                float ang = Random.Range(0f, Mathf.PI * 2f);
                float dist = Random.Range(140f, 340f);
                var delta = new Vector2(Mathf.Cos(ang) * dist, Mathf.Sin(ang) * dist * 0.75f + 80f);
                StartCoroutine(Tween.Drift(go.gameObject, delta, Random.Range(0.8f, 1.2f),
                    1f, 1f, Random.Range(-220f, 220f)));
            }
        }

        private IEnumerator DelayedDrift(GameObject go, Vector2 delta, float dur, float delay,
            float startScale, float endScale)
        {
            if (go == null) yield break;
            go.SetActive(false);
            yield return new WaitForSecondsRealtime(delay);
            if (go == null) yield break;
            go.SetActive(true);
            yield return Tween.Drift(go, delta, dur, startScale, endScale);
        }

        private void SpawnFloatLabel(Transform panelView, string label)
            => SpawnFloatLabel(panelView, label,
                UiKit.Hex("#ecd9a8"), new Color(0.29f, 0.21f, 0.12f, 0.88f));

        private void SpawnFloatLabel(Transform panelView, string label, Color textCol, Color bgCol)
        {
            var go = NewUi("Float", panelView);
            var rt = (RectTransform)go;
            rt.anchorMin = new Vector2(0.5f, 0.55f);
            rt.anchorMax = new Vector2(0.5f, 0.55f);
            rt.sizeDelta = new Vector2(230, 42);
            var bgImg = UiKit.RoundedImage(go.gameObject, bgCol);
            bgImg.raycastTarget = false;
            var t = AddText(go, label, 24, textCol,
                TextAnchor.MiddleCenter, FontStyle.BoldAndItalic);
            Stretch(t.transform);
            StartCoroutine(Tween.FloatUp(go, 80f, 0.9f));
        }

        /// <summary>Почему действие в кадре не сработало — короткая подсказка игроку.</summary>
        private string MisfireReason(int panelIdx, List<World> snapshots)
        {
            var p = _panels[panelIdx];
            if (p.SceneId == null) return null;
            if (p.Characters.Count < 2) return null;          // ещё не собрана пара — не промах
            var snap = snapshots != null && panelIdx < snapshots.Count ? snapshots[panelIdx] : null;
            if (snap != null)
                foreach (var c in p.Characters)
                    if (snap.HasFlag(c, "locked_out")) return "Её не впускают сюда";
            return "Здесь ничего не складывается";
        }

        private IEnumerator WinSequence(List<RuleEvent> events)
        {
            _gameGroup.interactable = false;
            _gameGroup.blocksRaycasts = false;
            yield return new WaitForSecondsRealtime(0.35f);

            for (int i = 0; i < _panelViews.Count; i++)
            {
                if (_panelViews[i] != null)
                    StartCoroutine(Tween.Pulse(_panelViews[i], 0.07f, 0.3f));
                var ev = events.FirstOrDefault(e => e.PanelIndex == i);
                if (ev != null) Sfx.PlayRule(ev.RuleId);
                yield return new WaitForSecondsRealtime(0.32f);
            }

            yield return new WaitForSecondsRealtime(0.2f);

            // галочка цели уже стоит (поставлена мгновенно при сборке) — добавим залп конфетти
            SpawnConfetti(_gameRoot.transform, 22);
            StartCoroutine(Tween.Pulse(_goalBox.transform, 0.3f, 0.4f));
            yield return new WaitForSecondsRealtime(0.35f);

            var fc = Lv.FactCard;
            string acc = fc?.Accuracy ?? "fact";
            _accText.text = acc == "fact" ? "ФАКТ" : acc == "legend" ? "ЛЕГЕНДА" : "УПРОЩЕНИЕ";
            _accBg.color = acc == "fact" ? UiKit.Hex("#5d7a3a")
                : acc == "legend" ? UiKit.Hex("#7a4a7a") : UiKit.Hex("#a07a2a");
            _factText.text = fc?.Text ?? "";
            _srcText.text = fc != null ? "— " + fc.Source : "";
            _nextLevelBtn.GetComponentInChildren<Text>().text =
                _levelIdx < _levels.Count - 1 ? "Дальше →" : "К главе";

            _overlay.SetActive(true);
            _overlay.transform.SetAsLastSibling();
            _overlayGroup.alpha = 0f;
            StartCoroutine(Tween.Fade(_overlayGroup, 0f, 1f, 0.3f));
            yield return Tween.Scale(_card, 0.8f, 1f, 0.35f);
        }

        // ================= UI-ХЕЛПЕРЫ =================

        /// <summary>Пиктограммы между парой фигур: любовь / зависть / союз.</summary>
        private List<string> PairIcons(World snap, string a, string b)
        {
            var icons = new List<string>();
            if (snap.HasRelation("loves", a, b) || snap.HasRelation("loves", b, a))
                icons.Add("icon_love");
            if (snap.HasRelation("envies", a, b) || snap.HasRelation("envies", b, a))
                icons.Add("icon_envy");
            if (icons.Count == 0 &&
                (snap.HasRelation("ally_of", a, b) || snap.HasRelation("ally_of", b, a)))
                icons.Add("icon_ally");
            return icons;
        }

        /// <summary>Обмен ролями в кадре (2 фигуры — своп, 3 — ротация).</summary>
        private void SwapPanel(int idx)
        {
            var list = _panels[idx].Characters;
            if (list.Count < 2) return;
            if (list.Count == 2)
            {
                var t = list[0];
                list[0] = list[1];
                list[1] = t;
            }
            else
            {
                var f = list[0];
                list.RemoveAt(0);
                list.Add(f);
            }
            Sfx.Play("select");
            Render(idx, null);
        }

        private static Transform NewUi(string name, Transform parent)
        {
            var go = new GameObject(name, typeof(RectTransform));
            go.transform.SetParent(parent, false);
            return go.transform;
        }

        private static RectTransform Anchor(Transform t,
            Vector2 aMin, Vector2 aMax, Vector2 offMin, Vector2 offMax)
        {
            var rt = (RectTransform)t;
            rt.anchorMin = aMin;
            rt.anchorMax = aMax;
            rt.offsetMin = offMin;
            rt.offsetMax = offMax;
            return rt;
        }

        private Button AnchoredButton(Transform parent, string label,
            UnityEngine.Events.UnityAction onClick, Color bg, Color fg,
            Vector2 anchor, Vector2 pos, float w, float h, int fontSize)
        {
            var go = NewUi("Btn_" + label, parent);
            var rt = (RectTransform)go;
            rt.anchorMin = anchor;
            rt.anchorMax = anchor;
            rt.anchoredPosition = pos;
            rt.sizeDelta = new Vector2(w, h);
            UiKit.RoundedImage(go.gameObject, bg);
            var btn = go.gameObject.AddComponent<Button>();
            btn.onClick.AddListener(onClick);
            var t = AddText(go, label, fontSize, fg, TextAnchor.MiddleCenter);
            Stretch(t.transform);
            return btn;
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
            ((RectTransform)go).sizeDelta = new Vector2(width, height);
            var le = go.gameObject.AddComponent<LayoutElement>();
            le.preferredWidth = width;
            le.preferredHeight = height;
            UiKit.RoundedImage(go.gameObject, bg);
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

        private static string Initials(string name)
        {
            var words = name.Split(' ');
            return words.Length >= 2
                ? char.ToUpper(words[0][0]).ToString() + char.ToUpper(words[words.Length - 1][0])
                : name.Substring(0, Mathf.Min(2, name.Length)).ToUpper();
        }
    }
}
