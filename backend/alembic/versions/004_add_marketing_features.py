"""add_marketing_campaigns

Revision ID: 004
Revises: 003
Create Date: 2024-01-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем новые поля в таблицу marketing_campaigns
    op.add_column('marketing_campaigns', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('marketing_campaigns', sa.Column('content_type', sa.String(length=100), nullable=True))
    op.add_column('marketing_campaigns', sa.Column('target_audience', sa.String(length=255), nullable=True))
    op.add_column('marketing_campaigns', sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('marketing_campaigns', sa.Column('scheduled_date', sa.Date(), nullable=True))
    op.add_column('marketing_campaigns', sa.Column('published_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('marketing_campaigns', sa.Column('ai_prompt', sa.Text(), nullable=True))
    op.add_column('marketing_campaigns', sa.Column('ai_generated', sa.String(length=10), server_default='false', nullable=True))
    op.add_column('marketing_campaigns', sa.Column('views', sa.Integer(), server_default='0', nullable=True))
    op.add_column('marketing_campaigns', sa.Column('likes', sa.Integer(), server_default='0', nullable=True))
    op.add_column('marketing_campaigns', sa.Column('shares', sa.Integer(), server_default='0', nullable=True))
    
    # Создаём индексы
    op.execute('CREATE INDEX IF NOT EXISTS idx_marketing_user_platform ON marketing_campaigns (user_id, platform)')
    op.execute('CREATE INDEX IF NOT EXISTS idx_marketing_user_status ON marketing_campaigns (user_id, status)')
    op.execute('CREATE INDEX IF NOT EXISTS idx_marketing_scheduled_date ON marketing_campaigns (scheduled_date)')
    op.execute('CREATE INDEX IF NOT EXISTS idx_marketing_platform ON marketing_campaigns (platform)')
    op.execute('CREATE INDEX IF NOT EXISTS idx_marketing_status ON marketing_campaigns (status)')


def downgrade() -> None:
    # Удаляем индексы
    op.execute('DROP INDEX IF EXISTS idx_marketing_status')
    op.execute('DROP INDEX IF EXISTS idx_marketing_platform')
    op.execute('DROP INDEX IF EXISTS idx_marketing_scheduled_date')
    op.execute('DROP INDEX IF EXISTS idx_marketing_user_status')
    op.execute('DROP INDEX IF EXISTS idx_marketing_user_platform')
    
    # Удаляем колонки
    op.drop_column('marketing_campaigns', 'shares')
    op.drop_column('marketing_campaigns', 'likes')
    op.drop_column('marketing_campaigns', 'views')
    op.drop_column('marketing_campaigns', 'ai_generated')
    op.drop_column('marketing_campaigns', 'ai_prompt')
    op.drop_column('marketing_campaigns', 'published_date')
    op.drop_column('marketing_campaigns', 'scheduled_date')
    op.drop_column('marketing_campaigns', 'tags')
    op.drop_column('marketing_campaigns', 'target_audience')
    op.drop_column('marketing_campaigns', 'content_type')
    op.drop_column('marketing_campaigns', 'description')
