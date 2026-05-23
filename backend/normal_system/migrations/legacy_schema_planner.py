from collections.abc import Iterable, Mapping

from sqlalchemy import bindparam, text
from sqlalchemy.ext.asyncio import AsyncConnection


TABLES = ("chatRoom_user", "chatRoom_room", "chatRoom_message")
TABLE_BY_LOWER_NAME = {table.lower(): table for table in TABLES}


def _canonical_table_name(table_name: str) -> str | None:
    return TABLE_BY_LOWER_NAME.get(table_name.lower())


def normalize_schema_snapshot(
    columns: Mapping[str, Iterable[str]],
    indexes: Mapping[str, Iterable[str]],
) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    normalized_columns: dict[str, set[str]] = {table: set() for table in TABLES}
    normalized_indexes: dict[str, set[str]] = {table: set() for table in TABLES}

    for table_name, table_columns in columns.items():
        canonical_name = _canonical_table_name(table_name)
        if canonical_name is not None:
            normalized_columns[canonical_name].update(table_columns)

    for table_name, table_indexes in indexes.items():
        canonical_name = _canonical_table_name(table_name)
        if canonical_name is not None:
            normalized_indexes[canonical_name].update(table_indexes)

    return normalized_columns, normalized_indexes


def _table_columns(columns: Mapping[str, Iterable[str]], table: str) -> set[str]:
    return set(columns.get(table, set()))


def _table_indexes(indexes: Mapping[str, Iterable[str]], table: str) -> set[str]:
    return set(indexes.get(table, set()))


def plan_room_display_metadata_migration(
    columns: Mapping[str, Iterable[str]],
) -> list[str]:
    room_columns = _table_columns(columns, "chatRoom_room")
    statements: list[str] = []

    missing_columns = {
        "description": "ALTER TABLE chatRoom_room ADD COLUMN description TEXT NULL",
        "tags": "ALTER TABLE chatRoom_room ADD COLUMN tags JSON NULL",
        "min_age": "ALTER TABLE chatRoom_room ADD COLUMN min_age INT NULL",
        "max_age": "ALTER TABLE chatRoom_room ADD COLUMN max_age INT NULL",
        "max_members": (
            "ALTER TABLE chatRoom_room "
            "ADD COLUMN max_members INT NOT NULL DEFAULT 20"
        ),
    }

    for column, statement in missing_columns.items():
        if column not in room_columns:
            statements.append(statement)

    if {"description", "tags"} & (set(missing_columns) - room_columns):
        statements.append(
            "UPDATE chatRoom_room "
            "SET description = COALESCE(description, ''), "
            "tags = COALESCE(tags, JSON_ARRAY())"
        )

    return statements


def plan_room_intro_metadata_migration(
    columns: Mapping[str, Iterable[str]],
) -> list[str]:
    room_columns = _table_columns(columns, "chatRoom_room")
    statements: list[str] = []

    missing_columns = {
        "notice": "ALTER TABLE chatRoom_room ADD COLUMN notice TEXT NULL",
        "rules": "ALTER TABLE chatRoom_room ADD COLUMN rules TEXT NULL",
        "peak_online_members": (
            "ALTER TABLE chatRoom_room "
            "ADD COLUMN peak_online_members INT NOT NULL DEFAULT 1"
        ),
    }

    for column, statement in missing_columns.items():
        if column not in room_columns:
            statements.append(statement)

    if set(missing_columns) - room_columns:
        statements.append(
            "UPDATE chatRoom_room "
            "SET notice = COALESCE(notice, ''), "
            "rules = COALESCE(rules, ''), "
            "peak_online_members = COALESCE(peak_online_members, 1)"
        )

    return statements


def plan_chat_refactor_migration(
    columns: Mapping[str, Iterable[str]],
    indexes: Mapping[str, Iterable[str]],
    foreign_keys: Iterable[str],
) -> list[str]:
    user_columns = _table_columns(columns, "chatRoom_user")
    room_columns = _table_columns(columns, "chatRoom_room")
    message_columns = _table_columns(columns, "chatRoom_message")
    user_indexes = _table_indexes(indexes, "chatRoom_user")
    room_indexes = _table_indexes(indexes, "chatRoom_room")
    message_indexes = _table_indexes(indexes, "chatRoom_message")
    foreign_key_names = set(foreign_keys)

    statements: list[str] = []

    if "avatar_key" not in user_columns:
        statements.append("ALTER TABLE chatRoom_user ADD COLUMN avatar_key VARCHAR(32) NULL")
        user_columns = user_columns | {"avatar_key"}

    if "owner_id" not in room_columns:
        statements.append("ALTER TABLE chatRoom_room ADD COLUMN owner_id INT NULL")
        room_columns = room_columns | {"owner_id"}

    if "message_type" not in message_columns:
        statements.append(
            "ALTER TABLE chatRoom_message ADD COLUMN message_type VARCHAR(20) NULL"
        )
        message_columns = message_columns | {"message_type"}

    if "client_message_id" not in message_columns:
        statements.append(
            "ALTER TABLE chatRoom_message ADD COLUMN client_message_id VARCHAR(64) NULL"
        )
        message_columns = message_columns | {"client_message_id"}

    if "avatar_key" in user_columns:
        statements.append(
            "UPDATE chatRoom_user SET avatar_key = 'kanra' WHERE avatar_key IS NULL"
        )

    if "message_type" in message_columns:
        statements.append(
            "UPDATE chatRoom_message SET message_type = 'user' "
            "WHERE message_type IS NULL"
        )

    if "owner_id" in room_columns and {"id", "room_id", "user_id"} <= message_columns:
        statements.append(
            "UPDATE chatRoom_room r "
            "JOIN ("
            "SELECT room_id, user_id "
            "FROM chatRoom_message m1 "
            "WHERE m1.user_id IS NOT NULL "
            "AND m1.id = ("
            "SELECT MIN(m2.id) FROM chatRoom_message m2 "
            "WHERE m2.room_id = m1.room_id AND m2.user_id IS NOT NULL"
            ")"
            ") first_message ON first_message.room_id = r.id "
            "SET r.owner_id = first_message.user_id "
            "WHERE r.owner_id IS NULL"
        )

    if "avatar_key" in user_columns and "idx_chatRoom_user_avatar_key" not in user_indexes:
        statements.append(
            "CREATE INDEX idx_chatRoom_user_avatar_key ON chatRoom_user (avatar_key)"
        )

    if "owner_id" in room_columns and "idx_chatRoom_room_owner_id" not in room_indexes:
        statements.append(
            "CREATE INDEX idx_chatRoom_room_owner_id ON chatRoom_room (owner_id)"
        )

    if (
        {"room_id", "created_at", "id"} <= message_columns
        and "idx_chatRoom_message_room_created_id" not in message_indexes
    ):
        statements.append(
            "CREATE INDEX idx_chatRoom_message_room_created_id "
            "ON chatRoom_message (room_id, created_at, id)"
        )

    if (
        "client_message_id" in message_columns
        and "uq_chatRoom_message_client_message_id" not in message_indexes
    ):
        statements.append(
            "CREATE UNIQUE INDEX uq_chatRoom_message_client_message_id "
            "ON chatRoom_message (client_message_id)"
        )

    if (
        "owner_id" in room_columns
        and "fk_chatRoom_room_owner" not in foreign_key_names
    ):
        statements.append(
            "ALTER TABLE chatRoom_room "
            "ADD CONSTRAINT fk_chatRoom_room_owner "
            "FOREIGN KEY (owner_id) REFERENCES chatRoom_user(id) "
            "ON DELETE RESTRICT"
        )

    return statements


async def inspect_schema(conn: AsyncConnection) -> tuple[dict[str, set[str]], dict[str, set[str]], set[str]]:
    raw_columns: dict[str, set[str]] = {}
    raw_indexes: dict[str, set[str]] = {}

    column_rows = await conn.execute(
        text(
            "SELECT table_name, column_name "
            "FROM information_schema.columns "
            "WHERE table_schema = DATABASE() "
            "AND table_name IN :tables"
        ).bindparams(bindparam("tables", expanding=True, value=TABLES))
    )
    for table_name, column_name in column_rows:
        raw_columns.setdefault(table_name, set()).add(column_name)

    index_rows = await conn.execute(
        text(
            "SELECT table_name, index_name "
            "FROM information_schema.statistics "
            "WHERE table_schema = DATABASE() "
            "AND table_name IN :tables"
        ).bindparams(bindparam("tables", expanding=True, value=TABLES))
    )
    for table_name, index_name in index_rows:
        raw_indexes.setdefault(table_name, set()).add(index_name)

    fk_rows = await conn.execute(
        text(
            "SELECT constraint_name "
            "FROM information_schema.table_constraints "
            "WHERE table_schema = DATABASE() "
            "AND constraint_type = 'FOREIGN KEY' "
            "AND table_name IN :tables"
        ).bindparams(bindparam("tables", expanding=True, value=TABLES))
    )
    foreign_keys = {constraint_name for (constraint_name,) in fk_rows}
    columns, indexes = normalize_schema_snapshot(raw_columns, raw_indexes)

    return columns, indexes, foreign_keys


async def apply_pending_schema_migrations(conn: AsyncConnection) -> list[str]:
    columns, indexes, foreign_keys = await inspect_schema(conn)
    statements = [
        *plan_room_display_metadata_migration(columns),
        *plan_room_intro_metadata_migration(columns),
        *plan_chat_refactor_migration(columns, indexes, foreign_keys),
    ]

    for statement in statements:
        await conn.execute(text(statement))

    return statements
