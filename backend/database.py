import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parent / "smartaccess.db"

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as conn:
        conn.executescript("""
        PRAGMA foreign_keys = ON;
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            message TEXT NOT NULL,
            distance_cm REAL,
            barrier_state TEXT,
            mode TEXT,
            source TEXT NOT NULL DEFAULT 'system',
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS latest_telemetry (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            distance_cm REAL,
            presence_detected INTEGER NOT NULL DEFAULT 0,
            barrier_state TEXT NOT NULL DEFAULT 'UNKNOWN',
            mode TEXT NOT NULL DEFAULT 'MANUAL',
            updated_at TEXT NOT NULL
        );
        INSERT OR IGNORE INTO latest_telemetry
        (id, distance_cm, presence_detected, barrier_state, mode, updated_at)
        VALUES (1, NULL, 0, 'UNKNOWN', 'MANUAL', datetime('now'));
        """)

def record_event(event_type, message, distance_cm=None, barrier_state=None,
                 mode=None, source="system", created_at=None):
    created_at = created_at or datetime.now(timezone.utc).isoformat()
    with connect() as conn:
        conn.execute("""INSERT INTO events
            (event_type, message, distance_cm, barrier_state, mode, source, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (event_type, message, distance_cm, barrier_state, mode, source, created_at))

def save_telemetry(data):
    distance = data.get("distance_cm")
    presence = bool(data.get("presence_detected", False))
    state = str(data.get("barrier_state", "UNKNOWN")).upper()
    mode = str(data.get("mode", "MANUAL")).upper()
    timestamp = data.get("timestamp") or datetime.now(timezone.utc).isoformat()
    with connect() as conn:
        conn.execute("""UPDATE latest_telemetry SET distance_cm=?, presence_detected=?,
            barrier_state=?, mode=?, updated_at=? WHERE id=1""",
            (distance, int(presence), state, mode, timestamp))
    record_event("TELEMETRY", "Leitura recebida", distance, state, mode, "arduino", timestamp)

def get_latest():
    with connect() as conn:
        row = conn.execute("SELECT * FROM latest_telemetry WHERE id=1").fetchone()
        return dict(row) if row else {}

def get_events(limit=50):
    with connect() as conn:
        rows = conn.execute("SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(row) for row in rows]
