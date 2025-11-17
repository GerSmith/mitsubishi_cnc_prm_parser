# main.py

import sys
import argparse
from pathlib import Path

from parser import parse_prm_file
from models import PrmFile
from utils import load_descriptions


def main():
    parser = argparse.ArgumentParser(description="Парсер файла ALL.PRM от ЧПУ Mitsubishi M800")
    parser.add_argument(
        "input_file",
        nargs="?",
        default="ALL.PRM",
        help="Путь к файлу ALL.PRM (по умолчанию: ALL.PRM)",
    )
    parser.add_argument("-o", "--output", help="Путь для экспорта в Excel (например, output.xlsx)")
    parser.add_argument(
        "--descriptions", type=Path, help="Путь к YAML-файлу со справочником описаний параметров"
    )
    parser.add_argument(
        "--axis-names",
        action="store_true",
        help="Использовать имена осей из параметра 1013 (X/Y/Z и т.д.) вместо A1/A2/...",
    )
    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ Файл не найден: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Загрузка справочника
    descriptions_path = args.descriptions or Path("descriptions.yaml")
    descriptions = {}
    if args.descriptions is not None:
        # Пользователь явно указал путь — сообщаем, если файл не найден
        if not descriptions_path.exists():
            print(
                f"ℹ️  Файл справочника не найден: {descriptions_path}. Экспорт выполняется без описаний."
            )
        else:
            try:
                descriptions = load_descriptions(descriptions_path)
            except ValueError as e:
                print(f"❌ {e}", file=sys.stderr)
                sys.exit(1)
    else:
        # Используем descriptions.yaml по умолчанию — молча, если его нет
        if descriptions_path.exists():
            try:
                descriptions = load_descriptions(descriptions_path)
            except ValueError as e:
                print(f"❌ {e}", file=sys.stderr)
                sys.exit(1)

    # Парсинг
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
        print(f";{line.lstrip(';')}")

    # Вывод первых 10 параметров с описанием
    print(f"\n--- Параметры (всего: {total}) ---")
    for i, (key, param) in enumerate(list(prm.parameters.items())[:10], start=1):
        parts = [f"N{param.number}"]
        if param.axis is not None:
            parts.append(f"A{param.axis}")
        if param.tool is not None:
            parts.append(f"T{param.tool}")
        if param.keep is not None:
            parts.append(f"K{param.keep}")
        full_name = "".join(parts)
        desc = descriptions.get(param.number, {}).get("description", "")
        print(f"{i:2d}. {full_name} = {repr(param.value)}{f' → {desc}' if desc else ''}")

    if total > 10:
        print(f"... и ещё {total - 10} параметров")

    # Экспорт в Excel, если указан флаг
    if args.output:
        try:
            from exporters.to_excel import export_to_excel

            export_to_excel(
                prm, Path(args.output), descriptions=descriptions, use_axis_names=args.axis_names
            )
            print(f"\n✅ Экспорт в Excel завершён: {args.output}")
        except ImportError as e:
            print(f"❌ Ошибка импорта: {e}. Убедитесь, что установлен openpyxl.", file=sys.stderr)
            sys.exit(1)

    print("\n✅ Парсинг завершён успешно.")


if __name__ == "__main__":
    main()
