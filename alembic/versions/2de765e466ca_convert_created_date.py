"""convert created datetimes to utc

Revision ID: 2de765e466ca
Revises: 10855dae57b7
Create Date: 2015-05-19 23:01:13.266389

"""

# revision identifiers, used by Alembic.
revision = '2de765e466ca'
down_revision = '10855dae57b7'

from alembic import op
import sqlalchemy as sa
from datetime import datetime
from pytz import timezone, utc

pacific = timezone('US/Pacific')
Request = sa.Table(
    'request',
    sa.MetaData(),
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('date_created', sa.DateTime),
)

def upgrade():
    connection = op.get_bind()

    # Assume all existing requests were entered in Pacific time, and
    # convert them to UTC.
    for request in connection.execute(Request.select()):
        date_created = request.date_created.replace(tzinfo=pacific)
        date_created = date_created.astimezone(utc)
        connection.execute(
            Request.update().where(Request.c.id == request.id)
                            .values(date_created=date_created)
        )


def downgrade():
    connection = op.get_bind()

    # Assume all existing requests were entered in UTC, and convert
    # them to Pacific time.
    for request in connection.execute(Request.select()):
        date_created = request.date_created.replace(tzinfo=utc)
        date_created = date_created.astimezone(pacific)
        connection.execute(
            Request.update().where(Request.c.id == request.id)
                            .values(date_created=date_created)
        )
