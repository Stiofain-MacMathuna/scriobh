"""create initial schema

Revision ID: 5e75fd378f5a
Revises: 
Create Date: 2025-08-23 20:12:15.417086

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5e75fd378f5a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Needed for gen_random_uuid() on Supabase/Postgres
    op.execute('create extension if not exists "pgcrypto";')

    # Users table (email+hashed password; UUID PK)
    op.execute(
        """
        create table if not exists users (
            id uuid primary key default gen_random_uuid(),
            email text unique not null,
            password_hash text not null,
            created_at timestamptz not null default now()
        );
        """
    )

    # Notes table (owned by user)
    op.execute(
        """
        create table if not exists notes (
            id bigserial primary key,
            title text not null,
            content text not null,
            user_id uuid not null references users(id) on delete cascade,
            created_at timestamptz not null default now(),
            updated_at timestamptz not null default now()
        );
        """
    )

    # Helpful indexes
    op.execute("create index if not exists idx_notes_user on notes(user_id);")
    # Optional uniqueness per user (comment out if you want duplicate titles):
    # op.execute("create unique index if not exists uq_notes_user_title on notes(user_id, title);")
    

def downgrade() -> None:
    # Drop in reverse order of dependencies
    op.execute("drop index if exists idx_notes_user;")
    # op.execute("drop index if exists uq_notes_user_title;")
    op.execute("drop table if exists notes;")
    op.execute("drop table if exists users;")
    op.execute('drop extension if exists "pgcrypto";')
