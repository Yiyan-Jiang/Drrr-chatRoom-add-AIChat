class RoomPresence:
    def __init__(self):
        self._room_sids: dict[int, set[str]] = {}
        self._sid_rooms: dict[str, set[int]] = {}
        self._sid_user_ids: dict[str, int] = {}

    def join(self, sid: str, room_id: int, user_id: int | None = None) -> int:
        self._room_sids.setdefault(room_id, set()).add(sid)
        self._sid_rooms.setdefault(sid, set()).add(room_id)
        if user_id is not None:
            self._sid_user_ids[sid] = user_id
        return self.count(room_id)

    def join_user_entered_room(self, sid: str, room_id: int, user_id: int) -> bool:
        user_was_in_room = user_id in self.members(room_id)
        self.join(sid, room_id, user_id=user_id)
        return not user_was_in_room

    def is_sid_in_room(self, sid: str, room_id: int) -> bool:
        return sid in self._room_sids.get(room_id, set())

    def leave(self, sid: str, room_id: int) -> int:
        room_sids = self._room_sids.get(room_id)
        if room_sids is not None:
            room_sids.discard(sid)
            if not room_sids:
                self._room_sids.pop(room_id, None)

        sid_rooms = self._sid_rooms.get(sid)
        if sid_rooms is not None:
            sid_rooms.discard(room_id)
            if not sid_rooms:
                self._sid_rooms.pop(sid, None)
                self._sid_user_ids.pop(sid, None)

        return self.count(room_id)

    def leave_user_left_room(self, sid: str, room_id: int) -> bool:
        user_id = self._sid_user_ids.get(sid)
        if not self.is_sid_in_room(sid, room_id):
            return False
        self.leave(sid, room_id)
        if user_id is None:
            return True
        return user_id not in self.members(room_id)

    def disconnect(self, sid: str) -> dict[int, int]:
        room_ids = list(self._sid_rooms.pop(sid, set()))
        self._sid_user_ids.pop(sid, None)
        changed_counts: dict[int, int] = {}

        for room_id in room_ids:
            room_sids = self._room_sids.get(room_id)
            if room_sids is not None:
                room_sids.discard(sid)
                if not room_sids:
                    self._room_sids.pop(room_id, None)
            changed_counts[room_id] = self.count(room_id)

        return changed_counts

    def count(self, room_id: int) -> int:
        room_sids = self._room_sids.get(room_id, set())
        user_ids = {
            self._sid_user_ids[sid]
            for sid in room_sids
            if sid in self._sid_user_ids
        }
        return len(user_ids) if user_ids else len(room_sids)

    def total_viewers(self) -> int:
        return len(set(self._sid_user_ids.values()))

    def members(self, room_id: int) -> list[int]:
        user_ids = {
            self._sid_user_ids[sid]
            for sid in self._room_sids.get(room_id, set())
            if sid in self._sid_user_ids
        }
        return sorted(user_ids)

    def clear_room(self, room_id: int) -> None:
        sids = list(self._room_sids.pop(room_id, set()))
        for sid in sids:
            sid_rooms = self._sid_rooms.get(sid)
            if sid_rooms is not None:
                sid_rooms.discard(room_id)
                if not sid_rooms:
                    self._sid_rooms.pop(sid, None)
                    self._sid_user_ids.pop(sid, None)
