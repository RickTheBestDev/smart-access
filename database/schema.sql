-- O schema é criado automaticamente por backend/database.py.
-- Este arquivo documenta a estrutura para o dossiê técnico.
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    message TEXT NOT NULL,
    distance_cm REAL,
    barrier_state TEXT,
    mode TEXT,
    source TEXT NOT NULL DEFAULT 'system',
    created_at TEXT NOT NULL
);

CREATE TABLE latest_telemetry (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    distance_cm REAL,
    presence_detected INTEGER NOT NULL DEFAULT 0,
    barrier_state TEXT NOT NULL DEFAULT 'UNKNOWN',
    mode TEXT NOT NULL DEFAULT 'MANUAL',
    updated_at TEXT NOT NULL
);
