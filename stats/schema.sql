-- Вся база. Больше в ней ничего нет и быть не должно: ни идентификаторов, ни времени —
-- иначе счётчик превращается в сбор данных о человеке, а приложение обещает обратное.
CREATE TABLE IF NOT EXISTS counters (
  k TEXT PRIMARY KEY,
  n INTEGER NOT NULL DEFAULT 0
);
