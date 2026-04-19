from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

UTC = timezone.utc


class Database:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = str(path)

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def init(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                '''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    full_name TEXT,
                    username TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS groups_table (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    branch TEXT NOT NULL,
                    subject_name TEXT NOT NULL,
                    group_number TEXT NOT NULL,
                    created_by INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE(branch, subject_name, group_number)
                );

                CREATE TABLE IF NOT EXISTS attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    username TEXT,
                    full_name TEXT NOT NULL,
                    branch TEXT NOT NULL,
                    subject_name TEXT NOT NULL,
                    level_name TEXT NOT NULL,
                    block_name TEXT NOT NULL,
                    group_id INTEGER NOT NULL,
                    group_number TEXT NOT NULL,
                    total_questions INTEGER NOT NULL,
                    started_at TEXT NOT NULL,
                    submitted_at TEXT,
                    status TEXT NOT NULL,
                    score INTEGER DEFAULT 0,
                    answers_json TEXT NOT NULL DEFAULT '{}',
                    questions_json TEXT NOT NULL,
                    FOREIGN KEY(group_id) REFERENCES groups_table(id)
                );
                CREATE INDEX IF NOT EXISTS idx_attempts_active ON attempts(status, user_id);
                CREATE INDEX IF NOT EXISTS idx_attempts_group ON attempts(branch, subject_name, group_id, status);
                '''
            )

    def upsert_user(self, user_id: int, full_name: str | None, username: str | None) -> None:
        now = self.now_iso()
        with self.connect() as conn:
            conn.execute(
                '''
                INSERT INTO users(user_id, full_name, username, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    full_name = COALESCE(excluded.full_name, users.full_name),
                    username = excluded.username,
                    updated_at = excluded.updated_at
                ''',
                (user_id, full_name, username, now, now),
            )

    def get_user(self, user_id: int) -> sqlite3.Row | None:
        with self.connect() as conn:
            row = conn.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
        return row

    def create_group(self, branch: str, subject_name: str, group_number: str, created_by: int) -> tuple[bool, str]:
        with self.connect() as conn:
            try:
                conn.execute(
                    '''
                    INSERT INTO groups_table(branch, subject_name, group_number, created_by, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    ''',
                    (branch, subject_name, group_number, created_by, self.now_iso()),
                )
                return True, 'Guruh saqlandi.'
            except sqlite3.IntegrityError:
                return False, 'Bu filial + fan + guruh allaqachon mavjud.'

    def list_groups(self, branch: str, subject_name: str) -> list[sqlite3.Row]:
        with self.connect() as conn:
            rows = conn.execute(
                '''
                SELECT * FROM groups_table
                WHERE branch = ? AND subject_name = ?
                ORDER BY CAST(group_number AS INTEGER), group_number COLLATE NOCASE
                ''',
                (branch, subject_name),
            ).fetchall()
        return list(rows)

    def list_branch_groups(self, branch: str) -> list[sqlite3.Row]:
        with self.connect() as conn:
            rows = conn.execute(
                '''
                SELECT * FROM groups_table
                WHERE branch = ?
                ORDER BY subject_name COLLATE NOCASE, CAST(group_number AS INTEGER), group_number COLLATE NOCASE
                ''',
                (branch,),
            ).fetchall()
        return list(rows)

    def list_branch_subjects(self, branch: str) -> list[str]:
        with self.connect() as conn:
            rows = conn.execute(
                '''
                SELECT DISTINCT subject_name
                FROM groups_table
                WHERE branch = ?
                ORDER BY subject_name COLLATE NOCASE
                ''',
                (branch,),
            ).fetchall()
        return [row['subject_name'] for row in rows]

    def list_groups_for_branch_subject(self, branch: str, subject_name: str) -> list[sqlite3.Row]:
        with self.connect() as conn:
            rows = conn.execute(
                '''
                SELECT * FROM groups_table
                WHERE branch = ? AND subject_name = ?
                ORDER BY CAST(group_number AS INTEGER), group_number COLLATE NOCASE
                ''',
                (branch, subject_name),
            ).fetchall()
        return list(rows)

    def get_group(self, group_id: int) -> sqlite3.Row | None:
        with self.connect() as conn:
            row = conn.execute('SELECT * FROM groups_table WHERE id = ?', (group_id,)).fetchone()
        return row

    def find_active_attempt(self, user_id: int) -> sqlite3.Row | None:
        with self.connect() as conn:
            row = conn.execute(
                '''
                SELECT * FROM attempts
                WHERE user_id = ? AND status = 'active'
                ORDER BY id DESC LIMIT 1
                ''',
                (user_id,),
            ).fetchone()
        return row

    def create_attempt(
        self,
        *,
        user_id: int,
        username: str | None,
        full_name: str,
        branch: str,
        subject_name: str,
        level_name: str,
        block_name: str,
        group_id: int,
        group_number: str,
        questions: list[dict[str, Any]],
    ) -> int:
        with self.connect() as conn:
            cursor = conn.execute(
                '''
                INSERT INTO attempts(
                    user_id, username, full_name, branch, subject_name, level_name, block_name,
                    group_id, group_number, total_questions, started_at, status, answers_json, questions_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', '{}', ?)
                ''',
                (
                    user_id,
                    username,
                    full_name,
                    branch,
                    subject_name,
                    level_name,
                    block_name,
                    group_id,
                    group_number,
                    len(questions),
                    self.now_iso(),
                    json.dumps(questions, ensure_ascii=False),
                ),
            )
            return int(cursor.lastrowid)

    def get_attempt(self, attempt_id: int) -> sqlite3.Row | None:
        with self.connect() as conn:
            row = conn.execute('SELECT * FROM attempts WHERE id = ?', (attempt_id,)).fetchone()
        return row

    def save_answer(self, attempt_id: int, question_index: int, option_index: int) -> None:
        attempt = self.get_attempt(attempt_id)
        if not attempt:
            return
        answers = json.loads(attempt['answers_json'])
        answers[str(question_index)] = option_index
        with self.connect() as conn:
            conn.execute(
                'UPDATE attempts SET answers_json = ? WHERE id = ?',
                (json.dumps(answers, ensure_ascii=False), attempt_id),
            )

    def finalize_attempt(self, attempt_id: int, status: str = 'submitted') -> sqlite3.Row | None:
        attempt = self.get_attempt(attempt_id)
        if not attempt or attempt['status'] != 'active':
            return attempt
        questions = json.loads(attempt['questions_json'])
        answers = json.loads(attempt['answers_json'])
        score = 0
        for idx, q in enumerate(questions):
            if answers.get(str(idx)) == q['correct_index']:
                score += 1
        with self.connect() as conn:
            conn.execute(
                '''
                UPDATE attempts
                SET status = ?, submitted_at = ?, score = ?
                WHERE id = ?
                ''',
                (status, self.now_iso(), score, attempt_id),
            )
        return self.get_attempt(attempt_id)

    def get_answered_count(self, attempt_id: int) -> int:
        attempt = self.get_attempt(attempt_id)
        if not attempt:
            return 0
        answers = json.loads(attempt['answers_json'])
        return len(answers)

    def get_current_question_index(self, attempt_id: int) -> int:
        attempt = self.get_attempt(attempt_id)
        if not attempt:
            return 0
        answers = json.loads(attempt['answers_json'])
        if not answers:
            return 0
        return min(len(answers), attempt['total_questions'] - 1)

    def get_expired_attempts(self, minutes: int) -> list[sqlite3.Row]:
        threshold = datetime.now(UTC) - timedelta(minutes=minutes)
        with self.connect() as conn:
            rows = conn.execute(
                '''
                SELECT * FROM attempts
                WHERE status = 'active' AND started_at <= ?
                ''',
                (threshold.isoformat(),),
            ).fetchall()
        return list(rows)

    def list_students_with_results(self, group_id: int) -> list[sqlite3.Row]:
        with self.connect() as conn:
            rows = conn.execute(
                '''
                SELECT a1.*
                FROM attempts a1
                JOIN (
                    SELECT full_name, MAX(id) AS max_id
                    FROM attempts
                    WHERE group_id = ? AND status IN ('submitted', 'time_up')
                    GROUP BY full_name
                ) latest ON latest.max_id = a1.id
                ORDER BY (CASE WHEN a1.total_questions > 0 THEN (a1.score * 1.0 / a1.total_questions) ELSE 0 END) DESC, a1.full_name COLLATE NOCASE
                ''',
                (group_id,),
            ).fetchall()
        return list(rows)



    def list_export_attempts_for_branch(self, branch: str) -> list[sqlite3.Row]:
        with self.connect() as conn:
            rows = conn.execute(
                '''
                SELECT *
                FROM attempts
                WHERE branch = ? AND status IN ('submitted', 'time_up')
                ORDER BY subject_name COLLATE NOCASE,
                         CAST(group_number AS INTEGER), group_number COLLATE NOCASE,
                         level_name COLLATE NOCASE,
                         block_name COLLATE NOCASE,
                         (CASE WHEN total_questions > 0 THEN (score * 1.0 / total_questions) ELSE 0 END) DESC,
                         submitted_at ASC,
                         id ASC
                ''',
                (branch,),
            ).fetchall()
        return list(rows)

    def list_branches_with_results(self) -> list[str]:
        with self.connect() as conn:
            rows = conn.execute(
                '''
                SELECT DISTINCT branch
                FROM attempts
                WHERE status IN ('submitted', 'time_up')
                ORDER BY branch COLLATE NOCASE
                '''
            ).fetchall()
        return [row['branch'] for row in rows]

    @staticmethod
    def now_iso() -> str:
        return datetime.now(UTC).isoformat()
