from sqlalchemy import Column, Integer, String, Text, Date, Numeric, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class FinanceRecord(Base):
    """Финансовая транзакция (доход или расход)"""
    __tablename__ = "finance_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    description = Column(Text, nullable=True)
    amount = Column(Numeric(15, 2), nullable=False)
    category = Column(String(100), nullable=True, index=True)
    subcategory = Column(String(100), nullable=True)
    type = Column(String(20), nullable=False)  # income, expense
    
    # Дополнительные поля
    counterparty = Column(String(255), nullable=True)  # Контрагент
    payment_method = Column(String(50), nullable=True)  # Способ оплаты
    account = Column(String(100), nullable=True)  # Счёт
    tags = Column(Text, nullable=True)  # JSON массив тегов
    notes = Column(Text, nullable=True)  # Заметки
    
    # Для CSV импорта
    source_file = Column(String(255), nullable=True)  # Имя файла источника
    raw_data = Column(Text, nullable=True)  # Исходные данные из CSV
    
    # AI анализ
    ai_category = Column(String(100), nullable=True)  # Категория от AI
    ai_confidence = Column(Numeric(3, 2), nullable=True)  # Уверенность AI (0-1)
    is_verified = Column(Boolean, default=False)  # Проверено пользователем
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="finance_records")
    
    # Индексы для оптимизации запросов
    __table_args__ = (
        Index('idx_user_date', 'user_id', 'date'),
        Index('idx_user_category', 'user_id', 'category'),
        Index('idx_user_type', 'user_id', 'type'),
    )


class FinanceBudget(Base):
    """Бюджет по категориям"""
    __tablename__ = "finance_budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(100), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)  # Плановая сумма
    period = Column(String(20), nullable=False, default="monthly")  # monthly, yearly
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="finance_budgets")
    
    __table_args__ = (
        Index('idx_user_category_budget', 'user_id', 'category'),
    )


class FinanceGoal(Base):
    """Финансовые цели"""
    __tablename__ = "finance_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    target_amount = Column(Numeric(15, 2), nullable=False)
    current_amount = Column(Numeric(15, 2), default=0)
    deadline = Column(Date, nullable=True)
    status = Column(String(20), default="active")  # active, completed, cancelled
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="finance_goals")
