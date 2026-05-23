import unittest

from normal_system.migrations.legacy_schema_planner import (
    normalize_schema_snapshot,
    plan_chat_refactor_migration,
    plan_room_intro_metadata_migration,
)


class SchemaMigrationPlanTest(unittest.TestCase):
    def test_legacy_schema_planner_lives_under_normal_system_migrations(self):
        from normal_system.migrations import legacy_schema_planner

        self.assertFalse(legacy_schema_planner.__name__.startswith("schema_migrations"))

    def test_normalizes_mysql_lowercase_table_names(self):
        columns, indexes = normalize_schema_snapshot(
            columns={
                "chatroom_room": {"id", "description", "owner_id"},
                "chatroom_user": {"id", "avatar_key"},
            },
            indexes={
                "chatroom_room": {"idx_chatRoom_room_owner_id"},
                "chatroom_user": {"idx_chatRoom_user_avatar_key"},
            },
        )

        self.assertEqual(columns["chatRoom_room"], {"id", "description", "owner_id"})
        self.assertEqual(columns["chatRoom_user"], {"id", "avatar_key"})
        self.assertEqual(indexes["chatRoom_room"], {"idx_chatRoom_room_owner_id"})

    def test_plans_missing_chat_refactor_columns(self):
        statements = plan_chat_refactor_migration(
            columns={
                "chatRoom_user": {"id", "username", "password", "created_at"},
                "chatRoom_room": {"id", "name", "created_at"},
                "chatRoom_message": {
                    "id",
                    "user_id",
                    "content",
                    "room_id",
                    "created_at",
                },
            },
            indexes={},
            foreign_keys=set(),
        )

        joined = "\n".join(statements)
        self.assertIn("ADD COLUMN avatar_key", joined)
        self.assertIn("ADD COLUMN owner_id", joined)
        self.assertIn("ADD COLUMN message_type", joined)
        self.assertIn("ADD COLUMN client_message_id", joined)
        self.assertIn("UPDATE chatRoom_user", joined)
        self.assertIn("UPDATE chatRoom_message", joined)

    def test_plans_room_intro_metadata_columns(self):
        statements = plan_room_intro_metadata_migration(
            columns={
                "chatRoom_room": {"id", "name", "description", "created_at"},
            },
        )

        joined = "\n".join(statements)
        self.assertIn("ADD COLUMN notice", joined)
        self.assertIn("ADD COLUMN rules", joined)
        self.assertIn("ADD COLUMN peak_online_members", joined)
        self.assertIn("DEFAULT 1", joined)
        self.assertIn("UPDATE chatRoom_room", joined)

    def test_does_not_plan_room_intro_metadata_existing_columns_again(self):
        statements = plan_room_intro_metadata_migration(
            columns={
                "chatRoom_room": {
                    "id",
                    "name",
                    "description",
                    "notice",
                    "rules",
                    "peak_online_members",
                    "created_at",
                },
            },
        )

        joined = "\n".join(statements)
        self.assertNotIn("ADD COLUMN notice", joined)
        self.assertNotIn("ADD COLUMN rules", joined)
        self.assertNotIn("ADD COLUMN peak_online_members", joined)

    def test_does_not_plan_existing_columns_again(self):
        statements = plan_chat_refactor_migration(
            columns={
                "chatRoom_user": {"id", "username", "password", "avatar_key", "created_at"},
                "chatRoom_room": {"id", "name", "owner_id", "created_at"},
                "chatRoom_message": {
                    "id",
                    "content",
                    "room_id",
                    "message_type",
                    "client_message_id",
                    "created_at",
                },
            },
            indexes={
                "chatRoom_user": {"idx_chatRoom_user_avatar_key"},
                "chatRoom_room": {"idx_chatRoom_room_owner_id"},
                "chatRoom_message": {
                    "idx_chatRoom_message_room_created_id",
                    "uq_chatRoom_message_client_message_id",
                },
            },
            foreign_keys={"fk_chatRoom_room_owner"},
        )

        joined = "\n".join(statements)
        self.assertNotIn("ADD COLUMN", joined)
        self.assertNotIn("CREATE INDEX", joined)
        self.assertNotIn("CREATE UNIQUE INDEX", joined)
        self.assertNotIn("ADD CONSTRAINT fk_chatRoom_room_owner", joined)

    def test_plans_owner_id_for_partially_migrated_room_table(self):
        statements = plan_chat_refactor_migration(
            columns={
                "chatRoom_user": {"id", "username", "password", "avatar_key", "created_at"},
                "chatRoom_room": {
                    "id",
                    "name",
                    "description",
                    "tags",
                    "min_age",
                    "max_age",
                    "max_members",
                    "created_at",
                },
                "chatRoom_message": {
                    "id",
                    "user_id",
                    "content",
                    "room_id",
                    "message_type",
                    "client_message_id",
                    "created_at",
                },
            },
            indexes={
                "chatRoom_user": {"idx_chatRoom_user_avatar_key"},
                "chatRoom_message": {
                    "idx_chatRoom_message_room_created_id",
                    "uq_chatRoom_message_client_message_id",
                },
            },
            foreign_keys=set(),
        )

        joined = "\n".join(statements)
        self.assertIn("ALTER TABLE chatRoom_room ADD COLUMN owner_id INT NULL", joined)
        self.assertIn("CREATE INDEX idx_chatRoom_room_owner_id", joined)
        self.assertIn("ADD CONSTRAINT fk_chatRoom_room_owner", joined)
        self.assertNotIn("ADD COLUMN avatar_key", joined)
        self.assertNotIn("ADD COLUMN message_type", joined)


if __name__ == "__main__":
    unittest.main()
