# models.py

"""Здесь определены структуры данных: Header, Parameter и PrmFile."""

from dataclasses import dataclass
from typing import Optional, Dict, List, Union


@dataclass
class Header:
    """Метаданные из строк, начинающихся с ';'."""

    raw_lines: List[str]

    @property
    def datetime(self) -> Optional[str]:
        if len(self.raw_lines) >= 1:
            return self.raw_lines[0].lstrip(";")
        return None

    @property
    def cnc_model(self) -> Optional[str]:
        if len(self.raw_lines) >= 2:
            return self.raw_lines[1].lstrip(";")
        return None

    @property
    def serials(self) -> List[str]:
        return [line.lstrip(";") for line in self.raw_lines[2:]]


@dataclass
class Parameter:
    """
    Представление одного параметра ЧПУ.
    Примеры:
      N1P28 → number=1, axis=None, tool=None, value='28'
      N1001T1P1 → number=1001, tool=1, value='1'
      N2025A4P9000 → number=2025, axis=4, value='9000'
      N1926K1P192 → number=1926, keep=1, value='192'
    """

    number: int
    value: str  # всегда строка (может быть пустой)
    axis: Optional[int] = None  # из A1..A9 → 1..9
    tool: Optional[int] = None  # из T1..T9 → 1..9
    keep: Optional[int] = None  # из K1..K9 → 1..9

    def key(self) -> str:
        """Уникальный идентификатор параметра для сравнения и хранения."""
        parts = [str(self.number)]
        if self.axis is not None:
            parts.append(f"A{self.axis}")
        if self.tool is not None:
            parts.append(f"T{self.tool}")
        if self.keep is not None:
            parts.append(f"K{self.keep}")
        return "_".join(parts)


@dataclass
class PrmFile:
    """Полное представление файла ALL.PRM."""

    header: Header
    parameters: Dict[str, Parameter]  # ключ — результат .key()
    source_path: Optional[str] = None
