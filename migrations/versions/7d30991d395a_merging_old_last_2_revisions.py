"""merging old last 2 revisions

Revision ID: 7d30991d395a
Revises: cd8eb8860d8a, 9485c5134ac0
Create Date: 2021-03-10 11:06:04.020907

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d30991d395a'
down_revision = ('cd8eb8860d8a', '9485c5134ac0')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
