CREATE TABLE IF NOT EXISTS signups (email TEXT PRIMARY KEY, note TEXT, lang TEXT, created_at TEXT NOT NULL, updated_at TEXT);
-- plyn-stats
CREATE TABLE IF NOT EXISTS hits (at TEXT NOT NULL, kind TEXT NOT NULL, path TEXT, lang TEXT, referrer TEXT, utm TEXT, country TEXT, device TEXT, bot INTEGER NOT NULL DEFAULT 0);
CREATE INDEX IF NOT EXISTS hits_at ON hits(at);
ALTER TABLE hits ADD COLUMN ms INTEGER;  -- time on page, kind leave
ALTER TABLE hits ADD COLUMN interacted INTEGER;  -- any click or key before leaving
ALTER TABLE hits ADD COLUMN vid TEXT;  -- random visit number from cookie plyn-vid, only with consent
