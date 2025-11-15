#!/bin/bash

# Скрипт проверки работоспособности приложения
# Использование: ./verify.sh

echo "🔍 Проверка работоспособности Alfa Copilot"
echo ""

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция проверки
check_service() {
    local name=$1
    local url=$2
    local expected=$3
    
    echo -n "Проверка ${name}... "
    response=$(curl -s -o /dev/null -w "%{http_code}" "${url}" 2>/dev/null)
    
    if [ "$response" = "$expected" ]; then
        echo -e "${GREEN}✅ OK${NC} (HTTP ${response})"
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (HTTP ${response}, ожидалось ${expected})"
        return 1
    fi
}

# Проверка доступности сервисов
echo "1️⃣ Проверка контейнеров..."
docker-compose ps --format "table {{.Name}}\t{{.Status}}" | grep -v "NAME"
echo ""

# Проверка API
echo "2️⃣ Проверка API endpoints..."
check_service "API Docs" "http://localhost:8000/docs" "200"
check_service "API Health" "http://localhost:8000/api/v1/finance/summary" "200"
check_service "API Trends" "http://localhost:8000/api/v1/finance/summary-with-trends" "200"
echo ""

# Проверка Frontend
echo "3️⃣ Проверка Frontend..."
check_service "Frontend" "http://localhost:3000" "200"
check_service "Nginx Proxy" "http://localhost:80" "200"
echo ""

# Проверка LLM сервисов
echo "4️⃣ Проверка LLM сервисов..."
check_service "Ollama" "http://localhost:11434" "200"
check_service "LiteLLM" "http://localhost:4000/health" "200"
echo ""

# Проверка тестовых данных
echo "5️⃣ Проверка данных..."
finance_data=$(curl -s http://localhost:8000/api/v1/finance/summary 2>/dev/null)
total_income=$(echo "$finance_data" | python3 -c "import sys, json; print(json.load(sys.stdin)['total_income'])" 2>/dev/null)

if [ ! -z "$total_income" ]; then
    echo -e "${GREEN}✅ Финансовые данные доступны${NC} (доход: ${total_income})"
else
    echo -e "${YELLOW}⚠️  Финансовых данных нет (это нормально для нового развертывания)${NC}"
fi
echo ""

# Проверка docker-compose.yml
echo "6️⃣ Проверка конфигурации..."
if docker-compose config --quiet 2>/dev/null; then
    echo -e "${GREEN}✅ docker-compose.yml валиден${NC}"
else
    echo -e "${RED}❌ docker-compose.yml содержит ошибки${NC}"
fi
echo ""

# Проверка образов
echo "7️⃣ Проверка Docker образов..."
api_image=$(docker-compose config | grep -A 1 "api:" | grep "image:" | awk '{print $2}')
frontend_image=$(docker-compose config | grep -A 1 "frontend:" | grep "image:" | awk '{print $2}' | head -1)

echo "API образ: ${api_image}"
echo "Frontend образ: ${frontend_image}"

if [[ $api_image == *"stepanpd"* ]] && [[ $frontend_image == *"stepanpd"* ]]; then
    echo -e "${GREEN}✅ Используются образы из Docker Registry${NC}"
else
    echo -e "${YELLOW}⚠️  Используются локальные образы${NC}"
fi
echo ""

# Итоги
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Проверка завершена!${NC}"
echo ""
echo "📚 Полезные команды:"
echo "  • Логи API:      docker-compose logs -f api"
echo "  • Логи Frontend: docker-compose logs -f frontend"
echo "  • Перезапуск:    docker-compose restart"
echo "  • Статус:        docker-compose ps"
echo ""
echo "🌐 Ссылки:"
echo "  • Frontend:      http://localhost:3000"
echo "  • API Docs:      http://localhost:8000/docs"
echo "  • Nginx:         http://localhost:80"
