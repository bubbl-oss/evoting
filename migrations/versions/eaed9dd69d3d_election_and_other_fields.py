"""election and other fields

Revision ID: eaed9dd69d3d
Revises: aed13d63b342
Create Date: 2021-03-07 00:19:38.866172

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eaed9dd69d3d'
down_revision = 'aed13d63b342'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('election', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ending_at', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('election', schema=None) as batch_op:
        batch_op.drop_column('ending_at')

    # ### end Alembic commands ###