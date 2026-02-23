"""Create analysis_jobs and webhook_configs tables

Revision ID: 001
Revises:
Create Date: 2026-02-22

Task: T-1.1.003
Agent: build-1
Requirements: TECH-004, TECH-005
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create analysis_jobs and webhook_configs tables.

    Implements:
    - TECH-004: Database schema for analysis_jobs table
    - TECH-005: Database schema for webhook_configs table
    """
    # Create analysis_jobs table (TECH-004)
    op.create_table(
        'analysis_jobs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('job_type', sa.Enum(
            'alert_analysis',
            'ioc_investigation',
            'event_correlation',
            'report_generation',
            'action_recommendation',
            name='analysisjobtype'
        ), nullable=False),
        sa.Column('status', sa.Enum(
            'pending',
            'processing',
            'completed',
            'failed',
            'cancelled',
            name='analysisjobstatus'
        ), nullable=False, index=True, server_default='pending'),
        sa.Column('payload', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('result', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_retries', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('timeout_seconds', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('session_id', sa.String(100), nullable=True, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )

    # Create composite index for job queue queries
    op.create_index(
        'ix_analysis_jobs_status_priority',
        'analysis_jobs',
        ['status', 'priority']
    )

    # Create webhook_configs table (TECH-005)
    op.create_table(
        'webhook_configs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('url', sa.String(2048), nullable=False),
        sa.Column('event_types', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('secret', sa.String(256), nullable=True),
        sa.Column('timeout_seconds', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('max_retries', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('retry_delay_seconds', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', index=True),
        sa.Column('headers', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('last_triggered_at', sa.DateTime(), nullable=True),
        sa.Column('last_success_at', sa.DateTime(), nullable=True),
        sa.Column('last_failure_at', sa.DateTime(), nullable=True),
        sa.Column('failure_count', sa.Integer(), nullable=False, server_default='0'),
    )


def downgrade() -> None:
    """Drop analysis_jobs and webhook_configs tables."""
    # Drop webhook_configs table
    op.drop_table('webhook_configs')

    # Drop analysis_jobs table
    op.drop_index('ix_analysis_jobs_status_priority', table_name='analysis_jobs')
    op.drop_table('analysis_jobs')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS analysisjobstatus')
    op.execute('DROP TYPE IF EXISTS analysisjobtype')
