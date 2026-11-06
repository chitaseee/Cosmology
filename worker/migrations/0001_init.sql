-- Initial schema for Kayhan analytics.
-- Apply with: wrangler d1 migrations apply kayhan-analytics --remote

CREATE TABLE IF NOT EXISTS page_views (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  path TEXT NOT NULL,
  visited_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_page_views_visited_at
  ON page_views(visited_at);

CREATE INDEX IF NOT EXISTS idx_page_views_path
  ON page_views(path);
