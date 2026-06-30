from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_posts_router_exports_expected_http_endpoints():
    router_path = ROOT / "normal_system" / "routers" / "post.py"
    assert router_path.exists()

    content = router_path.read_text(encoding="utf-8")

    assert 'APIRouter(prefix="/posts"' in content
    assert '@router.get("/", response_model=PaginatedPostsResponse)' in content
    assert '@router.post("/", response_model=PostDetail' in content
    assert '@router.get("/{post_id:int}", response_model=PostDetail)' in content
    assert '@router.get("/favorites/mine", response_model=PaginatedPostsResponse)' in content
    assert '@router.post("/{post_id:int}/comments"' in content
    assert '@router.put("/{post_id:int}/like"' in content
    assert '@router.delete("/{post_id:int}/like"' in content
    assert '@router.put("/{post_id:int}/favorite"' in content
    assert '@router.delete("/{post_id:int}/favorite"' in content
    assert "get_current_user_id" in content


def test_posts_router_is_exported_and_mounted():
    routers_init = (ROOT / "normal_system" / "routers" / "__init__.py").read_text(
        encoding="utf-8"
    )
    app_factory = (ROOT / "app_factory.py").read_text(encoding="utf-8")

    assert "post_router" in routers_init
    assert "post_router" in app_factory


def test_normal_migration_creates_posts_tables():
    migrations = list(
        (ROOT / "normal_system" / "alembic" / "versions").glob("*create_posts.py")
    )
    assert migrations

    content = migrations[0].read_text(encoding="utf-8")

    assert '"chatRoom_post"' in content
    assert '"chatRoom_post_comment"' in content
    assert '"chatRoom_post_like"' in content
    assert '"chatRoom_post_favorite"' in content
    assert "uq_post_like_post_user" in content
    assert "uq_post_favorite_post_user" in content
