# main.py

import sys
import argparse
from pathlib import Path

from parser import parse_prm_file
from models import PrmFile


def main():
    parser = argparse.ArgumentParser(description="Парсер файла ALL.PRM от ЧПУ Mitsubishi M800")
    parser.add_argument("input_file", nargs="?", default="ALL.PRM", help="Путь к файлу ALL.PRM (по умолчанию: ALL.PRM)")
    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ Файл не найден: {input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            prm: PrmFile = parse_prm_file(f, source_path=str(input_path))
    except ValueError as e:
        print(f"❌ Ошибка парсинга: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}", file=sys.stderr)
        sys.exit(1)

    # Вывод метаданных
    print("✅ Файл успешно загружен!")
    print("\n--- Заголовок (метаданные) ---")
    for i, line in enumerate(prm.header.raw_lines, start=1):
        print(f"{line.lstrip(';')}")

    # Вывод количества параметров
    total = len(prm.parameters)
    print(f"\n--- Параметры (всего: {total}) ---")

    # Вывод первых 10 параметров для проверки
    for i, (key, param) in enumerate(list(prm.parameters.items())[:10], start=1):
        axis_str = f"A{param.axis}" if param.axis is not None else ""
        tool_str = f"T{param.tool}" if param.tool is not None else ""
        keep_str = f"K{param.keep}" if param.keep is not None else ""
        suffix = f"{axis_str}{tool_str}{keep_str}" if axis_str or tool_str or keep_str else ""
        print(f"{i:2d}. N{param.number}{suffix} = {repr(param.value)}")

    if total > 10:
        print(f"... и ещё {total - 10} параметров")

    print("\n✅ Парсинг завершён успешно.")


if __name__ == "__main__":
    main()
