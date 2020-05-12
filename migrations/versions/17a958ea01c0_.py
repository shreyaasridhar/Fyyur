"""empty message

Revision ID: 17a958ea01c0
Revises: 0b543d15585e
Create Date: 2020-05-12 05:44:39.413651

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '17a958ea01c0'
down_revision = '0b543d15585e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('artists', 'phone',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('venues', 'address',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('venues', 'address',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('artists', 'phone',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    # ### end Alembic commands ###
