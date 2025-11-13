# exporters/to_excel.py

from pathlib import Path
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from models import PrmFile


def export_to_excel(prm: PrmFile, output_path: Path):
    wb = Workbook()

    # Лист 1: Метаданные
    ws_header = wb.active
    ws_header.title = "Header"
    ws_header.append(["Field", "Value"])
    for i, line in enumerate(prm.header.raw_lines, start=1):
        ws_header.append([f"Line {i}", line.lstrip(";")])

    # Лист 2: Параметры
    ws_params = wb.create_sheet(title="Parameters")
    ws_params.append(["Parameter", "Axis", "Tool", "Keep", "Value"])

    for key in prm.parameters.keys():
        p = prm.parameters[key]
        ws_params.append(
            [
                p.number,
                p.axis if p.axis is not None else "",
                p.tool if p.tool is not None else "",
                p.keep if p.keep is not None else "",
                p.value,
            ]
        )

    # 🔒 Закрепляем первую строку на листе Parameters
    ws_params.freeze_panes = f"A2"

    wb.save(output_path)
