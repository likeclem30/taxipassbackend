"""empty message

Revision ID: db70e1737c97
Revises: 
Create Date: 2020-12-22 08:32:01.646484

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'db70e1737c97'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('passenger_model',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('authId', sa.Integer(), nullable=True),
    sa.Column('firstName', sa.String(length=250), nullable=True),
    sa.Column('lastName', sa.String(length=250), nullable=True),
    sa.Column('dateOfBirth', sa.String(length=250), nullable=True),
    sa.Column('email', sa.String(length=250), nullable=True),
    sa.Column('phoneNumber', sa.String(length=250), nullable=True),
    sa.Column('image', sa.String(length=250), nullable=True),
    sa.Column('homeLocation', sa.String(length=250), nullable=True),
    sa.Column('homePickupTime', sa.String(length=250), nullable=True),
    sa.Column('workLocation', sa.String(length=250), nullable=True),
    sa.Column('workPickupTime', sa.String(length=250), nullable=True),
    sa.Column('paymentMethod', sa.String(length=250), nullable=True),
    sa.Column('emailStatus', sa.Integer(), nullable=True),
    sa.Column('phoneNumberStatus', sa.Integer(), nullable=True),
    sa.Column('suspendedAt', sa.DateTime(), nullable=True),
    sa.Column('updateTimestamp', sa.DateTime(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('authId'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phoneNumber')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('passenger_model')
    # ### end Alembic commands ###
