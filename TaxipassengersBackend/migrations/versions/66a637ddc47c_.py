"""empty message

Revision ID: 66a637ddc47c
Revises: db70e1737c97
Create Date: 2020-12-22 14:25:50.376851

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '66a637ddc47c'
down_revision = 'db70e1737c97'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('passenger_model', sa.Column('rating', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('passenger_model', 'rating')
    # ### end Alembic commands ###