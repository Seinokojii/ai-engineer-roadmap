#!/usr/bin/env python3
"""
day_001-002.py — Day 001–002: среда разработки (uv, pyproject, ruff, pytest)
Запуск: uv run python lessons/day_001-002.py

Что делает:
  1. Показывает, в каком окружении запущен: версия Python и путь к .venv проекта.
  2. Сверяет pyproject.toml и uv.lock: что объявлено и что именно установлено.
  3. Прогоняет те же проверки, что CI: ruff check, ruff format --check, pytest.
  4. Напоминает «Твой ход» — изменение, которое делается руками.

Заметка дня: notes/01_Foundations/Day_001-002_Environment.md
"""

import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def header(title: str) -> None:
    print("\n" + "=" * 55 + f"\n  {title}\n" + "=" * 55)


def run(cmd: list[str]) -> bool:
    """Запускает команду из корня репозитория, печатает хвост вывода и код возврата."""
    print(f"\n  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    out = (result.stdout + result.stderr).strip().splitlines()
    for line in out[-3:]:
        print(f"    {line}")
    ok = result.returncode == 0
    print(f"    → {'OK' if ok else 'ОШИБКА'} (код {result.returncode})")
    return ok


def step1_environment() -> None:
    header("STEP 1: в каком окружении мы запущены")
    venv = Path(sys.prefix)
    print(f"  Python:  {sys.version.split()[0]}")
    print(f"  Окружение: {venv}")
    inside = venv == ROOT / ".venv"
    print(f"  Это .venv проекта? {'да' if inside else 'НЕТ — запусти через uv run'}")


def step2_declared_vs_locked() -> None:
    header("STEP 2: pyproject.toml (что нужно) против uv.lock (что стоит)")
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    lock = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))
    locked = {p["name"]: p["version"] for p in lock.get("package", [])}

    declared = project["project"]["dependencies"] + project["dependency-groups"]["dev"]
    print(f"  {'объявлено в pyproject':<28}{'зафиксировано в uv.lock'}")
    for spec in declared:
        name = spec.split(">")[0].split("=")[0].split("<")[0].strip()
        print(f"  {spec:<28}{name}=={locked.get(name, '?')}")
    print(f"\n  Всего пакетов в lock вместе с зависимостями зависимостей: {len(locked)}")


def step3_ci_checks() -> bool:
    header("STEP 3: те же проверки, что в .github/workflows/ci.yml")
    checks = [
        ["uv", "run", "ruff", "check", "."],
        ["uv", "run", "ruff", "format", "--check", "."],
        ["uv", "run", "pytest"],
    ]
    return all([run(cmd) for cmd in checks])


def step4_your_move() -> None:
    header("STEP 4: ✋ Твой ход (руками, 10–20 минут)")
    print("""  1. В tests/test_config.py в test_key_from_env_file замени "test-key"
     в последней строке на "other-key" и запусти: uv run pytest
     Прочитай вывод: слева то, что вернул код, справа то, что ждал тест.
  2. Верни как было — тест снова зелёный.
  3. Открой test_local_model_from_env_file и объясни себе вслух,
     зачем там monkeypatch.delenv("LOCAL_MODEL"). Подсказка: что будет,
     если в твоём терминале уже задана переменная LOCAL_MODEL?""")


def main() -> None:
    step1_environment()
    step2_declared_vs_locked()
    ok = step3_ci_checks()
    step4_your_move()
    if ok:
        print("\n  ГОТОВО. Все проверки зелёные — так же их увидит CI.")
    else:
        print("\n  Есть красные проверки — разбери вывод выше.")
    print('  git add lessons/day_001-002.py && git commit -m "feat: Day 001-002 environment"')
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
