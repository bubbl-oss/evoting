"""empty message

Revision ID: 8cd04b190de8
Revises: 531ca9346f5f
Create Date: 2021-03-07 21:04:50.144125

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8cd04b190de8'
down_revision = '531ca9346f5f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('_alembic_tmp_candidate')
    with op.batch_alter_table('candidate', schema=None) as batch_op:
        batch_op.alter_column('image',
               existing_type=sa.VARCHAR(),
               nullable=True)
        batch_op.alter_column('position',
               existing_type=sa.VARCHAR(length=200),
               nullable=True)
        batch_op.create_index(batch_op.f('ix_candidate_name'), ['name'], unique=False)

    with op.batch_alter_table('election', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('ending_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('name', sa.String(), nullable=False))
        batch_op.add_column(sa.Column('password', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('starting_at', sa.DateTime(), nullable=True))
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.create_index(batch_op.f('ix_election_name'), ['name'], unique=False)
        batch_op.create_index(batch_op.f('ix_election_starting_at'), ['starting_at'], unique=False)
        batch_op.drop_column('time')
        batch_op.drop_column('name_of_election')
        batch_op.drop_column('date')
        batch_op.drop_column('published')

    with op.batch_alter_table('status', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(), nullable=False))
        batch_op.drop_column('status')

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('type_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('verified', sa.Boolean(), nullable=True))
        batch_op.create_unique_constraint(batch_op.f('uq_user_email'), ['email'])
        batch_op.create_foreign_key(batch_op.f('fk_user_type_id_type'), 'type', ['type_id'], ['id'])

    with op.batch_alter_table('vote', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vote', schema=None) as batch_op:
        batch_op.drop_column('password')

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_user_type_id_type'), type_='foreignkey')
        batch_op.drop_constraint(batch_op.f('uq_user_email'), type_='unique')
        batch_op.drop_column('verified')
        batch_op.drop_column('type_id')

    with op.batch_alter_table('status', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.VARCHAR(), nullable=False))
        batch_op.drop_column('name')

    with op.batch_alter_table('election', schema=None) as batch_op:
        batch_op.add_column(sa.Column('published', sa.BOOLEAN(), nullable=True))
        batch_op.add_column(sa.Column('date', sa.DATETIME(), nullable=True))
        batch_op.add_column(sa.Column('name_of_election', sa.VARCHAR(), nullable=False))
        batch_op.add_column(sa.Column('time', sa.DATETIME(), nullable=True))
        batch_op.drop_index(batch_op.f('ix_election_starting_at'))
        batch_op.drop_index(batch_op.f('ix_election_name'))
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.drop_column('starting_at')
        batch_op.drop_column('password')
        batch_op.drop_column('name')
        batch_op.drop_column('ending_at')
        batch_op.drop_column('description')

    with op.batch_alter_table('candidate', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_candidate_name'))
        batch_op.alter_column('position',
               existing_type=sa.VARCHAR(length=200),
               nullable=False)
        batch_op.alter_column('image',
               existing_type=sa.VARCHAR(),
               nullable=False)

    op.create_table('_alembic_tmp_candidate',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.Column('image', sa.VARCHAR(), nullable=True),
    sa.Column('bio', sa.TEXT(), nullable=True),
    sa.Column('position', sa.VARCHAR(length=200), nullable=True),
    sa.Column('election_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['election_id'], ['election.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
