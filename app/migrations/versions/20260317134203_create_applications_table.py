"""create applications table

Revision ID: ${timestamp_app}
Revises:
Create Date: $(date -u +"%Y-%m-%d %H:%M:%S")

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum

# revision identifiers, used by Alembic.
revision = '${timestamp_app}'
down_revision = None
branch_labels = None
depends_on = None

class ApplicationStatus(enum.Enum):
    draft = "draft"
    submitted = "submitted"
    under_review = "under_review"
    approved = "approved"
    rejected = "rejected"

def upgrade():
    op.create_table(
        'applications',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('status', sa.Enum(ApplicationStatus), nullable=False, default=ApplicationStatus.draft),
        sa.Column('personal_details', JSONB, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()'))
    )

    # Create indexes
    op.create_index('ix_applications_user_id', 'applications', ['user_id'])
    op.create_index('ix_applications_status', 'applications', ['status'])

def downgrade():
    op.drop_index('ix_applications_status')
    op.drop_index('ix_applications_user_id')
    op.drop_table('applications')
