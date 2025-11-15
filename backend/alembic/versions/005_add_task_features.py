"""add_task_features

Revision ID: 005
Revises: 004
Create Date: 2024-01-15 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Изменяем значение по умолчанию для status
    op.execute("ALTER TABLE tasks ALTER COLUMN status SET DEFAULT 'todo'")
    
    # Добавляем новые поля
    op.add_column('tasks', sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tasks', sa.Column('category', sa.String(length=100), nullable=True))
    op.add_column('tasks', sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('tasks', sa.Column('ai_suggested', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('tasks', sa.Column('ai_context', sa.Text(), nullable=True))
    op.add_column('tasks', sa.Column('is_recurring', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('tasks', sa.Column('recurrence_pattern', sa.String(length=100), nullable=True))
    op.add_column('tasks', sa.Column('parent_task_id', sa.Integer(), nullable=True))
    op.add_column('tasks', sa.Column('attachments', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('tasks', sa.Column('linked_document_id', sa.Integer(), nullable=True))
    op.add_column('tasks', sa.Column('estimated_minutes', sa.Integer(), nullable=True))
    op.add_column('tasks', sa.Column('actual_minutes', sa.Integer(), nullable=True))
    
    # Добавляем foreign key для parent_task_id
    op.create_foreign_key(
        'fk_tasks_parent_task_id',
        'tasks', 'tasks',
        ['parent_task_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Создаём индексы
    op.execute('CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks (user_id)')
    op.execute('CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks (priority)')
    op.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status)')
    op.execute('CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks (due_date)')
    op.execute('CREATE INDEX IF NOT EXISTS idx_tasks_category ON tasks (category)')
    op.execute('CREATE INDEX IF NOT EXISTS idx_tasks_user_status ON tasks (user_id, status)')
    op.execute('CREATE INDEX IF NOT EXISTS idx_tasks_user_priority ON tasks (user_id, priority)')
    op.execute('CREATE INDEX IF NOT EXISTS idx_tasks_user_due_date ON tasks (user_id, due_date)')
    op.execute('CREATE INDEX IF NOT EXISTS idx_tasks_user_category ON tasks (user_id, category)')


def downgrade() -> None:
    # Удаляем индексы
    op.execute('DROP INDEX IF EXISTS idx_tasks_user_category')
    op.execute('DROP INDEX IF EXISTS idx_tasks_user_due_date')
    op.execute('DROP INDEX IF EXISTS idx_tasks_user_priority')
    op.execute('DROP INDEX IF EXISTS idx_tasks_user_status')
    op.execute('DROP INDEX IF EXISTS idx_tasks_category')
    op.execute('DROP INDEX IF EXISTS idx_tasks_due_date')
    op.execute('DROP INDEX IF EXISTS idx_tasks_status')
    op.execute('DROP INDEX IF EXISTS idx_tasks_priority')
    op.execute('DROP INDEX IF EXISTS idx_tasks_user_id')
    
    # Удаляем foreign key
    op.drop_constraint('fk_tasks_parent_task_id', 'tasks', type_='foreignkey')
    
    # Удаляем колонки
    op.drop_column('tasks', 'actual_minutes')
    op.drop_column('tasks', 'estimated_minutes')
    op.drop_column('tasks', 'linked_document_id')
    op.drop_column('tasks', 'attachments')
    op.drop_column('tasks', 'parent_task_id')
    op.drop_column('tasks', 'recurrence_pattern')
    op.drop_column('tasks', 'is_recurring')
    op.drop_column('tasks', 'ai_context')
    op.drop_column('tasks', 'ai_suggested')
    op.drop_column('tasks', 'tags')
    op.drop_column('tasks', 'category')
    op.drop_column('tasks', 'completed_at')
    
    # Возвращаем старое значение по умолчанию для status
    op.execute("ALTER TABLE tasks ALTER COLUMN status SET DEFAULT 'pending'")
