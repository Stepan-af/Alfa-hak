#!/usr/bin/env python3
"""
Скрипт для тестирования отправки Magic Link email
Использование: docker exec -it alfacopilot-api python test_email.py
"""

import asyncio
import sys
import os

# Добавляем путь к app
sys.path.insert(0, "/app")

from app.services.email import send_magic_link_email
from app.config import settings


async def test_email():
    print("\n" + "=" * 80)
    print("📧 ТЕСТ ОТПРАВКИ MAGIC LINK EMAIL")
    print("=" * 80)
    print(f"\n📝 Текущие настройки SMTP:")
    print(f"   Host: {settings.SMTP_HOST}")
    print(f"   Port: {settings.SMTP_PORT}")
    print(f"   User: {settings.SMTP_USER}")
    print(f"   From: {settings.SMTP_FROM}")
    print(f"   DEBUG: {settings.DEBUG}")
    print()
    
    # Запрашиваем email для отправки
    email = input("🔹 Введите email для отправки тестового письма: ").strip()
    
    if not email or '@' not in email:
        print("❌ Ошибка: Неверный формат email")
        return
    
    print(f"\n⏳ Отправка тестового письма на {email}...")
    
    try:
        await send_magic_link_email(email, "test-token-12345")
        print("\n✅ УСПЕШНО! Письмо отправлено.")
        
        if settings.DEBUG:
            print("\n💡 Режим DEBUG=true: письмо не отправлено, ссылка выше ↑")
        else:
            print(f"\n💡 Проверьте почту {email}")
            print("   Если письма нет, проверьте:")
            print("   1. Папку 'Спам'")
            print("   2. Подождите 1-2 минуты")
            print("   3. Логи выше на наличие ошибок")
        
    except Exception as e:
        print(f"\n❌ ОШИБКА при отправке: {e}")
        print("\n🔧 Проверьте:")
        print("   1. Правильность SMTP настроек в .env файле")
        print("   2. Для Gmail: используйте App Password, а не обычный пароль")
        print("   3. Создайте App Password: https://myaccount.google.com/apppasswords")
        print("\n📖 Подробная инструкция: /app/../EMAIL_SETUP.md")
        return
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    try:
        asyncio.run(test_email())
    except KeyboardInterrupt:
        print("\n\n⚠️  Отменено пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
