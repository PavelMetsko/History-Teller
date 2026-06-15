// History Teller — JS-движок симуляции. Семантика 1:1 с tools/simulate.py и Engine.cs.
'use strict';

function newWorld() {
  return { flags: {}, relations: new Set() };
}
function relKey(rel, from, to) { return rel + '|' + from + '|' + to; }
function hasFlag(w, c, f) { return !!(w.flags[c] && w.flags[c].has(f)); }
function setFlag(w, c, f) { (w.flags[c] = w.flags[c] || new Set()).add(f); }
function removeFlag(w, c, f) { if (w.flags[c]) w.flags[c].delete(f); }
function hasRel(w, rel, from, to) { return w.relations.has(relKey(rel, from, to)); }
function isAlive(w, c) { return !hasFlag(w, c, 'dead'); }

function actorMatches(actor, charId, binding, world, charDefs) {
  const def = charDefs[charId];
  for (const t of actor.tags || []) if (!def.tags.includes(t)) return false;
  for (const f of actor.flags || []) if (!hasFlag(world, charId, f)) return false;
  for (const f of actor.notFlags || []) if (hasFlag(world, charId, f)) return false;
  for (const rc of actor.relations || []) {
    const other = binding[rc.to];
    if (!other || !hasRel(world, rc.rel, charId, other)) return false;
  }
  return true;
}

function* permutations(items, k) {
  if (k === 0) { yield []; return; }
  if (k > items.length) return;
  for (let i = 0; i < items.length; i++) {
    const rest = items.slice(0, i).concat(items.slice(i + 1));
    for (const tail of permutations(rest, k - 1)) yield [items[i], ...tail];
  }
}

function findBindings(actors, present, world, charDefs) {
  const alive = present.filter(c => isAlive(world, c));
  const slotted = actors.filter(a => a.slot !== undefined && a.slot !== null);

  if (slotted.length) {
    // позиционные роли: актор с slot привязан к позиции в кадре
    const binding = {}, used = new Set();
    for (const a of slotted) {
      if (a.slot >= present.length) return [];
      const c = present[a.slot];
      if (!isAlive(world, c) || used.has(c)) return [];
      binding[a.var] = c;
      used.add(c);
    }
    const rest = actors.filter(a => a.slot === undefined || a.slot === null);
    const free = alive.filter(c => !used.has(c));
    const out = [];
    for (const perm of permutations(free, rest.length)) {
      const b = { ...binding };
      rest.forEach((a, i) => { b[a.var] = perm[i]; });
      if (actors.every(a => actorMatches(a, b[a.var], b, world, charDefs)))
        out.push(b);
    }
    return out;
  }

  const out = [];
  for (const perm of permutations(alive, actors.length)) {
    const binding = {};
    actors.forEach((a, i) => { binding[a.var] = perm[i]; });
    if (actors.every(a => actorMatches(a, binding[a.var], binding, world, charDefs)))
      out.push(binding);
  }
  return out;
}

function applyEffects(effects, binding, world) {
  for (const e of effects) {
    if (e.type === 'setFlag') setFlag(world, binding[e.target], e.flag);
    else if (e.type === 'removeFlag') removeFlag(world, binding[e.target], e.flag);
    else if (e.type === 'addRelation') world.relations.add(relKey(e.rel, binding[e.from], binding[e.to]));
    else if (e.type === 'removeRelation') world.relations.delete(relKey(e.rel, binding[e.from], binding[e.to]));
    else throw new Error('unknown effect type ' + e.type);
  }
}

// Мир со стартовыми условиями уровня (initialState).
function initialWorld(level) {
  const w = newWorld();
  const init = (level && level.initialState) || {};
  for (const c in (init.flags || {}))
    for (const f of init.flags[c]) setFlag(w, c, f);
  for (const [r, f, t] of (init.relations || []))
    w.relations.add(relKey(r, f, t));
  return w;
}

// panels: [{sceneId, characters:[]}]; rules уже отсортированы по priority desc.
// snapshots: если передан массив — туда пишется копия состояния после каждой панели (для UI).
// initial: стартовый мир (НЕ мутируется снаружи — передавайте свежий, напр. initialWorld(level)).
function simulate(panels, content, log, snapshots, initial) {
  const world = initial || newWorld();
  const rules = content.rulesByPriorityDesc;
  panels.forEach((panel, i) => {
    if (panel && panel.sceneId) {
      const sceneTags = content.scenes[panel.sceneId].tags;
      for (const rule of rules) {
        if (!(rule.trigger.sceneTags || []).every(t => sceneTags.includes(t))) continue;
        for (const binding of findBindings(rule.trigger.actors, panel.characters, world, content.characters)) {
          // Эффект в этой же панели мог инвалидировать биндинг (персонаж погиб) — перепроверка.
          const stillValid = rule.trigger.actors.every(a =>
            isAlive(world, binding[a.var]) &&
            actorMatches(a, binding[a.var], binding, world, content.characters));
          if (!stillValid) continue;
          applyEffects(rule.effects, binding, world);
          if (log) log.push('panel ' + (i + 1) + ": rule '" + rule.id + "' " + JSON.stringify(binding));
        }
      }
    }
    if (snapshots) snapshots.push(snapshotWorld(world));
  });
  return world;
}

function snapshotWorld(w) {
  const flags = {};
  for (const c in w.flags) flags[c] = new Set(w.flags[c]);
  return { flags, relations: new Set(w.relations) };
}

function goalMet(goal, world) {
  if (goal.all) return goal.all.every(g => goalMet(g, world));
  if (goal.any) return goal.any.some(g => goalMet(g, world));
  if (goal.not) return !goalMet(goal.not, world);
  if (goal.flag) return hasFlag(world, goal.flag.char, goal.flag.is);
  if (goal.relation) { const r = goal.relation; return hasRel(world, r.rel, r.from, r.to); }
  throw new Error('unknown goal node');
}

function buildContent(characters, scenes, rules) {
  const byId = arr => Object.fromEntries(arr.map(x => [x.id, x]));
  return {
    characters: byId(characters),
    scenes: byId(scenes),
    rulesByPriorityDesc: [...rules].sort((a, b) => (b.priority || 0) - (a.priority || 0))
  };
}

// ---------- солвер (для валидации и подсказок) ----------

function* combinations(items, k) {
  if (k === 0) { yield []; return; }
  for (let i = 0; i <= items.length - k; i++)
    for (const tail of combinations(items.slice(i + 1), k - 1))
      yield [items[i], ...tail];
}

function panelOptions(level, content) {
  // порядок персонажей = роли-слоты → перебираем размещения
  const opts = [];
  for (const sid of level.scenes) {
    const slots = content.scenes[sid].slots || 2;
    const maxK = Math.min(slots, level.characters.length);
    for (let k = 0; k <= maxK; k++)
      for (const perm of permutations(level.characters, k))
        opts.push({ sceneId: sid, characters: perm });
  }
  return opts;
}

function solve(level, content, maxSolutions) {
  const opts = panelOptions(level, content);
  const n = level.panels;
  const solutions = [];
  const idx = new Array(n).fill(0);
  while (true) {
    const assignment = idx.map(i => opts[i]);
    const w = simulate(assignment, content, null, null, initialWorld(level));
    if (goalMet(level.goal, w)) {
      solutions.push(assignment);
      if (maxSolutions && solutions.length >= maxSolutions) break;
    }
    let pos = n - 1;
    while (pos >= 0 && ++idx[pos] === opts.length) idx[pos--] = 0;
    if (pos < 0) break;
  }
  return { solutions, searchSpace: Math.pow(opts.length, n) };
}

if (typeof module !== 'undefined') {
  module.exports = { newWorld, initialWorld, simulate, goalMet, buildContent, solve, hasFlag, hasRel, isAlive, snapshotWorld };
}
