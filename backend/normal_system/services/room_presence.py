"""维护当前进程内连接、房间与用户的在线关系。"""


class RoomPresence:
    """维护单进程内房间连接，并按用户 ID 对多连接成员去重。"""

    def __init__(self):
        """初始化连接与用户、房间的进程内映射。"""
        self._room_sids: dict[int, set[str]] = {}
        self._sid_rooms: dict[str, set[int]] = {}
        self._sid_user_ids: dict[str, int] = {}

    def join(self, sid: str, room_id: int, user_id: int | None = None) -> int:
        """登记连接进入房间，并返回按用户去重后的当前人数。"""
        self._room_sids.setdefault(room_id, set()).add(sid)
        self._sid_rooms.setdefault(sid, set()).add(room_id)
        if user_id is not None:
            self._sid_user_ids[sid] = user_id
        return self.count(room_id)

    def join_user_entered_room(self, sid: str, room_id: int, user_id: int) -> bool:
        """登记用户的连接，返回该用户是否首次出现在此房间。"""
        user_was_in_room = user_id in self.members(room_id)
        self.join(sid, room_id, user_id=user_id)
        return not user_was_in_room

    def is_sid_in_room(self, sid: str, room_id: int) -> bool:
        """判断连接是否已登记在指定房间。"""
        return sid in self._room_sids.get(room_id, set())

    def leave(self, sid: str, room_id: int) -> int:
        """移除连接在房间中的记录，清理空映射并返回剩余人数。"""
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
        """移除连接并判断该用户是否已无其他连接留在房间。"""
        user_id = self._sid_user_ids.get(sid)
        if not self.is_sid_in_room(sid, room_id):
            return False
        self.leave(sid, room_id)
        if user_id is None:
            return True
        return user_id not in self.members(room_id)

    def disconnect(self, sid: str) -> dict[int, int]:
        """移除断开的连接，返回各受影响房间的剩余人数。"""
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
        """按用户 ID 去重统计房间人数，无用户映射时统计连接数。"""
        room_sids = self._room_sids.get(room_id, set())
        user_ids = {
            self._sid_user_ids[sid] for sid in room_sids if sid in self._sid_user_ids
        }
        return len(user_ids) if user_ids else len(room_sids)

    def total_viewers(self) -> int:
        """统计当前所有已登记房间中的去重在线用户数。"""
        return len(set(self._sid_user_ids.values()))

    def members(self, room_id: int) -> list[int]:
        """按用户 ID 升序返回房间的去重成员列表。"""
        user_ids = {
            self._sid_user_ids[sid]
            for sid in self._room_sids.get(room_id, set())
            if sid in self._sid_user_ids
        }
        return sorted(user_ids)

    def clear_room(self, room_id: int) -> None:
        """移除房间在线记录，并清理不再属于任何房间的连接映射。"""
        sids = list(self._room_sids.pop(room_id, set()))
        for sid in sids:
            sid_rooms = self._sid_rooms.get(sid)
            if sid_rooms is not None:
                sid_rooms.discard(room_id)
                if not sid_rooms:
                    self._sid_rooms.pop(sid, None)
                    self._sid_user_ids.pop(sid, None)
