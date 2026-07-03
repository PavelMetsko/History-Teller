import Testing
@testable import Simulation

/// Зеркало проверок C#-движка (Simulation/Tests/SimulationTests.cs) и эталона tools/simulate.py.
/// Ожидаемые числа: caesar search space = 27000, cleopatra = 100.
/// JSON продублирован из Content/rome/ — при изменении контента обновить.
struct SimulationTests {

    static let charactersJson = """
    [
      { "id": "caesar",    "name": "Юлий Цезарь",  "tags": ["ruler", "roman"] },
      { "id": "brutus",    "name": "Марк Брут",    "tags": ["senator", "roman"] },
      { "id": "cassius",   "name": "Гай Кассий",   "tags": ["senator", "roman"] },
      { "id": "cleopatra", "name": "Клеопатра",    "tags": ["ruler", "charming"] },
      { "id": "antony",    "name": "Марк Антоний", "tags": ["general", "roman"] }
    ]
    """

    static let scenesJson = """
    [
      { "id": "forum",      "name": "Форум",          "tags": ["public"],   "slots": 2 },
      { "id": "back_room",  "name": "Тайная комната", "tags": ["secret"],   "slots": 2 },
      { "id": "senate",     "name": "Сенат",          "tags": ["senate"],   "slots": 2 },
      { "id": "palace",     "name": "Дворец",         "tags": ["romantic"], "slots": 2 },
      { "id": "battlefield","name": "Поле боя",       "tags": ["battle"],   "slots": 2 }
    ]
    """

    static let rulesJson = """
    [
      { "id": "befriend", "priority": 1,
        "trigger": { "sceneTags": ["public"], "actors": [ { "var": "A" }, { "var": "B" } ] },
        "effects": [
          { "type": "addRelation", "rel": "ally_of", "from": "A", "to": "B" },
          { "type": "addRelation", "rel": "ally_of", "from": "B", "to": "A" } ] },
      { "id": "conspire", "priority": 2,
        "trigger": { "sceneTags": ["secret"], "actors": [ { "var": "A" }, { "var": "B" } ] },
        "effects": [
          { "type": "setFlag", "target": "A", "flag": "plotting" },
          { "type": "setFlag", "target": "B", "flag": "plotting" } ] },
      { "id": "betrayal_kill", "priority": 10,
        "trigger": { "sceneTags": ["senate"], "actors": [
          { "var": "A", "slot": 0, "flags": ["plotting"], "relations": [ { "rel": "ally_of", "to": "B" } ] },
          { "var": "B", "slot": 1 } ] },
        "effects": [
          { "type": "setFlag", "target": "B", "flag": "dead" },
          { "type": "setFlag", "target": "A", "flag": "traitor" },
          { "type": "addRelation", "rel": "betrayed", "from": "A", "to": "B" } ] },
      { "id": "battle_justice", "priority": 10,
        "trigger": { "sceneTags": ["battle"], "actors": [
          { "var": "A", "slot": 0, "tags": ["general"] },
          { "var": "B", "slot": 1, "flags": ["traitor"] } ] },
        "effects": [
          { "type": "setFlag", "target": "B", "flag": "dead" },
          { "type": "addRelation", "rel": "avenged", "from": "A", "to": "B" } ] },
      { "id": "charm", "priority": 5,
        "trigger": { "sceneTags": ["romantic"], "actors": [
          { "var": "A", "slot": 0, "tags": ["charming"] }, { "var": "B", "slot": 1 } ] },
        "effects": [
          { "type": "addRelation", "rel": "loves", "from": "B", "to": "A" } ] }
    ]
    """

    static let caesarLevelJson = """
    {
      "id": "caesar_assassination", "title": "И ты, Брут?", "epoch": "rome",
      "panels": 3,
      "scenes": ["forum", "back_room", "senate"],
      "characters": ["caesar", "brutus", "cassius"],
      "goal": { "all": [
        { "flag": { "char": "caesar", "is": "dead" } },
        { "relation": { "rel": "betrayed", "from": "brutus", "to": "caesar" } } ] }
    }
    """

    static let cleopatraLevelJson = """
    {
      "id": "cleopatra_charm", "title": "Царица и диктатор", "epoch": "rome",
      "panels": 2,
      "scenes": ["forum", "palace"],
      "characters": ["caesar", "cleopatra"],
      "goal": { "all": [
        { "relation": { "rel": "ally_of", "from": "caesar", "to": "cleopatra" } },
        { "relation": { "rel": "loves",   "from": "caesar", "to": "cleopatra" } } ] }
    }
    """

    static let philippiLevelJson = """
    {
      "id": "philippi", "title": "Месть за Цезаря", "epoch": "rome",
      "panels": 3,
      "scenes": ["back_room", "senate", "battlefield"],
      "characters": ["caesar", "brutus", "cassius", "antony"],
      "initialState": { "relations": [ ["ally_of", "brutus", "caesar"] ] },
      "goal": { "all": [
        { "flag": { "char": "caesar", "is": "dead" } },
        { "flag": { "char": "brutus", "is": "dead" } },
        { "relation": { "rel": "betrayed", "from": "brutus", "to": "caesar" } },
        { "relation": { "rel": "avenged", "from": "antony", "to": "brutus" } } ] }
    }
    """

    static func db() throws -> ContentDb {
        try ContentDb.fromJson(charactersJson: charactersJson, scenesJson: scenesJson, rulesJson: rulesJson)
    }

    @Test func caesarLevelCanonicalSolutionMeetsGoal() throws {
        let db = try Self.db()
        let level = try ContentDb.loadLevel(Self.caesarLevelJson)
        let panels = [
            Panel(sceneId: "forum",     characters: ["caesar", "brutus"]),
            Panel(sceneId: "back_room", characters: ["brutus", "cassius"]),
            Panel(sceneId: "senate",    characters: ["brutus", "caesar"]),
        ]
        let world = Engine.simulate(panels, db).world

        #expect(world.hasFlag("caesar", World.deadFlag), "Цезарь должен быть мёртв")
        #expect(world.hasRelation("betrayed", "brutus", "caesar"), "Брут должен предать Цезаря")
        #expect(level.goal.isMet(world))
    }

    @Test func caesarLevelWithoutConspiracyDoesNotMeetGoal() throws {
        let db = try Self.db()
        let level = try ContentDb.loadLevel(Self.caesarLevelJson)
        let panels = [
            Panel(sceneId: "forum",  characters: ["caesar", "brutus"]),
            Panel(sceneId: "forum",  characters: ["brutus", "cassius"]),
            Panel(sceneId: "senate", characters: ["brutus", "caesar"]), // Брут не plotting — убийства нет
        ]
        let world = Engine.simulate(panels, db).world

        #expect(world.isAlive("caesar"))
        #expect(!level.goal.isMet(world))
    }

    @Test func deadCharacterCannotActNoDoubleKill() throws {
        // Регрессия: оба сговорились, оба союзники → в Сенате первый по биндингу
        // убивает второго; мёртвый НЕ должен успеть убить в ответ.
        let db = try Self.db()
        let panels = [
            Panel(sceneId: "forum",     characters: ["caesar", "brutus"]),
            Panel(sceneId: "back_room", characters: ["caesar", "brutus"]),
            Panel(sceneId: "senate",    characters: ["brutus", "caesar"]),
        ]
        let world = Engine.simulate(panels, db).world

        let caesarDead = world.hasFlag("caesar", World.deadFlag)
        let brutusDead = world.hasFlag("brutus", World.deadFlag)
        #expect(!(caesarDead && brutusDead), "Двойное убийство: мёртвый персонаж действовал")
        #expect(caesarDead || brutusDead, "Кто-то один должен погибнуть")
    }

    @Test func cleopatraLevelCanonicalSolutionMeetsGoal() throws {
        let db = try Self.db()
        let level = try ContentDb.loadLevel(Self.cleopatraLevelJson)
        let panels = [
            Panel(sceneId: "forum",  characters: ["caesar", "cleopatra"]),
            Panel(sceneId: "palace", characters: ["cleopatra", "caesar"]),
        ]
        let world = Engine.simulate(panels, db).world

        #expect(world.hasRelation("loves", "caesar", "cleopatra"))
        #expect(!world.hasRelation("loves", "cleopatra", "caesar"),
                "Charm направленный: влюбляется собеседник, не Клеопатра")
        #expect(level.goal.isMet(world))
    }

    @Test func solverCaesarLevelIsSolvableWithExpectedSearchSpace() throws {
        let result = Solver.solve(try ContentDb.loadLevel(Self.caesarLevelJson), try Self.db())
        #expect(result.searchSpace == 27000) // (1+3+6)*3 опций ^ 3 (размещения)
        #expect(result.isSolvable)
    }

    @Test func solverCleopatraLevelIsSolvableWithExpectedSearchSpace() throws {
        let result = Solver.solve(try ContentDb.loadLevel(Self.cleopatraLevelJson), try Self.db())
        #expect(result.searchSpace == 100) // (1+2+2)*2 опций ^ 2 (размещения)
        #expect(result.isSolvable)
    }

    @Test func philippiLevelInitialStateCanonicalSolutionMeetsGoal() throws {
        let db = try Self.db()
        let level = try ContentDb.loadLevel(Self.philippiLevelJson)
        let panels = [
            Panel(sceneId: "back_room",   characters: ["brutus", "cassius"]),
            Panel(sceneId: "senate",      characters: ["brutus", "caesar"]),
            Panel(sceneId: "battlefield", characters: ["antony", "brutus"]),
        ]
        let world = Engine.simulate(panels, db, initial: level.createInitialWorld()).world

        #expect(world.hasFlag("caesar", World.deadFlag))
        #expect(world.hasFlag("brutus", World.deadFlag))
        #expect(world.hasRelation("avenged", "antony", "brutus"))
        #expect(level.goal.isMet(world))
    }

    @Test func philippiSolverHasSolutionsAndUnsolvableWithoutInitialState() throws {
        let db = try Self.db()
        var level = try ContentDb.loadLevel(Self.philippiLevelJson)
        #expect(Solver.solve(level, db).isSolvable)

        level.initialState = nil // без стартового ally_of Брут не может предать
        #expect(!Solver.solve(level, db).isSolvable)
    }
}
