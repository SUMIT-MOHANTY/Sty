"""create appointments table

Revision ID: 2023_create_appointments_table
Revises: 2023_create_time_slots_table
Create Date: 2023-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2023_create_appointments_table'
down_revision = '2023_create_time_slots_table'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'appointments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('application_id', sa.Integer(), nullable=False),
        sa.Column('time_slot_id', sa.Integer(), nullable=False),
        sa.Column('location_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, default='scheduled'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ),
        sa.ForeignKeyConstraint(['time_slot_id'], ['time_slots.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_appointments_application_id'), 'appointments', ['application_id'], unique=True)
    op.create_index(op.f('ix_appointments_time_slot_id'), 'appointments', ['time_slot_id'], unique=False)
    op.create_index(op.f('ix_appointments_user_id'), 'appointments', ['user_id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_appointments_user_id'), table_name='appointments')
    op.drop_index(op.f('ix_appointments_time_slot_id'), table_name='appointments')
    op.drop_index(op.f('ix_appointments_application_id'), table_name='appointments')
    op.drop_table('appointments')
