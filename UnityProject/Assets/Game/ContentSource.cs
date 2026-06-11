using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using HistoryTeller.Simulation;

namespace HistoryTeller.Game
{
    /// <summary>
    /// Загрузка контента из Assets/Resources/Content/ (копия Content/ из репозитория).
    /// Позже заменяется на Addressables без изменения остального кода.
    /// </summary>
    public static class ContentSource
    {
        public sealed class Loaded
        {
            public ContentDb Db;
            public List<LevelDef> Levels;
        }

        public static Loaded LoadEpoch(string epoch)
        {
            string Read(string name)
            {
                var asset = Resources.Load<TextAsset>($"Content/{epoch}/{name}");
                if (asset == null)
                    throw new System.Exception($"Content/{epoch}/{name} не найден в Resources");
                return asset.text;
            }

            var db = ContentDb.FromJson(Read("characters"), Read("scenes"), Read("rules"));
            var levels = Resources.LoadAll<TextAsset>($"Content/{epoch}/levels")
                .Select(t => ContentDb.LoadLevel(t.text))
                .OrderBy(l => l.Order)
                .ToList();
            if (levels.Count == 0)
                throw new System.Exception($"Нет уровней в Content/{epoch}/levels");
            return new Loaded { Db = db, Levels = levels };
        }
    }
}
