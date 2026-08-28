// Счётчики прохождения глав.
//
// Хранится РОВНО одна вещь: строка-ключ и число. Ни идентификатора установки, ни времени,
// ни страны, ни версии — по базе нельзя ни узнать, кто играл, ни выстроить события в порядке.
// Это сделано намеренно: приложение обещает в политике, что не собирает о человеке ничего,
// и счётчик «главу N кто-то когда-то прошёл» этого обещания не трогает.
//
// Из-за этого же тут нет и не будет ответа на вопрос «этот покупатель играл до покупки?» —
// такой вопрос требует связать два события одного человека, а связывать нечем.
//
// Ключи (приложение шлёт каждый максимум один раз за установку):
//   open:<глава>            игрок открыл карту главы
//   done:<глава>:<уровень>  игрок прошёл эпизод
//
// Секреты (wrangler secret put):
//   READ_TOKEN   чем открывается GET / — иначе счётчики читал бы кто угодно
// Привязки (wrangler.toml):
//   DB           база D1 history-teller-stats

/** Ключи приходят из открытого интернета: пускаем только то, что похоже на наши. */
const KEY = /^(open:[a-z_]{1,24}|done:[a-z_]{1,24}:[a-z0-9_]{1,48})$/;
const MAX_KEYS = 16;

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    try {
      if (request.method === 'POST' && url.pathname === '/c') return await count(request, env);
      if (request.method === 'GET' && url.pathname === '/p') return await rates(request, env, ctx);
      if (request.method === 'GET' && url.pathname === '/') return await report(url, env);
      return new Response('нет такого маршрута\n', { status: 404 });
    } catch (e) {
      // Клиент шлёт счётчики «в никуда» и ответ не читает, но 500 в логах Worker'а
      // отличить от 204 полезно.
      return new Response(`${e.message}\n`, { status: 500 });
    }
  },
};

async function count(request, env) {
  let keys;
  try {
    keys = (await request.json()).e;
  } catch {
    return new Response('жду {"e":["done:rome:sabines"]}\n', { status: 400 });
  }
  if (!Array.isArray(keys)) return new Response('e должен быть списком\n', { status: 400 });

  // Дубли внутри одного запроса схлопываем: иначе один и тот же ключ дал бы +N.
  const clean = [...new Set(keys.filter((k) => typeof k === 'string' && KEY.test(k)))].slice(0, MAX_KEYS);
  if (!clean.length) return new Response(null, { status: 204 });

  // batch — одна транзакция и один заход в базу вместо N.
  await env.DB.batch(
    clean.map((k) =>
      env.DB.prepare('INSERT INTO counters (k, n) VALUES (?, 1) ON CONFLICT(k) DO UPDATE SET n = n + 1').bind(k)
    )
  );
  // 204 без тела: приложению ответ не нужен, а лишние байты оно шлёт по мобильной сети.
  return new Response(null, { status: 204 });
}

/**
 * Доли прохождения для игры: `{"rome":{"lucretia":71}}` — «эпизод прошли 71% из тех,
 * кто до него добрался».
 *
 * Наружу уходят ТОЛЬКО проценты. Абсолютные числа не отдаём ни в каком виде: пока игроков
 * мало, «прошли 3» на карточке читается как «игра мёртвая», и это ровно то, чего быть
 * не должно на витрине. По той же причине эпизод молчит, пока в знаменателе меньше
 * MIN_SAMPLE: «100%» с одного игрока — не факт, а шум.
 *
 * Знаменатель локальный — предыдущий эпизод главы, а для первого — открытия главы. Тогда
 * число читается как сложность («здесь спотыкаются»), а не как «докуда вообще доходят»:
 * от общего знаменателя доля падала бы монотонно просто потому, что эпизод дальше по списку.
 */
async function rates(request, env, ctx) {
  // Считаем по всей таблице и ходим в манифест — незачем делать это на каждый запуск игры.
  // Ключ кеша нормализуем: иначе `/p?что-угодно` — это промах мимо кеша, и любой желающий
  // гоняет D1 столько раз, сколько придумает разных строк.
  const cache = caches.default;
  const key = `${new URL(request.url).origin}/p`;
  const hit = await cache.match(key);
  if (hit) return hit;

  const [{ results }, manifest] = await Promise.all([
    env.DB.prepare('SELECT k, n FROM counters').all(),
    fetch(`${env.CDN_BASE}/manifest.json`, { cf: { cacheTtl: 600 } }).then((r) => r.json()),
  ]);
  const n = Object.fromEntries(results.map((r) => [r.k, r.n]));
  const min = Number(env.MIN_SAMPLE) || 20;

  const out = {};
  for (const chapter of manifest.chapters || []) {
    const levels = chapter.levels || [];
    const chapterRates = {};
    for (let i = 0; i < levels.length; i++) {
      // Порядок эпизодов берём из манифеста — он же задаёт порядок прохождения в игре.
      const denom = i === 0 ? n[`open:${chapter.id}`] : n[`done:${chapter.id}:${levels[i - 1]}`];
      if (!denom || denom < min) continue;
      const num = n[`done:${chapter.id}:${levels[i]}`] || 0;
      // Ноль означает «сюда ещё никто не дошёл», а не «эпизод непроходим», — но на карточке
      // читается именно вторым. Молчим, пока не пройдёт хоть кто-то.
      if (!num) continue;
      // Сверху обрезаем: у тех, кто обновился с версии без счётчиков, `done` есть, а `open` нет,
      // и числитель бывает больше знаменателя.
      chapterRates[levels[i]] = Math.min(100, Math.round((num / denom) * 100));
    }
    if (Object.keys(chapterRates).length) out[chapter.id] = chapterRates;
  }

  const response = new Response(JSON.stringify({ v: 1, p: out }), {
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': 'public, max-age=600',
    },
  });
  ctx.waitUntil(cache.put(key, response.clone()));
  return response;
}

async function report(url, env) {
  // Сравнение без раннего выхода: побайтовое сравнение строк подсказывало бы длину
  // совпавшего префикса тому, кто мерит время ответа.
  if (!safeEqual(url.searchParams.get('token') || '', env.READ_TOKEN || '')) {
    return new Response('нужен ?token=\n', { status: 401 });
  }
  const { results } = await env.DB.prepare('SELECT k, n FROM counters ORDER BY k').all();

  const opened = results.filter((r) => r.k.startsWith('open:'));
  const done = results.filter((r) => r.k.startsWith('done:'));
  const lines = ['ОТКРЫЛИ ГЛАВУ', ...row(opened, (k) => k.slice(5)), '', 'ПРОШЛИ ЭПИЗОД'];
  for (const chapter of [...new Set(done.map((r) => r.k.split(':')[1]))]) {
    lines.push(`  ${chapter}`);
    // По убыванию: воронка главы читается сверху вниз — сколько дошло до каждого эпизода.
    const inChapter = done.filter((r) => r.k.split(':')[1] === chapter).sort((a, b) => b.n - a.n);
    lines.push(...row(inChapter, (k) => `  ${k.split(':')[2]}`));
  }
  return new Response(lines.join('\n') + '\n', {
    headers: { 'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'no-store' },
  });
}

const row = (rows, name) =>
  rows.length ? rows.map((r) => `  ${name(r.k).padEnd(30)} ${r.n}`) : ['  (пусто)'];

function safeEqual(a, b) {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}
