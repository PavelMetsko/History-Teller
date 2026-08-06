// Прокси между редактором в браузере и GitHub.
//
// Токен живёт секретом Worker'а и в браузер не попадает: репозиторий публичный, редактор
// раздаётся статикой, и любой ключ в клиентском коде утёк бы вместе с ним.
//
// Доступ к самому Worker'у закрывает Cloudflare Access — он пускает только владельца,
// поэтому отдельной авторизации здесь нет.
//
// Секреты (wrangler secret put):
//   GITHUB_TOKEN   fine-grained PAT на этот репозиторий: contents=write, actions=write
// Переменные (wrangler.toml):
//   REPO, BRANCH, CDN_BASE

const api = 'https://api.github.com';

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const cors = {
      'Access-Control-Allow-Origin': env.ALLOW_ORIGIN || '*',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    };
    if (request.method === 'OPTIONS') return new Response(null, { headers: cors });

    const reply = (body, status = 200) =>
      new Response(JSON.stringify(body), {
        status,
        headers: { ...cors, 'Content-Type': 'application/json; charset=utf-8' },
      });

    try {
      if (url.pathname === '/api/version') return reply(await version(env));
      if (url.pathname === '/api/save' && request.method === 'POST') {
        return reply(await save(env, await request.json()));
      }
      if (url.pathname === '/api/publish' && request.method === 'POST') {
        return reply(await publish(env));
      }
      return reply({ ok: false, error: 'нет такого маршрута' }, 404);
    } catch (e) {
      return reply({ ok: false, error: e.message }, 500);
    }
  },
};

const gh = async (env, path, init = {}) => {
  const r = await fetch(`${api}/repos/${env.REPO}${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${env.GITHUB_TOKEN}`,
      Accept: 'application/vnd.github+json',
      'User-Agent': 'history-teller-editor',
      ...(init.body ? { 'Content-Type': 'application/json' } : {}),
    },
  });
  const text = await r.text();
  if (!r.ok) throw new Error(`GitHub ${r.status}: ${text.slice(0, 300)}`);
  return text ? JSON.parse(text) : {};
};

/** Версия, которая сейчас реально лежит в облаке. */
async function version(env) {
  const r = await fetch(`${env.CDN_BASE}/manifest.json`, { cf: { cacheTtl: 0 } });
  if (!r.ok) return { version: 0 };
  return { version: (await r.json()).version ?? 0 };
}

/**
 * Одна правка — один коммит, даже если файлов несколько.
 *
 * Через Contents API вышло бы по коммиту на файл, и история распалась бы на «поправил ru»,
 * «поправил en», «поправил уровень» без общего смысла. Поэтому собираем дерево вручную:
 * блобы → дерево поверх текущего → коммит → сдвиг ветки.
 */
async function save(env, { files, binary, message }) {
  const branch = env.BRANCH || 'main';
  const textPaths = Object.keys(files || {});
  const binPaths = Object.keys(binary || {});
  const paths = [...textPaths, ...binPaths];
  if (!paths.length) return { ok: false, error: 'нечего сохранять' };

  for (const p of paths) {
    // Путь приходит из браузера — пускаем строго внутрь Content/.
    if (p.includes('..') || !/^[\w./-]+$/.test(p)) {
      return { ok: false, error: `недопустимый путь: ${p}` };
    }
  }

  const ref = await gh(env, `/git/ref/heads/${branch}`);
  const head = ref.object.sha;
  const headCommit = await gh(env, `/git/commits/${head}`);

  // Дерево принимает только текст, поэтому картинки сперва загружаем блобами
  // и кладём в дерево по их sha.
  const blobs = {};
  for (const p of binPaths) {
    const blob = await gh(env, '/git/blobs', {
      method: 'POST',
      body: JSON.stringify({ content: binary[p], encoding: 'base64' }),
    });
    blobs[p] = blob.sha;
  }

  const tree = await gh(env, '/git/trees', {
    method: 'POST',
    body: JSON.stringify({
      base_tree: headCommit.tree.sha,
      tree: [
        ...textPaths.map(p => ({
          path: `Content/${p}`, mode: '100644', type: 'blob', content: files[p],
        })),
        ...binPaths.map(p => ({
          path: `Content/${p}`, mode: '100644', type: 'blob', sha: blobs[p],
        })),
      ],
    }),
  });

  const commit = await gh(env, '/git/commits', {
    method: 'POST',
    body: JSON.stringify({
      message: message || `Правка контента из редактора: ${paths.join(', ')}`,
      tree: tree.sha,
      parents: [head],
    }),
  });

  await gh(env, `/git/refs/heads/${branch}`, {
    method: 'PATCH',
    body: JSON.stringify({ sha: commit.sha }),
  });

  return { ok: true, written: paths, commit: commit.sha.slice(0, 7) };
}

/**
 * Запускает workflow публикации. Он же прогоняет валидатор, поэтому сломанный контент
 * до облака не доедет — здесь ничего проверять не нужно.
 */
async function publish(env) {
  const branch = env.BRANCH || 'main';
  await gh(env, '/actions/workflows/publish-content.yml/dispatches', {
    method: 'POST',
    body: JSON.stringify({ ref: branch }),
  });
  return { ok: true, dispatched: true };
}
