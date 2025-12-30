CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL
);

INSERT OR IGNORE INTO users (username, password) VALUES ('erik', 'kire');
INSERT OR IGNORE INTO users (username, password) VALUES ('mark', 'kram');