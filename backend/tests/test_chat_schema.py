import unittest

from normal_system.schemas import (
    MessageInDB,
    PaginatedMessagesResponse,
    RoomInDB,
    UserPublic,
)


class ChatSchemaTest(unittest.TestCase):
    def test_user_public_contains_avatar_key_with_default(self):
        user = UserPublic(
            id=1,
            username="alice",
            created_at="2026-05-17T12:00:00",
        )

        self.assertEqual(user.avatar_key, "kanra")

    def test_room_response_contains_owner_id_and_owner(self):
        owner = UserPublic(
            id=7,
            username="owner",
            avatar_key="zawa",
            created_at="2026-05-17T12:00:00",
        )

        room = RoomInDB(
            id=1,
            name="room",
            owner_id=7,
            owner=owner,
            created_at="2026-05-17T12:00:00",
        )

        self.assertEqual(room.owner_id, 7)
        self.assertEqual(room.owner.avatar_key, "zawa")

    def test_message_response_supports_system_message_and_author(self):
        message = MessageInDB(
            id=1,
            content="-- alice 离开了房间 --",
            room_id=2,
            user_id=None,
            message_type="system",
            client_message_id=None,
            author=None,
            created_at="2026-05-17T12:00:00",
        )

        self.assertEqual(message.message_type, "system")
        self.assertIsNone(message.user_id)
        self.assertIsNone(message.author)

    def test_paginated_messages_response_contains_cursor_metadata(self):
        page = PaginatedMessagesResponse(items=[], has_more=False, next_before_id=None)

        self.assertEqual(page.items, [])
        self.assertFalse(page.has_more)
        self.assertIsNone(page.next_before_id)


if __name__ == "__main__":
    unittest.main()
