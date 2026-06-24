import asyncio
import os
import unittest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException


class UserDeleteOwnershipTest(unittest.TestCase):
    def setUp(self):
        self.env_patcher = patch.dict(
            os.environ,
            {
                "DATABASE_URL": "mysql+aiomysql://user:pass@localhost:3306/chat_rooms",
                "CHAT_JWT_SECRET": "secret",
            },
        )
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()

    def test_delete_user_account_rejects_another_user(self):
        from normal_system.routers.user import delete_user_account

        delete_mock = AsyncMock(return_value=True)
        with patch("normal_system.routers.user.delete_user", delete_mock):
            with self.assertRaises(HTTPException) as ctx:
                asyncio.run(
                    delete_user_account(
                        user_id=2,
                        current_user_id=1,
                        db=object(),
                    )
                )

        self.assertEqual(ctx.exception.status_code, 403)
        self.assertEqual(ctx.exception.detail, "Cannot delete another user")
        delete_mock.assert_not_called()

    def test_delete_user_account_allows_current_user(self):
        from normal_system.routers.user import delete_user_account

        db = object()
        delete_mock = AsyncMock(return_value=True)
        with patch("normal_system.routers.user.delete_user", delete_mock):
            asyncio.run(
                delete_user_account(
                    user_id=1,
                    current_user_id=1,
                    db=db,
                )
            )

        delete_mock.assert_awaited_once_with(db, 1)

    def test_delete_user_deletes_owned_rooms_before_deleting_user(self):
        from normal_system.repositories import delete_user

        user = object()
        db = AsyncMock()
        executed_statements = []

        async def record_execute(statement):
            executed_statements.append(str(statement.compile(compile_kwargs={"literal_binds": True})))

        db.execute.side_effect = record_execute

        with patch("normal_system.repositories.get_user_by_id", AsyncMock(return_value=user)):
            result = asyncio.run(delete_user(db, 3))

        self.assertTrue(result)
        self.assertTrue(
            any(
                'DELETE FROM "chatRoom_message" WHERE "chatRoom_message".room_id IN' in statement
                and '"chatRoom_room".owner_id = 3' in statement
                for statement in executed_statements
            )
        )
        self.assertTrue(
            any(
                'DELETE FROM "chatRoom_room" WHERE "chatRoom_room".owner_id = 3' in statement
                for statement in executed_statements
            )
        )
        self.assertFalse(any("SET owner_id=NULL" in statement for statement in executed_statements))
        db.delete.assert_awaited_once_with(user)
        db.commit.assert_awaited_once()


if __name__ == "__main__":
    with patch.dict(
        os.environ,
        {
            "DATABASE_URL": "mysql+aiomysql://user:pass@localhost:3306/chat_rooms",
            "CHAT_JWT_SECRET": "secret",
        },
    ):
        unittest.main()
