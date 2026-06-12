import json
from .db import get_conn, get_cursor


def upsert_user(google_id: str, email: str, name: str, picture: str) -> dict:
    """Insert or update a Google user, return the row."""
    with get_conn() as conn:
        with get_cursor(conn) as cur:
            cur.execute(
                """
                INSERT INTO users (google_id, email, name, picture)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (google_id) DO UPDATE
                    SET email   = EXCLUDED.email,
                        name    = EXCLUDED.name,
                        picture = EXCLUDED.picture
                RETURNING id, google_id, email, name, picture, created_at
                """,
                (google_id, email, name, picture),
            )
            return dict(cur.fetchone())


def save_report(user_id: int, report: dict, title: str | None = None) -> dict:
    with get_conn() as conn:
        with get_cursor(conn) as cur:
            cur.execute(
                """
                INSERT INTO saved_reports (user_id, report, title)
                VALUES (%s, %s, %s)
                RETURNING id, user_id, title, saved_at
                """,
                (user_id, json.dumps(report), title),
            )
            return dict(cur.fetchone())


def get_saved_reports(user_id: int) -> list[dict]:
    with get_conn() as conn:
        with get_cursor(conn) as cur:
            cur.execute(
                """
                SELECT id, title, saved_at, report
                FROM saved_reports
                WHERE user_id = %s
                ORDER BY saved_at DESC
                """,
                (user_id,),
            )
            return [dict(row) for row in cur.fetchall()]


def delete_saved_report(user_id: int, report_id: int) -> bool:
    """Returns True if a row was deleted, False if it didn't exist / belong to user."""
    with get_conn() as conn:
        with get_cursor(conn) as cur:
            cur.execute(
                "DELETE FROM saved_reports WHERE id = %s AND user_id = %s",
                (report_id, user_id),
            )
            return cur.rowcount > 0