"""
Redis 服务封装模块

提供便捷的 Redis 数据操作封装，支持：
- 字符串、哈希、集合、列表等数据结构
- JSON 序列化/反序列化
- 过期时间管理
- 批量操作
- 键管理
"""

import json
from typing import Any, Optional, List, Dict, Union
from datetime import timedelta
from redis.asyncio import Redis
from core.redis_client import get_redis_client


class RedisService:
    """
    Redis 服务封装类
    
    提供便捷的 Redis 数据操作方法，简化常用操作。
    """
    
    def __init__(self, redis: Optional[Redis] = None):
        """
        初始化 Redis 服务
        
        Args:
            redis (Optional[Redis]): Redis 客户端实例，如果为 None 则使用默认客户端
        """
        self.redis = redis or get_redis_client()
    
    # ==================== 字符串操作 ====================
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[Union[int, timedelta]] = None,
        serialize: bool = True
    ) -> bool:
        """
        设置键值对
        
        Args:
            key (str): 键名
            value (Any): 值（如果是复杂对象会自动序列化为 JSON）
            expire (Optional[Union[int, timedelta]]): 过期时间（秒或 timedelta）
            serialize (bool): 是否自动序列化复杂对象为 JSON
            
        Returns:
            bool: 操作是否成功
        """
        # 序列化复杂对象
        if serialize and not isinstance(value, (str, int, float, bytes)):
            value = json.dumps(value, ensure_ascii=False)
        
        if expire:
            if isinstance(expire, timedelta):
                expire = int(expire.total_seconds())
            return await self.redis.setex(key, expire, value)
        else:
            return await self.redis.set(key, value)
    
    async def get(
        self, 
        key: str, 
        default: Any = None,
        deserialize: bool = True
    ) -> Any:
        """
        获取键值
        
        Args:
            key (str): 键名
            default (Any): 如果键不存在返回的默认值
            deserialize (bool): 是否自动反序列化 JSON 字符串
            
        Returns:
            Any: 键对应的值，如果不存在返回 default
        """
        value = await self.redis.get(key)
        if value is None:
            return default
        
        # 尝试反序列化 JSON
        if deserialize and isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                pass
        
        return value
    
    async def delete(self, *keys: str) -> int:
        """
        删除一个或多个键
        
        Args:
            *keys (str): 要删除的键名（可变参数）
            
        Returns:
            int: 删除的键数量
        """
        if not keys:
            return 0
        return await self.redis.delete(*keys)
    
    async def exists(self, key: str) -> bool:
        """
        检查键是否存在
        
        Args:
            key (str): 键名
            
        Returns:
            bool: 键是否存在
        """
        return bool(await self.redis.exists(key))
    
    async def expire(self, key: str, seconds: Union[int, timedelta]) -> bool:
        """
        设置键的过期时间
        
        Args:
            key (str): 键名
            seconds (Union[int, timedelta]): 过期时间（秒或 timedelta）
            
        Returns:
            bool: 操作是否成功
        """
        if isinstance(seconds, timedelta):
            seconds = int(seconds.total_seconds())
        return await self.redis.expire(key, seconds)
    
    async def ttl(self, key: str) -> int:
        """
        获取键的剩余过期时间
        
        Args:
            key (str): 键名
            
        Returns:
            int: 剩余秒数，-1 表示永不过期，-2 表示键不存在
        """
        return await self.redis.ttl(key)
    
    # ==================== 哈希操作 ====================
    
    async def hset(self, key: str, field: str, value: Any, serialize: bool = True) -> int:
        """
        设置哈希字段值
        
        Args:
            key (str): 哈希键名
            field (str): 字段名
            value (Any): 字段值（复杂对象会自动序列化）
            serialize (bool): 是否自动序列化
            
        Returns:
            int: 新增字段数量（0 表示更新，1 表示新增）
        """
        if serialize and not isinstance(value, (str, int, float, bytes)):
            value = json.dumps(value, ensure_ascii=False)
        return await self.redis.hset(key, field, value)
    
    async def hget(self, key: str, field: str, default: Any = None, deserialize: bool = True) -> Any:
        """
        获取哈希字段值
        
        Args:
            key (str): 哈希键名
            field (str): 字段名
            default (Any): 默认值
            deserialize (bool): 是否自动反序列化
            
        Returns:
            Any: 字段值
        """
        value = await self.redis.hget(key, field)
        if value is None:
            return default
        
        if deserialize and isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                pass
        
        return value
    
    async def hgetall(self, key: str, deserialize: bool = True) -> Dict[str, Any]:
        """
        获取哈希所有字段和值
        
        Args:
            key (str): 哈希键名
            deserialize (bool): 是否自动反序列化值
            
        Returns:
            Dict[str, Any]: 字段和值的字典
        """
        data = await self.redis.hgetall(key)
        if not data:
            return {}
        
        if deserialize:
            result = {}
            for k, v in data.items():
                if isinstance(v, str):
                    try:
                        result[k] = json.loads(v)
                    except (json.JSONDecodeError, TypeError):
                        result[k] = v
                else:
                    result[k] = v
            return result
        
        return data
    
    async def hmset(self, key: str, mapping: Dict[str, Any], serialize: bool = True) -> bool:
        """
        批量设置哈希字段
        
        Args:
            key (str): 哈希键名
            mapping (Dict[str, Any]): 字段和值的字典
            serialize (bool): 是否自动序列化值
            
        Returns:
            bool: 操作是否成功
        """
        if serialize:
            mapping = {
                k: json.dumps(v, ensure_ascii=False) if not isinstance(v, (str, int, float, bytes)) else v
                for k, v in mapping.items()
            }
        return await self.redis.hmset(key, mapping)
    
    async def hdel(self, key: str, *fields: str) -> int:
        """
        删除哈希字段
        
        Args:
            key (str): 哈希键名
            *fields (str): 要删除的字段名（可变参数）
            
        Returns:
            int: 删除的字段数量
        """
        if not fields:
            return 0
        return await self.redis.hdel(key, *fields)
    
    async def hexists(self, key: str, field: str) -> bool:
        """
        检查哈希字段是否存在
        
        Args:
            key (str): 哈希键名
            field (str): 字段名
            
        Returns:
            bool: 字段是否存在
        """
        return bool(await self.redis.hexists(key, field))
    
    # ==================== 集合操作 ====================
    
    async def sadd(self, key: str, *values: Any) -> int:
        """
        向集合添加成员
        
        Args:
            key (str): 集合键名
            *values (Any): 要添加的值（可变参数）
            
        Returns:
            int: 新增成员数量
        """
        if not values:
            return 0
        # 确保所有值都是字符串
        str_values = [str(v) for v in values]
        return await self.redis.sadd(key, *str_values)
    
    async def smembers(self, key: str) -> set:
        """
        获取集合所有成员
        
        Args:
            key (str): 集合键名
            
        Returns:
            set: 成员集合
        """
        return await self.redis.smembers(key)
    
    async def sismember(self, key: str, value: Any) -> bool:
        """
        检查值是否是集合成员
        
        Args:
            key (str): 集合键名
            value (Any): 要检查的值
            
        Returns:
            bool: 是否是成员
        """
        return bool(await self.redis.sismember(key, str(value)))
    
    async def srem(self, key: str, *values: Any) -> int:
        """
        从集合移除成员
        
        Args:
            key (str): 集合键名
            *values (Any): 要移除的值（可变参数）
            
        Returns:
            int: 移除的成员数量
        """
        if not values:
            return 0
        str_values = [str(v) for v in values]
        return await self.redis.srem(key, *str_values)
    
    async def scard(self, key: str) -> int:
        """
        获取集合成员数量
        
        Args:
            key (str): 集合键名
            
        Returns:
            int: 成员数量
        """
        return await self.redis.scard(key)
    
    # ==================== 列表操作 ====================
    
    async def lpush(self, key: str, *values: Any) -> int:
        """
        从列表左侧推入元素
        
        Args:
            key (str): 列表键名
            *values (Any): 要推入的值（可变参数）
            
        Returns:
            int: 推入后列表长度
        """
        if not values:
            return 0
        str_values = [json.dumps(v, ensure_ascii=False) if not isinstance(v, (str, int, float, bytes)) else str(v) 
                     for v in values]
        return await self.redis.lpush(key, *str_values)
    
    async def rpush(self, key: str, *values: Any) -> int:
        """
        从列表右侧推入元素
        
        Args:
            key (str): 列表键名
            *values (Any): 要推入的值（可变参数）
            
        Returns:
            int: 推入后列表长度
        """
        if not values:
            return 0
        str_values = [json.dumps(v, ensure_ascii=False) if not isinstance(v, (str, int, float, bytes)) else str(v) 
                     for v in values]
        return await self.redis.rpush(key, *str_values)
    
    async def lrange(self, key: str, start: int = 0, end: int = -1, deserialize: bool = True) -> List[Any]:
        """
        获取列表指定范围元素
        
        Args:
            key (str): 列表键名
            start (int): 起始索引
            end (int): 结束索引（-1 表示到末尾）
            deserialize (bool): 是否自动反序列化
            
        Returns:
            List[Any]: 元素列表
        """
        values = await self.redis.lrange(key, start, end)
        if not values:
            return []
        
        if deserialize:
            result = []
            for v in values:
                if isinstance(v, str):
                    try:
                        result.append(json.loads(v))
                    except (json.JSONDecodeError, TypeError):
                        result.append(v)
                else:
                    result.append(v)
            return result
        
        return list(values)
    
    async def llen(self, key: str) -> int:
        """
        获取列表长度
        
        Args:
            key (str): 列表键名
            
        Returns:
            int: 列表长度
        """
        return await self.redis.llen(key)
    
    # ==================== 批量操作 ====================
    
    async def pipeline(self):
        """
        创建管道对象，用于批量操作
        
        Returns:
            Pipeline: Redis 管道对象
            
        Example:
            pipe = await redis_service.pipeline()
            pipe.set("key1", "value1")
            pipe.set("key2", "value2")
            await pipe.execute()
        """
        return self.redis.pipeline()
    
    # ==================== 键模式操作 ====================
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """
        查找匹配模式的键
        
        Args:
            pattern (str): 匹配模式（支持通配符 * 和 ?）
            
        Returns:
            List[str]: 匹配的键列表
            
        Warning:
            在生产环境中慎用，如果键数量很大可能影响性能
        """
        return list(await self.redis.keys(pattern))
    
    async def scan(self, cursor: int = 0, match: Optional[str] = None, count: int = 10):
        """
        增量迭代键（推荐用于生产环境）
        
        Args:
            cursor (int): 游标，从 0 开始
            match (Optional[str]): 匹配模式
            count (int): 每次返回的键数量
            
        Returns:
            tuple: (新游标, 键列表)
        """
        return await self.redis.scan(cursor=cursor, match=match, count=count)


# 创建全局单例实例
_redis_service: Optional[RedisService] = None


def get_redis_service(redis: Optional[Redis] = None) -> RedisService:
    """
    获取 Redis 服务实例（单例模式）
    
    Args:
        redis (Optional[Redis]): Redis 客户端实例，如果为 None 则使用默认客户端
        
    Returns:
        RedisService: Redis 服务实例
    """
    global _redis_service
    if _redis_service is None or redis is not None:
        _redis_service = RedisService(redis)
    return _redis_service


async def get_redis_service_dependency() -> RedisService:
    """
    获取 Redis 服务实例（用于 FastAPI 依赖注入）
    
    这是一个专门用于 FastAPI Depends() 的函数，不接受任何参数，
    避免 FastAPI 解析依赖时出现类型错误。
    
    Returns:
        RedisService: Redis 服务实例
    """
    return get_redis_service()
