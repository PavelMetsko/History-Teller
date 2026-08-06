// Редактор контента History Teller.
//
// Валидация идёт тем же движком, что и в игре (собран в engine.js из :engine-js), но в воркере:
// солвер брутфорсный и на тяжёлых уровнях думает десятки секунд.

// Откуда берём исходный контент. Локально страница отдаётся из корня репозитория,
// поэтому Content/ лежит рядом. Хостинг будет читать через GitHub API — тогда меняется
// только эта функция.
const SRC = '../Content';
const readText = (p) => fetch(`${SRC}/${p}`).then(r => {
  if (!r.ok) throw new Error(`${p}: HTTP ${r.status}`);
  return r.text();
});
const readJson = (p) => readText(p).then(JSON.parse);
const artUrl = (name) => `${SRC}/art/${name}.webp`;

const LANGS = ['ru', 'en', 'es', 'de', 'fr', 'it', 'pt', 'pl', 'nl'];

// Все читаемые человеком тексты живут в каталогах i18n под ключом level.<id>.<key>.
// В самом файле уровня их нет: он описывает только механику (каст, сцены, цель-предикат,
// эталон), а достоверность факт-карточки — метаданные, и остаётся там.
const TEXTS = [
  { key: 'title',  label: 'Название' },
  { key: 'goal',   label: 'Цель', rows: 2 },
  { key: 'hint',   label: 'Подсказка', rows: 3 },
  { key: 'intro',  label: 'Вступление', rows: 2 },
  { key: 'fact',   label: 'Факт-карточка', rows: 5 },
  { key: 'source', label: 'Источник' },
];

const txt = (lid, key, lang) => state.i18n[lang]?.[`level.${lid}.${key}`] ?? '';
const txtKey = (lid, key) => `level.${lid}.${key}`;

const state = { db: null, dbRaw: null, chapters: [], levels: [], disabled: new Set(),
                selected: null, i18n: {}, lang: 'ru', pending: new Map() };

// ---- воркер ----

const worker = new Worker('worker.js');
let seq = 0;
const pending = new Map();
worker.onmessage = (e) => {
  const { id, result, cached } = e.data;
  const resolve = pending.get(id);
  if (resolve) { pending.delete(id); resolve({ ...result, cached }); }
};
const analyze = (levelJson) => new Promise((resolve) => {
  const id = ++seq;
  pending.set(id, resolve);
  worker.postMessage({ id, kind: 'analyze', db: state.dbRaw, level: levelJson });
});

// ---- загрузка ----

async function boot() {
  const status = document.getElementById('status');
  try {
    const [characters, scenes, rules, chapters, disabled, ...cats] = await Promise.all([
      readText('rome/characters.json'),
      readText('rome/scenes.json'),
      readText('rome/rules.json'),
      readJson('chapters.json'),
      readJson('disabled.json').catch(() => []),
      ...LANGS.map(l => readJson(`i18n/${l}.json`)),
    ]);
    state.i18n = Object.fromEntries(LANGS.map((l, i) => [l, cats[i]]));
    state.dbRaw = { characters, scenes, rules };
    state.db = {
      characters: Object.fromEntries(JSON.parse(characters).map(c => [c.id, c])),
      scenes: Object.fromEntries(JSON.parse(scenes).map(s => [s.id, s])),
    };
    state.chapters = chapters.sort((a, b) => a.number - b.number);
    state.disabled = new Set(disabled);

    // Уровни лежат по эпохам; имя файла совпадает с id.
    const lists = await Promise.all(state.chapters.map(async (ch) => {
      const ids = await levelIdsOf(ch.id);
      return Promise.all(ids.map(async (id) => ({ ...(await readJson(`${ch.id}/levels/${id}.json`)), _chapter: ch.id })));
    }));
    state.levels = lists.flat();

    status.textContent = `${state.chapters.length} глав · ${state.levels.length} уровней`;
    renderSidebar();
  } catch (err) {
    status.textContent = 'ошибка: ' + err.message;
  }
}

// Каталога уровней по HTTP не видно, поэтому состав главы берём из манифеста —
// он же источник истины для игры. Локально его собирает tools/publish_content.py.
async function levelIdsOf(chapterId) {
  if (!state._manifest) {
    state._manifest = await fetch('../dist/content/manifest.json')
      .then(r => r.ok ? r.json() : Promise.reject(new Error('нет dist/content/manifest.json — запусти tools/publish_content.py')));
  }
  return (state._manifest.chapters.find(c => c.id === chapterId)?.levels) ?? [];
}

// ---- список слева ----

function renderSidebar() {
  const el = document.getElementById('sidebar');
  el.innerHTML = '';
  for (const ch of state.chapters) {
    const head = document.createElement('div');
    head.className = 'chapter';
    head.textContent = `${ch.number}. ${ch.id}`;
    el.appendChild(head);

    for (const lv of state.levels.filter(l => l._chapter === ch.id).sort((a, b) => a.order - b.order)) {
      const row = document.createElement('div');
      row.className = 'lvl';
      row.dataset.id = lv.id;
      row.innerHTML = `<span class="ord">${lv.order}</span><span class="nm"></span>`;
      row.querySelector('.nm').textContent = txt(lv.id, 'title', 'ru') || lv.id;
      if (state.disabled.has(lv.id)) {
        const off = document.createElement('span');
        off.className = 'off';
        off.textContent = 'ВЫКЛ';
        row.appendChild(off);
      }
      row.onclick = () => select(lv.id);
      el.appendChild(row);
    }
  }
}

function select(id) {
  state.selected = id;
  document.querySelectorAll('.lvl').forEach(r => r.classList.toggle('sel', r.dataset.id === id));
  document.getElementById('main').classList.add('detail-open');
  renderDetail(state.levels.find(l => l.id === id));
}

// ---- карточка уровня ----

function renderDetail(lv) {
  const el = document.getElementById('detail');
  el.className = 'open';
  el.innerHTML = '';

  el.appendChild(node(`<h2></h2>`, h => h.textContent = txt(lv.id, 'title', 'ru') || lv.id));
  el.appendChild(node(`<div class="sub"></div>`,
    d => d.textContent = `${lv.id} · ${lv._chapter} · порядок ${lv.order}${lv.act ? ' · ' + lv.act : ''}`));

  el.appendChild(section('Тексты', textsEditor(lv)));

  el.appendChild(section('Условие победы (механика)', node('<div></div>', d => {
    d.appendChild(node('<pre></pre>', p => p.textContent = JSON.stringify(lv.goal, null, 1)));
  })));

  el.appendChild(section('Каст', node('<div class="cast"></div>', box => {
    for (const cid of lv.characters) box.appendChild(charFigure(cid));
  })));

  el.appendChild(section('Сцены', node('<div class="scenes"></div>', box => {
    for (const sid of lv.scenes) box.appendChild(node('<figure></figure>', f => {
      const img = document.createElement('img');
      img.src = artUrl('scene_' + sid);
      img.alt = sid;
      f.appendChild(img);
      f.appendChild(node('<figcaption></figcaption>', c => {
        c.textContent = `${state.db.scenes[sid]?.name ?? sid} · ${state.db.scenes[sid]?.slots ?? '?'} мест`;
        c.style.cssText = 'font-size:10px;color:var(--ink-soft);margin-top:2px';
      }));
    }));
  })));

  if (lv.solution) {
    el.appendChild(section('Эталонное решение', node('<div class="panels"></div>', box => {
      for (const p of lv.solution) box.appendChild(panelCard(p));
    })));
  }

  // ---- проверка ----
  const verdict = node('<div id="verdict"></div>');
  const btn = node('<button></button>', b => {
    b.textContent = 'Проверить';
    b.onclick = async () => {
      b.disabled = true;
      b.textContent = 'Считаю…';
      const started = Date.now();
      const { _chapter, ...clean } = lv;
      const r = await analyze(JSON.stringify(clean));
      b.disabled = false;
      b.textContent = 'Проверить';
      showVerdict(verdict, r, Date.now() - started);
    };
  });
  el.appendChild(section('Валидация', node('<div></div>', d => { d.appendChild(btn); d.appendChild(verdict); })));


}

function showVerdict(box, r, wallMs) {
  box.className = 'show';
  box.innerHTML = '';
  if (!r.ok) {
    box.appendChild(note('bad', 'Движок не смог разобрать уровень: ' + r.error));
    return;
  }
  const tight = r.distinct === 1;
  box.appendChild(node('<div class="metrics"></div>', m => {
    m.appendChild(metric(r.raw, 'решений'));
    m.appendChild(metric(r.distinct, 'различимых'));
    m.appendChild(metric(r.searchSpace, 'перебор'));
  }));

  // Ломает уровень только первое; остальное — оттенки «туго/свободно», и врать про них нельзя:
  // инструмент, который кричит на рабочие уровни (rubicon живёт с двумя решениями), читать перестают.
  if (r.raw === 0) {
    box.appendChild(note('bad', 'Уровень нерешаем: ни одна расстановка не приводит к цели.'));
  } else if (r.solutionOk === false) {
    box.appendChild(note('bad', 'Эталонное решение НЕ приводит к цели — уровень сломан.'));
  } else if (r.solutionOk === null) {
    box.appendChild(note('bad', 'Поле solution не задано — эталон нечем проверить.'));
  } else if (tight) {
    box.appendChild(note('ok', 'Решение единственное — как надо.'));
  } else if (r.distinct <= 3) {
    box.appendChild(note('ok',
      `Различимых решений ${r.distinct}. Допустимо, но проверь, что все они читаются как одна и та же история.`));
  } else {
    box.appendChild(note('bad',
      `Различимых решений ${r.distinct} — цель свободна настолько, что игрок дойдёт случайно.`));
  }
  box.appendChild(node('<div style="font-size:11px;color:var(--ink-soft);margin-top:6px"></div>',
    d => d.textContent = r.cached ? 'из кеша' : `посчитано за ${(r.ms / 1000).toFixed(1)} с`));
}

// ---- редактор текстов ----

// Правки копятся в state.pending и уезжают на диск по кнопке: сохранять на каждую букву —
// это 9 файлов каталогов на каждое нажатие клавиши.
function textsEditor(lv) {
  return node('<div></div>', box => {
    box.appendChild(node('<div class="langs"></div>', tabs => {
      for (const l of LANGS) tabs.appendChild(node('<button class="lang"></button>', b => {
        b.textContent = l;
        b.classList.toggle('on', l === state.lang);
        b.onclick = () => { state.lang = l; renderDetail(lv); };
      }));
    }));

    for (const f of TEXTS) {
      const value = pendingOr(lv.id, f.key, state.lang);
      const ruValue = txt(lv.id, f.key, 'ru');
      box.appendChild(node('<label class="field"></label>', label => {
        label.appendChild(node('<span></span>', s2 => s2.textContent = f.label));
        const input = f.rows
          ? node('<textarea></textarea>', el => el.rows = f.rows)
          : node('<input type="text">');
        input.value = value;
        input.oninput = () => setPending(lv.id, f.key, state.lang, input.value);
        label.appendChild(input);
        // Перевод легко сверять с оригиналом, только когда оригинал перед глазами.
        if (state.lang !== 'ru' && ruValue) {
          label.appendChild(node('<span class="ru"></span>', r => r.textContent = ruValue));
        }
      }));
    }

    box.appendChild(saveBar());
  });
}

function pendingOr(lid, key, lang) {
  const k = `${lang}|${txtKey(lid, key)}`;
  return state.pending.has(k) ? state.pending.get(k) : txt(lid, key, lang);
}

function setPending(lid, key, lang, value) {
  const k = `${lang}|${txtKey(lid, key)}`;
  if (txt(lid, key, lang) === value) state.pending.delete(k);
  else state.pending.set(k, value);
  refreshSaveBar();
}

function saveBar() {
  return node('<div class="savebar"></div>', bar => {
    bar.appendChild(node('<button id="save"></button>', b => { b.onclick = save; }));
    bar.appendChild(node('<button class="ghost" id="publish"></button>', b => {
      b.textContent = 'Опубликовать';
      b.onclick = publish;
    }));
    bar.appendChild(node('<span id="saveinfo"></span>'));
    setTimeout(refreshSaveBar, 0);
  });
}

function refreshSaveBar() {
  const b = document.getElementById('save');
  if (!b) return;
  const n = state.pending.size;
  b.textContent = n ? `Сохранить (${n})` : 'Сохранено';
  b.disabled = n === 0;
}

async function save() {
  const b = document.getElementById('save');
  const info = document.getElementById('saveinfo');
  b.disabled = true; b.textContent = 'Сохраняю…';

  // Правки разложены по языкам; на диск уходят только затронутые каталоги.
  const byLang = new Map();
  for (const [k, value] of state.pending) {
    const [lang, key] = [k.slice(0, k.indexOf('|')), k.slice(k.indexOf('|') + 1)];
    if (!byLang.has(lang)) byLang.set(lang, { ...state.i18n[lang] });
    byLang.get(lang)[key] = value;
  }
  const files = {};
  for (const [lang, table] of byLang) files[`i18n/${lang}.json`] = JSON.stringify(table, null, 2) + '\n';

  const r = await fetch('/api/save', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ files }),
  }).then(x => x.json()).catch(e => ({ ok: false, error: e.message }));

  if (r.ok) {
    for (const [lang, table] of byLang) state.i18n[lang] = table;
    state.pending.clear();
    info.textContent = `записано: ${r.written.join(', ')}`;
    renderSidebar();
    document.querySelectorAll('.lvl').forEach(x => x.classList.toggle('sel', x.dataset.id === state.selected));
  } else {
    info.textContent = 'ошибка: ' + r.error;
  }
  refreshSaveBar();
}

async function publish() {
  const b = document.getElementById('publish');
  const info = document.getElementById('saveinfo');
  if (state.pending.size && !confirm('Есть несохранённые правки. Публиковать без них?')) return;
  b.disabled = true; b.textContent = 'Публикую…';
  info.textContent = 'валидатор → манифест → R2, это займёт пару минут';

  const version = await fetch('/api/version').then(r => r.json()).then(v => v.version + 1).catch(() => 0);
  const r = await fetch('/api/publish', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ version }),
  }).then(x => x.json()).catch(e => ({ ok: false, error: e.message }));

  b.disabled = false; b.textContent = 'Опубликовать';
  info.textContent = r.ok
    ? `опубликовано, версия ${version}`
    : 'не опубликовано: ' + (r.error || (r.steps || []).filter(s => !s.ok).map(s => s.name).join(', '));
  if (!r.ok && r.steps) console.log(r.steps);
}

// ---- мелкие помощники ----

function node(html, fn) {
  const t = document.createElement('template');
  t.innerHTML = html.trim();
  const el = t.content.firstElementChild;
  if (fn) fn(el);
  return el;
}
function section(title, body) {
  const s = document.createElement('section');
  s.appendChild(node('<h3></h3>', h => h.textContent = title));
  s.appendChild(body);
  return s;
}
function metric(value, label) {
  return node('<div class="metric"></div>', d => {
    d.appendChild(node('<b></b>', b => b.textContent = value));
    d.appendChild(node('<span></span>', s => s.textContent = label));
  });
}
function note(kind, text) {
  return node(`<div class="note ${kind}"></div>`, d => d.textContent = text);
}
function charFigure(cid) {
  return node('<figure></figure>', f => {
    const img = document.createElement('img');
    img.src = artUrl('char_' + cid);
    img.alt = cid;
    // Арта может не быть — это ошибка контента, и её надо видеть, а не гадать по битой картинке.
    img.onerror = () => img.replaceWith(node('<div class="miss">нет арта</div>'));
    f.appendChild(img);
    f.appendChild(node('<figcaption></figcaption>', c => c.textContent = state.db.characters[cid]?.name ?? cid));
  });
}
function panelCard(p) {
  return node('<div class="panel"></div>', d => {
    d.appendChild(node('<div class="ph"></div>', ph => {
      if (p.scene) ph.style.backgroundImage = `url(${artUrl('scene_' + p.scene)})`;
      for (const cid of p.characters ?? []) {
        const img = document.createElement('img');
        img.src = artUrl('char_' + cid);
        img.alt = cid;
        ph.appendChild(img);
      }
    }));
    d.appendChild(node('<div class="cap"></div>',
      c => c.textContent = state.db.scenes[p.scene]?.name ?? p.scene ?? '—'));
  });
}

boot();
