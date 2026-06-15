using System.Collections.Generic;
using UnityEngine;

namespace HistoryTeller.Game
{
    /// <summary>Звуки из Resources/Sfx (генерируются tools/make_sfx.py). Sfx.Play("kill").</summary>
    public sealed class Sfx : MonoBehaviour
    {
        /// <summary>Глобальный выключатель (настройки).</summary>
        public static bool Enabled = true;

        private static Sfx _instance;
        private readonly Dictionary<string, AudioClip> _clips =
            new Dictionary<string, AudioClip>();
        private AudioSource _source;

        public static void Play(string name, float volume = 1f)
        {
            if (!Enabled) return;
            if (_instance == null)
            {
                var go = new GameObject("Sfx");
                DontDestroyOnLoad(go);
                _instance = go.AddComponent<Sfx>();
                _instance._source = go.AddComponent<AudioSource>();
                _instance._source.playOnAwake = false;
                foreach (var clip in Resources.LoadAll<AudioClip>("Sfx"))
                    _instance._clips[clip.name] = clip;
            }
            if (_instance._clips.TryGetValue(name, out var c))
                _instance._source.PlayOneShot(c, volume);
        }

        /// <summary>Звук по id сработавшего правила.</summary>
        public static void PlayRule(string ruleId)
        {
            switch (ruleId)
            {
                case "betrayal_kill":
                case "battle_justice": Play("kill"); break;
                case "charm": Play("love"); break;
                case "rivals": Play("envy"); break;
                case "conspire": Play("conspire"); break;
                case "befriend": Play("ally", 0.6f); break;
                case "offer_crown": Play("crown"); break;
                default: Play("place", 0.4f); break;
            }
        }
    }
}
