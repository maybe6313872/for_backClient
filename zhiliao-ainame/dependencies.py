"""
FastAPI 依赖注入模块

本模块定义了 FastAPI 应用中使用的依赖项，包括数据库会话和邮件服务的依赖注入函数。
这些函数会被 FastAPI 自动调用，用于在请求处理过程中提供必要的服务实例。
"""

from core.mail import create_mail_instance
from fastapi_mail import FastMail
from sqlalchemy.ext.asyncio import AsyncSession
from models import AsyncSessionFactory, AsyncSessionFactoryTest
from core.redis_client import get_redis_client
from redis.asyncio import Redis


async def get_session() -> AsyncSession:
    """
    获取数据库会话的依赖注入函数
    
    这是一个异步生成器函数，用于在请求处理过程中提供数据库会话。
    使用 yield 确保会话在使用完毕后能够正确关闭，即使发生异常也能正常清理资源。
    
    Yields:
        AsyncSession: SQLAlchemy 异步数据库会话对象
        
    Note:
        此函数使用上下文管理器模式，确保数据库连接在使用后自动关闭。
        每个请求都会创建一个新的会话实例。
    """
    # 创建数据库会话
    session = AsyncSessionFactory()
    try:
        # 将会话提供给请求处理函数使用
        yield session
    finally:
        # 无论是否发生异常，都确保关闭会话
        await session.close()

async def get_session_test() -> AsyncSession:
    """
    获取数据库会话的依赖注入函数
    
    这是一个异步生成器函数，用于在请求处理过程中提供数据库会话。
    使用 yield 确保会话在使用完毕后能够正确关闭，即使发生异常也能正常清理资源。
    
    Yields:
        AsyncSession: SQLAlchemy 异步数据库会话对象
        
    Note:
        此函数使用上下文管理器模式，确保数据库连接在使用后自动关闭。
        每个请求都会创建一个新的会话实例。
    """
    # 创建数据库会话
    session = AsyncSessionFactoryTest()
    try:
        # 将会话提供给请求处理函数使用
        yield session
    finally:
        # 无论是否发生异常，都确保关闭会话
        await session.close()


async def get_mail() -> FastMail:
    """
    获取邮件服务实例的依赖注入函数
    
    返回一个 FastMail 实例，用于发送邮件。
    每次调用都会创建一个新的邮件服务实例，确保线程/协程安全。
    
    Returns:
        FastMail: 配置好的邮件服务实例
        
    Note:
        邮件服务实例是每次请求时创建的，这样可以避免多线程/协程环境下的冲突。
    """
    return create_mail_instance()


async def get_redis() -> Redis:
    """
    获取 Redis 客户端实例的依赖注入函数
    
    返回 Redis 异步客户端实例，用于 Redis 操作。
    使用单例模式，所有请求共享同一个 Redis 连接池。
    
    Returns:
        Redis: Redis 异步客户端实例
        
    Note:
        Redis 客户端使用连接池管理，适合高并发场景。
    """
    return get_redis_client()