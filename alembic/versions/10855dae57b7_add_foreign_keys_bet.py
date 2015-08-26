"""add foreign keys between User and Department

Revision ID: 10855dae57b7
Revises: 134e5fea7601
Create Date: 2015-05-19 10:59:16.315012

"""

# revision identifiers, used by Alembic.
revision = '10855dae57b7'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('user', 'department', new_column_name='department_id')
    op.add_column('department', sa.Column('primary_contact_id', sa.INTEGER, sa.ForeignKey("user.id")))
    op.add_column('department', sa.Column('backup_contact_id', sa.INTEGER, sa.ForeignKey("user.id")))


def downgrade():
    op.drop_column('department', 'primary_contact_id')
    op.drop_column('department', 'backup_contact_id')
    op.alter_column('user', 'department_id', new_column_name='department')
