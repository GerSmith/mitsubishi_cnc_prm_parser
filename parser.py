# parser.py

"""Парсер:
    - Проверяет начало и конец на %;
    - Извлекает заголовок;
    - Пропускает PARA101().
    - Парсит параметры с помощью регулярного выражения.
"""

import re
from typing import List, TextIO
from models import Header, Parameter, PrmFile


# Регулярное выражение для разбора строк параметров
# Поддерживаем:
#   N123P456
#   N123T1P456
#   N123A2P456
#   N123K3P456
PARAM_REGEX = re.compile(
    r'^N(?P<number>\d+)'
    r'(?:T(?P<tool>\d+))?'
    r'(?:A(?P<axis>\d+))?'
    r'(?:K(?P<keep>\d+))?'
    r'P(?P<value>.*)$'
)


def parse_prm_file(file: TextIO, source_path: str = None) -> PrmFile:
    """
    Парсит файл ALL.PRM из текстового потока.
    
    :param file: текстовый файл (или StringIO и т.п.)
    :param source_path: опционально — путь к файлу для отладки
    :return: объект PrmFile
    :raises ValueError: при нарушении формата
    """
    lines = [line.rstrip('\r\n') for line in file]

    # 1. Проверка начала и конца
    if not lines or lines[0] != '%':
        raise ValueError("Файл должен начинаться с '%'")
    if len(lines) < 2:
        raise ValueError("Файл должен содержать как минимум две строки: тело и пустую строку в конце")
    if lines[-1] != '%':
        raise ValueError("Файл должен заканчиваться '%'")

    # 2. Извлечение заголовка (строки со ';')
    header_lines = []
    i = 1
    while i < len(lines) and lines[i].startswith(';'):
        header_lines.append(lines[i])
        i += 1

    header = Header(raw_lines=header_lines)

    # 3. Ожидаем PARA101()
    if i >= len(lines) or lines[i] != 'PARA101()':
        raise ValueError("Ожидалась строка 'PARA101()' после заголовка")
    i += 1

    # 4. Парсинг параметров
    parameters = {}
    while i < len(lines) - 2:  # пропускаем последние две строки: '%' и пустая
        line = lines[i]
        if not line:
            i += 1
            continue

        # Пропускаем нераспознанные строки (например, комментарии)
        if not line.startswith('N'):
            i += 1
            continue

        match = PARAM_REGEX.match(line)
        if not match:
            raise ValueError(f"Невозможно распарсить строку параметра: {line}")

        number = int(match.group('number'))
        tool = int(match.group('tool')) if match.group('tool') else None
        axis = int(match.group('axis')) if match.group('axis') else None
        keep = int(match.group('keep')) if match.group('keep') else None
        value = match.group('value')  # может быть пустой строкой

        param = Parameter(number=number, value=value, axis=axis, tool=tool)
        key = param.key()
        if key in parameters:
            # В теории такого быть не должно, но на случай дублей — перезапишем
            pass
        parameters[key] = param

        i += 1

    return PrmFile(header=header, parameters=parameters, source_path=source_path)
