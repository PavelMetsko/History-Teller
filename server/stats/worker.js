// Статистика игроков History Teller.
//
// POST /e            — события из игры (iOS и Android). Открыт для всех: принимаем только
//                      ожидаемые типы и поля, всё остальное отбрасываем.
// GET  /admin/stats  — сводка для скрытого экрана в iOS. Пароль приходит в заголовке
//                      Authorization: Bearer …, сверяется с секретом ADMIN_PASSWORD на сервере.

const TYPES = new Set(["session", "level_start", "level_complete", "ad_unlock",
  // 4.0: реклама и мета
  "hint_use", "hint_ad", "inter_show", "daily_open", "daily_done", "gift_claim",
  "streak_restore", "rank_up", "premium_open", "purchase"]);
const DAY = 86_400_000;
const ID = /^[A-Za-z0-9_\-.]{1,64}$/;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    try {
      if (request.method === "POST" && url.pathname === "/e") return await ingest(request, env);
      if (request.method === "GET" && url.pathname === "/admin/stats") return await stats(request, env);
      return new Response("not found", { status: 404 });
    } catch (e) {
      return json({ error: String(e && e.message || e) }, 500);
    }
  },
};

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
  });
}

const clean = (v, max = 32) => (typeof v === "string" && v.length && v.length <= max && ID.test(v)) ? v : null;

async function ingest(request, env) {
  if (Number(request.headers.get("content-length") || 0) > 16_384) return json({ error: "too large" }, 413);
  const body = await request.json().catch(() => null);
  const iid = clean(body && body.iid, 64);
  const platform = body && (body.platform === "ios" || body.platform === "android") ? body.platform : null;
  if (!iid || !platform || !Array.isArray(body.events)) return json({ error: "bad request" }, 400);

  const now = Date.now();
  const country = (request.cf && request.cf.country) || null;
  const stmts = [
    env.DB.prepare(
      `INSERT INTO players (iid, platform, app_version, lang, country, first_seen, last_seen)
       VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?6)
       ON CONFLICT(iid) DO UPDATE SET platform = ?2, app_version = ?3, lang = ?4,
         country = COALESCE(?5, country), last_seen = ?6`
    ).bind(iid, platform, clean(body.ver, 16), clean(body.lang, 8), country, now),
  ];
  for (const ev of body.events.slice(0, 50)) {
    if (!ev || !TYPES.has(ev.type)) continue;
    stmts.push(env.DB.prepare("INSERT INTO events (iid, ts, type, level, chapter) VALUES (?1, ?2, ?3, ?4, ?5)")
      .bind(iid, now, ev.type, clean(ev.level, 64), clean(ev.chapter, 32)));
  }
  await env.DB.batch(stmts);
  return json({ ok: true });
}

/** Сравнение без утечки по времени — пароль не угадать посимвольно. */
async function authorized(request, env) {
  const got = (request.headers.get("authorization") || "").replace(/^Bearer\s+/i, "");
  if (!env.ADMIN_PASSWORD || !got) return false;
  const enc = new TextEncoder();
  const [a, b] = await Promise.all([got, env.ADMIN_PASSWORD].map(s => crypto.subtle.digest("SHA-256", enc.encode(s))));
  const x = new Uint8Array(a), y = new Uint8Array(b);
  let diff = 0;
  for (let i = 0; i < x.length; i++) diff |= x[i] ^ y[i];
  return diff === 0;
}

async function stats(request, env) {
  if (!(await authorized(request, env))) return json({ error: "unauthorized" }, 401);
  const now = Date.now();
  const q = (sql, ...args) => env.DB.prepare(sql).bind(...args);
  const [players, chapters, levels, countries, langs, versions, recent,
         daily, dailyNew, chapterCountries, levelCountries, cohorts, activeDays, eventTypes] = await env.DB.batch([
    q(`SELECT COUNT(*) total,
         SUM(platform = 'ios') ios, SUM(platform = 'android') android,
         SUM(first_seen >= ?1) new1, SUM(first_seen >= ?2) new7,
         SUM(last_seen >= ?1) active1, SUM(last_seen >= ?2) active7, SUM(last_seen >= ?3) active30
       FROM players`, now - DAY, now - 7 * DAY, now - 30 * DAY),
    q(`SELECT chapter,
         COUNT(DISTINCT CASE WHEN type = 'level_start' THEN iid END) players,
         SUM(type = 'level_start') starts,
         SUM(type = 'level_complete') completions,
         SUM(type = 'ad_unlock') ad_unlocks
       FROM events WHERE chapter IS NOT NULL GROUP BY chapter ORDER BY players DESC`),
    q(`SELECT level, chapter,
         COUNT(DISTINCT CASE WHEN type = 'level_start' THEN iid END) started,
         COUNT(DISTINCT CASE WHEN type = 'level_complete' THEN iid END) completed
       FROM events WHERE level IS NOT NULL GROUP BY level, chapter ORDER BY started DESC LIMIT 3000`),
    q(`SELECT COALESCE(country, '?') k, COUNT(*) n FROM players GROUP BY k ORDER BY n DESC LIMIT 250`),
    q(`SELECT COALESCE(lang, '?') k, COUNT(*) n FROM players GROUP BY k ORDER BY n DESC`),
    q(`SELECT platform || ' ' || COALESCE(app_version, '?') k, COUNT(*) n FROM players GROUP BY k ORDER BY n DESC LIMIT 10`),
    q(`SELECT e.ts, e.type, e.level, e.chapter, p.platform, p.country
       FROM events e LEFT JOIN players p ON p.iid = e.iid
       WHERE e.type != 'session' ORDER BY e.id DESC LIMIT 100`),
    // По дням (UTC) за 30 дней: сколько разных игроков что-то делали и сколько пришло новых.
    q(`SELECT ts / ${DAY} d, COUNT(DISTINCT iid) n FROM events WHERE ts >= ?1 GROUP BY d ORDER BY d`,
      now - 30 * DAY),
    q(`SELECT first_seen / ${DAY} d, COUNT(*) n FROM players WHERE first_seen >= ?1 GROUP BY d ORDER BY d`,
      now - 30 * DAY),
    // Откуда игроки глав и эпизодов: разные игроки, начавшие / прошедшие, по странам.
    q(`SELECT e.chapter, COALESCE(p.country, '?') k, COUNT(DISTINCT e.iid) n
       FROM events e LEFT JOIN players p ON p.iid = e.iid
       WHERE e.type = 'level_start' AND e.chapter IS NOT NULL
       GROUP BY e.chapter, k ORDER BY n DESC LIMIT 2000`),
    q(`SELECT e.level, COALESCE(p.country, '?') k,
         COUNT(DISTINCT CASE WHEN e.type = 'level_start' THEN e.iid END) started,
         COUNT(DISTINCT CASE WHEN e.type = 'level_complete' THEN e.iid END) completed
       FROM events e LEFT JOIN players p ON p.iid = e.iid
       WHERE e.level IS NOT NULL AND e.type IN ('level_start', 'level_complete')
       GROUP BY e.level, k ORDER BY started DESC LIMIT 8000`),
    // Удержание: игроки, пришедшие в день c (UTC), и кто из них заходил ровно через k дней.
    q(`SELECT c, COUNT(DISTINCT iid) n,
         COUNT(DISTINCT CASE WHEN k = 1 THEN iid END) d1,
         COUNT(DISTINCT CASE WHEN k = 3 THEN iid END) d3,
         COUNT(DISTINCT CASE WHEN k = 7 THEN iid END) d7,
         COUNT(DISTINCT CASE WHEN k = 14 THEN iid END) d14,
         COUNT(DISTINCT CASE WHEN k = 30 THEN iid END) d30,
         COUNT(DISTINCT CASE WHEN k >= 1 THEN iid END) back
       FROM (SELECT e.iid, p.first_seen / ${DAY} c, e.ts / ${DAY} - p.first_seen / ${DAY} k
             FROM events e JOIN players p ON p.iid = e.iid WHERE p.first_seen >= ?1)
       GROUP BY c ORDER BY c`, now - 60 * DAY),
    // Как часто возвращаются: сколько разных дней игрок заходил в игру.
    q(`SELECT days, COUNT(*) n FROM (SELECT COUNT(DISTINCT ts / ${DAY}) days FROM events GROUP BY iid)
       GROUP BY days ORDER BY days`),
    // Реклама и мета (4.0): сколько раз и сколько разных игроков, всего и за 7 дней.
    q(`SELECT type, COUNT(*) n, COUNT(DISTINCT iid) players, SUM(ts >= ?1) n7
       FROM events WHERE type NOT IN ('session', 'level_start', 'level_complete')
       GROUP BY type ORDER BY n DESC`, now - 7 * DAY),
  ]);
  return json({
    generatedAt: now,
    players: players.results[0],
    chapters: chapters.results,
    levels: levels.results,
    countries: countries.results,
    langs: langs.results,
    versions: versions.results,
    recent: recent.results,
    daily: daily.results,
    dailyNew: dailyNew.results,
    chapterCountries: chapterCountries.results,
    levelCountries: levelCountries.results,
    cohorts: cohorts.results,
    activeDays: activeDays.results,
    eventTypes: eventTypes.results,
  });
}
