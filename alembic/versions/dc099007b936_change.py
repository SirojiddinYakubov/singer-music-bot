"""change 

Revision ID: dc099007b936
Revises: 12bc8e6eaaf6
Create Date: 2024-03-16 10:56:45.081618

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dc099007b936'
down_revision: Union[str, None] = '12bc8e6eaaf6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'id',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=False,
               autoincrement=True,
               existing_server_default=sa.text("nextval('user_id_seq'::regclass)"))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'id',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=False,
               autoincrement=True,
               existing_server_default=sa.text("nextval('user_id_seq'::regclass)"))
    # ### end Alembic commands ###
