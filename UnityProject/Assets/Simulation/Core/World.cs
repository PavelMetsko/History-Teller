using System.Collections.Generic;

namespace HistoryTeller.Simulation
{
    /// <summary>Состояние мира: флаги персонажей + направленные отношения. Чистый C#, без UnityEngine.</summary>
    public sealed class World
    {
        public const string DeadFlag = "dead";

        private readonly Dictionary<string, HashSet<string>> _flags =
            new Dictionary<string, HashSet<string>>();
        private readonly HashSet<(string rel, string from, string to)> _relations =
            new HashSet<(string, string, string)>();

        public bool HasFlag(string charId, string flag) =>
            _flags.TryGetValue(charId, out var s) && s.Contains(flag);

        public void SetFlag(string charId, string flag)
        {
            if (!_flags.TryGetValue(charId, out var s))
                _flags[charId] = s = new HashSet<string>();
            s.Add(flag);
        }

        public void RemoveFlag(string charId, string flag)
        {
            if (_flags.TryGetValue(charId, out var s)) s.Remove(flag);
        }

        public bool HasRelation(string rel, string from, string to) =>
            _relations.Contains((rel, from, to));

        public void AddRelation(string rel, string from, string to) =>
            _relations.Add((rel, from, to));

        public void RemoveRelation(string rel, string from, string to) =>
            _relations.Remove((rel, from, to));

        public bool IsAlive(string charId) => !HasFlag(charId, DeadFlag);

        /// <summary>Глубокая копия (для снапшотов после каждой панели).</summary>
        public World Clone()
        {
            var w = new World();
            foreach (var kv in _flags)
                w._flags[kv.Key] = new HashSet<string>(kv.Value);
            foreach (var r in _relations)
                w._relations.Add(r);
            return w;
        }
    }
}
