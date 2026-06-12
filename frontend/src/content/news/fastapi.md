---
date: 2026-04-05
title: fastapi学习
category: 后端
tags: test, skill
---

# fastapi学习

后端框架

<!-- more -->

## quick start

### 安装

```bash
pip install fastapi
pip install uvicorn
```

### 代码

```python
from fastapi import FastAPI

app = FastAPI()

@app.get('/home')
async def home():
  return {'id':1}

if __name__ = '__main__':
  uvicorn.run('url',port=8000,debug=True,reload=True)
```

### 路径操作

```python
@app.post('/post',tage=['这是post接口'],summary='this is summary',description='this is description')
def Mypost():
  return 
```

### 路由分发

```python
from app.app01.urls import shop
app.include_router(shoop,prefox='/shop',tags=['yonghuzhongxinjieko'])

```

### 路径参数

```python
@appp.router('/user/{id}')
async def get_id(id:int,a=None,b:Union[str,None]=None):  #a,b是查询参数，可以有默认参数，有的话可以不选 
  return {
    "id":id
  }
```

### 请求体参数

```python
from pydantic import BaseModel
class User(BaseModel):
  name:str = Field(regex="^q")
  age:int = Field(default=0,gt=0,lt=100)
  birth:Union[data,None] = None
  fri:List[int]

  @validator('name')
  def name_must(cls ,value):
    assert valus.isalpha(),'name must be alpha'
    return value


@app.post('/')
def data(data:User):
  return data
```

### 表单数据
```base
pip install python-multipart
```

```python
@app.post('/')
def get_from(username:str=From(),password:str=From()):

```

### 文件上传

```python
@app.post('/file')
def get_file(file:bytes=File()):
  # 适合小文件上传
  return {
    "file":len(file)
  }

@app.post('/files')
def get_files(files: List[bytes] = File()):
  # 适合多文件上传
  return {
    "file":len(files)
  }

@app.post('/Uploadfile')
def get_Uploadfile(files:UploadFile):
  # 适合单文件上传
  return {
    "file":file.filename
  }  

@app.post('/Uploadfiles')
def get_Uploadfiles(files:List[UploadFile]):
  # 适合多文件上传
  return {
    "file":file.filename
  }  
```
---

## Request

```python
@app.post('/item')
def get_item(request:Request):
  print("IP",request.client.host)
  print("url",request.url)
  print("请求头",request.headers) #字典
  print("cookies",request.cookies)
```

## 请求静态文件

```python
@app.mount('/static',StaticFiles(directory='statics'))
```

## 响应模型参数

使用`response_model`规范输出

```python
class User(BaseModel):
  id:int
  username:str
  password:str

class UserOut(BaseModel):
  id:str
  username:str

@app.post("/user2",response_model=UserOut)
def creatUser(user:User):
```

* 使用`response_model_exclude_unset`去除返回默认值，未被设置的值不返回，
* 使用`response_model_exclude_none`去除None值，
* 使用`response_model_exclude_exclude={字段}`,排除字段，
* 使用`response_model_exclude_include={字段}`，只返回包含的字段

```python
class User(BaseModel):
  id:int
  username:str
  password:str

class UserOut(BaseModel):
  id:str
  username:str

@app.post("/user2",response_model=UserOut,response_model_exclude_unset=True)
def creatUser(user:User):
```

## jinja2



```python
from fastapi.templating import Jinja2Templates

app =FastAPI()

templates = Jinja2Templates(directory='templates')

@app.get('/')
def index():
  name = 'root'
  return templates.TempalteResponse(
    'index.html' #模板文件
    {
      "resquest":request,
      "user":name
    } , # context上下文对象，字典
  )

```

### 分支结构

```html
{% if age>18 %}
<div>日韩</div>
{% else %}
<div>欧美</div>
{% endif %}
```

```html
{ % for book in books % }
<div>{{ book }}</div>
{ % endif % }
```
---

## ORM（补一下）

### 数据库URL获取

数据库的 URL 不是直接“获取”的，而需要你根据数据库的类型和连接信息**手动编写**。

其标准格式如下：
`dialect+driver://username:password@host:port/database`[reference:0]

| 组成部分 | 说明与示例 |
| :--- | :--- |
| **`dialect`** | 数据库类型，例如 `mysql`, `postgresql`, `sqlite`, `oracle`, `mssql`[reference:1]。 |
| **`driver`** | (可选) 连接数据库的 Python 驱动库，例如 `pymysql`, `psycopg2`。如不指定，SQLAlchemy 会使用默认驱动[reference:2]。 |
| **`username`** | 连接数据库的用户名。 |
| **`password`** | 对应用户名的密码。 |
| **`host`** | 数据库服务器的地址（IP 或域名），本地可用 `localhost`[reference:3]。 |
| **`port`** | (可选) 数据库服务的端口号，不同数据库有默认端口（如 MySQL 为 3306）。 |
| **`database`** | 要连接的数据库名称。 |

> 请注意，对于 SQLite，因为它是基于文件的数据库，不需要服务器、用户名和密码，所以 URL 的格式稍有不同[reference:4]。

### 📝 根据不同数据库编写 URL
以下是一些常用数据库的 URL 编写示例，请根据你的实际信息替换代码中的示例值。

#### **MySQL**
使用 PyMySQL 驱动[reference:5]：
```python
# 格式: mysql+pymysql://用户名:密码@主机地址:端口号/数据库名
# 示例: 使用用户 'root'，密码 '123456'，连接本地的 'my_database'
database_url = "mysql+pymysql://root:123456@localhost:3306/my_database"
aiomysql(异步)
```

#### **PostgreSQL**
使用 psycopg2 驱动[reference:6]：
```python
# 格式: postgresql+psycopg2://用户名:密码@主机地址:端口号/数据库名
# 示例: 使用用户 'postgres'，密码 '123456'，连接本地的 'my_database'
database_url = "postgresql+psycopg2://postgres:123456@localhost:5432/my_database"
```

#### **SQLite**
SQLite 不需要指定用户名、密码和主机地址[reference:7][reference:8]。
- **使用相对路径**（推荐用于开发）：
    ```python
    # 文件 'my_database.db' 会生成在与 Python 脚本相同的目录下
    database_url = "sqlite:///my_database.db"
    ```
- **使用绝对路径**：
    ```python
    # Windows 示例
    database_url = "sqlite:///C:/path/to/your/database.db"
    # macOS/Linux 示例
    database_url = "sqlite:////absolute/path/to/your/database.db"
    ```

#### **Microsoft SQL Server**
使用 pymssql 驱动[reference:9]：
```python
# 格式: mssql+pymssql://用户名:密码@主机地址:端口号/数据库名
# 示例
database_url = "mssql+pymssql://sa:123456@localhost:1433/my_database"
```

### 💡 更多使用技巧
#### 从现有 Engine 查看 URL
如果你有一个已经创建好的 `engine` 对象，想查看它所使用的 URL，可以通过其 `url` 属性获取，这在你接手他人代码或调试时非常有用[reference:10]。
```python
from sqlalchemy import create_engine

# 假设这个 engine 已经创建好了
engine = create_engine("mysql+pymysql://user:pass@localhost/db")

# 打印完整的 URL 字符串
print(str(engine.url))

# 或获取 URL 的各个部分
print(engine.url.database)
```

#### 安全地存储 URL
⚠️ **请勿将包含明文密码的数据库 URL 直接硬编码在代码中，尤其是在公开项目里。**

推荐使用环境变量来安全地存储敏感信息。
```python
import os
from sqlalchemy import create_engine

# 从环境变量中读取完整的数据库 URL
# 你需要先在系统中设置这个环境变量，例如 'DATABASE_URL'
database_url = os.environ.get('DATABASE_URL')

# 确保环境变量已设置，否则程序应报错
if not database_url:
    raise ValueError("环境变量 DATABASE_URL 未设置")

engine = create_engine(database_url)
```
---

### SQLAlchemy

`pip i sqlalchemy`安装

下面是使用rawSQL执行简单的原始的SQL语句

```python
from sqlachemy import create_engine ， text

engine = create_engine('数据库url地址' , echo=True) #连接数据库

conn = engine.connect()

conn.execute(text('')) # 执行SQL语句，不能直接传入文本，需要text包装成函数

conn.commit() # 提交事务，使插入永久生效

from sqlalchemy.orm import Session

session = Session(engine)

session.execute(text("")) #执行 SQL 语句，并返回 Result 对象

session.commit()

```

当然我们可以使用py中的类来直接操作表格

```python
from sqlachemy import create_engine , MetaData ,Table ,Column , Integer , String

engine = create_engine('数据库url地址' , echo=True)

meta = MEtaData()

people = Table(
  'tablename' ,  #表名
  meta, #元数据对象作为参数来保持跟踪
  Column('id', Integer, primary_key=True, ), #设置主键
  Column('name', String, nullable=False )   #非空
  Column('age', Integer) 
)

meta.create_all(engine) # 根据 meta 中记录的所有表定义，在数据库中创建表

conn = engine.connect()

# 下面是数据库的增删改查

insert_statement = people.insert().values(name='Jok', age=11) #向people这张表执行数据的插入
res = conn.execute(insert_statement)
conn.commit()

select_statement = people.select().where(people.c.age > 19)
res = conn.execute(select_statement) #查询作为只读数据无需提交
for row in res.fetchall():
  print(row)

update_statement = people.update().where(people.c.age > 11).value()
res = conn.execute(update_statement)
conn.commit()

delete_statement = people.delete().where(people.c.age == 18)
res = conn.execute(delete_statement)
conn.commit()
```

如果想要在建表的时候提供外键约束

```python
from sqlachemy import create_engine , MetaData ,Table ,Column , Integer , String, Float ,ForeignKey

engine = create_engine('数据库url地址' , echo=True)

meta = MEtaData()

things = Table(
  'things',
  meta.
  Column('id' , Interger , primary_key = True)
  Column('description', String, nullable=False)
  Column('value', Float)
  Column('owner', Integer, ForeignKey('people.id')) # 外键关联了上面的people表

)

insert_things = people.insert().values([
  {'description' : '村好剑', 'value':18.8},
  {'description' : '村好药', 'value':5.8}
]) # 多行插入

conn.execute(insert_things)
conn.commit()

join_statement = people.join(things, people.c.id == things.c.owner) #联合查询
select_statement = people.select().with_only_columns(people.c.name, things.c.description).select_from(join_statement)

res = conn.execute(select_statement)

for row in res.fetchall():
  print(row)

group_statement = things.select().with_only_column(things.owner,func.sum(things.c.value)).group_by(thing.c.owner)
res = conn.execyte(group_statement)

for row in res.fetchall():
  print(row)

```

```python
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

engine = create_engine('',echo=True)

Base = declarative_base()

class Person(Base):
  __tablename__ = 'people'
  id = Column(Intger, primary_key=True)
  name = Column(String, nullable=False)
  age = Column(Integer)

  things = relationship('Thing', back_populates='person')
  #建立一对多的关系，things 属性会在 Person 实例上表现为一个列表，包含所有属于这个人的 Thing 对象。实现双向导航，自动处理外键关联

clss Thing(Base):
  __tablename__ = 'thing'
  id = Column(Integer, primary_key=True)
  description = Column(String, nullable=False)
  value = Column(Float)
  owner = Column(Integer, ForeignKey('people.id'))

  person = relattionship('Person',back_populates='person')

Base.metadata.create_all(engine) #创建所有尚未存在的表

Session = sessionmaker(bind=engine) 
#创建一个会话工厂（Session 类），用于后续生成与数据库交互的会话对象
session = Session()
#实例化一个会话对象（session），用于执行 ORM 操作（增删改查、事务控制等）。

new_person = Person(name='jok', age=11)
session.add(new_person)
session.flush() #将当前会话中所有挂起的操作（如 INSERT、UPDATE、DELETE）立即发送到数据库，但不提交事务.

new_thing = Thing(description='春豪剑', value=18.8, owner=new_person.id)
session.add(new_thing)

session.commit()

session.close()
```

```python
import pandas as pd
engine = create_engine('',echo=True)

df = pd.read_sql('') #执行sql语句
print(df)

new_data = pd.DataFrame({"name":["wa","ba"], "age":[11,222]})
new_data.to_sql('people', com=engine, if_exists='append', index=False)


```

### 补充

你的文档已经覆盖了 SQLAlchemy 的基础用法（Raw SQL、Core Table 操作、ORM 模型、关系、外键、pandas 集成），但还有很多**后端开发中常用**的部分可以补充，尤其是现代 SQLAlchemy 2.0+ 风格、性能优化、会话管理、最佳实践、迁移工具等。

下面我按逻辑结构为你补充完整的内容（修正你文档里的小 typo，如 `sqlachemy` → `sqlalchemy`、`MEtaData` → `MetaData`、`Interger` → `Integer`、`clss` → `class`、`relattionship` → `relationship`、`func.sum`、`thing.c.owner` 等）。补充部分用 **粗体** 或新代码块突出。

### 1. 安装与现代导入（推荐 SQLAlchemy 2.0+ 风格）
```python
# 推荐安装（包含异步支持可选）
pip install sqlalchemy[asyncio]  # 如果需要 async
# 或基础版：pip install sqlalchemy

from sqlalchemy import create_engine, text, select, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker, joinedload, selectinload
import sqlalchemy as sa
```

**补充说明**：SQLAlchemy 2.0 引入了统一的 `select()` 风格，强烈推荐使用 `Mapped` + `mapped_column` 的类型注解方式，便于 IDE 类型检查和 mypy。

### 2. Engine 创建（后端常用配置）
```python
# 基础创建
engine = create_engine(
    "postgresql+psycopg2://user:pass@localhost/dbname",  # 支持 mysql、sqlite、postgresql 等
    echo=False,          # 生产环境关闭 SQL 日志
    pool_size=20,        # 连接池大小
    max_overflow=10,     # 超出 pool_size 时的额外连接
    pool_pre_ping=True,  # 防止连接失效（生产必备）
    pool_recycle=3600    # 回收闲置连接（MySQL 常用）
)

# 异步引擎（FastAPI 等异步后端常用）
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
async_engine = create_async_engine("postgresql+asyncpg://...", echo=False)
```

**后端常用**：连接池参数 + `pool_pre_ping=True` 防止数据库断开连接导致的错误。

### 3. ORM 模型定义（现代推荐方式 + 常用字段）
```python
class Base(DeclarativeBase):
    pass

class Person(Base):
    __tablename__ = "people"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(sa.String(100), nullable=False, index=True)
    age: Mapped[int | None] = mapped_column(nullable=True)
    email: Mapped[str | None] = mapped_column(sa.String(255), unique=True, index=True)
    
    # 时间戳（后端几乎必备）
    created_at: Mapped[sa.DateTime] = mapped_column(sa.DateTime, server_default=sa.func.now())
    updated_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime, 
        server_default=sa.func.now(), 
        onupdate=sa.func.now()
    )
    
    # 关系（一对多）
    things: Mapped[list["Thing"]] = relationship(
        "Thing", 
        back_populates="person", 
        cascade="all, delete-orphan",  # 级联删除常用
        lazy="selectin"  # 推荐替换默认 lazy='select'，减少 N+1 查询
    )

class Thing(Base):
    __tablename__ = "things"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(sa.String(200), nullable=False)
    value: Mapped[float] = mapped_column(sa.Float)
    owner_id: Mapped[int] = mapped_column(ForeignKey("people.id"))  # 推荐用 owner_id 命名
    
    person: Mapped["Person"] = relationship("Person", back_populates="things")
```

**补充**：
- 使用 `Mapped` + `mapped_column`（SQLAlchemy 2.0+ 推荐）。
- 添加 `index=True`、`unique=True` 提升查询性能。
- `created_at` / `updated_at` + `server_default` / `onupdate` 是后端标准实践。
- `cascade="all, delete-orphan"` 处理一对多删除。
- **关系加载策略**（后端防 N+1 查询必备）：
  - `lazy="select"`（默认，访问时单独查询，易 N+1）
  - `lazy="selectin"`（推荐，一条额外 IN 查询加载）
  - `lazy="joined"`（JOIN 查询，适合一对一或数据量小）
  - 查询时用 `options(joinedload(Person.things))` 或 `selectinload` 显式 eager loading。

### 4. 会话管理（后端最常用部分）
```python
# 创建 session factory（全局只需一次）
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)  # 推荐设置

# 在 FastAPI/Flask 等框架中使用（依赖注入）
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 现代上下文管理器用法（推荐）
with SessionLocal() as session:
    # 操作...
    session.commit()

# 或事务上下文（更安全）
with SessionLocal.begin() as session:  # 自动 commit/rollback
    ...
```

**最佳实践**：
- 每个请求一个 session（不要全局共享）。
- `expire_on_commit=False` 防止 commit 后对象过期（常用）。
- 总是用 `try/finally` 或上下文管理器确保 `close()`。
- 异常时自动 `rollback()`（用 `Session.begin()`）。

### 5. 常用 CRUD 操作（2.0 风格）
```python
# 查询（推荐 select 风格）
stmt = select(Person).where(Person.age > 18).options(selectinload(Person.things))
result = session.execute(stmt)
people = result.scalars().all()  # 或 .unique().all()

# 插入（单条/批量）
new_person = Person(name="Jok", age=11)
session.add(new_person)
session.commit()  # 或 flush() + refresh

# 批量插入（性能更好）
session.execute(
    sa.insert(Person),
    [{"name": "A", "age": 20}, {"name": "B", "age": 30}]
)
session.commit()

# 更新
stmt = sa.update(Person).where(Person.id == 1).values(age=20)
session.execute(stmt)
session.commit()

# 删除
session.delete(person_obj)
# 或 stmt = sa.delete(Person).where(...)
```

**补充**：批量操作用 `insert()` / `update()` / `delete()` + `execute()` 比循环 `add()` 快很多。

### 6. 表创建与迁移（生产必备）
你的 `meta.create_all(engine)` 只适合开发。

**生产强烈推荐 Alembic**（SQLAlchemy 官方迁移工具）：
```bash
pip install alembic
alembic init migrations
```
- 配置 `alembic.ini` 和 `env.py`（绑定你的 models）。
- `alembic revision --autogenerate -m "add column"`
- `alembic upgrade head`

**额外**：在 `MetaData` 或 `Base.metadata` 中设置命名约定（自动生成 FK、index 名称）：
```python
from sqlalchemy import MetaData
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
}
Base.metadata = MetaData(naming_convention=naming_convention)
```

### 7. Pandas 集成补充
你的代码基本正确，但推荐：
```python
# 读取（支持 select 对象）
df = pd.read_sql(select(Person).where(Person.age > 18), con=engine)

# 写入（大批量数据用 chunksize）
new_data.to_sql(
    "people", 
    con=engine, 
    if_exists="append", 
    index=False,
    method="multi",      # 批量插入加速
    chunksize=1000
)
```

**注意**：`to_sql` 用 `method="multi"` 或自定义 `psycopg2` fast execute 能大幅提升性能。

### 8. 其他后端常用特性
- **Hybrid Property**：字段既能用于 Python 属性，也能用于查询过滤。
- **事件监听**（`@event.listens_for`）：自动处理 updated_at 等。
- **Repository Pattern**：将 CRUD 封装成 Repository 类，解耦业务逻辑（大型后端推荐）。
- **异步支持**：`async_sessionmaker` + `await session.execute()`（FastAPI 常用）。
- **性能优化**：
  - 避免 N+1：总是用 `joinedload` / `selectinload`。
  - 只查询需要的列：`select(Person.id, Person.name)` 而非整个对象。
  - 复杂查询时可混用 Core（`session.connection().execute()`）。
- **错误处理**：捕获 `SQLAlchemyError` 并 rollback。
- **测试**：用 SQLite 内存数据库或测试引擎。

### 推荐学习资源（按重要性）
- 官方文档：SQLAlchemy 2.0 Tutorial（尤其是 ORM 部分）。
- Alembic 官方文档。
- FastAPI + SQLAlchemy 结合示例（很多开源模板）。

你的原始文档适合入门，补充这些后就非常适合**生产后端开发**使用了（尤其是 FastAPI/Flask 项目）。

下面我针对你提到的 **三个重要点**，用清晰、实操的方式详细讲解（基于 FastAPI 最新推荐实践，适用于 2025-2026 年）。每个部分都配有代码示例，便于你直接复制使用。

### 1. 依赖注入（Depends）—— FastAPI 最优雅的核心特性

**为什么说它优雅？**  
FastAPI 的 `Depends` 让代码解耦、复用性强、测试方便。它像“自动注射器”一样，在路由函数运行前自动准备好你需要的对象（数据库会话、当前用户、权限等），用完后自动清理。

**数据库会话（Session）的标准写法（同步版，最常用入门版）**：

```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import sqlalchemy as sa

engine = create_engine("postgresql+psycopg2://user:pass@localhost/db", 
                       pool_pre_ping=True, pool_recycle=3600)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

# 依赖注入函数（推荐写法）
def get_db() -> Session:          # 或用 Iterator[Session]
    db = SessionLocal()
    try:
        yield db                  # 把 session “注入”给路由函数
    finally:
        db.close()                # 请求结束后自动关闭，防止连接泄漏
```

**在路由中使用**（推荐用 `Annotated`，Python 3.9+ 更清晰）：

```python
from fastapi import FastAPI, Depends, APIRouter
from typing import Annotated
from sqlalchemy.orm import Session

app = FastAPI()
router = APIRouter()

@router.get("/users/{user_id}")
def get_user(
    user_id: int, 
    db: Annotated[Session, Depends(get_db)]   # 这里自动注入 session
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

**优点**：
- 不用在每个路由里手动创建/关闭 session。
- FastAPI 会自动缓存同一个请求内的依赖（同一个请求多次调用 `Depends(get_db)` 只创建一次）。
- 测试时非常方便：可以 override 依赖，用 mock 的 session。

**生产小建议**：
- 大项目可以把 `get_db` 放到 `dependencies.py` 文件中。
- 如果想在依赖里自动 commit/rollback，可以用 `try/except` 包裹 `yield`。

### 2. 异步（async/await）—— 对高并发更友好

FastAPI 天生支持异步。当你的项目有较多 I/O 操作（数据库查询、外部 API 调用等）时，异步能显著提升并发能力（同一个线程能同时处理更多请求）。

**异步 SQLAlchemy 配置（推荐写法）**：

```python
# database.py（异步版）
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator

# 注意：使用 asyncpg（PostgreSQL）或 aiomysql（MySQL）
ASYNC_DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/db"

async_engine = create_async_engine(ASYNC_DATABASE_URL, 
                                   pool_pre_ping=True, 
                                   pool_recycle=3600)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,   # 强烈推荐
    autoflush=False
)

# 异步依赖注入
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:   # 自动管理上下文
        try:
            yield session
        finally:
            await session.close()   # 确保关闭
```

**在路由中使用异步**：

```python
from fastapi import Depends
from typing import Annotated

@router.get("/users/{user_id}")
async def get_user_async(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_async_db)]
):
    # 注意：查询也要用 await
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

**什么时候用异步？**
- 小 Demo 或低并发 → 同步版就够（更简单）。
- 中大型项目、需要高并发、或有较多网络 I/O → 推荐异步。
- 注意：不是所有数据库驱动都支持异步（PostgreSQL 用 `asyncpg` 最好）。

**小技巧**：可以用 `async with AsyncSessionLocal() as session:` 在 lifespan 事件中管理引擎的启动/关闭。

### 3. 错误处理 —— 使用 HTTPException

FastAPI 推荐用 `raise HTTPException` 来返回标准的 HTTP 错误，而不是 `return {"error": ...}`。

**基本用法**：

```python
from fastapi import HTTPException, status

@router.get("/items/{item_id}")
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,   # 404
            detail="Item not found"
        )
    
    if not item.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item is inactive"
        )
    
    return item
```

**常见 status_code**（推荐用 `status.HTTP_xxx`）：
- 400 Bad Request → 参数错误、业务逻辑不通过
- 401 Unauthorized → 未登录
- 403 Forbidden → 没权限
- 404 Not Found → 资源不存在
- 422 Unprocessable Entity → Pydantic 验证失败（自动触发）
- 500 Internal Server Error → 服务器内部错误（通常不要手动抛，留给 FastAPI 处理）

**最佳实践**：
- 在 CRUD 层或 service 层抛出自定义异常，然后在路由或全局 handler 中转为 `HTTPException`（保持业务逻辑干净）。
- 数据库错误时：捕获 `SQLAlchemyError`，rollback，然后抛 `HTTPException(500, "Database error")`，不要把原始 SQL 错误信息暴露给用户。
- 全局异常处理器（可选）：

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try later."}
    )
```

### 4. 自动生成的文档（/docs 和 /redoc）

这是 FastAPI 最“开箱即用”的杀手级特性之一，几乎不需要额外配置。

- 访问 `http://127.0.0.1:8000/docs` → **Swagger UI**（最常用，可直接在页面上测试 API，支持 Try it out）
- 访问 `http://127.0.0.1:8000/redoc` → **ReDoc**（更美观的只读文档）

**如何让文档更好看、更专业？**

```python
app = FastAPI(
    title="我的 Todo API",
    description="这是一个使用 FastAPI + SQLAlchemy 搭建的任务管理系统",
    version="1.0.0",
    contact={
        "name": "Alyssa",
        "email": "your@email.com",
    },
    # 可以自定义路径
    # docs_url="/api/docs",
    # redoc_url="/api/redoc",
)

# 在路由上加 tags 和 description
@router.post("/tasks/", response_model=TaskResponse, tags=["tasks"])
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """创建新任务"""
    ...
```

**小技巧**：
- 在 Pydantic 模型的字段上加 `Field(description="...")`，文档里会自动显示。
- 用 `response_model` 指定返回的数据结构，文档会自动展示响应示例。
- 生产环境可以设置 `docs_url=None` 来关闭文档（防止别人看到你的接口）。




---

欢迎来到我的博客！🎉
