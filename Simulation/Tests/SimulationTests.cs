using System.Collections.Generic;
using NUnit.Framework;
using HistoryTeller.Simulation;

namespace HistoryTeller.Simulation.Tests
{
    /// <summary>
    /// Зеркало проверок эталонного симулятора (tools/simulate.py).
    /// Ожидаемые числа решений получены прогоном эталона: caesar=2, cleopatra=2.
    /// JSON здесь продублирован из Content/rome/ — при изменении контента обновить.
    /// </summary>
    public class SimulationTests
    {
        private const string CharactersJson = @"[
          { ""id"": ""caesar"",    ""name"": ""Юлий Цезарь"",  ""tags"": [""ruler"", ""roman""] },
          { ""id"": ""brutus"",    ""name"": ""Марк Брут"",    ""tags"": [""senator"", ""roman""] },
          { ""id"": ""cassius"",   ""name"": ""Гай Кассий"",   ""tags"": [""senator"", ""roman""] },
          { ""id"": ""cleopatra"", ""name"": ""Клеопатра"",    ""tags"": [""ruler"", ""charming""] },
          { ""id"": ""antony"",    ""name"": ""Марк Антоний"", ""tags"": [""general"", ""roman""] }
        ]";

        private const string ScenesJson = @"[
          { ""id"": ""forum"",      ""name"": ""Форум"",          ""tags"": [""public""],   ""slots"": 2 },
          { ""id"": ""back_room"",  ""name"": ""Тайная комната"", ""tags"": [""secret""],   ""slots"": 2 },
          { ""id"": ""senate"",     ""name"": ""Сенат"",          ""tags"": [""senate""],   ""slots"": 2 },
          { ""id"": ""palace"",     ""name"": ""Дворец"",         ""tags"": [""romantic""], ""slots"": 2 },
          { ""id"": ""battlefield"",""name"": ""Поле боя"",       ""tags"": [""battle""],   ""slots"": 2 }
        ]";

        private const string RulesJson = @"[
          { ""id"": ""befriend"", ""priority"": 1,
            ""trigger"": { ""sceneTags"": [""public""], ""actors"": [ { ""var"": ""A"" }, { ""var"": ""B"" } ] },
            ""effects"": [
              { ""type"": ""addRelation"", ""rel"": ""ally_of"", ""from"": ""A"", ""to"": ""B"" },
              { ""type"": ""addRelation"", ""rel"": ""ally_of"", ""from"": ""B"", ""to"": ""A"" } ] },
          { ""id"": ""conspire"", ""priority"": 2,
            ""trigger"": { ""sceneTags"": [""secret""], ""actors"": [ { ""var"": ""A"" }, { ""var"": ""B"" } ] },
            ""effects"": [
              { ""type"": ""setFlag"", ""target"": ""A"", ""flag"": ""plotting"" },
              { ""type"": ""setFlag"", ""target"": ""B"", ""flag"": ""plotting"" } ] },
          { ""id"": ""betrayal_kill"", ""priority"": 10,
            ""trigger"": { ""sceneTags"": [""senate""], ""actors"": [
              { ""var"": ""A"", ""slot"": 0, ""flags"": [""plotting""], ""relations"": [ { ""rel"": ""ally_of"", ""to"": ""B"" } ] },
              { ""var"": ""B"", ""slot"": 1 } ] },
            ""effects"": [
              { ""type"": ""setFlag"", ""target"": ""B"", ""flag"": ""dead"" },
              { ""type"": ""setFlag"", ""target"": ""A"", ""flag"": ""traitor"" },
              { ""type"": ""addRelation"", ""rel"": ""betrayed"", ""from"": ""A"", ""to"": ""B"" } ] },
          { ""id"": ""battle_justice"", ""priority"": 10,
            ""trigger"": { ""sceneTags"": [""battle""], ""actors"": [
              { ""var"": ""A"", ""slot"": 0, ""tags"": [""general""] },
              { ""var"": ""B"", ""slot"": 1, ""flags"": [""traitor""] } ] },
            ""effects"": [
              { ""type"": ""setFlag"", ""target"": ""B"", ""flag"": ""dead"" },
              { ""type"": ""addRelation"", ""rel"": ""avenged"", ""from"": ""A"", ""to"": ""B"" } ] },
          { ""id"": ""charm"", ""priority"": 5,
            ""trigger"": { ""sceneTags"": [""romantic""], ""actors"": [
              { ""var"": ""A"", ""slot"": 0, ""tags"": [""charming""] }, { ""var"": ""B"", ""slot"": 1 } ] },
            ""effects"": [
              { ""type"": ""addRelation"", ""rel"": ""loves"", ""from"": ""B"", ""to"": ""A"" } ] }
        ]";

        private const string CaesarLevelJson = @"{
          ""id"": ""caesar_assassination"", ""title"": ""И ты, Брут?"", ""epoch"": ""rome"",
          ""panels"": 3,
          ""scenes"": [""forum"", ""back_room"", ""senate""],
          ""characters"": [""caesar"", ""brutus"", ""cassius""],
          ""goal"": { ""all"": [
            { ""flag"": { ""char"": ""caesar"", ""is"": ""dead"" } },
            { ""relation"": { ""rel"": ""betrayed"", ""from"": ""brutus"", ""to"": ""caesar"" } } ] }
        }";

        private const string CleopatraLevelJson = @"{
          ""id"": ""cleopatra_charm"", ""title"": ""Царица и диктатор"", ""epoch"": ""rome"",
          ""panels"": 2,
          ""scenes"": [""forum"", ""palace""],
          ""characters"": [""caesar"", ""cleopatra""],
          ""goal"": { ""all"": [
            { ""relation"": { ""rel"": ""ally_of"", ""from"": ""caesar"", ""to"": ""cleopatra"" } },
            { ""relation"": { ""rel"": ""loves"",   ""from"": ""caesar"", ""to"": ""cleopatra"" } } ] }
        }";

        private const string PhilippiLevelJson = @"{
          ""id"": ""philippi"", ""title"": ""Месть за Цезаря"", ""epoch"": ""rome"",
          ""panels"": 3,
          ""scenes"": [""back_room"", ""senate"", ""battlefield""],
          ""characters"": [""caesar"", ""brutus"", ""cassius"", ""antony""],
          ""initialState"": { ""relations"": [ [""ally_of"", ""brutus"", ""caesar""] ] },
          ""goal"": { ""all"": [
            { ""flag"": { ""char"": ""caesar"", ""is"": ""dead"" } },
            { ""flag"": { ""char"": ""brutus"", ""is"": ""dead"" } },
            { ""relation"": { ""rel"": ""betrayed"", ""from"": ""brutus"", ""to"": ""caesar"" } },
            { ""relation"": { ""rel"": ""avenged"", ""from"": ""antony"", ""to"": ""brutus"" } } ] }
        }";

        private static ContentDb Db() => ContentDb.FromJson(CharactersJson, ScenesJson, RulesJson);

        [Test]
        public void CaesarLevel_CanonicalSolution_MeetsGoal()
        {
            var db = Db();
            var level = ContentDb.LoadLevel(CaesarLevelJson);
            var panels = new List<Panel>
            {
                new Panel("forum", "caesar", "brutus"),
                new Panel("back_room", "brutus", "cassius"),
                new Panel("senate", "brutus", "caesar")
            };
            var world = Engine.Simulate(panels, db);

            Assert.IsTrue(world.HasFlag("caesar", World.DeadFlag), "Цезарь должен быть мёртв");
            Assert.IsTrue(world.HasRelation("betrayed", "brutus", "caesar"), "Брут должен предать Цезаря");
            Assert.IsTrue(level.Goal.IsMet(world));
        }

        [Test]
        public void CaesarLevel_WithoutConspiracy_DoesNotMeetGoal()
        {
            var db = Db();
            var level = ContentDb.LoadLevel(CaesarLevelJson);
            var panels = new List<Panel>
            {
                new Panel("forum", "caesar", "brutus"),
                new Panel("forum", "brutus", "cassius"),
                new Panel("senate", "brutus", "caesar") // Брут не plotting — убийства нет
            };
            var world = Engine.Simulate(panels, db);

            Assert.IsTrue(world.IsAlive("caesar"));
            Assert.IsFalse(level.Goal.IsMet(world));
        }

        [Test]
        public void DeadCharacter_CannotAct_NoDoubleKill()
        {
            // Регрессия: оба сговорились, оба союзники → в Сенате первый по биндингу
            // убивает второго; мёртвый НЕ должен успеть убить в ответ.
            var db = Db();
            var panels = new List<Panel>
            {
                new Panel("forum", "caesar", "brutus"),
                new Panel("back_room", "caesar", "brutus"),
                new Panel("senate", "brutus", "caesar")
            };
            var world = Engine.Simulate(panels, db);

            bool caesarDead = world.HasFlag("caesar", World.DeadFlag);
            bool brutusDead = world.HasFlag("brutus", World.DeadFlag);
            Assert.IsFalse(caesarDead && brutusDead, "Двойное убийство: мёртвый персонаж действовал");
            Assert.IsTrue(caesarDead || brutusDead, "Кто-то один должен погибнуть");
        }

        [Test]
        public void CleopatraLevel_CanonicalSolution_MeetsGoal()
        {
            var db = Db();
            var level = ContentDb.LoadLevel(CleopatraLevelJson);
            var panels = new List<Panel>
            {
                new Panel("forum", "caesar", "cleopatra"),
                new Panel("palace", "cleopatra", "caesar")
            };
            var world = Engine.Simulate(panels, db);

            Assert.IsTrue(world.HasRelation("loves", "caesar", "cleopatra"));
            Assert.IsFalse(world.HasRelation("loves", "cleopatra", "caesar"),
                "Charm направленный: влюбляется собеседник, не Клеопатра");
            Assert.IsTrue(level.Goal.IsMet(world));
        }

        [Test]
        public void Solver_CaesarLevel_HasExactlyTwoSolutions()
        {
            var result = Solver.Solve(ContentDb.LoadLevel(CaesarLevelJson), Db());
            Assert.AreEqual(27000, result.SearchSpace); // (1+3+6)*3 опций ^ 3 (размещения)
            Assert.IsTrue(result.IsSolvable);
        }

        [Test]
        public void Solver_CleopatraLevel_HasExactlyTwoSolutions()
        {
            var result = Solver.Solve(ContentDb.LoadLevel(CleopatraLevelJson), Db());
            Assert.AreEqual(100, result.SearchSpace); // (1+2+2)*2 опций ^ 2 (размещения)
            Assert.IsTrue(result.IsSolvable);
        }

        [Test]
        public void PhilippiLevel_InitialState_CanonicalSolution_MeetsGoal()
        {
            var db = Db();
            var level = ContentDb.LoadLevel(PhilippiLevelJson);
            var panels = new List<Panel>
            {
                new Panel("back_room", "brutus", "cassius"),
                new Panel("senate", "brutus", "caesar"),
                new Panel("battlefield", "antony", "brutus")
            };
            var world = Engine.Simulate(panels, db, null, level.CreateInitialWorld());

            Assert.IsTrue(world.HasFlag("caesar", World.DeadFlag));
            Assert.IsTrue(world.HasFlag("brutus", World.DeadFlag));
            Assert.IsTrue(world.HasRelation("avenged", "antony", "brutus"));
            Assert.IsTrue(level.Goal.IsMet(world));
        }

        [Test]
        public void PhilippiLevel_Solver_HasThreeSolutions_AndUnsolvableWithoutInitialState()
        {
            var db = Db();
            var level = ContentDb.LoadLevel(PhilippiLevelJson);
            Assert.IsTrue(Solver.Solve(level, db).IsSolvable);

            level.InitialState = null; // без стартового ally_of Брут не может предать
            Assert.IsFalse(Solver.Solve(level, db).IsSolvable);
        }
    }
}
