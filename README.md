# mitsubishi_prm_parser

![meme](meme.jpg)

### 0.1 Подготовка окружения

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
python.exe -m pip install --upgrade pip
```

### 0.2 Установка библиотеки openpyxl для работы с данными Excel

```bash
pip install openpyxl
```

### 1.1 Работа со скриптом

```bash
python .\main.py
```
Будет искать в директории проекта файл `ALL.PRM` что разпарсить его, если такого не найдёт выдаст ошибку

### 1.2 Экспорт в excel

```bash
python main.py ALL.PRM -o output.xlsx
```

или без явного указания файла `ALL.PRM`, подразумевая что он находится в той же директории что и скрипт

```bash
python main.py -o output.xlsx
```