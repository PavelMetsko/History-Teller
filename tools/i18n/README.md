# Локализация History Teller

Единый каталог `Content/i18n/<lang>.json` (ключ→строка), и UI, и контент.
В бандл копируются как `ios/Modules/GameContent/Resources/i18n_<lang>.json`.
Языки: ru(база) en es de fr it pt pl nl. Активный язык: настройка `ht.lang` → локаль устройства → en.

## Как добавить/перевести контент
1. Обнови русские исходники (levels/characters/scenes JSON).
2. `python3 tools/i18n/extract.py` — пересобрать `Content/i18n/ru.json` (базовый каталог ключей).
3. `GEMINI_API_KEY=... python3 tools/i18n/translate.py [langs...]` — перевести (Gemini, батчами, имена локализуются).
4. Скопировать в бандл: `for f in Content/i18n/*.json; do cp "$f" ios/Modules/GameContent/Resources/i18n_$(basename $f); done`
5. `cd ios && tuist generate` (новые ресурсы) + сборка.

Ключи: level.<id>.{title,goal,hint,intro,fact,source}, char.<id>, scene.<id>[.action],
chapter.<id>.{title,subtitle}, map.<epoch>, act.<epoch>.<n>, ui.<key>.
Контент локализуется на загрузке (`RomeContent.localize`); UI — через `L10n.s(key)`.
