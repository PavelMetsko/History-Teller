using System.Collections.Generic;
using Newtonsoft.Json;
using UnityEngine;

namespace HistoryTeller.Game
{
    /// <summary>Прогресс и настройки в PlayerPrefs (JSON). Позже мигрирует в iCloud-сейвы.</summary>
    public static class SaveSystem
    {
        public sealed class Data
        {
            public List<string> Completed = new List<string>();
            public bool SoundOn = true;
        }

        private const string Key = "ht_save_v1";
        private static Data _data;

        public static Data Get()
        {
            if (_data == null)
            {
                var s = PlayerPrefs.GetString(Key, "");
                _data = string.IsNullOrEmpty(s)
                    ? new Data()
                    : JsonConvert.DeserializeObject<Data>(s) ?? new Data();
            }
            return _data;
        }

        public static void Store()
        {
            PlayerPrefs.SetString(Key, JsonConvert.SerializeObject(Get()));
            PlayerPrefs.Save();
        }

        public static bool IsCompleted(string levelId) => Get().Completed.Contains(levelId);

        public static void MarkCompleted(string levelId)
        {
            if (IsCompleted(levelId)) return;
            Get().Completed.Add(levelId);
            Store();
        }

        public static void SetSound(bool on)
        {
            Get().SoundOn = on;
            Sfx.Enabled = on;
            Music.SetEnabled(on);
            Store();
        }

        public static void Reset()
        {
            _data = new Data();
            Store();
        }
    }
}
