"""Create request search column and trigger.

Revision ID: 5563ca9e7626
Revises: 30d3af507801
Create Date: 2014-03-06 13:13:52.831868

"""

# revision identifiers, used by Alembic.
revision = '5563ca9e7626'
down_revision = '20087beff9ea'

from alembic import op
import sqlalchemy as sa

def upgrade():
    # TODO(cj@postcode.io): This should probably be rewritten using Alembic and SQLAlchemy classes,
    # but I couldn't find the docs on using `to_tsvector` in this context. Le sigh.
    op.execute("CREATE INDEX request_search_index ON request USING gin(to_tsvector('english', text))")

def downgrade():
    op.drop_index("request_search_index", "request")
