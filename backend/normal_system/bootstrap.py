from common.normal_database import verify_normal_migrations_applied


async def init_db() -> None:
    import normal_system.models  # noqa: F401

    await verify_normal_migrations_applied()
