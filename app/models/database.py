import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


def get_db_connection(db_path):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path):
    db_path = Path(db_path)
    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass

    with sqlite3.connect(str(db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS disaster_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                source TEXT,
                published_at TEXT,
                location TEXT,
                disaster_type TEXT,
                severity TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS guidance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                disaster_type TEXT NOT NULL,
                tips TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                location TEXT,
                disaster_type TEXT,
                level TEXT,
                message TEXT,
                risk_percentage REAL
            )
            """
        )
        conn.commit()


def insert_reports(db_path, reports):
    if not reports:
        return

    with sqlite3.connect(str(db_path)) as conn:
        cursor = conn.cursor()
        cursor.executemany(
            """
            INSERT INTO disaster_reports (
                title, content, source, published_at, location, disaster_type, severity
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    report.get("title"),
                    report.get("content"),
                    report.get("source"),
                    report.get("published_at"),
                    report.get("location"),
                    report.get("disaster_type"),
                    report.get("severity"),
                )
                for report in reports
            ],
        )
        conn.commit()


def fetch_recent_reports(db_path, limit=100):
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT title, content, source, published_at, location, disaster_type, severity
            FROM disaster_reports
            ORDER BY published_at DESC, created_at DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cursor.fetchall()

    return [dict(row) for row in rows]


def insert_alerts(db_path, alerts, dedupe_hours=6):
    if not alerts:
        return

    cutoff = datetime.utcnow() - timedelta(hours=dedupe_hours)

    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        for alert in alerts:
            cursor.execute(
                """
                SELECT id FROM alerts
                WHERE message = ? AND level = ? AND location = ? AND created_at >= ?
                LIMIT 1
                """,
                (
                    alert.get("message"),
                    alert.get("level"),
                    alert.get("location"),
                    cutoff.strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
            existing = cursor.fetchone()
            if existing:
                continue

            cursor.execute(
                """
                INSERT INTO alerts (location, disaster_type, level, message, risk_percentage)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    alert.get("location"),
                    alert.get("disaster_type"),
                    alert.get("level"),
                    alert.get("message"),
                    alert.get("risk_percentage"),
                ),
            )
        conn.commit()


def fetch_recent_alerts(db_path, limit=50):
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT created_at, location, disaster_type, level, message, risk_percentage
            FROM alerts
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cursor.fetchall()

    return [dict(row) for row in rows]
