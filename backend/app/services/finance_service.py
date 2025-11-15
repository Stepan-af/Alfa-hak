"""Сервис для работы с финансами"""
import csv
import io
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from collections import defaultdict

from app.models.finance import FinanceRecord, FinanceBudget, FinanceGoal
from app.schemas.finance import (
    FinanceRecordCreate,
    FinanceRecordUpdate,
    CSVUploadResponse,
    FinanceSummary,
    CategorySummary,
    MonthlyTrend,
    CashFlowData,
    BudgetStatus,
    AIInsight,
    FinanceInsights,
    FinanceBudgetCreate,
    FinanceBudgetUpdate,
    FinanceGoalCreate,
    FinanceGoalUpdate,
)


class FinanceService:
    """Сервис для работы с финансовыми данными"""

    # Стандартные категории расходов
    EXPENSE_CATEGORIES = {
        "аренда": "Недвижимость",
        "коммунальные": "Коммунальные услуги",
        "зарплата": "Зарплата сотрудникам",
        "налоги": "Налоги и сборы",
        "интернет": "Связь и интернет",
        "реклама": "Маркетинг",
        "канцелярия": "Канцтовары",
        "транспорт": "Транспорт",
        "оборудование": "Оборудование",
        "программное": "ПО и подписки",
        "страхование": "Страхование",
        "банк": "Банковские услуги",
        "юридические": "Юридические услуги",
        "обучение": "Обучение",
    }

    INCOME_CATEGORIES = {
        "продажа": "Продажи",
        "услуга": "Услуги",
        "консультация": "Консультации",
        "аренда": "Доход от аренды",
        "инвестиции": "Инвестиции",
    }

    @staticmethod
    def categorize_transaction(description: str, transaction_type: str) -> tuple[str, float]:
        """
        Автоматическая категоризация транзакции на основе описания
        
        Returns:
            tuple: (category, confidence)
        """
        if not description:
            return ("Без категории", 0.0)

        description_lower = description.lower()
        categories = FinanceService.EXPENSE_CATEGORIES if transaction_type == "expense" else FinanceService.INCOME_CATEGORIES

        # Простая эвристика: ищем ключевые слова
        for keyword, category in categories.items():
            if keyword in description_lower:
                return (category, 0.8)

        return ("Прочее", 0.5)

    @staticmethod
    def parse_csv_row(row: Dict[str, str]) -> Optional[FinanceRecordCreate]:
        """
        Парсинг строки CSV в FinanceRecordCreate
        
        Ожидаемый формат CSV:
        - date (DD.MM.YYYY или YYYY-MM-DD)
        - description
        - amount (с минусом для расходов или отдельная колонка type)
        - category (опционально)
        """
        try:
            # Парсинг даты
            date_str = row.get('date', row.get('Дата', ''))
            if '.' in date_str:
                # Формат DD.MM.YYYY
                day, month, year = date_str.split('.')
                transaction_date = date(int(year), int(month), int(day))
            else:
                # Формат YYYY-MM-DD
                transaction_date = datetime.strptime(date_str, '%Y-%m-%d').date()

            # Парсинг суммы
            amount_str = row.get('amount', row.get('Сумма', ''))
            amount_str = amount_str.replace(',', '.').replace(' ', '').replace('₽', '')
            amount = abs(Decimal(amount_str))

            # Определение типа транзакции
            type_str = row.get('type', row.get('Тип', ''))
            if type_str:
                transaction_type = 'income' if type_str.lower() in ['доход', 'income', '+'] else 'expense'
            else:
                # Если тип не указан, определяем по знаку суммы
                transaction_type = 'expense' if '-' in row.get('amount', row.get('Сумма', '')) else 'income'

            description = row.get('description', row.get('Описание', row.get('Назначение', '')))
            category = row.get('category', row.get('Категория', ''))

            # Автоматическая категоризация, если категория не указана
            if not category:
                category, _ = FinanceService.categorize_transaction(description, transaction_type)

            return FinanceRecordCreate(
                date=transaction_date,
                description=description,
                amount=amount,
                category=category,
                type=transaction_type,
                counterparty=row.get('counterparty', row.get('Контрагент', '')),
                payment_method=row.get('payment_method', row.get('Способ оплаты', '')),
                account=row.get('account', row.get('Счёт', '')),
            )
        except Exception as e:
            print(f"Error parsing CSV row: {e}, row: {row}")
            return None

    @staticmethod
    async def upload_csv(
        db: Session,
        user_id: int,
        file_content: bytes,
        file_name: str,
        encoding: str = 'utf-8'
    ) -> CSVUploadResponse:
        """Загрузка финансовых данных из CSV"""
        
        records_created = 0
        records_failed = 0
        errors = []

        try:
            # Декодирование файла
            content = file_content.decode(encoding)
            csv_file = io.StringIO(content)
            
            # Определение разделителя
            sample = content[:1024]
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            # Чтение CSV
            reader = csv.DictReader(csv_file, delimiter=delimiter)
            
            for row_num, row in enumerate(reader, start=2):  # start=2 т.к. 1-я строка - заголовки
                record_data = FinanceService.parse_csv_row(row)
                
                if record_data:
                    try:
                        # Автоматическая категоризация с AI
                        ai_category, ai_confidence = FinanceService.categorize_transaction(
                            record_data.description or '',
                            record_data.type
                        )
                        
                        # Создание записи
                        db_record = FinanceRecord(
                            user_id=user_id,
                            date=record_data.date,
                            description=record_data.description,
                            amount=record_data.amount,
                            category=record_data.category,
                            type=record_data.type,
                            counterparty=record_data.counterparty,
                            payment_method=record_data.payment_method,
                            account=record_data.account,
                            source_file=file_name,
                            raw_data=str(row),
                            ai_category=ai_category,
                            ai_confidence=float(ai_confidence),
                            is_verified=False,
                        )
                        db.add(db_record)
                        records_created += 1
                        
                    except Exception as e:
                        records_failed += 1
                        errors.append(f"Строка {row_num}: {str(e)}")
                else:
                    records_failed += 1
                    errors.append(f"Строка {row_num}: не удалось распарсить данные")
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            return CSVUploadResponse(
                success=False,
                records_created=0,
                records_failed=0,
                errors=[f"Ошибка обработки файла: {str(e)}"],
                file_name=file_name
            )

        return CSVUploadResponse(
            success=records_created > 0,
            records_created=records_created,
            records_failed=records_failed,
            errors=errors[:10],  # Ограничиваем количество ошибок
            file_name=file_name
        )

    @staticmethod
    def get_summary(
        db: Session,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> FinanceSummary:
        """Получить финансовую сводку за период"""
        
        if not start_date:
            start_date = date.today().replace(day=1)  # Начало текущего месяца
        if not end_date:
            end_date = date.today()

        # Запрос всех транзакций за период
        records = db.query(FinanceRecord).filter(
            and_(
                FinanceRecord.user_id == user_id,
                FinanceRecord.date >= start_date,
                FinanceRecord.date <= end_date
            )
        ).all()

        # Подсчёт сумм
        total_income = sum(r.amount for r in records if r.type == 'income')
        total_expense = sum(r.amount for r in records if r.type == 'expense')
        
        # Группировка по категориям
        income_by_cat = defaultdict(lambda: {'amount': Decimal(0), 'count': 0})
        expense_by_cat = defaultdict(lambda: {'amount': Decimal(0), 'count': 0})
        
        for record in records:
            category = record.category or 'Без категории'
            if record.type == 'income':
                income_by_cat[category]['amount'] += record.amount
                income_by_cat[category]['count'] += 1
            else:
                expense_by_cat[category]['amount'] += record.amount
                expense_by_cat[category]['count'] += 1

        # Формирование списков категорий
        income_categories = [
            CategorySummary(
                category=cat,
                amount=data['amount'],
                count=data['count'],
                percentage=float(data['amount'] / total_income * 100) if total_income > 0 else 0
            )
            for cat, data in sorted(income_by_cat.items(), key=lambda x: x[1]['amount'], reverse=True)
        ]
        
        expense_categories = [
            CategorySummary(
                category=cat,
                amount=data['amount'],
                count=data['count'],
                percentage=float(data['amount'] / total_expense * 100) if total_expense > 0 else 0
            )
            for cat, data in sorted(expense_by_cat.items(), key=lambda x: x[1]['amount'], reverse=True)
        ]

        return FinanceSummary(
            total_income=total_income,
            total_expense=total_expense,
            net_income=total_income - total_expense,
            transaction_count=len(records),
            income_by_category=income_categories,
            expense_by_category=expense_categories,
            period_start=start_date,
            period_end=end_date
        )

    @staticmethod
    def get_cash_flow(
        db: Session,
        user_id: int,
        months: int = 12
    ) -> CashFlowData:
        """Получить данные денежного потока по месяцам"""
        
        end_date = date.today()
        start_date = end_date - timedelta(days=months * 30)

        # Группировка по месяцам
        records = db.query(
            extract('year', FinanceRecord.date).label('year'),
            extract('month', FinanceRecord.date).label('month'),
            FinanceRecord.type,
            func.sum(FinanceRecord.amount).label('total')
        ).filter(
            and_(
                FinanceRecord.user_id == user_id,
                FinanceRecord.date >= start_date,
                FinanceRecord.date <= end_date
            )
        ).group_by('year', 'month', FinanceRecord.type).all()

        # Организация данных по месяцам
        monthly_data = defaultdict(lambda: {'income': Decimal(0), 'expense': Decimal(0)})
        
        for year, month, trans_type, total in records:
            month_key = f"{int(year)}-{int(month):02d}"
            if trans_type == 'income':
                monthly_data[month_key]['income'] = total
            else:
                monthly_data[month_key]['expense'] = total

        # Формирование трендов
        trends = []
        for month_key in sorted(monthly_data.keys()):
            data = monthly_data[month_key]
            trends.append(MonthlyTrend(
                month=month_key,
                income=data['income'],
                expense=data['expense'],
                net=data['income'] - data['expense']
            ))

        # Средние значения
        avg_income = sum(t.income for t in trends) / len(trends) if trends else Decimal(0)
        avg_expense = sum(t.expense for t in trends) / len(trends) if trends else Decimal(0)
        
        # Максимумы
        highest_income_month = max(trends, key=lambda t: t.income).month if trends else ""
        highest_expense_month = max(trends, key=lambda t: t.expense).month if trends else ""

        return CashFlowData(
            monthly_trends=trends,
            average_income=avg_income,
            average_expense=avg_expense,
            highest_income_month=highest_income_month,
            highest_expense_month=highest_expense_month
        )

    @staticmethod
    def generate_insights(
        db: Session,
        user_id: int
    ) -> FinanceInsights:
        """Генерация AI инсайтов и рекомендаций"""
        
        insights = []
        
        # Получаем данные за последние 3 месяца
        end_date = date.today()
        start_date = end_date - timedelta(days=90)
        
        summary = FinanceService.get_summary(db, user_id, start_date, end_date)
        
        # Инсайт 1: Убыточность
        if summary.net_income < 0:
            insights.append(AIInsight(
                type="warning",
                title="Отрицательный денежный поток",
                description=f"За последние 3 месяца расходы превысили доходы на {abs(summary.net_income):,.2f} ₽",
                priority="high",
                amount=abs(summary.net_income)
            ))
        
        # Инсайт 2: Топовая категория расходов
        if summary.expense_by_category:
            top_expense = summary.expense_by_category[0]
            if top_expense.percentage > 30:
                insights.append(AIInsight(
                    type="tip",
                    title=f"Высокие расходы на {top_expense.category}",
                    description=f"Эта категория составляет {top_expense.percentage:.1f}% всех расходов. Рассмотрите возможность оптимизации.",
                    priority="medium",
                    category=top_expense.category,
                    amount=top_expense.amount
                ))
        
        # Инсайт 3: Рост доходов
        cash_flow = FinanceService.get_cash_flow(db, user_id, months=3)
        if len(cash_flow.monthly_trends) >= 2:
            last_month = cash_flow.monthly_trends[-1]
            prev_month = cash_flow.monthly_trends[-2]
            growth = ((last_month.income - prev_month.income) / prev_month.income * 100) if prev_month.income > 0 else 0
            
            if growth > 10:
                insights.append(AIInsight(
                    type="opportunity",
                    title="Рост доходов",
                    description=f"Доходы выросли на {growth:.1f}% по сравнению с прошлым месяцем!",
                    priority="low",
                    amount=last_month.income - prev_month.income
                ))

        return FinanceInsights(
            insights=insights,
            generated_at=datetime.now()
        )

    # ========== CRUD операции для бюджетов ==========

    @staticmethod
    def create_budget(db: Session, user_id: int, budget: FinanceBudgetCreate) -> FinanceBudget:
        """Создать бюджет"""
        db_budget = FinanceBudget(
            user_id=user_id,
            **budget.model_dump()
        )
        db.add(db_budget)
        db.commit()
        db.refresh(db_budget)
        return db_budget

    @staticmethod
    def get_budget_status(db: Session, budget_id: int, user_id: int) -> Optional[BudgetStatus]:
        """Получить статус выполнения бюджета"""
        budget = db.query(FinanceBudget).filter(
            FinanceBudget.id == budget_id,
            FinanceBudget.user_id == user_id
        ).first()
        
        if not budget:
            return None

        # Подсчёт потраченной суммы
        spent = db.query(func.sum(FinanceRecord.amount)).filter(
            and_(
                FinanceRecord.user_id == user_id,
                FinanceRecord.category == budget.category,
                FinanceRecord.type == 'expense',
                FinanceRecord.date >= budget.start_date,
                FinanceRecord.date <= (budget.end_date or date.today())
            )
        ).scalar() or Decimal(0)

        remaining = budget.amount - spent
        percentage_used = float(spent / budget.amount * 100) if budget.amount > 0 else 0

        return BudgetStatus(
            budget=budget,
            spent=spent,
            remaining=remaining,
            percentage_used=percentage_used,
            is_over_budget=spent > budget.amount
        )

    # ========== CRUD операции для целей ==========

    @staticmethod
    def create_goal(db: Session, user_id: int, goal: FinanceGoalCreate) -> FinanceGoal:
        """Создать финансовую цель"""
        db_goal = FinanceGoal(
            user_id=user_id,
            **goal.model_dump()
        )
        db.add(db_goal)
        db.commit()
        db.refresh(db_goal)
        return db_goal
