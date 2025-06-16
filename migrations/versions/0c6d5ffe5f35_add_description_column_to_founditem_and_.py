"""Add description column to FoundItem and LostItem

Revision ID: 0c6d5ffe5f35
Revises: dc4307138591
Create Date: 2025-06-16 19:48:10.439525

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c6d5ffe5f35'
down_revision = 'dc4307138591'
branch_labels = None
depends_on = None


def upgrade():
    # comment 테이블에 found_item_id, lost_item_id 컬럼 추가
    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('found_item_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('lost_item_id', sa.Integer(), nullable=True))
        batch_op.drop_column('item_id')
        # foreign key 제약조건 생성은 애플리케이션 모델에서 처리하거나 별도 마이그레이션에서 진행 권장
        # SQLite에서 제약조건 이름 없이 drop/create 시 에러 발생 가능성 높음

    # found_item 테이블에 description 컬럼 추가
    with op.batch_alter_table('found_item', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))


def downgrade():
    # found_item 테이블에서 description 컬럼 제거
    with op.batch_alter_table('found_item', schema=None) as batch_op:
        batch_op.drop_column('description')

    # comment 테이블에서 lost_item_id, found_item_id 컬럼 제거 및 item_id 컬럼 복원
    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('item_id', sa.INTEGER(), nullable=False))
        batch_op.drop_column('lost_item_id')
        batch_op.drop_column('found_item_id')
        # foreign key 제약조건 복원은 별도 마이그레이션이나 애플리케이션 모델에서 처리 권장
