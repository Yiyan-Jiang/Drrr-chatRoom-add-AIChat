import unittest

from pydantic import ValidationError

from normal_system.schemas import RoomCreate, RoomInDB, RoomUpdate


class RoomSchemaTest(unittest.TestCase):
    def test_room_create_accepts_display_metadata(self):
        room = RoomCreate(
            name="Study_1",
            description="quiet room",
            tags=["study", "quiet"],
            min_age=16,
            max_age=24,
            max_members=12,
            notice="Line 1\nLine 2",
            rules="Be kind",
        )

        self.assertEqual(room.tags, ["study", "quiet"])
        self.assertEqual(room.description, "quiet room")
        self.assertEqual(room.notice, "Line 1\nLine 2")
        self.assertEqual(room.rules, "Be kind")
        self.assertEqual(room.min_age, 16)
        self.assertEqual(room.max_age, 24)
        self.assertEqual(room.max_members, 12)

    def test_room_create_trims_name_and_description(self):
        room = RoomCreate(name="  Room_1  ", description="  short intro  ")

        self.assertEqual(room.name, "Room_1")
        self.assertEqual(room.description, "short intro")

    def test_room_create_rejects_invalid_name_characters(self):
        for name in ["Room-1", "Room 1", "Room😀"]:
            with self.subTest(name=name):
                with self.assertRaises(ValidationError):
                    RoomCreate(name=name)

    def test_room_create_rejects_name_longer_than_eight_characters(self):
        with self.assertRaises(ValidationError):
            RoomCreate(name="abcdefghi")

    def test_room_create_rejects_description_longer_than_twenty_characters(self):
        with self.assertRaises(ValidationError):
            RoomCreate(name="Room_1", description="x" * 21)

    def test_room_create_rejects_notice_and_rules_longer_than_two_hundred(self):
        with self.assertRaises(ValidationError):
            RoomCreate(name="Room_1", notice="x" * 201)
        with self.assertRaises(ValidationError):
            RoomCreate(name="Room_1", rules="x" * 201)

    def test_room_update_trims_name_and_description_only(self):
        update = RoomUpdate(
            name="  Room_2  ",
            description="  intro  ",
            notice="  keep notice whitespace\n",
            rules="\nkeep rules whitespace  ",
        )

        self.assertEqual(update.name, "Room_2")
        self.assertEqual(update.description, "intro")
        self.assertEqual(update.notice, "  keep notice whitespace\n")
        self.assertEqual(update.rules, "\nkeep rules whitespace  ")

    def test_room_create_rejects_invalid_age_range(self):
        with self.assertRaises(ValidationError):
            RoomCreate(name="Invalid Room", min_age=30, max_age=20)

    def test_room_response_normalizes_nullable_metadata(self):
        room = RoomInDB(
            id=1,
            name="Room_1",
            description=None,
            notice=None,
            rules=None,
            tags=None,
            min_age=None,
            max_age=None,
            max_members=None,
            peak_online_members=None,
            owner_id=2,
            owner={"id": 2, "username": "alice", "avatar_key": None},
            created_at="2026-04-28T12:00:00",
        )

        self.assertEqual(room.description, "")
        self.assertEqual(room.notice, "")
        self.assertEqual(room.rules, "")
        self.assertEqual(room.tags, [])
        self.assertEqual(room.max_members, 20)
        self.assertEqual(room.peak_online_members, 1)
        self.assertEqual(room.owner.username, "alice")


if __name__ == "__main__":
    unittest.main()
