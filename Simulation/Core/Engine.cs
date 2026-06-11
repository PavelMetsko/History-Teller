using System.Collections.Generic;
using System.Linq;

namespace HistoryTeller.Simulation
{
    /// <summary>
    /// Движок симуляции: прогоняет панели слева направо, применяя правила по убыванию приоритета.
    /// Семантика 1:1 с эталонным tools/simulate.py.
    /// </summary>
    public static class Engine
    {
        /// <param name="initial">Стартовый мир (мутируется!). Передавайте level.CreateInitialWorld().</param>
        /// <param name="snapshots">Если не null — копия состояния после каждой панели (для UI-бейджей).</param>
        public static World Simulate(IReadOnlyList<Panel> panels, ContentDb db,
            List<string> log = null, World initial = null, List<World> snapshots = null)
        {
            var world = initial ?? new World();
            for (int i = 0; i < panels.Count; i++)
            {
                var panel = panels[i];
                if (panel?.SceneId == null) { snapshots?.Add(world.Clone()); continue; }

                var sceneTags = db.Scenes[panel.SceneId].Tags;
                foreach (var rule in db.RulesByPriorityDesc)
                {
                    if (!rule.Trigger.SceneTags.All(t => sceneTags.Contains(t)))
                        continue;

                    foreach (var binding in FindBindings(rule.Trigger.Actors, panel.Characters, world, db))
                    {
                        // Биндинг мог быть инвалидирован эффектом в этой же панели
                        // (например, персонаж погиб) — перепроверяем живость и условия.
                        bool stillValid = rule.Trigger.Actors.All(a =>
                            world.IsAlive(binding[a.Var]) &&
                            ActorMatches(a, binding[a.Var], binding, world, db));
                        if (!stillValid) continue;

                        ApplyEffects(rule.Effects, binding, world);
                        log?.Add($"panel {i + 1}: rule '{rule.Id}' " +
                                 string.Join(", ", binding.Select(kv => $"{kv.Key}={kv.Value}")));
                    }
                }
                snapshots?.Add(world.Clone());
            }
            return world;
        }

        private static bool ActorMatches(ActorDef actor, string charId,
            Dictionary<string, string> binding, World world, ContentDb db)
        {
            var def = db.Characters[charId];
            if (!actor.Tags.All(t => def.Tags.Contains(t))) return false;
            if (!actor.Flags.All(f => world.HasFlag(charId, f))) return false;
            if (actor.NotFlags.Any(f => world.HasFlag(charId, f))) return false;
            foreach (var rc in actor.Relations)
            {
                if (!binding.TryGetValue(rc.To, out var other)) return false;
                if (!world.HasRelation(rc.Rel, charId, other)) return false;
            }
            return true;
        }

        /// <summary>Все инъективные назначения живых присутствующих персонажей на переменные акторов.</summary>
        private static List<Dictionary<string, string>> FindBindings(
            List<ActorDef> actors, List<string> present, World world, ContentDb db)
        {
            var alive = present.Where(world.IsAlive).ToList();
            var result = new List<Dictionary<string, string>>();
            foreach (var perm in Permutations(alive, actors.Count))
            {
                var binding = new Dictionary<string, string>();
                for (int i = 0; i < actors.Count; i++)
                    binding[actors[i].Var] = perm[i];

                // Условия отношений ссылаются на другие переменные — проверяем после полного назначения.
                if (actors.All(a => ActorMatches(a, binding[a.Var], binding, world, db)))
                    result.Add(binding);
            }
            return result;
        }

        private static void ApplyEffects(List<EffectDef> effects,
            Dictionary<string, string> binding, World world)
        {
            foreach (var e in effects)
            {
                switch (e.Type)
                {
                    case "setFlag":        world.SetFlag(binding[e.Target], e.Flag); break;
                    case "removeFlag":     world.RemoveFlag(binding[e.Target], e.Flag); break;
                    case "addRelation":    world.AddRelation(e.Rel, binding[e.From], binding[e.To]); break;
                    case "removeRelation": world.RemoveRelation(e.Rel, binding[e.From], binding[e.To]); break;
                    default: throw new System.ArgumentException("Unknown effect type: " + e.Type);
                }
            }
        }

        /// <summary>Упорядоченные выборки длины k без повторений (порядок генерации стабилен).</summary>
        internal static IEnumerable<List<string>> Permutations(List<string> items, int k)
        {
            if (k == 0) { yield return new List<string>(); yield break; }
            if (k > items.Count) yield break;

            for (int i = 0; i < items.Count; i++)
            {
                var rest = new List<string>(items);
                rest.RemoveAt(i);
                foreach (var tail in Permutations(rest, k - 1))
                {
                    tail.Insert(0, items[i]);
                    yield return tail;
                }
            }
        }
    }
}
