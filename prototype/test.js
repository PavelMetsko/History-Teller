// Паритет JS-движка с эталоном tools/simulate.py — data-driven по всем уровням.
const fs = require('fs');
const path = require('path');
const E = require('./engine.js');

const dir = path.join(__dirname, '..', 'Content', 'rome');
const read = f => JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8'));

const content = E.buildContent(read('characters.json'), read('scenes.json'), read('rules.json'));
const levels = fs.readdirSync(path.join(dir, 'levels')).sort()
  .map(f => read('levels/' + f));

let failed = 0;
function assert(cond, msg) {
  console.log((cond ? 'PASS' : 'FAIL') + ': ' + msg);
  if (!cond) failed++;
}

// Эталонные КАНОНИЧЕСКИЕ числа решений из tools/simulate.py
// (в сценах без ролей порядок персонажей не важен — дубли схлопываются)
const EXPECTED_SOLUTIONS = {
  caesar_assassination: 4,
  caesar_crown: 2,
  cleopatra_charm: 2,
  philippi: 1,
  rivals: 2
};

function canonicalCount(sols) {
  const seen = new Set();
  for (const sol of sols) {
    const key = sol.map(p => {
      const sc = content.scenes[p.sceneId];
      const chars = sc.roles ? p.characters : [...p.characters].sort();
      return p.sceneId + ':' + chars.join(',');
    }).join('|');
    seen.add(key);
  }
  return seen.size;
}

for (const lv of levels) {
  // 1. Эталонное решение уровня решает его
  const panels = lv.solution.map(p => ({ sceneId: p.scene, characters: p.characters }));
  const w = E.simulate(panels, content, null, null, E.initialWorld(lv));
  assert(E.goalMet(lv.goal, w), lv.id + ': эталонное решение решает уровень');

  // 2. Каноническое число решений совпадает с эталоном
  const n = canonicalCount(E.solve(lv, content).solutions);
  const exp = EXPECTED_SOLUTIONS[lv.id];
  assert(n === exp, lv.id + ': решений ' + n + ' (ожидалось ' + exp + ')');
}

// 3. Регрессия: мёртвый не действует (нет двойного убийства)
let w = E.simulate([
  { sceneId: 'forum', characters: ['caesar', 'brutus'] },
  { sceneId: 'back_room', characters: ['caesar', 'brutus'] },
  { sceneId: 'senate', characters: ['caesar', 'brutus'] }
], content);
assert(!(E.hasFlag(w, 'caesar', 'dead') && E.hasFlag(w, 'brutus', 'dead')), 'нет двойного убийства');

// 4. initialState: без стартового ally_of Филиппы нерешаемы
const philippi = levels.find(l => l.id === 'philippi');
const noInit = { ...philippi, initialState: {} };
assert(E.solve(noInit, content).solutions.length === 0, 'philippi: без initialState нерешаем (ally_of обязателен)');

// 5. Позиционные роли: charm работает только когда чарующая — в слоте 0
w = E.simulate([
  { sceneId: 'palace', characters: ['cleopatra', 'caesar'] }
], content);
assert(E.hasRel(w, 'loves', 'caesar', 'cleopatra') && !E.hasRel(w, 'loves', 'cleopatra', 'caesar'),
  'charm: чарующая в слоте 0 — работает');
w = E.simulate([
  { sceneId: 'palace', characters: ['caesar', 'cleopatra'] }
], content);
assert(!E.hasRel(w, 'loves', 'caesar', 'cleopatra'),
  'charm: чарующая в слоте 1 — НЕ работает (позиция важна)');

process.exit(failed ? 1 : 0);
