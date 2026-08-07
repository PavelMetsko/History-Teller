# Локализация History Teller

Единый каталог `Content/i18n/<lang>.json` (ключ→строка), и UI, и контент.
В бандл копируются как `ios/Modules/GameContent/Resources/i18n_<lang>.json`.
Языки: ru(база) en es de fr it pt pl nl. Активный язык: настройка `ht.lang` → локаль устройства → en.

Каталог — источник правды для всех текстов, включая русский. В файлах уровней текстов нет:
уровень описывает только механику. Имена персонажей и сцен пока живут в контенте
(`characters.json`, `scenes.json`), оттуда `extract.py` заводит для них ключи.

## Как добавить/перевести контент
1. Новые тексты пиши прямо в `Content/i18n/ru.json` (или через редактор).
2. `python3 tools/i18n/extract.py` — дописать ключи новых персонажей и сцен и услышать,
   где дыры: уровни без названия/цели и ключи-сироты. Каталог только дополняется,
   удалить ключ можно лишь руками.
3. `GEMINI_API_KEY=... python3 tools/i18n/translate.py --missing` — доперевести только новое.
   Без `--missing` гоняется весь каталог: дорого и перетряхивает выверенные строки.
4. Скопировать в бандл: `for f in Content/i18n/*.json; do cp "$f" ios/Modules/GameContent/Resources/i18n_$(basename $f); done`
5. `cd ios && tuist generate` (новые ресурсы) + сборка.

Ключи: level.<id>.{title,goal,hint,intro,fact,source}, char.<id>, scene.<id>[.action],
chapter.<id>.{title,subtitle}, map.<epoch>, act.<epoch>.<n>, ui.<key>.
Контент локализуется на загрузке (`RomeContent.localize`); UI — через `L10n.s(key)`.
