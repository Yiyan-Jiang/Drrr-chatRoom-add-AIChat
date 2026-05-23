import unittest

from normal_system.services.room_presence import RoomPresence


class RoomPresenceTest(unittest.TestCase):
    def test_join_counts_unique_socket_once(self):
        presence = RoomPresence()

        self.assertEqual(presence.join("sid-1", 3), 1)
        self.assertEqual(presence.join("sid-1", 3), 1)

        self.assertEqual(presence.count(3), 1)

    def test_join_reports_whether_user_entered_room_first_time(self):
        presence = RoomPresence()

        self.assertTrue(presence.join_user_entered_room("sid-1", 3, user_id=10))
        self.assertFalse(presence.join_user_entered_room("sid-1", 3, user_id=10))
        self.assertFalse(presence.join_user_entered_room("sid-2", 3, user_id=10))
        self.assertTrue(presence.join_user_entered_room("sid-3", 3, user_id=11))

        self.assertEqual(presence.members(3), [10, 11])

    def test_leave_decrements_room_count(self):
        presence = RoomPresence()
        presence.join("sid-1", 3)
        presence.join("sid-2", 3)

        self.assertEqual(presence.leave("sid-1", 3), 1)

        self.assertEqual(presence.count(3), 1)

    def test_disconnect_removes_socket_from_all_rooms(self):
        presence = RoomPresence()
        presence.join("sid-1", 3)
        presence.join("sid-1", 4)
        presence.join("sid-2", 3)

        changed_rooms = presence.disconnect("sid-1")

        self.assertEqual(changed_rooms, {3: 1, 4: 0})
        self.assertEqual(presence.count(3), 1)
        self.assertEqual(presence.count(4), 0)

    def test_total_viewers_counts_unique_user_ids(self):
        presence = RoomPresence()

        presence.join("sid-1", 3, user_id=10)
        presence.join("sid-2", 4, user_id=10)
        presence.join("sid-3", 4, user_id=11)

        self.assertEqual(presence.total_viewers(), 2)

    def test_members_deduplicates_same_user_across_tabs(self):
        presence = RoomPresence()

        presence.join("sid-1", 3, user_id=10)
        presence.join("sid-2", 3, user_id=10)
        presence.join("sid-3", 3, user_id=11)

        self.assertEqual(presence.members(3), [10, 11])
        self.assertEqual(presence.count(3), 2)

    def test_leave_reports_whether_user_has_left_room_completely(self):
        presence = RoomPresence()
        presence.join("sid-1", 3, user_id=10)
        presence.join("sid-2", 3, user_id=10)

        self.assertFalse(presence.leave_user_left_room("sid-1", 3))
        self.assertTrue(presence.leave_user_left_room("sid-2", 3))


if __name__ == "__main__":
    unittest.main()
