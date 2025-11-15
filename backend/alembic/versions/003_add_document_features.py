"""add_document_features

Revision ID: 003
Revises: 002
Create Date: 2025-11-12

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # ### Add columns to documents ###
    op.add_column('documents', sa.Column('document_type', sa.String(length=100), nullable=True))
    op.add_column('documents', sa.Column('variables', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('documents', sa.Column('file_format', sa.String(length=20), nullable=True, server_default='docx'))
    op.add_column('documents', sa.Column('version', sa.Integer(), nullable=True, server_default='1'))
    op.add_column('documents', sa.Column('counterparty_name', sa.String(length=255), nullable=True))
    op.add_column('documents', sa.Column('counterparty_inn', sa.String(length=50), nullable=True))
    op.add_column('documents', sa.Column('amount', sa.String(length=100), nullable=True))
    op.add_column('documents', sa.Column('currency', sa.String(length=10), nullable=True, server_default='RUB'))
    op.add_column('documents', sa.Column('ai_generated', sa.String(length=50), nullable=True))
    
    # Create indexes on documents (with IF NOT EXISTS check)
    op.execute("CREATE INDEX IF NOT EXISTS idx_doc_user_type ON documents (user_id, document_type)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_doc_user_status ON documents (user_id, status)")
    
    # ### Add columns to templates ###
    op.add_column('templates', sa.Column('document_type', sa.String(length=100), nullable=True))
    op.add_column('templates', sa.Column('variables', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('templates', sa.Column('is_system', sa.String(length=10), nullable=True, server_default='false'))
    op.add_column('templates', sa.Column('user_id', sa.Integer(), nullable=True))
    op.add_column('templates', sa.Column('usage_count', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('templates', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    
    # Create foreign key on templates
    op.create_foreign_key('fk_templates_user_id', 'templates', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    
    # Create index on templates
    op.create_index(op.f('ix_templates_category'), 'templates', ['category'], unique=False)


def downgrade():
    # ### Drop indexes on templates ###
    op.drop_index(op.f('ix_templates_category'), table_name='templates')
    
    # ### Drop foreign key on templates ###
    op.drop_constraint('fk_templates_user_id', 'templates', type_='foreignkey')
    
    # ### Remove columns from templates ###
    op.drop_column('templates', 'updated_at')
    op.drop_column('templates', 'usage_count')
    op.drop_column('templates', 'user_id')
    op.drop_column('templates', 'is_system')
    op.drop_column('templates', 'variables')
    op.drop_column('templates', 'document_type')
    
    # ### Drop indexes on documents ###
    op.execute("DROP INDEX IF EXISTS idx_doc_user_status")
    op.execute("DROP INDEX IF EXISTS idx_doc_user_type")
    
    # ### Remove columns from documents ###
    op.drop_column('documents', 'ai_generated')
    op.drop_column('documents', 'currency')
    op.drop_column('documents', 'amount')
    op.drop_column('documents', 'counterparty_inn')
    op.drop_column('documents', 'counterparty_name')
    op.drop_column('documents', 'version')
    op.drop_column('documents', 'file_format')
    op.drop_column('documents', 'variables')
    op.drop_column('documents', 'document_type')
