"""create documents table

Revision ID: ${timestamp_doc}
Revises: ${timestamp_app}
Create Date: $(date -u +"%Y-%m-%d %H:%M:%S")

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

# revision identifiers, used by Alembic.
revision = '${timestamp_doc}'
down_revision = '${timestamp_app}'
branch_labels = None
depends_on = None

class DocumentType(enum.Enum):
    passport_photo = "passport_photo"
    id_proof = "id_proof"
    address_proof = "address_proof"
    birth_certificate = "birth_certificate"
    other = "other"

def upgrade():
    op.create_table(
        'documents',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('application_id', UUID(as_uuid=True), sa.ForeignKey('applications.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.Enum(DocumentType), nullable=False),
        sa.Column('file_path', sa.String(255), nullable=False),
        sa.Column('uploaded_at', sa.DateTime, nullable=False, server_default=sa.text('now()'))
    )

    # Create indexes
    op.create_index('ix_documents_application_id', 'documents', ['application_id'])
    op.create_index('ix_documents_type', 'documents', ['type'])

def downgrade():
    op.drop_index('ix_documents_type')
    op.drop_index('ix_documents_application_id')
    op.drop_table('documents')
