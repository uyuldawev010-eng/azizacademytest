from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu(is_admin: bool) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text='Oylik imtihon')],
        [KeyboardButton(text='Natijalar')],
    ]
    if is_admin:
        rows.append([KeyboardButton(text='Guruh yaratish')])
        rows.append([KeyboardButton(text='Excel format yuklash')])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def simple_inline(items: list[tuple[str, str]], back_data: str | None = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for text, data in items:
        builder.row(InlineKeyboardButton(text=text, callback_data=data))
    if back_data:
        builder.row(InlineKeyboardButton(text='⬅️ Ortga', callback_data=back_data))
    return builder.as_markup()


def exam_options_keyboard(attempt_id: int, question_index: int, options: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for idx, _option in enumerate(options):
        label = f"{letters[idx]})" if idx < len(letters) else f"{idx + 1})"
        builder.row(
            InlineKeyboardButton(
                text=label,
                callback_data=f'ea:{attempt_id}:{question_index}:{idx}',
            )
        )
    return builder.as_markup()
