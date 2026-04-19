from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Bir nechta joydan .env ni qidiramiz: loyiha papkasi, ishga tushirilgan joriy papka,
# va app papka ichidan. Bu Windows foydalanuvchilarida yo‘l xatolari bo‘lsa ham yordam beradi.
ENV_CANDIDATES = [
    BASE_DIR / '.env',
    Path.cwd() / '.env',
    Path.cwd() / 'app' / '.env',
]
LOADED_ENV_PATH = None
for env_path in ENV_CANDIDATES:
    if env_path.exists():
        load_dotenv(env_path, override=True)
        LOADED_ENV_PATH = env_path
        break


@dataclass(frozen=True)
class Settings:
    bot_token: str
    admin_ids: set[int]
    database_path: Path
    questions_path: Path
    exam_minutes: int = 30


BRANCHES: Final[list[str]] = [
    'Niyozbosh',
    'Xalqabod',
    'Gulbahor',
    'Kasblar',
    'Kids1',
    'Kids2',
    'Do’stobod',
    'Olmazor',
    'Chinoz',
    'Krasin',
    'Pitiletka',
    'Qo’rg’oncha',
    'Kids 3',
]

SUBJECTS: Final[list[str]] = [
    'English',
    'Rus tili',
    'Kimyo',
    'Huquq',
    'Tarix',
    'Biologiya',
    'Hamshiralik',
    'IT',
    'Kampyuter',
]

KIMYO_PARTS: Final[list[str]] = ['Kimyo 1', 'Kimyo 2']
BIOLOGIYA_PARTS: Final[list[str]] = ['Biologiya 1', 'Biologiya 2']
HAMSHIRALIK_PARTS: Final[list[str]] = ['1-yordam', 'Anatomiya', 'Kasalliklar', 'Ineksiyalar']
IT_PARTS: Final[list[str]] = ['HTML&CSS 1', 'HTML&CSS 2', 'JAVASCRIPT 1', 'JAVASCRIPT 2']
KAMPYUTER_PARTS: Final[list[str]] = ['Kampyuter 1', 'Kampyuter 2']
ENGLISH_START_PARTS: Final[list[str]] = ['Starter']
ENGLISH_BEGINNER_PARTS: Final[list[str]] = ['Beginner 1', 'Beginner 2', 'Beginner 3']
ENGLISH_ELEMENTARY_PARTS: Final[list[str]] = ['Elementary 1', 'Elementary 2', 'Elementary 3']
ENGLISH_PREINTERMEDIATE_PARTS: Final[list[str]] = ['Pre-intermediate 1', 'Pre-intermediate 2', 'Pre-intermediate 3']
ENGLISH_INTERMEDIATE_PARTS: Final[list[str]] = ['Intermediate 1', 'Intermediate 2', 'Intermediate 3']
RUS_LEVELS: Final[list[str]] = ['A1', 'A2', 'B1']
RUS_A1_PARTS: Final[list[str]] = ['A1 (LEVEL 1)', 'A1 (LEVEL 2)', 'A1 (LEVEL 3)']
RUS_A2_PARTS: Final[list[str]] = ['A2 (LEVEL 1)', 'A2 (LEVEL 2)', 'A2 (LEVEL 3)']
RUS_B1_PARTS: Final[list[str]] = ['B1 (LEVEL 1)', 'B1 (LEVEL 2)', 'B1 (LEVEL 3)']

DIRECT_GROUP_SUBJECTS: Final[set[str]] = {'Huquq', 'Tarix'}

ENGLISH_LEVELS: Final[list[str]] = [
    'Starter',
    'Beginner',
    'Elementary',
    'Pre-Intermediate',
    'Intermediate',
]

LEVELS: Final[list[str]] = [
    'Beginner',
    'Elementary',
    'Pre-Intermediate',
]

BLOCKS: Final[list[str]] = ['1-4', '5-8', '9-12']


def _parse_admin_ids(raw: str) -> set[int]:
    ids: set[int] = set()
    for chunk in raw.split(','):
        chunk = chunk.strip()
        if chunk.isdigit():
            ids.add(int(chunk))
    return ids


def _clean_token(raw: str) -> str:
    token = raw.strip().strip('"').strip("'")
    # Token noto'g'ri ko'chirilganda yangi qatorlar yoki bo'shliqlar qolib ketishi mumkin.
    token = token.replace('\r', '').replace('\n', '').replace(' ', '')
    return token


def _validate_token_format(token: str) -> None:
    if not token:
        raise RuntimeError(
            "BOT_TOKEN topilmadi. Loyiha papkasidagi .env faylga token yozing.\n"
            "Misol:\n"
            "BOT_TOKEN=1234567890:AA...\n"
            "ADMIN_IDS=123456789"
        )
    if ':' not in token:
        raise RuntimeError("BOT_TOKEN formatida xato bor. Token ichida : belgisi bo'lishi kerak.")
    left, right = token.split(':', 1)
    if not left.isdigit() or len(right) < 20:
        raise RuntimeError("BOT_TOKEN noto'g'ri ko'rinmoqda. BotFather bergan tokenni to'liq qo'ying.")


def get_settings() -> Settings:
    token = _clean_token(os.getenv('BOT_TOKEN', ''))
    _validate_token_format(token)

    admin_ids = _parse_admin_ids(os.getenv('ADMIN_IDS', ''))
    database_path_raw = os.getenv('DATABASE_PATH', '').strip()
    database_path = Path(database_path_raw) if database_path_raw else (BASE_DIR / 'bot.db')
    if not database_path.is_absolute():
        database_path = (BASE_DIR / database_path).resolve()

    return Settings(
        bot_token=token,
        admin_ids=admin_ids,
        database_path=database_path,
        questions_path=BASE_DIR / 'data' / 'questions.json',
    )
