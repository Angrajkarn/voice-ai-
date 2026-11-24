"""Initial migration

Revision ID: 001_initial
Revises:
Create Date: 2026-11-23

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(50), nullable=False, unique=True),
        sa.Column('logo_url', sa.String(500), nullable=True),
        sa.Column('plan', sa.Enum('FREE', 'STARTER', 'PROFESSIONAL', 'ENTERPRISE', name='organizationplan'), default='FREE', nullable=False),
        sa.Column('plan_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('settings', postgresql.JSONB, default={}, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_organizations_slug', 'organizations', ['slug'])

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=True),
        sa.Column('password_hash', sa.String(255), nullable=True),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('role', sa.Enum('SUPER_ADMIN', 'ADMIN', 'MANAGER', 'AGENT', 'VIEWER', name='userrole'), default='VIEWER', nullable=False),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_organization_id', 'users', ['organization_id'])

    # Create customers table
    op.create_table(
        'customers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('external_id', sa.String(100), nullable=True),
        sa.Column('first_name', sa.String(50), nullable=False),
        sa.Column('last_name', sa.String(50), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(20), nullable=False),
        sa.Column('phone_raw', sa.String(50), nullable=True),
        sa.Column('company', sa.String(100), nullable=True),
        sa.Column('location', sa.String(100), nullable=True),
        sa.Column('language', sa.String(10), default='en-IN', nullable=False),
        sa.Column('timezone', sa.String(50), default='Asia/Kolkata', nullable=False),
        sa.Column('tags', postgresql.ARRAY(sa.String), default=[], nullable=False),
        sa.Column('custom_fields', postgresql.JSONB, default={}, nullable=False),
        sa.Column('status', sa.Enum('NEW', 'CONTACTED', 'HOT_LEAD', 'WARM_LEAD', 'COLD_LEAD', 'NOT_INTERESTED', 'CALLBACK_REQUESTED', 'DO_NOT_CALL', 'INVALID_NUMBER', 'OPTED_OUT', name='customerstatus'), default='NEW', nullable=False),
        sa.Column('interest_level', sa.Enum('HOT', 'WARM', 'COLD', 'UNKNOWN', name='interestlevel'), default='UNKNOWN', nullable=False),
        sa.Column('call_attempts', sa.Integer, default=0, nullable=False),
        sa.Column('max_call_attempts', sa.Integer, default=3, nullable=False),
        sa.Column('last_call_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_callback_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_call_status', sa.String(50), nullable=True),
        sa.Column('last_call_duration', sa.Integer, nullable=True),
        sa.Column('final_disposition', sa.String(200), nullable=True),
        sa.Column('do_not_call', sa.Boolean, default=False, nullable=False),
        sa.Column('opted_out_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('opt_out_reason', sa.String(500), nullable=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_customers_organization_id', 'customers', ['organization_id'])
    op.create_index('ix_customers_phone', 'customers', ['phone'])
    op.create_index('ix_customers_status', 'customers', ['status'])
    op.create_index('ix_customers_interest_level', 'customers', ['interest_level'])
    op.create_index('ix_customers_next_callback_at', 'customers', ['next_callback_at'])
    op.create_unique_constraint('ix_customers_org_phone', 'customers', ['organization_id', 'phone'])

    # Create campaigns table
    op.create_table(
        'campaigns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('purpose', sa.Text, nullable=False),
        sa.Column('ai_instructions', sa.Text, nullable=False),
        sa.Column('opening_script', sa.Text, nullable=False),
        sa.Column('knowledge_base', sa.Text, nullable=True),
        sa.Column('voice_id', sa.String(50), default='alloy', nullable=False),
        sa.Column('language', sa.String(10), default='en-IN', nullable=False),
        sa.Column('supported_languages', postgresql.ARRAY(sa.String), default=['en-IN', 'hi-IN', 'hinglish'], nullable=False),
        sa.Column('max_calls_per_day', sa.Integer, default=100, nullable=False),
        sa.Column('max_retry_attempts', sa.Integer, default=3, nullable=False),
        sa.Column('delay_between_calls', sa.Integer, default=30, nullable=False),
        sa.Column('calling_window_start', sa.String(5), default='09:00', nullable=False),
        sa.Column('calling_window_end', sa.String(5), default='18:00', nullable=False),
        sa.Column('calling_timezone', sa.String(50), default='Asia/Kolkata', nullable=False),
        sa.Column('skip_weekends', sa.Boolean, default=True, nullable=False),
        sa.Column('skip_holidays', sa.Boolean, default=False, nullable=False),
        sa.Column('allow_callbacks', sa.Boolean, default=True, nullable=False),
        sa.Column('callback_window_start', sa.String(5), default='09:00', nullable=False),
        sa.Column('callback_window_end', sa.String(5), default='18:00', nullable=False),
        sa.Column('max_callback_days', sa.Integer, default=7, nullable=False),
        sa.Column('sheets_sync_enabled', sa.Boolean, default=False, nullable=False),
        sa.Column('sheets_spreadsheet_id', sa.String(100), nullable=True),
        sa.Column('sheets_sheet_name', sa.String(100), default='Calls', nullable=False),
        sa.Column('sheets_auto_sync', sa.Boolean, default=True, nullable=False),
        sa.Column('status', sa.Enum('DRAFT', 'READY', 'RUNNING', 'PAUSED', 'COMPLETED', 'STOPPED', name='campaignstatus'), default='DRAFT', nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('paused_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('stopped_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_customers', sa.Integer, default=0, nullable=False),
        sa.Column('completed_calls', sa.Integer, default=0, nullable=False),
        sa.Column('failed_calls', sa.Integer, default=0, nullable=False),
        sa.Column('interested_count', sa.Integer, default=0, nullable=False),
        sa.Column('callback_count', sa.Integer, default=0, nullable=False),
        sa.Column('opt_out_count', sa.Integer, default=0, nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_campaigns_organization_id', 'campaigns', ['organization_id'])
    op.create_index('ix_campaigns_status', 'campaigns', ['status'])
    op.create_index('ix_campaigns_owner_id', 'campaigns', ['owner_id'])

    # Create campaign_customers table
    op.create_table(
        'campaign_customers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('priority', sa.Integer, default=0, nullable=False),
        sa.Column('status', sa.Enum('NEW', 'CONTACTED', 'HOT_LEAD', 'WARM_LEAD', 'COLD_LEAD', 'NOT_INTERESTED', 'CALLBACK_REQUESTED', 'DO_NOT_CALL', 'INVALID_NUMBER', 'OPTED_OUT', name='customerstatus'), default='NEW', nullable=False),
        sa.Column('assigned_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('called_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('campaigns.id', ondelete='CASCADE'), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False),
    )
    op.create_index('ix_campaign_customers_campaign_id', 'campaign_customers', ['campaign_id'])
    op.create_index('ix_campaign_customers_customer_id', 'campaign_customers', ['customer_id'])
    op.create_index('ix_campaign_customers_status', 'campaign_customers', ['status'])
    op.create_unique_constraint('uq_campaign_customer', 'campaign_customers', ['campaign_id', 'customer_id'])

    # Create calls table
    op.create_table(
        'calls',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('call_sid', sa.String(50), unique=True, nullable=True),
        sa.Column('direction', sa.Enum('OUTBOUND', 'INBOUND', name='calldirection'), default='OUTBOUND', nullable=False),
        sa.Column('status', sa.Enum('QUEUED', 'INITIATING', 'RINGING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'BUSY', 'NO_ANSWER', 'VOICEMAIL', 'INVALID_NUMBER', 'BLOCKED', 'CANCELLED', name='callstatus'), default='QUEUED', nullable=False),
        sa.Column('from_number', sa.String(20), nullable=False),
        sa.Column('to_number', sa.String(20), nullable=False),
        sa.Column('queued_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('initiated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('answered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration', sa.Integer, nullable=True),
        sa.Column('billable_duration', sa.Integer, nullable=True),
        sa.Column('disposition', sa.String(50), nullable=True),
        sa.Column('failure_reason', sa.Text, nullable=True),
        sa.Column('hangup_source', sa.String(50), nullable=True),
        sa.Column('interest_level', sa.Enum('HOT', 'WARM', 'COLD', 'UNKNOWN', name='interestlevel'), default='UNKNOWN', nullable=False),
        sa.Column('customer_intent', sa.Text, nullable=True),
        sa.Column('objections', postgresql.ARRAY(sa.Text), default=[], nullable=False),
        sa.Column('questions_asked', postgresql.ARRAY(sa.Text), default=[], nullable=False),
        sa.Column('summary', sa.Text, nullable=True),
        sa.Column('sentiment', sa.String(20), nullable=True),
        sa.Column('requires_human_followup', sa.Boolean, default=False, nullable=False),
        sa.Column('human_followup_reason', sa.Text, nullable=True),
        sa.Column('recording_url', sa.String(500), nullable=True),
        sa.Column('recording_sid', sa.String(50), nullable=True),
        sa.Column('transcript_url', sa.String(500), nullable=True),
        sa.Column('transcript_text', sa.Text, nullable=True),
        sa.Column('transcript_segments', postgresql.JSONB, default=[], nullable=False),
        sa.Column('sheets_synced', sa.Boolean, default=False, nullable=False),
        sa.Column('sheets_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sheets_sync_status', sa.Enum('PENDING', 'SYNCED', 'FAILED', 'RETRYING', name='syncstatus'), default='PENDING', nullable=False),
        sa.Column('sheets_sync_error', sa.Text, nullable=True),
        sa.Column('sheets_row_index', sa.Integer, nullable=True),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('campaigns.id', ondelete='CASCADE'), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_calls_campaign_id', 'calls', ['campaign_id'])
    op.create_index('ix_calls_customer_id', 'calls', ['customer_id'])
    op.create_index('ix_calls_status', 'calls', ['status'])
    op.create_index('ix_calls_call_sid', 'calls', ['call_sid'])
    op.create_index('ix_calls_to_number', 'calls', ['to_number'])
    op.create_index('ix_calls_sheets_sync_status', 'calls', ['sheets_sync_status'])

    # Create call_transcripts table
    op.create_table(
        'call_transcripts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('call_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('calls.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('full_text', sa.Text, nullable=False),
        sa.Column('segments', postgresql.JSONB, nullable=False),
        sa.Column('language', sa.String(10), default='en-IN', nullable=False),
        sa.Column('word_count', sa.Integer, default=0, nullable=False),
        sa.Column('duration', sa.Float, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Create call_recordings table
    op.create_table(
        'call_recordings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('call_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('calls.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('provider', sa.String(50), default='twilio', nullable=False),
        sa.Column('provider_id', sa.String(100), nullable=False),
        sa.Column('format', sa.String(20), default='mp3', nullable=False),
        sa.Column('duration', sa.Float, nullable=False),
        sa.Column('size_bytes', sa.BigInteger, nullable=False),
        sa.Column('channels', sa.Integer, default=1, nullable=False),
        sa.Column('sample_rate', sa.Integer, default=8000, nullable=False),
        sa.Column('drive_file_id', sa.String(100), nullable=True),
        sa.Column('drive_synced_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('drive_sync_status', sa.Enum('PENDING', 'SYNCED', 'FAILED', 'RETRYING', name='syncstatus'), default='PENDING', nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Create callbacks table
    op.create_table(
        'callbacks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('status', sa.Enum('SCHEDULED', 'COMPLETED', 'CANCELLED', 'FAILED', 'NO_ANSWER', name='callbackstatus'), default='SCHEDULED', nullable=False),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('scheduled_timezone', sa.String(50), default='Asia/Kolkata', nullable=False),
        sa.Column('reminder_sent', sa.Boolean, default=False, nullable=False),
        sa.Column('reminder_sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('source_call_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('calls.id', ondelete='SET NULL'), nullable=True),
        sa.Column('customer_notes', sa.Text, nullable=True),
        sa.Column('ai_notes', sa.Text, nullable=True),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('campaigns.id', ondelete='CASCADE'), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('assignee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('result_call_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('calls.id'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('outcome', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_callbacks_campaign_id', 'callbacks', ['campaign_id'])
    op.create_index('ix_callbacks_customer_id', 'callbacks', ['customer_id'])
    op.create_index('ix_callbacks_assignee_id', 'callbacks', ['assignee_id'])
    op.create_index('ix_callbacks_status', 'callbacks', ['status'])
    op.create_index('ix_callbacks_scheduled_at', 'callbacks', ['scheduled_at'])

    # Create integrations table
    op.create_table(
        'integrations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('type', sa.Enum('GOOGLE_SHEETS', 'GOOGLE_DRIVE', 'TWILIO', 'OPENAI', 'N8N', name='integrationtype'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('config', postgresql.JSONB, default={}, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_sync_status', sa.Enum('PENDING', 'SYNCED', 'FAILED', 'RETRYING', name='syncstatus'), default='PENDING', nullable=False),
        sa.Column('last_sync_error', sa.Text, nullable=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('campaigns.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_integrations_organization_id', 'integrations', ['organization_id'])
    op.create_index('ix_integrations_type', 'integrations', ['type'])
    op.create_unique_constraint('uq_integration_org_type_name', 'integrations', ['organization_id', 'type', 'name'])

    # Create sync_logs table
    op.create_table(
        'sync_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('integration_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('integrations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('operation', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(100), nullable=False),
        sa.Column('entity_id', sa.String(100), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'SYNCED', 'FAILED', 'RETRYING', name='syncstatus'), default='PENDING', nullable=False),
        sa.Column('error', sa.Text, nullable=True),
        sa.Column('request_data', postgresql.JSONB, nullable=True),
        sa.Column('response_data', postgresql.JSONB, nullable=True),
        sa.Column('retry_count', sa.Integer, default=0, nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_sync_logs_integration_id', 'sync_logs', ['integration_id'])
    op.create_index('ix_sync_logs_entity', 'sync_logs', ['entity_type', 'entity_id'])
    op.create_index('ix_sync_logs_status', 'sync_logs', ['status'])

    # Create automation_logs table
    op.create_table(
        'automation_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('campaigns.id', ondelete='CASCADE'), nullable=False),
        sa.Column('trigger_type', sa.String(100), nullable=False),
        sa.Column('trigger_data', postgresql.JSONB, nullable=False),
        sa.Column('action_type', sa.String(100), nullable=False),
        sa.Column('action_data', postgresql.JSONB, nullable=False),
        sa.Column('status', sa.String(20), default='PENDING', nullable=False),
        sa.Column('error', sa.Text, nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_automation_logs_campaign_id', 'automation_logs', ['campaign_id'])
    op.create_index('ix_automation_logs_trigger_status', 'automation_logs', ['trigger_type', 'status'])

    # Create suppression_list table
    op.create_table(
        'suppression_list',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('phone', sa.String(20), nullable=False),
        sa.Column('reason', sa.Enum('OPT_OUT', 'DND', 'INVALID', 'MANUAL', name='suppressionreason'), nullable=False),
        sa.Column('source', sa.Enum('CAMPAIGN', 'MANUAL', 'IMPORT', 'WEBHOOK', name='suppressionsource'), nullable=False),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('campaigns.id', ondelete='SET NULL'), nullable=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('customers.id', ondelete='SET NULL'), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('added_by', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_suppression_list_organization_id', 'suppression_list', ['organization_id'])
    op.create_index('ix_suppression_list_phone', 'suppression_list', ['phone'])
    op.create_index('ix_suppression_list_is_active', 'suppression_list', ['is_active'])
    op.create_unique_constraint('uq_suppression_org_phone', 'suppression_list', ['organization_id', 'phone'])

    # Create consent_records table
    op.create_table(
        'consent_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('phone', sa.String(20), nullable=False),
        sa.Column('status', sa.Enum('GRANTED', 'DENIED', 'PENDING', 'REVOKED', name='consentstatus'), default='PENDING', nullable=False),
        sa.Column('method', sa.Enum('VERBAL', 'SMS', 'EMAIL', 'WEB_FORM', 'CALL_RECORDING', name='consentmethod'), nullable=False),
        sa.Column('proof_url', sa.String(500), nullable=True),
        sa.Column('proof_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('campaigns.id', ondelete='SET NULL'), nullable=True),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('customers.id', ondelete='SET NULL'), nullable=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('granted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_consent_records_organization_id', 'consent_records', ['organization_id'])
    op.create_index('ix_consent_records_phone', 'consent_records', ['phone'])
    op.create_index('ix_consent_records_status', 'consent_records', ['status'])

    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('type', sa.Enum('CALL_COMPLETED', 'HOT_LEAD', 'CALLBACK_SCHEDULED', 'HUMAN_FOLLOWUP_REQUIRED', 'OPT_OUT', 'CAMPAIGN_COMPLETED', 'SYNC_FAILED', 'ERROR', name='notificationtype'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('data', postgresql.JSONB, default={}, nullable=False),
        sa.Column('is_read', sa.Boolean, default=False, nullable=False),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('campaigns.id', ondelete='SET NULL'), nullable=True),
        sa.Column('call_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('calls.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('ix_notifications_organization_id', 'notifications', ['organization_id'])
    op.create_index('ix_notifications_is_read', 'notifications', ['is_read'])

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(100), nullable=False),
        sa.Column('entity_id', sa.String(100), nullable=False),
        sa.Column('old_data', postgresql.JSONB, nullable=True),
        sa.Column('new_data', postgresql.JSONB, nullable=True),
        sa.Column('metadata', postgresql.JSONB, default={}, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_audit_logs_organization_id', 'audit_logs', ['organization_id'])
    op.create_index('ix_audit_logs_entity', 'audit_logs', ['entity_type', 'entity_id'])
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('audit_logs')
    op.drop_table('notifications')
    op.drop_table('consent_records')
    op.drop_table('suppression_list')
    op.drop_table('automation_logs')
    op.drop_table('sync_logs')
    op.drop_table('integrations')
    op.drop_table('callbacks')
    op.drop_table('call_recordings')
    op.drop_table('call_transcripts')
    op.drop_table('calls')
    op.drop_table('campaign_customers')
    op.drop_table('campaigns')
    op.drop_table('customers')
    op.drop_table('users')
    op.drop_table('organizations')