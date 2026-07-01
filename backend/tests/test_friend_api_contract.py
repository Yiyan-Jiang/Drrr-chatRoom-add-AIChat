from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_friend_router_exports_expected_http_endpoints():
    router_path = ROOT / "normal_system" / "routers" / "friend.py"
    assert router_path.exists()

    content = router_path.read_text(encoding="utf-8")

    assert 'APIRouter(prefix="/friends"' in content
    assert '@router.get("/", response_model=PaginatedFriendsResponse)' in content
    assert '@router.post("/requests", response_model=FriendRequestInDB' in content
    assert '@router.get("/requests", response_model=PaginatedFriendRequestsResponse)' in content
    assert '@router.post("/requests/{request_id:int}/accept"' in content
    assert '@router.post("/requests/{request_id:int}/reject"' in content
    assert '@router.post("/requests/{request_id:int}/cancel"' in content
    assert '@router.delete("/{friend_id:int}"' in content
    assert "get_current_user_id" in content


def test_private_messages_router_exports_history_endpoint():
    router_path = ROOT / "normal_system" / "routers" / "friend.py"
    content = router_path.read_text(encoding="utf-8")

    assert 'APIRouter(prefix="/private-messages"' in content
    assert '@private_message_router.get("/{friend_id:int}", response_model=PaginatedPrivateMessagesResponse)' in content


def test_friend_router_is_exported_and_mounted():
    routers_init = (ROOT / "normal_system" / "routers" / "__init__.py").read_text(
        encoding="utf-8"
    )
    app_factory = (ROOT / "app_factory.py").read_text(encoding="utf-8")

    assert "friend_router" in routers_init
    assert "private_message_router" in routers_init
    assert "friend_router" in app_factory
    assert "private_message_router" in app_factory


def test_normal_migration_creates_friend_private_chat_tables():
    migrations = list(
        (ROOT / "normal_system" / "alembic" / "versions").glob("*create_friends_private_chat.py")
    )
    assert migrations

    content = migrations[0].read_text(encoding="utf-8")

    assert '"chatRoom_friend_request"' in content
    assert '"chatRoom_friendship"' in content
    assert '"chatRoom_private_message"' in content
    assert "uq_friend_request_direction_status" in content
    assert "uq_friendship_pair" in content
    assert "uq_private_message_client_message_id" in content
