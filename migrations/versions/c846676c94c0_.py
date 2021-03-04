"""empty message

Revision ID: c846676c94c0
Revises: 80c1fb209f2b
Create Date: 2021-03-03 23:05:41.907862

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c846676c94c0'
down_revision = '80c1fb209f2b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('election', sa.Column('date_of_election', sa.DateTime(), nullable=True))
    op.add_column('election', sa.Column('owner', sa.Integer(), nullable=True))
    op.add_column('election', sa.Column('time_of_election', sa.DateTime(), nullable=True))
    op.drop_constraint(None, 'election', type_='foreignkey')
    op.create_foreign_key(None, 'election', 'user', ['owner'], ['id'])
    op.drop_column('election', 'date')
    op.drop_column('election', 'time')
    op.drop_column('election', 'user_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('election', sa.Column('user_id', sa.INTEGER(), nullable=False))
    op.add_column('election', sa.Column('time', sa.DATETIME(), nullable=True))
    op.add_column('election', sa.Column('date', sa.DATETIME(), nullable=True))
    op.drop_constraint(None, 'election', type_='foreignkey')
    op.create_foreign_key(None, 'election', 'user', ['user_id'], ['id'])
    op.drop_column('election', 'time_of_election')
    op.drop_column('election', 'owner')
    op.drop_column('election', 'date_of_election')
    # ### end Alembic commands ###
