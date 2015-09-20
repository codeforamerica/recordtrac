"""add user title

Revision ID: 17d099162949
Revises: 2de765e466ca
Create Date: 2015-08-26 19:48:30.818690

"""

# revision identifiers, used by Alembic.
revision = '17d099162949'
down_revision = '2de765e466ca'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('user', sa.Column('title', sa.String()))

def downgrade():
    op.drop_column('user', 'title')
