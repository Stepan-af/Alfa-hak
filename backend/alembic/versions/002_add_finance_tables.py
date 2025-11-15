"""add_finance_tables

Revision ID: 002
Revises: 001
Create Date: 2025-11-12

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # ### Add columns to finance_records ###
    op.add_column('finance_records', sa.Column('subcategory', sa.String(length=100), nullable=True))
    op.add_column('finance_records', sa.Column('counterparty', sa.String(length=255), nullable=True))
    op.add_column('finance_records', sa.Column('payment_method', sa.String(length=50), nullable=True))
    op.add_column('finance_records', sa.Column('account', sa.String(length=100), nullable=True))
    op.add_column('finance_records', sa.Column('tags', sa.Text(), nullable=True))
    op.add_column('finance_records', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column('finance_records', sa.Column('source_file', sa.String(length=255), nullable=True))
    op.add_column('finance_records', sa.Column('raw_data', sa.Text(), nullable=True))
    op.add_column('finance_records', sa.Column('ai_category', sa.String(length=100), nullable=True))
    op.add_column('finance_records', sa.Column('ai_confidence', sa.Numeric(precision=3, scale=2), nullable=True))
    op.add_column('finance_records', sa.Column('is_verified', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('finance_records', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    
    # Create indexes on finance_records
    op.create_index('idx_user_date', 'finance_records', ['user_id', 'date'], unique=False)
    op.create_index('idx_user_category', 'finance_records', ['user_id', 'category'], unique=False)
    op.create_index('idx_user_type', 'finance_records', ['user_id', 'type'], unique=False)
    op.create_index(op.f('ix_finance_records_category'), 'finance_records', ['category'], unique=False)
    op.create_index(op.f('ix_finance_records_date'), 'finance_records', ['date'], unique=False)
    
    # ### Create finance_budgets table ###
    op.create_table('finance_budgets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('period', sa.String(length=20), nullable=False, server_default='monthly'),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_finance_budgets_user_id'), 'finance_budgets', ['user_id'], unique=False)
    op.create_index('idx_user_category_budget', 'finance_budgets', ['user_id', 'category'], unique=False)
    
    # ### Create finance_goals table ###
    op.create_table('finance_goals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('target_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('current_amount', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('deadline', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_finance_goals_user_id'), 'finance_goals', ['user_id'], unique=False)


def downgrade():
    # ### Drop finance_goals table ###
    op.drop_index(op.f('ix_finance_goals_user_id'), table_name='finance_goals')
    op.drop_table('finance_goals')
    
    # ### Drop finance_budgets table ###
    op.drop_index('idx_user_category_budget', table_name='finance_budgets')
    op.drop_index(op.f('ix_finance_budgets_user_id'), table_name='finance_budgets')
    op.drop_table('finance_budgets')
    
    # ### Remove indexes from finance_records ###
    op.drop_index(op.f('ix_finance_records_date'), table_name='finance_records')
    op.drop_index(op.f('ix_finance_records_category'), table_name='finance_records')
    op.drop_index('idx_user_type', table_name='finance_records')
    op.drop_index('idx_user_category', table_name='finance_records')
    op.drop_index('idx_user_date', table_name='finance_records')
    
    # ### Remove columns from finance_records ###
    op.drop_column('finance_records', 'updated_at')
    op.drop_column('finance_records', 'is_verified')
    op.drop_column('finance_records', 'ai_confidence')
    op.drop_column('finance_records', 'ai_category')
    op.drop_column('finance_records', 'raw_data')
    op.drop_column('finance_records', 'source_file')
    op.drop_column('finance_records', 'notes')
    op.drop_column('finance_records', 'tags')
    op.drop_column('finance_records', 'account')
    op.drop_column('finance_records', 'payment_method')
    op.drop_column('finance_records', 'counterparty')
    op.drop_column('finance_records', 'subcategory')
