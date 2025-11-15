# Backend Python setup instructions

## Исправление ошибок импорта в VS Code

### Шаг 1: Убедитесь, что виртуальное окружение создано

```bash
cd backend

# Если используете pyenv
pyenv local 3.11.13

# Создайте виртуальное окружение
python -m venv .venv

# Активируйте его
source .venv/bin/activate  # macOS/Linux
```

### Шаг 2: Установите зависимости

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Шаг 3: Настройте VS Code

1. **Откройте Command Palette** (Cmd+Shift+P на macOS)
2. Введите: `Python: Select Interpreter`
3. Выберите интерпретатор из `./backend/.venv/bin/python`

**Или вручную:**
- Файл `.vscode/settings.json` уже создан с правильными настройками
- VS Code должен автоматически определить виртуальное окружение

### Шаг 4: Перезапустите VS Code

```bash
# Закройте и откройте VS Code или выполните:
# Command Palette (Cmd+Shift+P) -> "Developer: Reload Window"
```

### Шаг 5: Проверьте, что всё работает

```bash
cd backend

# Должно работать без ошибок
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
python -c "import sqlalchemy; print('SQLAlchemy:', sqlalchemy.__version__)"
python -c "from app.config import settings; print('Config loaded')"
```

## Альтернативный способ (если не помогло)

### Вариант 1: Используйте workspace settings

Создайте файл `backend.code-workspace` в корне проекта:

```json
{
  "folders": [
    {
      "path": "backend"
    },
    {
      "path": "frontend"
    }
  ],
  "settings": {
    "python.defaultInterpreterPath": "${workspaceFolder:backend}/.venv/bin/python"
  }
}
```

### Вариант 2: Установите Pylance (если не установлен)

1. Откройте Extensions (Cmd+Shift+X)
2. Найдите и установите "Pylance"
3. Перезапустите VS Code

### Вариант 3: Проверьте pyrightconfig.json

Создан файл `backend/pyrightconfig.json` для явной настройки Pylance.

## Структура виртуального окружения

Должна быть такая структура:

```
backend/
├── .venv/              # Виртуальное окружение
│   ├── bin/
│   │   └── python     # Python интерпретатор
│   └── lib/
├── app/
├── requirements.txt
└── ...
```

## Troubleshooting

### Проблема: VS Code не видит .venv

**Решение:**
```bash
cd backend
ls -la .venv/bin/python  # Проверьте, что файл существует
which python             # Должно показать путь к .venv
```

### Проблема: Импорты всё ещё подчёркнуты красным

**Решение:**
1. Откройте любой Python файл в backend
2. Внизу справа в VS Code кликните на версию Python
3. Выберите `.venv` интерпретатор
4. Нажмите Cmd+Shift+P -> "Python: Restart Language Server"

### Проблема: ModuleNotFoundError при запуске

**Решение:**
```bash
cd backend
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -m app.main
```

## Проверка настройки

После настройки выполните:

```bash
cd backend
source .venv/bin/activate
python -c "
from app.config import settings
from app.database import Base
from app.models import User
print('✅ Все импорты работают!')
"
```

Если видите "✅ Все импорты работают!" - всё настроено правильно!
