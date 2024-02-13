"""Add user_registration

Revision ID: 9ca7d0df1223
Revises: 608c6c350842
Create Date: 2024-02-13 20:22:15.760868

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9ca7d0df1223'
down_revision: Union[str, None] = '608c6c350842'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_registration',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('code_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['code_id'], ['referral_code.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.add_column('referral_code', sa.Column('owner_id', sa.Integer(), nullable=False))
    op.add_column('referral_code', sa.Column('expiration_date', sa.Date(), nullable=False))
    op.drop_constraint('referral_code_onwer_id_fkey', 'referral_code', type_='foreignkey')
    op.create_foreign_key(None, 'referral_code', 'user', ['owner_id'], ['id'])
    op.drop_column('referral_code', 'expiration_time')
    op.drop_column('referral_code', 'onwer_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('referral_code', sa.Column('onwer_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('referral_code', sa.Column('expiration_time', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'referral_code', type_='foreignkey')
    op.create_foreign_key('referral_code_onwer_id_fkey', 'referral_code', 'user', ['onwer_id'], ['id'])
    op.drop_column('referral_code', 'expiration_date')
    op.drop_column('referral_code', 'owner_id')
    op.drop_table('user_registration')
    # ### end Alembic commands ###
