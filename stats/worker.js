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
  async fetch(request, env) {
    const url = new URL(request.url);
    try {
      if (request.method === 'POST' && url.pathname === '/c') return await count(request, env);
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
