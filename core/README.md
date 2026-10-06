# MySQL 数据库说明

项目只使用 `chat_rooms` MySQL 数据库。普通业务的 Alembic 迁移是表结构演进的入口：

```bash
cd backend
alembic -c normal_system/alembic.ini upgrade head
```

执行前先创建数据库与数据库用户，并在 `backend/.env` 配置 `DATABASE_URL`。当前迁移包括账号、房间、群聊消息、帖子、好友和私聊消息。

## 历史 SQL 文件

- `init_database.sql`：旧版用户、房间和消息初始化脚本，不包含全部后续功能表。
- `chat_room_refactor_migration.sql`：旧版聊天室结构调整。
- `add_room_display_metadata.sql`：旧版房间展示字段调整。

新建空数据库应使用 Alembic，不应把历史初始化 SQL 当作完整的当前 schema。

已有旧版表时，先核对实际字段、索引和外键是否符合相应迁移，再建立正确的 Alembic 基线并升级。不要直接 `stamp head` 跳过尚未建立的功能表。

AI PostgreSQL 初始化脚本已移除，启动和迁移均不再依赖 PostgreSQL。
