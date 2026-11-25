"""Migrate campaign voice defaults to Twilio-supported voice IDs."""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "003_twilio_voice"
down_revision: str | None = "002_campaign_customer_timestamps"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("""
        UPDATE campaigns
        SET voice_id = CASE
            WHEN language = 'hi-IN' THEN 'Google.hi-IN-Wavenet-D'
            WHEN language = 'en-US' THEN 'Polly.Joanna'
            WHEN language = 'en-GB' THEN 'Polly.Amy'
            ELSE 'Google.en-IN-Wavenet-D'
        END
        WHERE voice_id IN (
            'alloy', 'en_IN-karun-medium', 'hi_IN-aryan-medium',
            'en_US-lessac-medium', 'en_GB-alan-medium'
        )
    """)
    op.alter_column("campaigns", "voice_id", type_=sa.String(length=80), server_default="Google.en-IN-Wavenet-D")


def downgrade() -> None:
    op.alter_column("campaigns", "voice_id", type_=sa.String(length=50), server_default="alloy")
