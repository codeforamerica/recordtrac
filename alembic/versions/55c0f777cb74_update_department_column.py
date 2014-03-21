"""Update department column on User

Revision ID: 55c0f777cb74
Revises: b681ff646b
Create Date: 2014-03-13 13:30:09.378653

"""

# revision identifiers, used by Alembic.
revision = '55c0f777cb74'
down_revision = '8ce10875836'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    op.alter_column(
        'user',
        sa.Column(
            'department',
            sa.Integer(),
            nullable=True
        )
    )
   
def downgrade():
        op.alter_column(
        'user',
        sa.Column(
            'department',
            sa.String(),
            nullable=True
        )
    )
