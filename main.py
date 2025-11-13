# main.py

import sys
import argparse
from pathlib import Path

from parser import parse_prm_file
from models import PrmFile


def main():
    parser = argparse.ArgumentParser(description="Парсер файла ALL.PRM от ЧПУ Mitsubishi M800")
    parser.add_argument(
        "input_file",
        nargs="?",
        default="ALL.PRM",
        help="Путь к файлу ALL.PRM (по умолчанию: ALL.PRM)",
    )
    parser.add_argument("-o", "--output", help="Путь для экспорта в Excel (например, output.xlsx)")
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

    total = len(prm.parameters)
    print("✅ Файл успешно загружен!")

    # Вывод метаданных
    print("\n--- Заголовок (метаданные) ---")
    for line in prm.header.raw_lines:
        print(f"{line.lstrip(';')}")

    # Вывод первых 10 параметров
    print(f"\n--- Параметры (всего: {total}) ---")
    for i, (key, param) in enumerate(list(prm.parameters.items())[:10], start=1):
        parts = [f"N{param.number}"]
        if param.axis is not None:
            parts.append(f"A{param.axis}")
        if param.tool is not None:
            parts.append(f"T{param.tool}")
        if param.keep is not None:
            parts.append(f"K{param.keep}")
        suffix = "".join(parts[1:])
        full_name = f"N{param.number}{suffix}" if suffix else f"N{param.number}"
        print(f"{i:2d}. {full_name} = {repr(param.value)}")

    if total > 10:
        print(f"... и ещё {total - 10} параметров")

    # Экспорт в Excel, если указан флаг
    if args.output:
        try:
            from exporters.to_excel import export_to_excel

            export_to_excel(prm, Path(args.output))
            print(f"\n✅ Экспорт в Excel завершён: {args.output}")
        except ImportError as e:
            print(f"❌ Ошибка импорта: {e}. Убедитесь, что установлен openpyxl.", file=sys.stderr)
            sys.exit(1)

    print("\n✅ Парсинг завершён успешно.")


if __name__ == "__main__":
    main()
