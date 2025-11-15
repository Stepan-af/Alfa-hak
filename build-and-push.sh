#!/bin/bash

# Скрипт для сборки и публикации Docker образов
# Использование: ./build-and-push.sh <registry-url> <version>
# Пример: ./build-and-push.sh ghcr.io/stepan-af v1.0.0

set -e

# Проверка аргументов
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "❌ Использование: ./build-and-push.sh <registry-url> <version>"
    echo "Пример: ./build-and-push.sh ghcr.io/stepan-af v1.0.0"
    echo "Пример: ./build-and-push.sh docker.io/stepanaf v1.0.0"
    exit 1
fi

REGISTRY_URL=$1
VERSION=$2
BACKEND_IMAGE="${REGISTRY_URL}/alfa-hak-backend"
FRONTEND_IMAGE="${REGISTRY_URL}/alfa-hak-frontend"

echo "🚀 Сборка и публикация образов в Docker Registry"
echo "Registry: ${REGISTRY_URL}"
echo "Version: ${VERSION}"
echo ""

# Билд и пуш backend
echo "📦 Сборка backend образа..."
docker build -t "${BACKEND_IMAGE}:${VERSION}" -t "${BACKEND_IMAGE}:latest" ./backend

echo "⬆️  Публикация backend образа..."
docker push "${BACKEND_IMAGE}:${VERSION}"
docker push "${BACKEND_IMAGE}:latest"

echo "✅ Backend опубликован:"
echo "  - ${BACKEND_IMAGE}:${VERSION}"
echo "  - ${BACKEND_IMAGE}:latest"
echo ""

# Билд и пуш frontend
echo "📦 Сборка frontend образа..."
docker build -t "${FRONTEND_IMAGE}:${VERSION}" -t "${FRONTEND_IMAGE}:latest" ./frontend

echo "⬆️  Публикация frontend образа..."
docker push "${FRONTEND_IMAGE}:${VERSION}"
docker push "${FRONTEND_IMAGE}:latest"

echo "✅ Frontend опубликован:"
echo "  - ${FRONTEND_IMAGE}:${VERSION}"
echo "  - ${FRONTEND_IMAGE}:latest"
echo ""

echo "🎉 Все образы успешно опубликованы!"
echo ""
echo "📝 Для использования обновите docker-compose.yml:"
echo "  api:"
echo "    image: ${BACKEND_IMAGE}:${VERSION}"
echo ""
echo "  frontend:"
echo "    image: ${FRONTEND_IMAGE}:${VERSION}"
