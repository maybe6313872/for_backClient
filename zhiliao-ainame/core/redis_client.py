"""
Redis 客户端配置模块

本模块提供了 Redis 客户端的创建和配置功能。
"""

from typing import Optional
from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool


# Redis 连接池（全局单例）
_redis_pool: Optional[ConnectionPool] = None
_redis_client: Optional[Redis] = None


def get_redis_client() -> Redis:
    """
    获取 Redis 客户端实例（单例模式）
    
    Returns:
        Redis: Redis 异步客户端实例
        
    Note:
        默认连接配置：
        - host: localhost
        - port: 6379
        - db: 0
        - decode_responses: True (自动解码响应为字符串)
    """
    global _redis_client, _redis_pool
    
    if _redis_client is None:
        # 创建连接池
        _redis_pool = ConnectionPool.from_url(
            "redis://localhost:6379/0",
            encoding="utf-8",
            decode_responses=True,
            max_connections=50
        )
        # 创建 Redis 客户端
        _redis_client = Redis(connection_pool=_redis_pool)
    
    return _redis_client


async def close_redis_client():
    """
    关闭 Redis 客户端和连接池
    
    应该在应用关闭时调用，清理资源。
    """
    global _redis_client, _redis_pool
    
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
    
    if _redis_pool:
        await _redis_pool.disconnect()
        _redis_pool = None
