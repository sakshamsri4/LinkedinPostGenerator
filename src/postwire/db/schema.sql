PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS items(
    id INTEGER PRIMARY KEY,
    source TEXT NOT NULL,
    external_id TEXT NOT NULL,
    url TEXT NOT NULL,
    url_canonical TEXT NOT NULL,
    title TEXT NOT NULL,
    body TEXT, 
    published_at INTEGER,
    fetched_at INTEGER NOT NULL,
    raw TEXT NOT NULL,
    UNIQUE(source, external_id)
);
CREATE INDEX IF NOT EXISTS idx_items_camonical ON items(source, url_canonical);
CREATE INDEX IF NOT EXISTS idx_items_published ON items(published_at DESC);
CREATE VIRTUAL TABLE IF NOT EXISTS item_vectors USING vec0(
    item_id INTEGER PRIMARY KEY,
    embedding FLOAT[384]
);

CREATE TABLE IF NOT EXISTS clusters(
    id INTEGER PRIMARY KEY,
    created_at INTEGER NOT NULL,
    size INTEGER NOT NULL,
    source_count INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS cluster_items(
    cluster_id INTEGER NOT NULL REFERENCES clusters(id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES items(id),
    PRIMARY KEY(cluster_id, item_id)
);
CREATE INDEX IF NOT EXISTS idx_cluster_items_item ON cluster_items(item_id);

CREATE TABLE IF NOT EXISTS seeds(
    id INTEGER PRIMARY KEY,
    cluster_id INTEGER NOT NULL REFERENCES clusters(id),
    run_id TEXT NOT NULL,
    topical_fit REAL NOT NULL,
    novelty REAL NOT NULL,
    corroboration REAL NOT NULL,
    score REAL NOT NULL,
    rank INTEGER,
    status TEXT NOT NULL DEFAULT 'new',
    created_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_seeds_run ON seeds(run_id, rank);
CREATE TABLE IF NOT EXISTS posts(
    id INTEGER PRIMARY KEY,
    urn TEXT UNIQUE,
    seed_id INTEGER REFERENCES seeds(id) ,
    text TEXT NOT NULL,
    format TEXT,
    source_item_ids TEXT NOT NULL,
    published_at INTEGER
);