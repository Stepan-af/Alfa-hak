#!/usr/bin/env python
"""
Test script to verify all imports work correctly
"""

print("🔍 Testing imports...")

try:
    import fastapi
    print(f"✅ FastAPI {fastapi.__version__}")
except ImportError as e:
    print(f"❌ FastAPI: {e}")

try:
    import sqlalchemy
    print(f"✅ SQLAlchemy {sqlalchemy.__version__}")
except ImportError as e:
    print(f"❌ SQLAlchemy: {e}")

try:
    from pydantic_settings import BaseSettings
    print("✅ pydantic-settings")
except ImportError as e:
    print(f"❌ pydantic-settings: {e}")

try:
    import redis
    print(f"✅ Redis {redis.__version__}")
except ImportError as e:
    print(f"❌ Redis: {e}")

try:
    import celery
    print(f"✅ Celery {celery.__version__}")
except ImportError as e:
    print(f"❌ Celery: {e}")

print("\n📦 Testing app imports...")

try:
    # Set dummy env vars for testing
    import os
    os.environ.setdefault("DATABASE_URL", "postgresql://test")
    os.environ.setdefault("REDIS_URL", "redis://test")
    os.environ.setdefault("JWT_SECRET_KEY", "test")
    os.environ.setdefault("SMTP_HOST", "test")
    os.environ.setdefault("SMTP_USER", "test")
    os.environ.setdefault("SMTP_PASSWORD", "test")
    os.environ.setdefault("SMTP_FROM", "test@test.com")
    os.environ.setdefault("OLLAMA_BASE_URL", "http://test")
    os.environ.setdefault("LITELLM_BASE_URL", "http://test")
    
    from app.database import Base
    print("✅ app.database")
except Exception as e:
    print(f"❌ app.database: {e}")

try:
    from app.models import User
    print("✅ app.models")
except Exception as e:
    print(f"❌ app.models: {e}")

print("\n✨ All imports tested!")
