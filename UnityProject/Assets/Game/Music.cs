using UnityEngine;

namespace HistoryTeller.Game
{
    /// <summary>Фоновая музыка (Resources/Music/theme, бесшовный луп). Подчиняется настройке звука.</summary>
    public sealed class Music : MonoBehaviour
    {
        private static Music _instance;
        private AudioSource _source;

        public static void Play()
        {
            if (_instance == null)
            {
                var go = new GameObject("Music");
                DontDestroyOnLoad(go);
                _instance = go.AddComponent<Music>();
                _instance._source = go.AddComponent<AudioSource>();
                _instance._source.clip = Resources.Load<AudioClip>("Music/theme");
                _instance._source.loop = true;
                _instance._source.volume = 0.32f;
                _instance._source.playOnAwake = false;
            }
            SetEnabled(Sfx.Enabled);
        }

        public static void SetEnabled(bool on)
        {
            if (_instance == null || _instance._source.clip == null) return;
            if (on && !_instance._source.isPlaying) _instance._source.Play();
            else if (!on && _instance._source.isPlaying) _instance._source.Stop();
        }
    }
}
