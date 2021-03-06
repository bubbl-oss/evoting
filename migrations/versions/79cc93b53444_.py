"""empty message

Revision ID: 79cc93b53444
Revises: 92088b5d3128
Create Date: 2021-03-08 01:55:12.314502

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '79cc93b53444'
down_revision = '92088b5d3128'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('type_id', sa.Integer(), nullable=False),
    sa.Column('verified', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['type_id'], ['type.id'], name=op.f('fk_user_type_id_type')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_user')),
    sa.UniqueConstraint('email', name=op.f('uq_user_email'))
    )
    op.create_table('election',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('starting_at', sa.DateTime(), nullable=True),
    sa.Column('ending_at', sa.DateTime(), nullable=True),
    sa.Column('link', sa.String(), nullable=True),
    sa.Column('status_id', sa.Integer(), nullable=False),
    sa.Column('number_of_voters', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['status_id'], ['status.id'], name=op.f('fk_election_status_id_status')),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_election_user_id_user')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_election'))
    )
    with op.batch_alter_table('election', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_election_name'), ['name'], unique=False)
        batch_op.create_index(batch_op.f('ix_election_starting_at'), ['starting_at'], unique=False)

    op.create_table('candidate',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('image', sa.String(), nullable=True),
    sa.Column('bio', sa.Text(), nullable=True),
    sa.Column('position', sa.String(length=200), nullable=True),
    sa.Column('election_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['election_id'], ['election.id'], name=op.f('fk_candidate_election_id_election')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_candidate'))
    )
    with op.batch_alter_table('candidate', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_candidate_name'), ['name'], unique=False)

    op.create_table('vote',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('election_id', sa.Integer(), nullable=False),
    sa.Column('candidate_id', sa.Integer(), nullable=False),
    sa.Column('password', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['candidate_id'], ['candidate.id'], name=op.f('fk_vote_candidate_id_candidate')),
    sa.ForeignKeyConstraint(['election_id'], ['election.id'], name=op.f('fk_vote_election_id_election')),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_vote_user_id_user')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_vote'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('vote')
    with op.batch_alter_table('candidate', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_candidate_name'))

    op.drop_table('candidate')
    with op.batch_alter_table('election', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_election_starting_at'))
        batch_op.drop_index(batch_op.f('ix_election_name'))

    op.drop_table('election')
    op.drop_table('user')
    # ### end Alembic commands ###
