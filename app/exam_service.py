from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

UTC = timezone.utc


class QuestionBank:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.data: dict[str, Any] = json.loads(path.read_text(encoding='utf-8'))

    def get_questions(self, subject_name: str, level_name: str | None, block_name: str | None) -> list[dict[str, Any]]:
        subject = self.data.get(subject_name, {})

        direct_questions = subject.get('__direct__')
        if isinstance(direct_questions, list):
            return direct_questions

        level = subject.get(level_name or '', {})
        questions = level.get(block_name or '', [])
        if not isinstance(questions, list):
            return []
        return questions


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value)


def remaining_seconds(started_at: str, minutes: int) -> int:
    start = parse_iso(started_at)
    end = start + timedelta(minutes=minutes)
    diff = int((end - datetime.now(UTC)).total_seconds())
    return max(diff, 0)


def format_remaining(seconds: int) -> str:
    mins, sec = divmod(seconds, 60)
    hours, mins = divmod(mins, 60)
    return f'{hours:02d}:{mins:02d}:{sec:02d}'


def is_special_part(attempt: dict[str, Any]) -> bool:
    return attempt.get('block_name') == 'Asosiy'


def header_line(attempt: dict[str, Any]) -> str:
    if is_special_part(attempt):
        return f"📘 <b>{attempt['subject_name']}</b> | {attempt['level_name']}"
    return f"📘 <b>{attempt['subject_name']}</b> | {attempt['level_name']} | Blok {attempt['block_name']}"


def option_label(index: int) -> str:
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if 0 <= index < len(letters):
        return f"{letters[index]})"
    return f"{index + 1})"


def format_question_with_options(question: dict[str, Any]) -> str:
    options = question.get('options', [])
    if not options:
        return question.get('question', '')
    lines = [question.get('question', ''), '']
    for idx, option in enumerate(options):
        lines.append(f"{option_label(idx)} {option}")
    return '\n'.join(lines)


def question_text(attempt: dict[str, Any], question_index: int, minutes: int) -> str:
    questions = json.loads(attempt['questions_json'])
    q = questions[question_index]
    left = format_remaining(remaining_seconds(attempt['started_at'], minutes))
    return (
        f"{header_line(attempt)}\n"
        f"🏫 Filial: {attempt['branch']}\n"
        f"👥 Guruh: {attempt['group_number']}\n"
        f"⏳ Qolgan vaqt: <b>{left}</b>\n\n"
        f"<b>{question_index + 1}-savol / {attempt['total_questions']}</b>\n"
        f"{format_question_with_options(q)}"
    )


def percent_text(score: int, total: int) -> str:
    if total <= 0:
        return '0%'
    percent = (score / total) * 100
    if float(percent).is_integer():
        return f"{int(percent)}%"
    return f"{percent:.1f}%"


def attempt_result_text(attempt: dict[str, Any]) -> str:
    score = int(attempt['score'] or 0)
    total = int(attempt['total_questions'] or 0)
    lines = [
        '📄 <b>Natija</b>',
        f"👤 O'quvchi: {attempt['full_name']}",
        f"🏫 Filial: {attempt['branch']}",
        f"📚 Fan: {attempt['subject_name']}",
    ]
    if is_special_part(attempt):
        lines.append(f"📂 Bo'lim: {attempt['level_name']}")
    else:
        lines.append(f"🎯 Daraja: {attempt['level_name']}")
        lines.append(f"🔢 Blok: {attempt['block_name']}")
    lines.extend([
        f"👥 Guruh: {attempt['group_number']}",
        f"📊 Foiz: <b>{percent_text(score, total)}</b>",
        f"📌 Holat: {attempt['status']}",
    ])
    return '\n'.join(lines)

