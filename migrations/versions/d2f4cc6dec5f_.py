"""empty message

Revision ID: d2f4cc6dec5f
Revises: 64ae0d34b81c
Create Date: 2021-03-04 01:43:18.579659

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2f4cc6dec5f'
down_revision = '64ae0d34b81c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'election', type_='foreignkey')
    op.create_foreign_key(None, 'election', 'user', ['owner'], ['id'])
    op.drop_column('election', 'user_id')
    op.drop_column('election', 'time')
    op.drop_column('election', 'date')
    op.drop_column('election', 'published')
    op.add_column('vote', sa.Column('password', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('vote', 'password')
    op.add_column('election', sa.Column('published', sa.BOOLEAN(), nullable=True))
    op.add_column('election', sa.Column('date', sa.DATETIME(), nullable=True))
    op.add_column('election', sa.Column('time', sa.DATETIME(), nullable=True))
    op.add_column('election', sa.Column('user_id', sa.INTEGER(), nullable=False))
    op.drop_constraint(None, 'election', type_='foreignkey')
    op.create_foreign_key(None, 'election', 'user', ['user_id'], ['id'])
    # ### end Alembic commands ###
