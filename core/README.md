## 普通聊天室库（MySQL）

先登录 MySQL：

> mysql -u root -p


然后
```SQL
SOURCE ~/Login and chat rooms/core/init_database.sql;
```

或者
```SQL
SOURCE ~\\Login and chat rooms\\core\\init_database.sql;
```

**注意的是应该将以上`~`绝对路径改成你自己的路径**

## AI 聊天历史库（PostgreSQL）

先确认 `core/init_ai_database.sql` 里的 `ai_user` 密码和 `backend/.env` 里的
`AI_DATABASE_URL` 一致。

### 方式一：在 PowerShell / CMD 里执行

注意：下面这条命令是在系统终端里执行，不是在 `postgres=#` 这个 psql 交互窗口里执行。

```bash
psql -U postgres -f "~/Login and chat rooms/core/init_ai_database.sql"
```

或者：

```bash
psql -U postgres -f "~\\Login and chat rooms\\core\\init_ai_database.sql"
```

### 方式二：已经进入 psql 交互窗口时执行

如果你已经看到 `postgres=#`，不要再输入 `psql -U postgres -f ...`，而是执行：

```sql
\i '~/Login and chat rooms/core/init_ai_database.sql'
```

如果提示符变成了 `postgres-#`，说明上一条 SQL 还没结束。可以先按 `Ctrl+C` 取消，
或者输入 `\r` 清空当前输入缓冲区，再执行上面的 `\i` 命令。

这个脚本会创建 `ai_chat` 数据库、`ai_user` 用户、`ai_chat_history` 表、相关索引，
并写入 `alembic_version=0001_create_ai_chat_history`，避免后端启动时再次提示 AI
迁移未应用。
