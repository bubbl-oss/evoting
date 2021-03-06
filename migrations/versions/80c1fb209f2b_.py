"""empty message

Revision ID: 80c1fb209f2b
Revises: 5e9359fb64b9
Create Date: 2021-03-03 22:54:55.282944

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '80c1fb209f2b'
down_revision = '5e9359fb64b9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('election', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('election', sa.Column('modified_at', sa.DateTime(), nullable=True))
    op.add_column('election', sa.Column('owner', sa.Integer(), nullable=False))
    op.drop_constraint(None, 'election', type_='foreignkey')
    op.create_foreign_key(None, 'election', 'user', ['owner'], ['id'])
    op.drop_column('election', 'user_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('election', sa.Column('user_id', sa.INTEGER(), nullable=False))
    op.drop_constraint(None, 'election', type_='foreignkey')
    op.create_foreign_key(None, 'election', 'user', ['user_id'], ['id'])
    op.drop_column('election', 'owner')
    op.drop_column('election', 'modified_at')
    op.drop_column('election', 'created_at')
    # ### end Alembic commands ###
