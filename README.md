# KZ Parser

Парсер для автоматизированной работы с порталом erap-public.kgp.kz.

## Функциональность

- Автоматическая авторизация через ЭЦП
- Поиск и загрузка неоплаченных штрафов
- Автоматическое сохранение документов в PDF формате

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/bellinel/kzpars.git
cd kzpars
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Использование

1. Запустите скрипт:
```bash
python main.py
```

2. Следуйте инструкциям в консоли для авторизации через ЭЦП.

## Требования

- Python 3.8+
- Google Chrome
- NCALayer для работы с ЭЦП 