#!/bin/bash

# Backend setup script
# Этот скрипт автоматически настраивает backend окружение

echo "🚀 Настройка Backend окружения..."

# Перейти в директорию backend
cd "$(dirname "$0")"

# Проверка Python версии
echo "📋 Проверка Python..."
if command -v pyenv &> /dev/null; then
    echo "✅ pyenv найден"
    pyenv local 3.11.13
else
    echo "⚠️  pyenv не найден, используем системный Python"
fi

PYTHON_VERSION=$(python --version)
echo "Python версия: $PYTHON_VERSION"

# Создание виртуального окружения
if [ ! -d ".venv" ]; then
    echo "📦 Создание виртуального окружения..."
    python -m venv .venv
    echo "✅ Виртуальное окружение создано"
else
    echo "✅ Виртуальное окружение уже существует"
fi

# Активация виртуального окружения
echo "🔧 Активация виртуального окружения..."
source .venv/bin/activate

# Обновление pip
echo "⬆️  Обновление pip..."
pip install --upgrade pip

# Установка зависимостей
echo "📥 Установка зависимостей..."
pip install -r requirements.txt

# Проверка установки
echo ""
echo "🧪 Проверка установки..."
python -c "import fastapi; print('✅ FastAPI:', fastapi.__version__)" 2>/dev/null || echo "❌ FastAPI не установлен"
python -c "import sqlalchemy; print('✅ SQLAlchemy:', sqlalchemy.__version__)" 2>/dev/null || echo "❌ SQLAlchemy не установлен"
python -c "import redis; print('✅ Redis:', redis.__version__)" 2>/dev/null || echo "❌ Redis не установлен"
python -c "import celery; print('✅ Celery:', celery.__version__)" 2>/dev/null || echo "❌ Celery не установлен"

echo ""
echo "✨ Готово! Для активации окружения используйте:"
echo "   cd backend && source .venv/bin/activate"
echo ""
echo "📝 Следующие шаги:"
echo "1. Настройте .env файл в корне проекта"
echo "2. В VS Code: Cmd+Shift+P -> 'Python: Select Interpreter' -> выберите ./backend/.venv/bin/python"
echo "3. Перезапустите VS Code"
