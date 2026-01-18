"""Add transcripts table with local and S3 storage support

Revision ID: 0002
Revises: 0001
Create Date: 2026-01-17 21:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create transcripts table
    op.create_table(
        'transcripts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('original_filename', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('file_type', sa.String(), nullable=False),
        sa.Column('local_path', sa.String(), nullable=True),
        sa.Column('s3_key', sa.String(), nullable=True),
        sa.Column('storage_type', sa.String(), nullable=False, server_default='local'),
        sa.Column('is_indexed', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('indexed_at', sa.DateTime(), nullable=True),
        sa.Column('chunk_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('tags', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_transcripts_filename', 'transcripts', ['filename'], unique=True)
    op.create_index('ix_transcripts_user_id', 'transcripts', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_transcripts_user_id', table_name='transcripts')
    op.drop_index('ix_transcripts_filename', table_name='transcripts')
    op.drop_table('transcripts')
