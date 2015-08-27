"""add user role

Revision ID: 300ee4d151d
Revises: 17d099162949
Create Date: 2015-08-26 21:56:36.400263

"""

# revision identifiers, used by Alembic.
revision = '300ee4d151d'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('user', sa.Column('role', sa.String()))

def downgrade():
    op.drop_column('user', 'role')

