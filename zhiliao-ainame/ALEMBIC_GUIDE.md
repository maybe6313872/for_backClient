# Alembic 数据库迁移工作原理详解

## 目录
1. [什么是 Alembic](#什么是-alembic)
2. [核心概念](#核心概念)
3. [工作原理](#工作原理)
4. [迁移文件结构](#迁移文件结构)
5. [项目中的配置](#项目中的配置)
6. [完整工作流程](#完整工作流程)
7. [常用命令](#常用命令)
8. [最佳实践](#最佳实践)

---

## 什么是 Alembic

**Alembic** 是 SQLAlchemy 的作者编写的数据库迁移工具。它用于管理数据库模式（Schema）的版本控制，类似于 Git 对代码的版本控制。

### 核心特点
- ✅ **版本控制**：跟踪数据库结构的变化历史
- ✅ **自动生成**：可以从 SQLAlchemy 模型自动生成迁移脚本
- ✅ **可逆操作**：支持升级（upgrade）和降级（downgrade）
- ✅ **多数据库支持**：支持 MySQL、PostgreSQL、SQLite 等
- ✅ **增量迁移**：只应用未执行的迁移

### 为什么需要数据库迁移？

在没有迁移工具之前：
- ❌ 数据库结构变化难以追踪
- ❌ 团队协作困难（每个人的数据库结构不一致）
- ❌ 无法回滚错误的数据库更改
- ❌ 生产环境部署困难

使用 Alembic 后：
- ✅ 数据库结构变化有历史记录
- ✅ 团队成员数据库结构一致
- ✅ 可以回滚到任意版本
- ✅ 生产环境部署变得简单可靠

---

## 核心概念

### 1. **迁移（Migration）**

迁移是一个 Python 文件，描述如何将数据库从一个版本升级到另一个版本。

### 2. **版本（Revision）**

每个迁移都有一个唯一的版本标识符（Revision ID），用于标识迁移的顺序。

### 3. **版本表（alembic_version）**

Alembic 在数据库中创建一个 `alembic_version` 表，记录当前数据库的版本号。

```sql
CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL PRIMARY KEY
);
```

### 4. **元数据（Metadata）**

SQLAlchemy 的 `Base.metadata` 包含了所有模型的定义（表、列、约束等）。Alembic 通过比较元数据来检测模型变化。

---

## 工作原理

### 流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                        1. 定义模型                                │
│                                                                   │
│  models/user.py                                                  │
│  ┌─────────────────────────────────────┐                        │
│  │ class User(Base):                   │                        │
│  │     __tablename__ = 'user'          │                        │
│  │     id: Mapped[int] = ...           │                        │
│  │     email: Mapped[str] = ...        │                        │
│  └─────────────────────────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  2. 注册模型到 Base.metadata                      │
│                                                                   │
│  models/__init__.py                                              │
│  ┌─────────────────────────────────────┐                        │
│  │ from . import user                  │                        │
│  │                                     │                        │
│  │ Base.metadata 现在包含:              │                        │
│  │ - user 表定义                       │                        │
│  │ - email_code 表定义                 │                        │
│  └─────────────────────────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              3. 运行 alembic revision --autogenerate             │
│                                                                   │
│  Alembic 执行以下步骤:                                            │
│                                                                   │
│  a) 读取 Base.metadata（当前模型状态）                            │
│  b) 连接数据库，读取现有表结构（数据库当前状态）                   │
│  c) 比较两者差异                                                   │
│  d) 生成迁移脚本（upgrade 和 downgrade 函数）                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    4. 生成迁移文件                                 │
│                                                                   │
│  alembic/versions/08369504438d_add_user_email_code_model.py      │
│  ┌─────────────────────────────────────┐                        │
│  │ def upgrade():                      │                        │
│  │     op.create_table('user', ...)    │                        │
│  │                                     │                        │
│  │ def downgrade():                    │                        │
│  │     op.drop_table('user')           │                        │
│  └─────────────────────────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                5. 运行 alembic upgrade head                      │
│                                                                   │
│  Alembic 执行以下步骤:                                            │
│                                                                   │
│  a) 检查 alembic_version 表，获取当前版本                         │
│  b) 读取所有迁移文件，构建版本链                                  │
│  c) 找出需要应用的迁移（当前版本到 head 之间的所有迁移）          │
│  d) 按顺序执行每个迁移的 upgrade() 函数                           │
│  e) 更新 alembic_version 表为最新版本                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    6. 数据库结构更新                               │
│                                                                   │
│  数据库现在包含:                                                  │
│  - user 表                                                        │
│  - email_code 表                                                  │
│  - alembic_version 表（版本号: 08369504438d）                     │
└─────────────────────────────────────────────────────────────────┘
```

### 详细工作流程

#### 步骤 1：模型定义

在 `models/user.py` 中定义数据库模型：

```python
from . import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, String

class User(Base):
    __tablename__ = 'user'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    username: Mapped[str] = mapped_column(String(100))
```

#### 步骤 2：元数据收集

在 `models/__init__.py` 中导入所有模型：

```python
from . import user  # 导入模型，注册到 Base.metadata
```

当导入 `user` 模块时，`User` 类的定义会执行，`__tablename__` 和列定义会被添加到 `Base.metadata` 中。

**项目中的实际例子**（`models/__init__.py`）：
```python
class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={...})

# 导入用户模型模块
# 确保所有模型都被注册到 Base.metadata 中
from . import user
```

#### 步骤 3：连接配置（env.py）

Alembic 通过 `env.py` 连接数据库和获取模型元数据：

**项目中的实际例子**（`alembic/env.py`）：
```python
import settings
from models import Base

# 获取数据库连接 URL
database_url = settings.DB_URI
config.set_main_option("sqlalchemy.url", database_url)

# 设置目标元数据（用于 autogenerate）
target_metadata = Base.metadata
```

关键点：
- `sqlalchemy.url`：数据库连接字符串
- `target_metadata`：SQLAlchemy 模型的元数据对象

#### 步骤 4：自动生成迁移

运行命令：
```bash
alembic revision --autogenerate -m "add user email_code model"
```

Alembic 内部执行过程：

1. **读取当前模型状态**：
   ```python
   # Alembic 从 env.py 获取
   target_metadata = Base.metadata
   # 现在包含所有模型的定义
   ```

2. **读取数据库当前状态**：
   ```python
   # Alembic 连接到数据库，执行类似以下的 SQL
   SHOW TABLES;
   DESCRIBE user;  # 如果有的话
   ```

3. **比较差异**：
   ```python
   # Alembic 比较：
   # - target_metadata 中的表（模型定义的）
   # - 数据库中的实际表
   # 找出差异：
   # - 新增的表
   # - 新增的列
   # - 修改的列
   # - 删除的列/表
   ```

4. **生成迁移脚本**：
   根据差异生成 `upgrade()` 和 `downgrade()` 函数

#### 步骤 5：应用迁移

运行命令：
```bash
alembic upgrade head
```

Alembic 内部执行过程：

1. **检查当前版本**：
   ```sql
   SELECT version_num FROM alembic_version;
   -- 返回当前版本号，例如：空（首次）或 '08369504438d'
   ```

2. **读取迁移文件**：
   ```python
   # Alembic 扫描 alembic/versions/ 目录
   # 读取所有迁移文件，解析 revision 和 down_revision
   # 构建版本链：
   # None -> 08369504438d -> ...
   ```

3. **确定需要应用的迁移**：
   ```python
   # 如果当前版本是 None（首次）
   # 需要应用：08369504438d
   # 
   # 如果当前版本是 08369504438d
   # 需要应用：空（已经是最新版本）
   ```

4. **执行迁移**：
   ```python
   # 对于每个需要应用的迁移：
   # 1. 执行 upgrade() 函数
   # 2. 更新 alembic_version 表
   
   # 例如执行 08369504438d 的 upgrade()：
   op.create_table('email_code', ...)
   op.create_table('user', ...)
   
   # 然后更新版本：
   UPDATE alembic_version SET version_num = '08369504438d';
   ```

5. **事务管理**：
   每个迁移都在一个事务中执行，如果失败会自动回滚。

---

## 迁移文件结构

### 迁移文件组成

**项目中的实际例子**（`alembic/versions/08369504438d_add_user_email_code_model.py`）：

```python
"""add user email_code model

Revision ID: 08369504438d
Revises: 
Create Date: 2025-12-02 13:30:23.386242

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# 1. 版本标识符（唯一）
revision: str = '08369504438d'

# 2. 前一个版本（版本链）
down_revision: Union[str, Sequence[str], None] = None  # None 表示这是第一个迁移

# 3. 分支标签（用于分支迁移）
branch_labels: Union[str, Sequence[str], None] = None

# 4. 依赖关系
depends_on: Union[str, Sequence[str], None] = None

# 5. 升级函数（应用迁移时执行）
def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('email_code',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('created_time', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_email_code'))
    )
    op.create_table('user',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('_password', sa.String(length=200), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_user')),
        sa.UniqueConstraint('email', name=op.f('uq_user_email'))
    )

# 6. 降级函数（回滚迁移时执行）
def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('user')
    op.drop_table('email_code')
```

### 关键组成部分说明

#### 1. **revision（版本标识符）**

```python
revision: str = '08369504438d'
```

- 每个迁移的唯一标识符
- 通常是随机生成的哈希值
- 用于标识和追踪迁移

#### 2. **down_revision（前一个版本）**

```python
down_revision: Union[str, Sequence[str], None] = None
```

- 指向当前迁移的前一个迁移
- `None` 表示这是第一个迁移（基础迁移）
- 用于构建版本链

**版本链示例**：
```
None -> 08369504438d -> abc123def456 -> xyz789ghi012
       (第一个)        (第二个)        (第三个)
```

#### 3. **upgrade() 函数**

```python
def upgrade() -> None:
    """将数据库从旧版本升级到新版本"""
    op.create_table('user', ...)
    op.add_column('user', sa.Column('age', sa.Integer()))
```

**常用的 Alembic 操作（op）**：
- `op.create_table()` - 创建表
- `op.drop_table()` - 删除表
- `op.add_column()` - 添加列
- `op.drop_column()` - 删除列
- `op.alter_column()` - 修改列
- `op.create_index()` - 创建索引
- `op.drop_index()` - 删除索引
- `op.create_foreign_key()` - 创建外键
- `op.drop_constraint()` - 删除约束

#### 4. **downgrade() 函数**

```python
def downgrade() -> None:
    """将数据库从新版本降级到旧版本"""
    op.drop_table('user')
```

- 与 `upgrade()` 相反的操作
- 用于回滚迁移

---

## 项目中的配置

### 1. alembic.ini 配置

**项目中的实际例子**（`alembic.ini`）：

```ini
[alembic]
# 迁移脚本的位置
script_location = %(here)s/alembic

# 预添加到 sys.path 的路径
prepend_sys_path = .

# 路径分隔符
path_separator = os
```

关键配置：
- `script_location`：迁移脚本目录
- `prepend_sys_path`：Python 模块搜索路径

### 2. env.py 配置

**项目中的实际例子**（`alembic/env.py`）：

```python
import settings
from models import Base

# 1. 获取数据库连接 URL
database_url = settings.DB_URI
config.set_main_option("sqlalchemy.url", database_url)

# 2. 设置目标元数据（用于 autogenerate）
target_metadata = Base.metadata

# 3. 定义在线迁移函数（连接数据库执行）
def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())

async def run_async_migrations() -> None:
    connectable = async_engine_from_config(...)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

# 4. 定义离线迁移函数（生成 SQL 脚本）
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()
```

关键点：
- **在线模式（Online）**：直接连接数据库执行迁移
- **离线模式（Offline）**：生成 SQL 脚本，不连接数据库

---

## 完整工作流程

### 场景：添加一个新模型

假设我们要添加一个 `Article` 模型：

#### 步骤 1：定义模型

```python
# models/article.py
from . import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, String, Text, DateTime
from datetime import datetime

class Article(Base):
    __tablename__ = 'article'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
```

#### 步骤 2：注册模型

```python
# models/__init__.py
from . import user
from . import article  # 新增
```

#### 步骤 3：生成迁移

```bash
alembic revision --autogenerate -m "add article model"
```

Alembic 会：
1. 读取 `Base.metadata`，发现新的 `article` 表
2. 连接数据库，检查是否有 `article` 表（没有）
3. 生成迁移文件：

```python
def upgrade() -> None:
    op.create_table('article',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_article'))
    )

def downgrade() -> None:
    op.drop_table('article')
```

#### 步骤 4：检查迁移文件

```python
# alembic/versions/xxx_add_article_model.py
revision: str = 'abc123def456'
down_revision: str = '08369504438d'  # 指向之前的迁移
```

版本链现在变成：
```
None -> 08369504438d -> abc123def456
```

#### 步骤 5：应用迁移

```bash
alembic upgrade head
```

执行过程：
1. 检查 `alembic_version` 表：当前版本是 `08369504438d`
2. 需要应用的迁移：`abc123def456`
3. 执行 `abc123def456` 的 `upgrade()` 函数
4. 更新 `alembic_version` 表为 `abc123def456`

#### 步骤 6：验证

```bash
# 查看当前版本
alembic current

# 查看迁移历史
alembic history

# 查看待应用的迁移
alembic heads
```

---

## 常用命令

### 1. 初始化 Alembic（首次使用）

```bash
alembic init alembic
```

### 2. 生成迁移文件

```bash
# 自动生成（推荐）
alembic revision --autogenerate -m "描述信息"

# 手动创建空迁移文件
alembic revision -m "描述信息"
```

### 3. 应用迁移

```bash
# 升级到最新版本
alembic upgrade head

# 升级到指定版本
alembic upgrade 08369504438d

# 升级一个版本
alembic upgrade +1

# 升级多个版本
alembic upgrade +2
```

### 4. 回滚迁移

```bash
# 回滚到上一个版本
alembic downgrade -1

# 回滚到指定版本
alembic downgrade 08369504438d

# 回滚到基础版本（删除所有表）
alembic downgrade base
```

### 5. 查看状态

```bash
# 查看当前数据库版本
alembic current

# 查看迁移历史
alembic history

# 查看待应用的迁移
alembic heads

# 查看迁移历史（详细信息）
alembic history --verbose
```

### 6. 生成 SQL 脚本（不执行）

```bash
# 离线模式，生成 SQL 脚本
alembic upgrade head --sql

# 生成特定版本的 SQL
alembic upgrade 08369504438d --sql
```

### 7. 合并迁移（解决分支）

```bash
# 如果有多个分支，合并它们
alembic merge -m "merge branches" branch1 branch2
```

---

## 最佳实践

### 1. 总是使用 autogenerate

**推荐**：
```bash
alembic revision --autogenerate -m "描述"
```

**不推荐**：手动编写迁移文件（容易出错）

### 2. 检查生成的迁移文件

自动生成的迁移可能不完美，需要人工检查：

```python
def upgrade() -> None:
    # 检查是否合理
    op.add_column('user', sa.Column('age', sa.Integer()))
    # 如果 age 应该有默认值，手动添加：
    # op.add_column('user', sa.Column('age', sa.Integer(), server_default='0'))
```

### 3. 编写清晰的迁移描述

```bash
# 好的描述
alembic revision --autogenerate -m "add user email_code model"
alembic revision --autogenerate -m "add index on user email"
alembic revision --autogenerate -m "change user password to nullable"

# 不好的描述
alembic revision --autogenerate -m "update"
alembic revision --autogenerate -m "fix"
```

### 4. 不要修改已应用的迁移

**重要**：如果迁移已经应用到生产环境，不要修改它！

应该创建新的迁移来修复问题：

```bash
# 错误的做法：修改已应用的迁移文件
# 正确的做法：创建新迁移
alembic revision --autogenerate -m "fix user email constraint"
```

### 5. 在迁移中添加数据迁移

有时需要迁移数据而不仅仅是结构：

```python
def upgrade() -> None:
    # 结构迁移
    op.add_column('user', sa.Column('full_name', sa.String(200)))
    
    # 数据迁移
    connection = op.get_bind()
    connection.execute(
        sa.text("UPDATE user SET full_name = CONCAT(first_name, ' ', last_name)")
    )
```

### 6. 测试迁移的降级

确保 `downgrade()` 函数正确工作：

```bash
# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1

# 再次应用
alembic upgrade head
```

### 7. 在团队中共享迁移文件

迁移文件应该提交到版本控制系统（Git）：

```bash
git add alembic/versions/
git commit -m "add migration: add article model"
```

### 8. 生产环境部署流程

```bash
# 1. 备份数据库
mysqldump -u user -p database > backup.sql

# 2. 检查当前版本
alembic current

# 3. 查看待应用的迁移
alembic heads

# 4. 生成 SQL 脚本（可选，用于审查）
alembic upgrade head --sql > migration.sql

# 5. 应用迁移
alembic upgrade head

# 6. 验证
alembic current
```

### 9. 处理大型迁移

对于大型迁移（如添加索引、修改大量数据），考虑：

- 分批处理
- 在低峰期执行
- 使用事务确保一致性
- 监控执行时间

### 10. 使用离线模式审查

在应用迁移前，使用离线模式生成 SQL 审查：

```bash
alembic upgrade head --sql
```

这样可以：
- 审查将执行的 SQL 语句
- 确认迁移逻辑正确
- 在生产环境应用前发现问题

---

## 常见问题

### 1. autogenerate 没有检测到变化

**原因**：
- 模型没有被导入到 `Base.metadata`
- `env.py` 中的 `target_metadata` 设置不正确

**解决方法**：
```python
# models/__init__.py
from . import user  # 确保导入所有模型

# alembic/env.py
from models import Base
target_metadata = Base.metadata  # 确保设置正确
```

### 2. 迁移冲突（多个分支）

**原因**：
- 团队成员同时创建了迁移
- 导致版本链分叉

**解决方法**：
```bash
# 合并分支
alembic merge -m "merge branches" branch1 branch2
```

### 3. 迁移失败后的恢复

**原因**：
- 迁移执行过程中出错
- 数据库处于不一致状态

**解决方法**：
```bash
# 1. 检查当前状态
alembic current

# 2. 手动修复数据库（如果必要）

# 3. 手动更新版本表（如果迁移部分完成）
# UPDATE alembic_version SET version_num = 'previous_version';

# 4. 重新应用迁移
alembic upgrade head
```

### 4. 如何删除一个迁移？

**注意**：如果迁移已应用到生产环境，不应该删除！

如果迁移还未应用：

```bash
# 1. 删除迁移文件
rm alembic/versions/xxx_migration.py

# 2. 检查版本链是否完整
alembic history
```

---

## 总结

Alembic 的工作原理可以概括为：

1. **模型定义**：在 Python 代码中定义 SQLAlchemy 模型
2. **元数据收集**：所有模型注册到 `Base.metadata`
3. **差异检测**：比较模型元数据和数据库实际结构
4. **迁移生成**：根据差异生成升级和降级脚本
5. **版本管理**：在数据库的 `alembic_version` 表中记录当前版本
6. **迁移应用**：按版本链顺序执行迁移脚本

### 关键优势

- ✅ **自动化**：从模型自动生成迁移
- ✅ **版本控制**：追踪数据库结构变化历史
- ✅ **可逆性**：支持升级和降级
- ✅ **团队协作**：确保团队成员数据库一致
- ✅ **生产部署**：简化生产环境数据库更新流程

通过使用 Alembic，数据库迁移变得可控、可追踪、可回滚，大大提高了开发效率和代码质量！
