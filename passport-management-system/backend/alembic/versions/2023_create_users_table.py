"""Create users table

Revision ID: 2023_create_users_table
Revises:
Create Date: 2023-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2023_create_users_table'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create enum type for user roles
    op.execute("CREATE TYPE user_roles AS ENUM ('regular', 'admin')")

    # Create users table with security considerations
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('role', sa.Enum('regular', 'admin', name='user_roles'), nullable=False, server_default='regular'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Create index for email lookups during authentication
    op.create_index('idx_users_email', 'users', ['email'])

    # Create index for role-based queries
    op.create_index('idx_users_role', 'users', ['role'])

def downgrade() -> None:
    op.drop_index('idx_users_role')
    op.drop_index('idx_users_email')
    op.drop_table('users')
    op.execute("DROP TYPE user_roles")
