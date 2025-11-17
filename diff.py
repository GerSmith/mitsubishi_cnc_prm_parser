# diff.py

import sys
import argparse
from pathlib import Path

from parser import parse_prm_file
from utils import load_descriptions
from comparator import compare_prm_files


def main():
    parser = argparse.ArgumentParser(
        description="Сравнение двух файлов ALL.PRM от ЧПУ Mitsubishi M800"
    )
    parser.add_argument("old_file", help="Путь к первому (старому) файлу ALL.PRM")
    parser.add_argument("new_file", help="Путь ко второму (новому) файлу ALL.PRM")
    parser.add_argument(
        "-o",
        "--output",
        default="diff.xlsx",
        help="Путь для сохранения Excel-отчёта (по умолчанию: diff.xlsx)",
    )
    parser.add_argument(
        "--descriptions", type=Path, help="YAML-файл со справочником описаний параметров"
    )
    parser.add_argument(
        "--axis-names", action="store_true", help="Использовать имена осей (X/Y/Z) вместо A1/A2/..."
    )
    args = parser.parse_args()

    try:
        # Загрузка справочника
        descriptions = {}
        if args.descriptions:
            if not args.descriptions.exists():
                print(f"ℹ️  Файл справочника не найден: {args.descriptions}", file=sys.stderr)
            else:
                descriptions = load_descriptions(args.descriptions)

        # Парсинг
        with open(args.old_file, "r", encoding="utf-8") as f:
            old_prm = parse_prm_file(f, source_path=args.old_file)

        with open(args.new_file, "r", encoding="utf-8") as f:
            new_prm = parse_prm_file(f, source_path=args.new_file)

        # Имена файлов для заголовков
        file1_name = Path(args.old_file).stem
        file2_name = Path(args.new_file).stem

        # Сравнение
        output_path = Path(args.output)
        compare_prm_files(
            old_prm,
            new_prm,
            output_path=output_path,
            descriptions=descriptions,
            use_axis_names=args.axis_names,
            file1_name=file1_name,
            file2_name=file2_name,
        )

        print(f"✅ Отчёт о различиях сохранён: {output_path}")

    except Exception as e:
        print(f"❌ Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
