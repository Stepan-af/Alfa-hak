"""Add chat features

Revision ID: 006
Revises: 005
Create Date: 2025-11-12

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if chat_conversations table exists, if not create it
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if 'chat_conversations' not in inspector.get_table_names():
        op.create_table(
            'chat_conversations',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=255), nullable=False, server_default='Новый разговор'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('is_archived', sa.Boolean(), server_default='false', nullable=True),
            sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_chat_conversations_id', 'chat_conversations', ['id'])
        op.create_index('ix_chat_conversations_user_id', 'chat_conversations', ['user_id'])
        op.create_index('ix_chat_conversations_updated_at', 'chat_conversations', ['updated_at'])
    
    # Check and modify chat_messages table
    if 'chat_messages' in inspector.get_table_names():
        # Get existing columns
        existing_columns = {col['name'] for col in inspector.get_columns('chat_messages')}
        
        # Add conversation_id if not exists
        if 'conversation_id' not in existing_columns:
            # First add conversation_id column (nullable temporarily)
            op.add_column('chat_messages', sa.Column('conversation_id', sa.Integer(), nullable=True))
            
            # Create default conversation for existing messages
            op.execute("""
                INSERT INTO chat_conversations (user_id, title, created_at, updated_at)
                SELECT DISTINCT user_id, 'Старые сообщения', MIN(created_at), MAX(created_at)
                FROM chat_messages
                GROUP BY user_id
            """)
            
            # Update chat_messages with conversation_id
            op.execute("""
                UPDATE chat_messages cm
                SET conversation_id = cc.id
                FROM chat_conversations cc
                WHERE cm.user_id = cc.user_id AND cc.title = 'Старые сообщения'
            """)
            
            # Make conversation_id non-nullable
            op.alter_column('chat_messages', 'conversation_id', nullable=False)
            
            # Add foreign key
            op.create_foreign_key(
                'fk_chat_messages_conversation_id',
                'chat_messages', 'chat_conversations',
                ['conversation_id'], ['id'],
                ondelete='CASCADE'
            )
        
        # Add new columns if they don't exist
        if 'embedding' not in existing_columns:
            op.add_column('chat_messages', sa.Column('embedding', Vector(384), nullable=True))
        
        if 'tokens_used' not in existing_columns:
            op.add_column('chat_messages', sa.Column('tokens_used', sa.Integer(), nullable=True))
        
        if 'model_used' not in existing_columns:
            op.add_column('chat_messages', sa.Column('model_used', sa.String(length=100), nullable=True))
        
        if 'context_documents' not in existing_columns:
            op.add_column('chat_messages', sa.Column('context_documents', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
        
        if 'context_tasks' not in existing_columns:
            op.add_column('chat_messages', sa.Column('context_tasks', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
        
        if 'context_finance' not in existing_columns:
            op.add_column('chat_messages', sa.Column('context_finance', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
        
        if 'context_marketing' not in existing_columns:
            op.add_column('chat_messages', sa.Column('context_marketing', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
        
        if 'user_rating' not in existing_columns:
            op.add_column('chat_messages', sa.Column('user_rating', sa.Integer(), nullable=True))
        
        if 'user_feedback' not in existing_columns:
            op.add_column('chat_messages', sa.Column('user_feedback', sa.Text(), nullable=True))
        
        # Drop user_id column if exists (moved to conversation)
        if 'user_id' in existing_columns:
            op.drop_column('chat_messages', 'user_id')
        
        # Drop context_type column if exists (replaced with specific context columns)
        if 'context_type' in existing_columns:
            op.drop_column('chat_messages', 'context_type')
        
        # Create indexes if not exist
        existing_indexes = {idx['name'] for idx in inspector.get_indexes('chat_messages')}
        
        if 'ix_chat_messages_conversation_id' not in existing_indexes:
            op.create_index('ix_chat_messages_conversation_id', 'chat_messages', ['conversation_id'])
        
        if 'ix_chat_messages_role' not in existing_indexes:
            op.create_index('ix_chat_messages_role', 'chat_messages', ['role'])
        
        if 'ix_chat_messages_created_at' not in existing_indexes:
            op.create_index('ix_chat_messages_created_at', 'chat_messages', ['created_at'])
        
        # Create vector index if embedding column exists
        if 'embedding' in {col['name'] for col in inspector.get_columns('chat_messages')}:
            try:
                op.execute('CREATE INDEX IF NOT EXISTS ix_chat_messages_embedding ON chat_messages USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)')
            except Exception:
                pass  # Index might already exist or pgvector not fully configured


def downgrade() -> None:
    # Simplified downgrade - just remove added columns and indexes
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if 'chat_messages' in inspector.get_table_names():
        try:
            op.execute('DROP INDEX IF EXISTS ix_chat_messages_embedding')
        except Exception:
            pass
        
        op.drop_index('ix_chat_messages_created_at', table_name='chat_messages', if_exists=True)
        op.drop_index('ix_chat_messages_role', table_name='chat_messages', if_exists=True)
        op.drop_index('ix_chat_messages_conversation_id', table_name='chat_messages', if_exists=True)
    
    if 'chat_conversations' in inspector.get_table_names():
        op.drop_index('ix_chat_conversations_updated_at', table_name='chat_conversations', if_exists=True)
        op.drop_index('ix_chat_conversations_user_id', table_name='chat_conversations', if_exists=True)
        op.drop_index('ix_chat_conversations_id', table_name='chat_conversations', if_exists=True)

