"""create time slots table

Revision ID: 2023_create_time_slots_table
Revises: 2023_create_locations_table
Create Date: 2023-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2023_create_time_slots_table'
down_revision = '2023_create_locations_table'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'time_slots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('location_id', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('max_appointments', sa.Integer(), nullable=False),
        sa.Column('current_appointments', sa.Integer(), nullable=False, default=0),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_time_slots_location_id'), 'time_slots', ['location_id'], unique=False)
    op.create_index(op.f('ix_time_slots_start_time'), 'time_slots', ['start_time'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_time_slots_start_time'), table_name='time_slots')
    op.drop_index(op.f('ix_time_slots_location_id'), table_name='time_slots')
    op.drop_table('time_slots')
