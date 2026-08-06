#!/bin/sh
# Сборка редактора: движок в JS + локальный запуск.
#
# editor/engine.js — собранный артефакт, в гит не коммитится. Пересобирать после любой
# правки движка, иначе редактор будет валидировать старой логикой.
set -e
cd "$(dirname "$0")/.."

echo "→ собираю движок под JS"
(cd android && ./gradlew -q :engine-js:build)
cp android/engine-js/build/dist/js/productionExecutable/engine-js.js editor/engine.js
echo "  editor/engine.js — $(du -h editor/engine.js | cut -f1)"

# Состав глав редактор берёт из манифеста: по HTTP каталог не перечислить.
if [ ! -f dist/content/manifest.json ]; then
    echo "→ манифеста нет, собираю"
    python3 tools/publish_content.py >/dev/null
fi

echo
echo "готово. Запуск (из корня репозитория):"
echo "    python3 -m http.server 8080"
echo "    открыть http://localhost:8080/editor/"
