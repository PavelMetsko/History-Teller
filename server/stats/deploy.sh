#!/bin/sh
# Деплой сервера статистики (Cloudflare Worker + D1) одной командой.
#   sh server/stats/deploy.sh 'ПАРОЛЬ_АДМИНКИ'
# Нужен вход в Cloudflare: npx wrangler login (один раз).
set -e
cd "$(dirname "$0")"
PW="$1"
[ -n "$PW" ] || { echo "usage: sh deploy.sh 'admin-password'"; exit 1; }

# База: создаём, если её ещё нет, и вписываем её id в wrangler.toml.
if grep -q REPLACE_WITH_D1_ID wrangler.toml; then
  ID=$(npx wrangler d1 create ht-stats 2>&1 | grep -Eo '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' | head -1)
  [ -n "$ID" ] || ID=$(npx wrangler d1 list --json | python3 -c "import sys,json;print([d['uuid'] for d in json.load(sys.stdin) if d['name']=='ht-stats'][0])")
  sed -i '' "s/REPLACE_WITH_D1_ID/$ID/" wrangler.toml
  echo "D1 ht-stats: $ID"
fi

npx wrangler d1 execute ht-stats --remote --file=schema.sql
npx wrangler deploy
printf '%s' "$PW" | npx wrangler secret put ADMIN_PASSWORD

echo "проверка:"
curl -s -o /dev/null -w "POST /e -> %{http_code}\n" -X POST https://stats.historyteller.app/e \
  -H 'content-type: application/json' -d '{"iid":"deploy-check","platform":"ios","events":[]}'
curl -s -o /dev/null -w "GET /admin/stats -> %{http_code}\n" https://stats.historyteller.app/admin/stats \
  -H "authorization: Bearer $PW"
