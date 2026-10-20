-- Статистика игроков History Teller (D1). Игрок — анонимный ID установки, без личных данных.
CREATE TABLE IF NOT EXISTS players (
  iid         TEXT PRIMARY KEY,   -- случайный UUID установки
  platform    TEXT NOT NULL,      -- ios | android
  app_version TEXT,
  lang        TEXT,
  country     TEXT,               -- из Cloudflare (request.cf.country), не от клиента
  first_seen  INTEGER NOT NULL,   -- unix ms
  last_seen   INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS players_last_seen ON players(last_seen);
CREATE INDEX IF NOT EXISTS players_first_seen ON players(first_seen);

CREATE TABLE IF NOT EXISTS events (
  id      INTEGER PRIMARY KEY AUTOINCREMENT,
  iid     TEXT NOT NULL,
  ts      INTEGER NOT NULL,       -- время сервера, unix ms
  type    TEXT NOT NULL,          -- session | level_start | level_complete | ad_unlock
  level   TEXT,
  chapter TEXT
);
CREATE INDEX IF NOT EXISTS events_ts ON events(ts);
CREATE INDEX IF NOT EXISTS events_type_level ON events(type, level);
CREATE INDEX IF NOT EXISTS events_type_chapter ON events(type, chapter, iid);
