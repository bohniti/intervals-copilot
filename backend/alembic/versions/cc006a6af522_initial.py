"""initial — full schema with new activity types, tags, and session_routes

Revision ID: cc006a6af522
Revises:
Create Date: 2026-03-09 12:00:00
"""
from alembic import op

revision = "cc006a6af522"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types with idempotent DO-block so re-runs never fail
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE activitytype AS ENUM (
                'bouldering', 'sport_climb', 'multi_pitch',
                'cycling', 'hiking', 'fitness', 'other'
            );
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE activitysource AS ENUM (
                'manual', 'chat_cli', 'garmin', 'intervals_icu'
            );
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE gradesystem AS ENUM (
                'yds', 'french', 'font', 'uiaa', 'ice_wis', 'alpine', 'vscale'
            );
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE climbstyle AS ENUM (
                'onsight', 'flash', 'redpoint', 'top_rope', 'attempt', 'aid', 'solo'
            );
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)

    # activities table
    op.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            id               SERIAL PRIMARY KEY,
            created_at       TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at       TIMESTAMP NOT NULL DEFAULT NOW(),
            activity_type    activitytype NOT NULL,
            title            TEXT NOT NULL,
            date             TIMESTAMP NOT NULL,
            duration_minutes INTEGER,
            distance_km      DOUBLE PRECISION,
            elevation_gain_m DOUBLE PRECISION,
            lat              DOUBLE PRECISION,
            lon              DOUBLE PRECISION,
            location_name    TEXT,
            notes            TEXT,
            source           activitysource NOT NULL DEFAULT 'manual',
            raw_json         JSONB,
            tags             JSONB NOT NULL DEFAULT '[]',
            area             TEXT,
            partner          TEXT,
            intervals_activity_id TEXT
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_activities_date ON activities (date)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_activities_activity_type ON activities (activity_type)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_activities_intervals_id ON activities (intervals_activity_id)")

    # session_routes table
    op.execute("""
        CREATE TABLE IF NOT EXISTS session_routes (
            id           SERIAL PRIMARY KEY,
            activity_id  INTEGER NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
            created_at   TIMESTAMP NOT NULL DEFAULT NOW(),
            route_name   TEXT,
            grade        TEXT,
            grade_system gradesystem,
            style        climbstyle,
            pitches      INTEGER,
            height_m     DOUBLE PRECISION,
            rock_type    TEXT,
            sector       TEXT,
            notes        TEXT,
            sort_order   INTEGER NOT NULL DEFAULT 0
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_session_routes_activity_id ON session_routes (activity_id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS session_routes")
    op.execute("DROP TABLE IF EXISTS activities")
    op.execute("DROP TYPE IF EXISTS activitytype")
    op.execute("DROP TYPE IF EXISTS activitysource")
    op.execute("DROP TYPE IF EXISTS gradesystem")
    op.execute("DROP TYPE IF EXISTS climbstyle")
