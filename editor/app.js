// Редактор контента History Teller.
//
// Валидация идёт тем же движком, что и в игре (engine.js собран из :engine-js), но в воркере:
// солвер брутфорсный и на тяжёлых уровнях думает десятки секунд.
//
// Правки копятся в черновике и уезжают на диск по кнопке. Сохранять на каждое нажатие нельзя:
// одна буква в тексте — это перезапись файла каталога, а их девять.

// Два режима работы. Локально страница отдаётся dev-сервером из корня репозитория: контент
// лежит рядом, правки пишутся прямо в рабочее дерево и видны в `git diff`. На хостинге контент
// читается из публичного репозитория, а пишется через Worker, который держит токен у себя.
const LOCAL = ['localhost', '127.0.0.1'].includes(location.hostname);

const CFG = LOCAL ? {
  content: '../Content',
  manifest: '../dist/content/manifest.json',
  api: '',
} : {
  content: 'https://raw.githubusercontent.com/PavelMetsko/History-Teller/main/Content',
  manifest: 'https://pub-6903ffa4531e43d19ab534800387df28.r2.dev/manifest.json',
  api: 'https://history-teller-editor-api.workers.dev',
};

const readText = (p) => fetch(`${CFG.content}/${p}`).then(r => {
  if (!r.ok) throw new Error(`${p}: HTTP ${r.status}`);
  return r.text();
});
const readJson = (p) => readText(p).then(JSON.parse);
const artUrl = (name) => `${CFG.content}/art/${name}.webp`;

const LANGS = ['ru', 'en', 'es', 'de', 'fr', 'it', 'pt', 'pl', 'nl'];

// Все читаемые человеком тексты живут в каталогах i18n под ключом level.<id>.<key>.
// В самом файле уровня их нет: он описывает только механику, а достоверность
// факт-карточки — метаданные, и остаётся там.
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

const state = {
  db: null, dbRaw: null, chapters: [], levels: [], disabled: new Set(),
  selected: null, i18n: {}, lang: 'ru',
  pending: new Map(),   // «<язык>|<ключ>» → новый текст
  draft: null,          // правленая копия уровня
  original: null,       // как уровень лежит на диске — чтобы понять, изменилось ли
  disabledOnDisk: [],
};

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
    state.disabledOnDisk = [...disabled].sort();

    const lists = await Promise.all(state.chapters.map(async (ch) => {
      const ids = await levelIdsOf(ch.id);
      return Promise.all(ids.map(id => readJson(`${ch.id}/levels/${id}.json`)));
    }));
    state.levels = lists.flat();

    status.textContent = `${state.chapters.length} глав · ${state.levels.length} уровней`;
    renderSidebar();
  } catch (err) {
    status.textContent = 'ошибка: ' + err.message;
  }
}

// Каталог по HTTP не перечислить, поэтому состав главы берём из манифеста — он же
// источник истины для игры. Локально его собирает tools/publish_content.py.
async function levelIdsOf(chapterId) {
  if (!state._manifest) {
    state._manifest = await fetch(CFG.manifest)
      .then(r => r.ok ? r.json() : Promise.reject(new Error(
        LOCAL ? 'нет dist/content/manifest.json — запусти tools/publish_content.py'
              : 'манифест недоступен: ' + CFG.manifest)));
  }
  return (state._manifest.chapters.find(c => c.id === chapterId)?.levels) ?? [];
}

// ---- список слева ----

function renderSidebar() {
  const el = document.getElementById('sidebar');
  el.innerHTML = '';
  for (const ch of state.chapters) {
    el.appendChild(node('<div class="chapter"></div>', h => h.textContent = `${ch.number}. ${ch.id}`));
    for (const lv of state.levels.filter(l => l.epoch === ch.id).sort((a, b) => a.order - b.order)) {
      el.appendChild(node('<div class="lvl"></div>', row => {
        row.dataset.id = lv.id;
        row.classList.toggle('sel', lv.id === state.selected);
        row.appendChild(node('<span class="ord"></span>', s => s.textContent = lv.order));
        row.appendChild(node('<span class="nm"></span>', s => s.textContent = txt(lv.id, 'title', 'ru') || lv.id));
        if (state.disabled.has(lv.id)) row.appendChild(node('<span class="off">ВЫКЛ</span>'));
        row.onclick = () => select(lv.id);
      }));
    }
  }
}

function select(id) {
  if (dirty() && !confirm('Есть несохранённые правки. Уйти и потерять их?')) return;
  state.selected = id;
  state.pending.clear();
  state.disabled = new Set(state.disabledOnDisk);
  state.original = state.levels.find(l => l.id === id);
  // Только что созданного на диске ещё нет — считаем, что менялось всё.
  state.draft = structuredClone(state.original);
  if (!state._manifest.chapters.some(c => c.levels.includes(id))) state.original = null;
  document.getElementById('main').classList.add('detail-open');
  renderSidebar();
  renderDetail();
}

const levelChanged = () => !!state.draft && JSON.stringify(state.draft) !== JSON.stringify(state.original);
const disabledChanged = () => JSON.stringify([...state.disabled].sort()) !== JSON.stringify(state.disabledOnDisk);
const dirty = () => state.pending.size > 0 || levelChanged() || disabledChanged();

/// Любая правка механики делает прежний вердикт враньём — прячем его.
function touched() {
  const v = document.getElementById('verdict');
  if (v) v.className = '';
  refreshSaveBar();
}

// ---- карточка уровня ----

function renderDetail() {
  const lv = state.draft;
  const el = document.getElementById('detail');
  el.className = 'open';
  el.innerHTML = '';

  el.appendChild(node('<h2></h2>', h => h.textContent = txt(lv.id, 'title', 'ru') || lv.id));
  el.appendChild(node('<div class="sub"></div>',
    d => d.textContent = `${lv.id} · ${lv.epoch} · порядок ${lv.order}`));

  el.appendChild(section('Тексты', textsEditor(lv)));
  el.appendChild(section('Каст', castEditor(lv)));
  el.appendChild(section('Сцены', scenesEditor(lv)));
  el.appendChild(section('Эталонное решение', solutionEditor(lv)));
  el.appendChild(section('Свойства', fieldsEditor(lv)));
  el.appendChild(section('Условие победы', goalEditor(lv)));
  el.appendChild(section('Валидация', validationBlock(lv)));
  el.appendChild(saveBar());
}

// ---- каст ----

function castEditor(lv) {
  return node('<div class="cast"></div>', row => {
    for (const cid of lv.characters) row.appendChild(charChip(cid, () => {
      lv.characters = lv.characters.filter(x => x !== cid);
      // Персонаж мог стоять в эталоне — иначе решение сошлётся в пустоту.
      for (const p of lv.solution ?? []) p.characters = (p.characters ?? []).filter(x => x !== cid);
      renderDetail(); touched();
    }));
    row.appendChild(addTile('персонажа', () => picker('Добавить персонажа',
      Object.values(state.db.characters).filter(c => !lv.characters.includes(c.id)),
      c => ({ id: c.id, name: c.name, art: 'char_' + c.id }),
      id => { lv.characters.push(id); renderDetail(); touched(); })));
  });
}

function charChip(cid, onRemove) {
  return node('<figure></figure>', f => {
    const img = document.createElement('img');
    img.src = artUrl('char_' + cid);
    img.alt = cid;
    img.onerror = () => img.replaceWith(node('<div class="miss">нет арта</div>'));
    f.appendChild(img);
    f.appendChild(node('<figcaption></figcaption>', c => c.textContent = state.db.characters[cid]?.name ?? cid));
    if (onRemove) f.appendChild(node('<button class="x">×</button>', b => { b.title = 'Убрать'; b.onclick = onRemove; }));
  });
}

// ---- сцены ----

function scenesEditor(lv) {
  return node('<div class="scenes"></div>', row => {
    for (const sid of lv.scenes) row.appendChild(node('<figure></figure>', f => {
      const img = document.createElement('img');
      img.src = artUrl('scene_' + sid);
      img.alt = sid;
      img.onerror = () => img.replaceWith(node('<div class="miss wide">нет арта</div>'));
      f.appendChild(img);
      f.appendChild(node('<figcaption></figcaption>', c =>
        c.textContent = `${state.db.scenes[sid]?.name ?? sid} · ${state.db.scenes[sid]?.slots ?? '?'} мест`));
      f.appendChild(node('<button class="x">×</button>', b => {
        b.title = 'Убрать';
        b.onclick = () => {
          lv.scenes = lv.scenes.filter(x => x !== sid);
          // Сцена могла стоять в эталоне и быть обложкой.
          for (const p of lv.solution ?? []) if (p.scene === sid) p.scene = lv.scenes[0] ?? null;
          if (lv.cover === sid) lv.cover = lv.scenes[0] ?? null;
          renderDetail(); touched();
        };
      }));
    }));
    row.appendChild(addTile('сцену', () => picker('Добавить сцену',
      Object.values(state.db.scenes).filter(s => !lv.scenes.includes(s.id)),
      s => ({ id: s.id, name: `${s.name} · ${s.slots} мест`, art: 'scene_' + s.id, wide: true }),
      id => { lv.scenes.push(id); renderDetail(); touched(); })));
  });
}

// ---- эталонное решение ----

function solutionEditor(lv) {
  if (!lv.solution) lv.solution = [];
  while (lv.solution.length < lv.panels) lv.solution.push({ scene: lv.scenes[0] ?? null, characters: [] });
  lv.solution.length = lv.panels;

  return node('<div class="panels"></div>', box => {
    lv.solution.forEach((p, i) => {
      const slots = state.db.scenes[p.scene]?.slots ?? 0;
      box.appendChild(node('<div class="panel edit"></div>', d => {
        d.appendChild(node('<div class="ph"></div>', ph => {
          if (p.scene) ph.style.backgroundImage = `url(${artUrl('scene_' + p.scene)})`;
          for (const cid of p.characters ?? []) {
            const img = document.createElement('img');
            img.src = artUrl('char_' + cid);
            img.alt = cid;
            ph.appendChild(img);
          }
        }));
        d.appendChild(node('<select></select>', sel => {
          for (const sid of lv.scenes) sel.appendChild(node('<option></option>', o => {
            o.value = sid;
            o.textContent = state.db.scenes[sid]?.name ?? sid;
            o.selected = sid === p.scene;
          }));
          sel.onchange = () => {
            p.scene = sel.value;
            // Мест в новой сцене может быть меньше — лишних убираем, иначе эталон невалиден.
            p.characters = (p.characters ?? []).slice(0, state.db.scenes[p.scene]?.slots ?? 0);
            renderDetail(); touched();
          };
        }));
        d.appendChild(node('<div class="slots"></div>', row => {
          for (const cid of lv.characters) {
            const on = (p.characters ?? []).includes(cid);
            row.appendChild(node('<button class="slot"></button>', b => {
              b.textContent = state.db.characters[cid]?.name ?? cid;
              b.classList.toggle('on', on);
              // Занять больше мест, чем есть в сцене, нельзя — движок такое не примет.
              b.disabled = !on && (p.characters?.length ?? 0) >= slots;
              b.onclick = () => {
                p.characters = on ? p.characters.filter(x => x !== cid) : [...(p.characters ?? []), cid];
                renderDetail(); touched();
              };
            }));
          }
        }));
        d.appendChild(node('<div class="cap"></div>',
          c => c.textContent = `панель ${i + 1} · ${p.characters?.length ?? 0} из ${slots}`));
      }));
    });
  });
}

// ---- свойства ----

function fieldsEditor(lv) {
  const FIELDS = [
    { k: 'order',  label: 'Порядок', type: 'number' },
    { k: 'panels', label: 'Панелей', type: 'number' },
    { k: 'act',    label: 'Акт' },
    { k: 'music',  label: 'Музыка' },
  ];
  return node('<div class="fields"></div>', box => {
    for (const f of FIELDS) box.appendChild(node('<label class="field small"></label>', label => {
      label.appendChild(node('<span></span>', s => s.textContent = f.label));
      label.appendChild(node('<input>', inp => {
        inp.type = f.type ?? 'text';
        inp.value = lv[f.k] ?? '';
        inp.oninput = () => {
          lv[f.k] = f.type === 'number' ? (parseInt(inp.value, 10) || 0) : inp.value;
          if (f.k === 'panels') renderDetail();
          touched();
        };
      }));
    }));

    box.appendChild(node('<label class="field small"></label>', label => {
      label.appendChild(node('<span>Обложка</span>'));
      label.appendChild(node('<select></select>', sel => {
        for (const sid of lv.scenes) sel.appendChild(node('<option></option>', o => {
          o.value = sid; o.textContent = state.db.scenes[sid]?.name ?? sid; o.selected = sid === lv.cover;
        }));
        sel.onchange = () => { lv.cover = sel.value; touched(); };
      }));
    }));

    box.appendChild(node('<label class="toggle"></label>', label => {
      const cb = node('<input type="checkbox">');
      cb.checked = state.disabled.has(lv.id);
      cb.onchange = () => {
        cb.checked ? state.disabled.add(lv.id) : state.disabled.delete(lv.id);
        renderSidebar();
        touched();
      };
      label.appendChild(cb);
      label.appendChild(node('<span>Выключен — не показывать в игре</span>'));
    }));
  });
}

// ---- цель ----

// Цель — дерево предикатов, и конструктор для него стоил бы дороже всего остального вместе.
// Формы целей повторяются, так что править их текстом и копировать с соседнего уровня —
// быстрее. Ошибку разбора показываем сразу: движок на сломанном JSON просто откажется считать.
function goalEditor(lv) {
  return node('<div></div>', box => {
    const err = node('<div class="note bad" style="display:none"></div>');
    box.appendChild(node('<textarea class="code" rows="14"></textarea>', ta => {
      ta.value = JSON.stringify(lv.goal, null, 1);
      ta.oninput = () => {
        try {
          lv.goal = JSON.parse(ta.value);
          err.style.display = 'none';
          ta.classList.remove('broken');
        } catch (e) {
          err.textContent = 'JSON не разбирается: ' + e.message;
          err.style.display = '';
          ta.classList.add('broken');
        }
        touched();
      };
    }));
    box.appendChild(err);
  });
}

// ---- создание уровня ----

function newLevel() {
  if (dirty() && !confirm('Есть несохранённые правки. Уйти и потерять их?')) return;
  const id = (prompt('id нового уровня (латиницей, станет именем файла):') || '').trim();
  if (!id) return;
  if (!/^[a-z0-9_]+$/.test(id)) return alert('Только строчные латинские буквы, цифры и подчёркивание.');
  if (state.levels.some(l => l.id === id)) return alert('Уровень с таким id уже есть.');

  const epoch = prompt('глава: ' + state.chapters.map(c => c.id).join(', '), state.chapters[0].id);
  if (!epoch || !state.chapters.some(c => c.id === epoch)) return;

  const last = state.levels.filter(l => l.epoch === epoch).sort((a, b) => a.order - b.order).at(-1);
  const level = {
    id, order: (last?.order ?? 0) + 10, act: last?.act ?? '', epoch, panels: 2,
    scenes: [], characters: [],
    goal: { all: [] },
    solution: [], cover: null, music: last?.music ?? 'tension',
    factCard: { accuracy: 'fact' },
  };
  state.levels.push(level);
  // Уровень появится у игроков только после публикации: манифест собирается из файлов,
  // а файла ещё нет — сначала сохранить.
  select(id);
  document.getElementById('saveinfo').textContent = 'новый уровень — сохрани, потом опубликуй';
}

// ---- валидация ----

function validationBlock(lv) {
  const verdict = node('<div id="verdict"></div>');
  const btn = node('<button></button>', b => {
    b.textContent = 'Проверить';
    b.onclick = async () => {
      b.disabled = true; b.textContent = 'Считаю…';
      const r = await analyze(JSON.stringify(lv));
      b.disabled = false; b.textContent = 'Проверить';
      showVerdict(verdict, r);
    };
  });
  return node('<div></div>', d => { d.appendChild(btn); d.appendChild(verdict); });
}

function showVerdict(box, r) {
  box.className = 'show';
  box.innerHTML = '';
  if (!r.ok) {
    box.appendChild(note('bad', 'Движок не смог разобрать уровень: ' + r.error));
    return;
  }
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
  } else if (r.distinct === 1) {
    box.appendChild(note('ok', 'Решение единственное — как надо.'));
  } else if (r.distinct <= 3) {
    box.appendChild(note('ok',
      `Различимых решений ${r.distinct}. Допустимо, но проверь, что все они читаются как одна и та же история.`));
  } else {
    box.appendChild(note('bad',
      `Различимых решений ${r.distinct} — цель свободна настолько, что игрок дойдёт случайно.`));
  }
  box.appendChild(node('<div class="dim"></div>',
    d => d.textContent = r.cached ? 'из кеша' : `посчитано за ${(r.ms / 1000).toFixed(1)} с`));
}

// ---- тексты ----

function textsEditor(lv) {
  return node('<div></div>', box => {
    box.appendChild(node('<div class="langs"></div>', tabs => {
      for (const l of LANGS) tabs.appendChild(node('<button class="lang"></button>', b => {
        b.textContent = l;
        b.classList.toggle('on', l === state.lang);
        b.onclick = () => { state.lang = l; renderDetail(); };
      }));
    }));

    for (const f of TEXTS) {
      const ruValue = txt(lv.id, f.key, 'ru');
      box.appendChild(node('<label class="field"></label>', label => {
        label.appendChild(node('<span></span>', s => s.textContent = f.label));
        const input = f.rows ? node('<textarea></textarea>', el => el.rows = f.rows) : node('<input type="text">');
        input.value = pendingOr(lv.id, f.key, state.lang);
        input.oninput = () => setPending(lv.id, f.key, state.lang, input.value);
        label.appendChild(input);
        // Перевод сверять с оригиналом можно только когда оригинал перед глазами.
        if (state.lang !== 'ru' && ruValue) {
          label.appendChild(node('<span class="ru"></span>', r => r.textContent = ruValue));
        }
      }));
    }
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

// ---- сохранение и публикация ----

function saveBar() {
  return node('<div class="savebar"></div>', bar => {
    bar.appendChild(node('<button id="save"></button>', b => { b.onclick = save; }));
    bar.appendChild(node('<button class="ghost" id="publish">Опубликовать</button>', b => { b.onclick = publish; }));
    bar.appendChild(node('<span id="saveinfo"></span>'));
    setTimeout(refreshSaveBar, 0);
  });
}

function refreshSaveBar() {
  const b = document.getElementById('save');
  if (!b) return;
  const n = state.pending.size + (levelChanged() ? 1 : 0) + (disabledChanged() ? 1 : 0);
  b.textContent = n ? `Сохранить (${n})` : 'Сохранено';
  b.disabled = n === 0;
}

async function save() {
  const b = document.getElementById('save');
  const info = document.getElementById('saveinfo');
  b.disabled = true; b.textContent = 'Сохраняю…';

  const files = {};

  // Тексты разложены по языкам; на диск уходят только затронутые каталоги.
  const byLang = new Map();
  for (const [k, value] of state.pending) {
    const cut = k.indexOf('|');
    const [lang, key] = [k.slice(0, cut), k.slice(cut + 1)];
    if (!byLang.has(lang)) byLang.set(lang, { ...state.i18n[lang] });
    byLang.get(lang)[key] = value;
  }
  for (const [lang, table] of byLang) files[`i18n/${lang}.json`] = JSON.stringify(table, null, 2) + '\n';

  if (levelChanged()) {
    files[`${state.draft.epoch}/levels/${state.draft.id}.json`] = JSON.stringify(state.draft, null, 1) + '\n';
  }
  if (disabledChanged()) {
    files['disabled.json'] = JSON.stringify([...state.disabled].sort(), null, 2) + '\n';
  }

  const r = await fetch(CFG.api + '/api/save', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ files }),
  }).then(x => x.json()).catch(e => ({ ok: false, error: e.message }));

  if (r.ok) {
    for (const [lang, table] of byLang) state.i18n[lang] = table;
    state.pending.clear();
    const i = state.levels.findIndex(l => l.id === state.draft.id);
    if (i >= 0) state.levels[i] = structuredClone(state.draft);
    state.original = state.levels[i];
    state.disabledOnDisk = [...state.disabled].sort();
    info.textContent = `записано: ${r.written.join(', ')}`;
    renderSidebar();
  } else {
    info.textContent = 'ошибка: ' + r.error;
  }
  refreshSaveBar();
}

async function publish() {
  const b = document.getElementById('publish');
  const info = document.getElementById('saveinfo');
  if (dirty() && !confirm('Есть несохранённые правки. Публиковать без них?')) return;
  b.disabled = true; b.textContent = 'Публикую…';
  info.textContent = 'валидатор → манифест → R2, это займёт пару минут';

  const version = LOCAL
    ? await fetch(CFG.api + '/api/version').then(r => r.json()).then(v => v.version + 1).catch(() => 0)
    : 0;   // в облаке номер выбирает CI, отталкиваясь от того, что реально лежит в R2
  const r = await fetch(CFG.api + '/api/publish', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ version }),
  }).then(x => x.json()).catch(e => ({ ok: false, error: e.message }));

  b.disabled = false; b.textContent = 'Опубликовать';
  if (!r.ok) {
    info.textContent = 'не опубликовано: ' + (r.error || (r.steps || []).filter(x => !x.ok).map(x => x.name).join(', '));
    if (r.steps) console.log(r.steps);
  } else if (r.dispatched) {
    // На хостинге публикацией занимается CI: он только запущен, результат будет позже.
    info.textContent = 'публикация запущена — идёт в GitHub Actions, займёт пару минут';
  } else {
    info.textContent = `опубликовано, версия ${version}`;
  }
}

// ---- выбор из каталога ----

function picker(title, items, shape, onPick) {
  const overlay = node('<div class="overlay"></div>');
  const search = node('<input class="search" placeholder="поиск…">');
  const grid = node('<div class="pickgrid"></div>');

  const draw = () => {
    const q = search.value.trim().toLowerCase();
    grid.innerHTML = '';
    for (const raw of items) {
      const it = shape(raw);
      if (q && !it.name.toLowerCase().includes(q) && !it.id.includes(q)) continue;
      grid.appendChild(node('<button class="pick"></button>', b => {
        const img = document.createElement('img');
        img.src = artUrl(it.art);
        if (it.wide) img.className = 'wide';
        img.onerror = () => img.replaceWith(node('<div class="miss">нет арта</div>'));
        b.appendChild(img);
        b.appendChild(node('<span></span>', s => s.textContent = it.name));
        b.onclick = () => { overlay.remove(); onPick(it.id); };
      }));
    }
    if (!grid.children.length) grid.appendChild(node('<div class="dim">ничего не найдено</div>'));
  };

  overlay.appendChild(node('<div class="sheet"></div>', sheet => {
    sheet.appendChild(node('<div class="sheethead"></div>', h => {
      h.appendChild(node('<b></b>', b => b.textContent = title));
      h.appendChild(node('<button class="ghost">Закрыть</button>', b => b.onclick = () => overlay.remove()));
    }));
    sheet.appendChild(search);
    sheet.appendChild(grid);
  }));
  overlay.onclick = (e) => { if (e.target === overlay) overlay.remove(); };
  document.body.appendChild(overlay);
  search.oninput = draw;
  draw();
  search.focus();
}

function addTile(what, onClick) {
  return node('<button class="add">+</button>', b => {
    b.title = 'Добавить ' + what;
    b.onclick = onClick;
  });
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

document.getElementById('newlevel').onclick = newLevel;
window.onbeforeunload = () => dirty() ? '' : undefined;
boot();
