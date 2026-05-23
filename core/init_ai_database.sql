-- AI database bootstrap for PostgreSQL.
-- Run this script as a PostgreSQL superuser, for example:
-- psql -U postgres -f "D:/python excise/Login and chat rooms/core/init_ai_database.sql"
--
-- Keep the password here aligned with backend/.env AI_DATABASE_URL.

SELECT 'CREATE DATABASE ai_chat'
WHERE NOT EXISTS (
  SELECT 1 FROM pg_database WHERE datname = 'ai_chat'
)
\gexec

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = 'ai_user'
  ) THEN
    CREATE ROLE ai_user LOGIN PASSWORD 'change-me-in-env';
  ELSE
    ALTER ROLE ai_user WITH LOGIN PASSWORD 'change-me-in-env';
  END IF;
END
$$;

GRANT ALL PRIVILEGES ON DATABASE ai_chat TO ai_user;

\connect ai_chat

CREATE TABLE IF NOT EXISTS ai_chat_history (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  character VARCHAR(20) NOT NULL DEFAULT 'sakura',
  role VARCHAR(20) NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_ai_chat_history_user_id
  ON ai_chat_history (user_id);

CREATE INDEX IF NOT EXISTS ix_ai_chat_history_character
  ON ai_chat_history (character);

CREATE TABLE IF NOT EXISTS alembic_version (
  version_num VARCHAR(32) NOT NULL PRIMARY KEY
);

INSERT INTO alembic_version (version_num)
VALUES ('0001_create_ai_chat_history')
ON CONFLICT (version_num) DO NOTHING;

GRANT USAGE, CREATE ON SCHEMA public TO ai_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ai_user;
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO ai_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ai_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO ai_user;
