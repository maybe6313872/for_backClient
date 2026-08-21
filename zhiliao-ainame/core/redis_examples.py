"""
Redis 服务使用示例

展示如何使用 RedisService 进行各种数据操作
"""

from core.redis_service import get_redis_service
from datetime import timedelta


async def example_usage():
    """使用示例"""
    redis_service = get_redis_service()
    
    # ==================== 字符串操作 ====================
    
    # 设置简单值
    await redis_service.set("user:1:name", "张三")
    
    # 设置带过期时间的值
    await redis_service.set("session:abc123", "user_id_123", expire=3600)  # 1小时后过期
    await redis_service.set("token:xyz", "token_value", expire=timedelta(hours=2))  # 2小时后过期
    
    # 设置复杂对象（自动序列化为 JSON）
    user_data = {"id": 1, "name": "张三", "email": "zhangsan@example.com"}
    await redis_service.set("user:1:data", user_data)
    
    # 获取值
    name = await redis_service.get("user:1:name")
    user_data = await redis_service.get("user:1:data")  # 自动反序列化
    
    # 检查键是否存在
    exists = await redis_service.exists("user:1:name")
    
    # 删除键
    await redis_service.delete("user:1:name")
    
    # ==================== 哈希操作 ====================
    
    # 设置哈希字段
    await redis_service.hset("user:1", "name", "张三")
    await redis_service.hset("user:1", "age", 25)
    await redis_service.hset("user:1", "profile", {"city": "北京", "job": "工程师"})  # 自动序列化
    
    # 批量设置哈希字段
    await redis_service.hmset("user:2", {
        "name": "李四",
        "age": 30,
        "email": "lisi@example.com"
    })
    
    # 获取哈希字段
    name = await redis_service.hget("user:1", "name")
    profile = await redis_service.hget("user:1", "profile")  # 自动反序列化
    
    # 获取所有哈希字段
    user_info = await redis_service.hgetall("user:1")
    
    # 检查哈希字段是否存在
    has_name = await redis_service.hexists("user:1", "name")
    
    # 删除哈希字段
    await redis_service.hdel("user:1", "age")
    
    # ==================== 集合操作 ====================
    
    # 添加集合成员
    await redis_service.sadd("tags", "python", "fastapi", "redis")
    
    # 获取集合所有成员
    tags = await redis_service.smembers("tags")
    
    # 检查是否是集合成员
    is_member = await redis_service.sismember("tags", "python")
    
    # 获取集合大小
    count = await redis_service.scard("tags")
    
    # 移除集合成员
    await redis_service.srem("tags", "python")
    
    # ==================== 列表操作 ====================
    
    # 从左侧推入
    await redis_service.lpush("messages", "消息1", "消息2")
    
    # 从右侧推入
    await redis_service.rpush("messages", "消息3", "消息4")
    
    # 获取列表范围
    messages = await redis_service.lrange("messages", 0, -1)  # 获取所有
    first_5 = await redis_service.lrange("messages", 0, 4)  # 获取前5个
    
    # 获取列表长度
    length = await redis_service.llen("messages")
    
    # ==================== 批量操作 ====================
    
    # 使用管道进行批量操作
    pipe = await redis_service.pipeline()
    pipe.set("key1", "value1")
    pipe.set("key2", "value2")
    pipe.hset("hash1", "field1", "value1")
    await pipe.execute()
    
    # ==================== 过期时间管理 ====================
    
    # 设置过期时间
    await redis_service.set("temp:data", "value", expire=60)  # 60秒后过期
    
    # 获取剩余过期时间
    ttl = await redis_service.ttl("temp:data")  # 返回剩余秒数
    
    # 延长过期时间
    await redis_service.expire("temp:data", 120)  # 延长到120秒
    await redis_service.expire("temp:data", timedelta(minutes=5))  # 延长到5分钟
    
    # ==================== 实际应用场景 ====================
    
    # 场景1: 缓存用户信息
    user_info = {"id": 1, "name": "张三", "email": "zhangsan@example.com"}
    await redis_service.set("cache:user:1", user_info, expire=3600)  # 缓存1小时
    
    # 场景2: 存储会话数据
    session_data = {"user_id": 1, "login_time": "2024-01-01 10:00:00"}
    await redis_service.hmset("session:abc123", session_data)
    await redis_service.expire("session:abc123", 7200)  # 2小时后过期
    
    # 场景3: 记录用户标签
    await redis_service.sadd("user:1:tags", "VIP", "活跃用户", "付费用户")
    
    # 场景4: 消息队列
    await redis_service.lpush("queue:emails", {"to": "user@example.com", "subject": "Hello"})
    # 处理消息时从右侧弹出
    # message = await redis_service.rpop("queue:emails")
    
    # 场景5: 计数器
    await redis_service.set("counter:views", 0)
    # 使用 Redis 的 INCR 命令（需要直接调用 redis 客户端）
    # await redis_service.redis.incr("counter:views")
