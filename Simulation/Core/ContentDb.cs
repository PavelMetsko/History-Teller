using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace HistoryTeller.Simulation
{
    /// <summary>
    /// Загруженный контент эпохи. Принимает JSON-строки — источник (TextAsset, Addressables, файл)
    /// решается на уровне Unity, движок об этом не знает.
    /// </summary>
    public sealed class ContentDb
    {
        public Dictionary<string, CharacterDef> Characters { get; private set; }
        public Dictionary<string, SceneDef> Scenes { get; private set; }
        public List<RuleDef> RulesByPriorityDesc { get; private set; }

        public static ContentDb FromJson(string charactersJson, string scenesJson, string rulesJson)
        {
            return new ContentDb
            {
                Characters = JsonConvert.DeserializeObject<List<CharacterDef>>(charactersJson)
                    .ToDictionary(c => c.Id),
                Scenes = JsonConvert.DeserializeObject<List<SceneDef>>(scenesJson)
                    .ToDictionary(s => s.Id),
                RulesByPriorityDesc = JsonConvert.DeserializeObject<List<RuleDef>>(rulesJson)
                    .OrderByDescending(r => r.Priority)
                    .ToList()
            };
        }

        public static LevelDef LoadLevel(string levelJson)
        {
            var obj = JObject.Parse(levelJson);
            var level = new LevelDef
            {
                Id = (string)obj["id"],
                Order = (int?)obj["order"] ?? 0,
                Title = (string)obj["title"],
                Epoch = (string)obj["epoch"],
                Panels = (int)obj["panels"],
                Scenes = obj["scenes"].ToObject<List<string>>(),
                Characters = obj["characters"].ToObject<List<string>>(),
                InitialText = (string)obj["initialText"],
                Goal = GoalNode.Parse((JObject)obj["goal"])
            };
            if (obj["initialState"] != null)
                level.InitialState = obj["initialState"].ToObject<InitialStateDef>();
            if (obj["factCard"] != null)
                level.FactCard = obj["factCard"].ToObject<FactCard>();
            if (obj["solution"] != null)
            {
                level.Solution = new List<Panel>();
                foreach (var t in obj["solution"])
                    level.Solution.Add(new Panel(
                        (string)t["scene"],
                        t["characters"].ToObject<List<string>>().ToArray()));
            }
            return level;
        }
    }
}
