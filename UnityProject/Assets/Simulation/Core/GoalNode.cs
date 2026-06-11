using System;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json.Linq;

namespace HistoryTeller.Simulation
{
    /// <summary>Дерево условий цели уровня: all / any / not / flag / relation.</summary>
    public abstract class GoalNode
    {
        public abstract bool IsMet(World world);

        public static GoalNode Parse(JObject obj)
        {
            if (obj["all"] != null)
                return new AllGoal(obj["all"].Select(t => Parse((JObject)t)).ToList());
            if (obj["any"] != null)
                return new AnyGoal(obj["any"].Select(t => Parse((JObject)t)).ToList());
            if (obj["not"] != null)
                return new NotGoal(Parse((JObject)obj["not"]));
            if (obj["flag"] != null)
            {
                var f = obj["flag"];
                return new FlagGoal((string)f["char"], (string)f["is"]);
            }
            if (obj["relation"] != null)
            {
                var r = obj["relation"];
                return new RelationGoal((string)r["rel"], (string)r["from"], (string)r["to"]);
            }
            throw new ArgumentException("Unknown goal node: " + obj);
        }
    }

    public sealed class AllGoal : GoalNode
    {
        public readonly List<GoalNode> Children;
        public AllGoal(List<GoalNode> children) { Children = children; }
        public override bool IsMet(World w) => Children.All(c => c.IsMet(w));
    }

    public sealed class AnyGoal : GoalNode
    {
        public readonly List<GoalNode> Children;
        public AnyGoal(List<GoalNode> children) { Children = children; }
        public override bool IsMet(World w) => Children.Any(c => c.IsMet(w));
    }

    public sealed class NotGoal : GoalNode
    {
        public readonly GoalNode Child;
        public NotGoal(GoalNode child) { Child = child; }
        public override bool IsMet(World w) => !Child.IsMet(w);
    }

    public sealed class FlagGoal : GoalNode
    {
        public readonly string Char;
        public readonly string Flag;
        public FlagGoal(string charId, string flag) { Char = charId; Flag = flag; }
        public override bool IsMet(World w) => w.HasFlag(Char, Flag);
    }

    public sealed class RelationGoal : GoalNode
    {
        public readonly string Rel;
        public readonly string From;
        public readonly string To;
        public RelationGoal(string rel, string from, string to) { Rel = rel; From = from; To = to; }
        public override bool IsMet(World w) => w.HasRelation(Rel, From, To);
    }
}
