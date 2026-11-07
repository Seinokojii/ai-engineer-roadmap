#!/usr/bin/env python3
"""
day_003-004.py — Day 003–004: Python для AI-кода
Запуск: uv run python lessons/day_003-004.py

Что делает:
  1. Прогоняет 10 «грязных» строк через normalize и script_of: до и после.
  2. Создаёт отзывы через pydantic: хорошие проходят, плохие падают с точной ошибкой.
  3. Оборачивает ValidationError в своё исключение ValidationFailed.
  4. Показывает logging: те же вызовы на уровне INFO и DEBUG.
  5. Пишет итог в reports/day_003-004.json через pathlib.

Заметка дня: notes/01_Foundations/Day_003-004_Python_for_AI.md
"""

import json
import logging
import sys
from pathlib import Path

from pydantic import ValidationError

from aieng.errors import AiengError, ValidationFailed
from aieng.text import Review, normalize, script_of

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

log = logging.getLogger("day_003-004")

DIRTY = [
    "  Очень   вкусный кофе!  ",
    "Кофейня\u00a0«Зерно» — топ",
    "Норм,\tно  долго ждали",
    "\ufeffСпасибо за сервис",
    "ёлка у входа красивая",  # «ё» из двух символов
    "Абдан  даамдуу, үй-бүлө менен келебиз",
    "Ыңгайлуу жай,\u202fкызмат жакшы",
    "заказ через WhatsApp, всё ок",
    "Kофе холодный",  # первая буква — латинская K
    "Great   coffee,  “nice”  staff",
]


def header(title: str) -> None:
    print("\n" + "=" * 60 + f"\n  {title}\n" + "=" * 60)


def step1_normalize() -> list[dict]:
    header("STEP 1: normalize + script_of на 10 грязных строках")
    rows = []
    for raw in DIRTY:
        clean = normalize(raw)
        script = script_of(clean)
        rows.append({"raw": raw, "clean": clean, "script": script, "changed": raw != clean})
        mark = "*" if raw != clean else " "
        print(f"  {mark} {raw!r:44} → {clean!r}")
        print(f"    {'':44}   алфавит: {script}, символов {len(raw)} → {len(clean)}")
    changed = sum(r["changed"] for r in rows)
    print(
        f"\n  Изменено строк: {changed}. «ёлка» на экране та же, но символов стало меньше:\n"
        "  две точки слились с буквой. «mixed» у «Kофе» — латинская K в русском слове."
    )
    return rows


def step2_validate() -> list[dict]:
    header("STEP 2: pydantic проверяет данные на границе")
    cases = [
        {"text": "Отлично", "rating": 5},
        {"text": "  Норм  ", "rating": "4"},
        {"text": "Без оценки"},
        {"text": "Отлично", "rating": 7},
        {"text": "   \u00a0 ", "rating": 3},
        {"text": "Плохо", "rating": "пять"},
    ]
    results = []
    for data in cases:
        try:
            review = Review(**data)
            print(f"  OK    {data!s:42} → text={review.text!r}, rating={review.rating!r}")
            results.append({"input": data, "ok": True, "rating": review.rating})
        except ValidationError as err:
            first = err.errors()[0]
            field = ".".join(map(str, first["loc"]))
            print(f"  ОТКАЗ {data!s:42} → поле {field}: {first['msg']}")
            results.append({"input": data, "ok": False, "field": field, "msg": first["msg"]})
    print("\n  Заметь: rating='4' стал int 4, а 'пять' отклонён — pydantic приводит, но не гадает.")
    return results


def parse_review(data: dict) -> Review:
    """Граница системы: снаружи приходит dict, внутрь уходит Review или наше исключение."""
    try:
        return Review(**data)
    except ValidationError as err:
        raise ValidationFailed(f"bad review: {err.error_count()} error(s)") from err


def step3_own_exception() -> None:
    header("STEP 3: своё исключение вместо чужого")
    try:
        parse_review({"text": "", "rating": 9})
    except AiengError as err:
        print(f"  Поймали {type(err).__name__}: {err}")
        print(f"  Причина сохранена в __cause__: {type(err.__cause__).__name__}")
    print("  Вызывающий код ловит AiengError и не зависит от того, что внутри pydantic.")


def step4_logging() -> None:
    header("STEP 4: logging — уровень меняется, код нет")
    logging.basicConfig(
        stream=sys.stdout, format="  %(levelname)-7s %(name)s: %(message)s", force=True
    )

    logging.getLogger().setLevel(logging.INFO)
    print("  Уровень INFO — подробности normalize не видны:")
    log.info("нормализую 2 строки")
    normalize("  два  пробела ")
    normalize("«кавычки»")

    logging.getLogger().setLevel(logging.DEBUG)
    print("\n  Уровень DEBUG — видно, что именно поменял normalize:")
    log.info("нормализую 2 строки")
    normalize("  два  пробела ")
    normalize("«кавычки»")
    logging.getLogger().setLevel(logging.WARNING)


def main() -> None:
    rows = step1_normalize()
    reviews = step2_validate()
    step3_own_exception()
    step4_logging()

    report = REPORTS / "day_003-004.json"
    report.write_text(
        json.dumps({"normalize": rows, "reviews": reviews}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n  Отчёт: {report.relative_to(ROOT)}")
    print("\n  ГОТОВО. Дальше: «Твой ход» в заметке дня.")
    print('  git add lessons/day_003-004.py && git commit -m "feat: Day 003-004 aieng.text"')


if __name__ == "__main__":
    main()
