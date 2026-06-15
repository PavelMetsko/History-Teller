using System.Collections.Generic;

namespace HistoryTeller.Simulation
{
    /// <summary>Все определения — чистые данные, загружаются из JSON. Движок не знает конкретных персонажей.</summary>
    public sealed class CharacterDef
    {
        public string Id;
        public string Name;
        public List<string> Tags = new List<string>();
    }

    public sealed class SceneDef
    {
        public string Id;
        public string Name;
        public List<string> Tags = new List<string>();
        public int Slots = 2;
        public string Action;     // глагол карты действия («заговор», «соблазнение»)
        public string ActionIcon; // иконка действия для UI
        public List<string> Roles; // подписи ролей-слотов («убийца», «жертва»); null = порядок не важен
    }

    public sealed class RelationCondition
    {
        public string Rel;
        public string To; // имя переменной другого актора
    }

    public sealed class ActorDef
    {
        public string Var;
        public int Slot = -1; // ≥0 — жёсткая привязка к позиции в кадре (роль)
        public List<string> Tags = new List<string>();      // требуемые теги CharacterDef
        public List<string> Flags = new List<string>();     // требуемые флаги состояния
        public List<string> NotFlags = new List<string>();  // запрещённые флаги
        public List<RelationCondition> Relations = new List<RelationCondition>();
    }

    public sealed class TriggerDef
    {
        public List<string> SceneTags = new List<string>();
        public List<ActorDef> Actors = new List<ActorDef>();
    }

    public sealed class EffectDef
    {
        public string Type;   // setFlag | removeFlag | addRelation | removeRelation
        public string Target; // var (для флагов)
        public string Flag;
        public string Rel;    // (для отношений)
        public string From;
        public string To;
    }

    public sealed class RuleDef
    {
        public string Id;
        public int Priority;
        public TriggerDef Trigger = new TriggerDef();
        public List<EffectDef> Effects = new List<EffectDef>();
    }

    public sealed class FactCard
    {
        public string Accuracy; // fact | simplification | legend
        public string Text;
        public string Source;
    }

    /// <summary>Стартовые условия уровня (например, «Брут — союзник Цезаря»).</summary>
    public sealed class InitialStateDef
    {
        public Dictionary<string, List<string>> Flags = new Dictionary<string, List<string>>();
        public List<List<string>> Relations = new List<List<string>>(); // [rel, from, to]
    }

    public sealed class LevelDef
    {
        public string Id;
        public int Order;
        public string Title;
        public string Epoch;
        public int Panels;
        public List<string> Scenes = new List<string>();
        public List<string> Characters = new List<string>();
        public InitialStateDef InitialState;
        public string InitialText;
        public string GoalText; // цель-предложение для чекбокса («Брут предаёт и убивает Цезаря»)
        public string GoalHint; // подсказка про запрещающие условия («Антоний не должен…»)
        public GoalNode Goal;
        public FactCard FactCard;
        public List<Panel> Solution; // эталонное решение (для подсказок и валидации)

        /// <summary>Свежий мир со стартовыми условиями. Вызывать для каждой симуляции (мир мутируется).</summary>
        public World CreateInitialWorld()
        {
            var w = new World();
            if (InitialState == null) return w;
            foreach (var kv in InitialState.Flags)
                foreach (var f in kv.Value)
                    w.SetFlag(kv.Key, f);
            foreach (var r in InitialState.Relations)
                w.AddRelation(r[0], r[1], r[2]);
            return w;
        }
    }

    /// <summary>Заполнение одной панели игроком.</summary>
    public sealed class Panel
    {
        public string SceneId;                                // null = пустая панель
        public List<string> Characters = new List<string>();

        public Panel() { }
        public Panel(string sceneId, params string[] characters)
        {
            SceneId = sceneId;
            Characters = new List<string>(characters);
        }
    }
}
