# utils.py

import yaml
from pathlib import Path
from typing import Dict, Optional


def load_descriptions(path: Optional[Path]) -> Dict[int, dict]:
    """
    Загружает справочник описаний параметров из YAML-файла.
    Возвращает словарь: {параметр: {описание}}
    """
    if path is None or not path.exists():
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"Ошибка парсинга YAML в файле {path}: {e}")
    except Exception as e:
        raise ValueError(f"Не удалось прочитать файл {path}: {e}")

    if data is None:
        return {}

    if not isinstance(data, dict):
        raise ValueError(f"Файл {path} должен содержать словарь верхнего уровня.")

    # Преобразуем ключи в int и проверяем структуру
    normalized = {}
    for key, value in data.items():
        try:
            param_num = int(key)
        except (ValueError, TypeError):
            raise ValueError(f"Некорректный номер параметра в YAML: '{key}'. Ожидалось число.")

        if not isinstance(value, dict):
            raise ValueError(f"Описание параметра {param_num} должно быть словарём.")

        # Ожидаемые поля (необязательные, но проверим типы)
        expected_str_fields = {"group", "subgroup", "shortname", "description"}
        for field in expected_str_fields:
            if field in value and value[field] is not None and not isinstance(value[field], str):
                raise ValueError(
                    f"Поле '{field}' у параметра {param_num} должно быть строкой или null."
                )

        normalized[param_num] = value

    return normalized
