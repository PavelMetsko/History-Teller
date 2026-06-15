using System.Collections.Generic;
using System.Linq;

namespace HistoryTeller.Simulation
{
    /// <summary>
    /// Brute-force солвер: проверяет решаемость уровня перебором всех расстановок.
    /// Для контент-пайплайна и подсказок; пространство поиска у таких пазлов маленькое.
    /// </summary>
    public static class Solver
    {
        public sealed class Result
        {
            public List<List<Panel>> Solutions = new List<List<Panel>>();
            public long SearchSpace;
            public bool IsSolvable => Solutions.Count > 0;
        }

        public static Result Solve(LevelDef level, ContentDb db, int maxSolutions = int.MaxValue)
        {
            var options = PanelOptions(level, db);
            var result = new Result
            {
                SearchSpace = Pow(options.Count, level.Panels)
            };

            foreach (var assignment in CartesianPower(options, level.Panels))
            {
                var world = Engine.Simulate(assignment, db, null, level.CreateInitialWorld());
                if (level.Goal.IsMet(world))
                {
                    result.Solutions.Add(assignment);
                    if (result.Solutions.Count >= maxSolutions) break;
                }
            }
            return result;
        }

        /// <summary>Все варианты заполнения панели. Порядок персонажей = роли-слоты → размещения.</summary>
        private static List<Panel> PanelOptions(LevelDef level, ContentDb db)
        {
            var options = new List<Panel>();
            foreach (var sceneId in level.Scenes)
            {
                int slots = db.Scenes[sceneId].Slots;
                int maxK = System.Math.Min(slots, level.Characters.Count);
                for (int k = 0; k <= maxK; k++)
                    foreach (var perm in Permutations(level.Characters, k))
                        options.Add(new Panel { SceneId = sceneId, Characters = perm });
            }
            return options;
        }

        /// <summary>Упорядоченные размещения длины k.</summary>
        private static IEnumerable<List<string>> Permutations(List<string> items, int k)
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

        private static IEnumerable<List<Panel>> CartesianPower(List<Panel> options, int n)
        {
            var indices = new int[n];
            while (true)
            {
                yield return indices.Select(i => options[i]).ToList();
                int pos = n - 1;
                while (pos >= 0 && ++indices[pos] == options.Count)
                    indices[pos--] = 0;
                if (pos < 0) yield break;
            }
        }

        private static IEnumerable<List<string>> Combinations(List<string> items, int k)
        {
            if (k == 0) { yield return new List<string>(); yield break; }
            for (int i = 0; i <= items.Count - k; i++)
                foreach (var tail in Combinations(items.Skip(i + 1).ToList(), k - 1))
                {
                    tail.Insert(0, items[i]);
                    yield return tail;
                }
        }

        private static long Pow(long b, int e)
        {
            long r = 1;
            for (int i = 0; i < e; i++) r *= b;
            return r;
        }
    }
}
