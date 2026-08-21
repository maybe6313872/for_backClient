"""
SQLAlchemy 数据库模型初始化模块

本模块配置 SQLAlchemy 异步引擎和会话工厂，定义所有数据库模型的基类。
使用 aiomysql 作为异步 MySQL 驱动。

主要功能：
- 创建异步数据库引擎
- 配置连接池参数
- 定义数据库模型的基类
- 设置数据库命名约定
"""

# SQLAlchemy 异步引擎创建函数
# 用途：创建异步数据库引擎，用于管理数据库连接池和执行异步 SQL 操作
# 特点：支持异步 I/O，适合 FastAPI 等异步 Web 框架
from sqlalchemy.ext.asyncio import create_async_engine

# SQLAlchemy 会话工厂函数
# 用途：创建会话工厂，用于生成数据库会话实例
# 特点：可以配置会话的各种参数（自动刷新、过期策略等）
from sqlalchemy.orm import sessionmaker

# SQLAlchemy 异步会话类
# 用途：提供异步数据库会话，用于执行异步数据库操作（查询、插入、更新、删除）
# 特点：所有数据库操作都是异步的，不会阻塞事件循环
from sqlalchemy.ext.asyncio import AsyncSession

# SQLAlchemy 声明式基类
# 用途：所有数据库模型的基类，提供 ORM 映射功能
# 特点：使用声明式方式定义模型，自动处理表结构映射
from sqlalchemy.orm import DeclarativeBase

# SQLAlchemy 元数据类
# 用途：存储数据库表结构信息（表名、列名、约束等）
# 特点：用于定义数据库对象的命名约定，确保生成的 SQL 符合规范
from sqlalchemy import MetaData

from settings import DB_URI, DB_URI_TEST

# 处理数据库 URI（将 ainame:// 转换为 mysql+aiomysql://）
database_uri = DB_URI
if database_uri and database_uri.startswith("ainame://"):
    database_uri = database_uri.replace("ainame://", "mysql+aiomysql://")

# 创建异步数据库引擎
# 使用 aiomysql 驱动连接 MySQL 数据库
engine = create_async_engine(
    database_uri,                # 数据库连接 URI（从配置中读取）
    echo=True,                   # 将输出所有执行SQL的日志（默认是关闭的，开发时开启便于调试）
    pool_size=10,                # 连接池大小（默认是5个），保持10个连接
    max_overflow=20,             # 允许连接池最大的连接数（默认是10个），最多30个连接
    pool_timeout=10,             # 获得连接超时时间（默认是30s），10秒内获取不到连接则超时
    pool_recycle=3600,           # 连接回收时间（默认是-1，代表永不回收），1小时后回收连接
    pool_pre_ping=True,          # 连接前是否预检查（默认为False），确保连接有效
)

# 创建异步会话工厂
# 用于创建数据库会话实例
AsyncSessionFactory = sessionmaker(
    bind=engine,                 # Engine或者其子类对象（这里是AsyncEngine）
    class_=AsyncSession,          # Session类的代替（默认是Session类），使用异步会话
    autoflush=True,              # 是否在查找之前执行flush操作（默认是True），自动刷新
    expire_on_commit=False       # 是否在执行commit操作后Session就过期（默认是True），设为False保持对象可用
)

# 处理数据库 URI（将 ainame:// 转换为 mysql+aiomysql://）
database_uri2 = DB_URI_TEST
if database_uri2 and database_uri2.startswith("ainame://"):
    database_uri2 = database_uri2.replace("ainame://", "mysql+aiomysql://")

# 创建异步数据库引擎
# 使用 aiomysql 驱动连接 MySQL 数据库
engine2 = create_async_engine(
    database_uri2,                # 数据库连接 URI（从配置中读取）
    echo=True,                   # 将输出所有执行SQL的日志（默认是关闭的，开发时开启便于调试）
    pool_size=10,                # 连接池大小（默认是5个），保持10个连接
    max_overflow=20,             # 允许连接池最大的连接数（默认是10个），最多30个连接
    pool_timeout=10,             # 获得连接超时时间（默认是30s），10秒内获取不到连接则超时
    pool_recycle=3600,           # 连接回收时间（默认是-1，代表永不回收），1小时后回收连接
    pool_pre_ping=True,          # 连接前是否预检查（默认为False），确保连接有效
)

# 创建异步会话工厂
# 用于创建数据库会话实例
AsyncSessionFactoryTest = sessionmaker(
    bind=engine2,                 # Engine或者其子类对象（这里是AsyncEngine）
    class_=AsyncSession,          # Session类的代替（默认是Session类），使用异步会话
    autoflush=True,              # 是否在查找之前执行flush操作（默认是True），自动刷新
    expire_on_commit=False       # 是否在执行commit操作后Session就过期（默认是True），设为False保持对象可用
)


class Base(DeclarativeBase):
    """
    数据库模型基类
    
    所有数据库模型都应继承此类。
    定义了数据库对象的命名约定，确保生成的 SQL 语句符合规范。
    
    Attributes:
        metadata (MetaData): SQLAlchemy 元数据对象，包含命名约定规则
        
    Naming Conventions:
        - ix: 索引命名格式
        - uq: 唯一约束命名格式
        - ck: 检查约束命名格式
        - fk: 外键约束命名格式
        - pk: 主键约束命名格式
    """
    metadata = MetaData(naming_convention={
        "ix": 'ix_%(column_0_label)s',                                    # 索引命名：ix_列名
        "uq": "uq_%(table_name)s_%(column_0_name)s",                      # 唯一约束命名：uq_表名_列名
        "ck": "ck_%(table_name)s_%(constraint_name)s",                    # 检查约束命名：ck_表名_约束名
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",  # 外键命名：fk_表名_列名_引用表名
        "pk": "pk_%(table_name)s"                                          # 主键命名：pk_表名
    })


# 导入用户模型模块
# 确保所有模型都被注册到 Base.metadata 中
from . import user
# 导入文章模型模块
from . import art
# 导入学校相关模型模块
from .school import (
    School,
    Teacher,
    Student,
    Course,
    StudentCourse
)
# 导入学校相关模型模块
from .order import (
    Company,
    Order,
    Product,
    OrderProduct
)