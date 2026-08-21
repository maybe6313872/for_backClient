# Redis 服务使用指南

## 简介

`RedisService` 是对 Redis 操作的封装，提供了更便捷的数据存储和读取方法，支持：
- 自动 JSON 序列化/反序列化
- 过期时间管理
- 字符串、哈希、集合、列表等数据结构
- 批量操作
- 键管理

## 快速开始

### 1. 导入服务

```python
from core.redis_service import get_redis_service

# 获取服务实例
redis_service = get_redis_service()
```

### 2. 基本使用

#### 字符串操作

```python
# 设置值（自动序列化复杂对象）
await redis_service.set("user:1:name", "张三")
await redis_service.set("user:1:data", {"id": 1, "name": "张三"}, expire=3600)

# 获取值（自动反序列化）
name = await redis_service.get("user:1:name")
user_data = await redis_service.get("user:1:data")  # 返回字典对象

# 检查是否存在
exists = await redis_service.exists("user:1:name")

# 删除
await redis_service.delete("user:1:name")
```

#### 哈希操作

```python
# 设置哈希字段
await redis_service.hset("user:1", "name", "张三")
await redis_service.hset("user:1", "profile", {"city": "北京", "age": 25})

# 批量设置
await redis_service.hmset("user:2", {
    "name": "李四",
    "email": "lisi@example.com",
    "age": 30
})

# 获取字段
name = await redis_service.hget("user:1", "name")
profile = await redis_service.hget("user:1", "profile")  # 自动反序列化

# 获取所有字段
user_info = await redis_service.hgetall("user:1")

# 检查字段是否存在
has_name = await redis_service.hexists("user:1", "name")

# 删除字段
await redis_service.hdel("user:1", "age")
```

#### 集合操作

```python
# 添加成员
await redis_service.sadd("tags", "python", "fastapi", "redis")

# 获取所有成员
tags = await redis_service.smembers("tags")

# 检查是否是成员
is_member = await redis_service.sismember("tags", "python")

# 获取集合大小
count = await redis_service.scard("tags")

# 移除成员
await redis_service.srem("tags", "python")
```

#### 列表操作

```python
# 从左侧推入
await redis_service.lpush("messages", "消息1", "消息2")

# 从右侧推入
await redis_service.rpush("messages", "消息3", "消息4")

# 获取列表范围
all_messages = await redis_service.lrange("messages", 0, -1)
first_5 = await redis_service.lrange("messages", 0, 4)

# 获取列表长度
length = await redis_service.llen("messages")
```

### 3. 过期时间管理

```python
# 设置值时指定过期时间（秒）
await redis_service.set("temp:data", "value", expire=60)

# 使用 timedelta
from datetime import timedelta
await redis_service.set("session:123", "data", expire=timedelta(hours=2))

# 单独设置过期时间
await redis_service.expire("key", 3600)
await redis_service.expire("key", timedelta(hours=1))

# 获取剩余过期时间
ttl = await redis_service.ttl("key")  # 返回剩余秒数，-1表示永不过期，-2表示不存在
```

### 4. 批量操作

```python
# 使用管道进行批量操作
pipe = await redis_service.pipeline()
pipe.set("key1", "value1")
pipe.set("key2", "value2")
pipe.hset("hash1", "field1", "value1")
await pipe.execute()
```

## 实际应用场景

### 场景1: 缓存用户信息

```python
# 存储用户信息，缓存1小时
user_info = {"id": 1, "name": "张三", "email": "zhangsan@example.com"}
await redis_service.set("cache:user:1", user_info, expire=3600)

# 读取缓存
cached_user = await redis_service.get("cache:user:1")
if cached_user:
    return cached_user
else:
    # 从数据库查询
    user = await get_user_from_db(1)
    await redis_service.set("cache:user:1", user, expire=3600)
    return user
```

### 场景2: 存储会话数据

```python
# 存储会话
session_data = {
    "user_id": 1,
    "login_time": "2024-01-01 10:00:00",
    "permissions": ["read", "write"]
}
await redis_service.hmset("session:abc123", session_data)
await redis_service.expire("session:abc123", 7200)  # 2小时后过期

# 读取会话
session = await redis_service.hgetall("session:abc123")
user_id = await redis_service.hget("session:abc123", "user_id")
```

### 场景3: 记录用户标签

```python
# 添加标签
await redis_service.sadd("user:1:tags", "VIP", "活跃用户", "付费用户")

# 检查标签
is_vip = await redis_service.sismember("user:1:tags", "VIP")

# 获取所有标签
tags = await redis_service.smembers("user:1:tags")
```

### 场景4: 消息队列

```python
# 发送消息
message = {"to": "user@example.com", "subject": "Hello", "body": "World"}
await redis_service.lpush("queue:emails", message)

# 处理消息（从右侧弹出）
# 注意：rpop 需要直接调用 redis 客户端
message = await redis_service.redis.rpop("queue:emails")
if message:
    message_data = json.loads(message)
    # 处理消息
```

### 场景5: 计数器

```python
# 使用 Redis 的 INCR 命令（需要直接调用 redis 客户端）
await redis_service.redis.incr("counter:views")
count = await redis_service.redis.get("counter:views")
```

## 在 FastAPI 路由中使用

```python
from fastapi import APIRouter, Depends
from core.redis_service import get_redis_service
from core.redis_service import RedisService

router = APIRouter()

@router.get("/cache/{key}")
async def get_cache(
    key: str,
    redis_service: RedisService = Depends(get_redis_service)
):
    """获取缓存数据"""
    value = await redis_service.get(key)
    if value is None:
        raise HTTPException(status_code=404, detail="缓存不存在")
    return {"key": key, "value": value}

@router.post("/cache/{key}")
async def set_cache(
    key: str,
    value: dict,
    expire: int = 3600,
    redis_service: RedisService = Depends(get_redis_service)
):
    """设置缓存数据"""
    await redis_service.set(key, value, expire=expire)
    return {"message": "缓存设置成功"}
```

## 注意事项

1. **自动序列化**: 复杂对象（字典、列表等）会自动序列化为 JSON，简单类型（str、int、float）不会序列化

2. **自动反序列化**: 读取时会尝试将 JSON 字符串反序列化为 Python 对象

3. **过期时间**: 
   - 可以传入整数（秒）或 `timedelta` 对象
   - 使用 `expire` 参数设置过期时间
   - 使用 `ttl()` 查询剩余时间

4. **性能优化**: 
   - 使用管道（pipeline）进行批量操作
   - 避免在生产环境使用 `keys()` 命令，使用 `scan()` 代替

5. **键命名规范**: 建议使用冒号分隔的层次结构，如 `user:1:profile`、`session:abc123`

## 高级用法

### 自定义 Redis 客户端

```python
from redis.asyncio import Redis
from core.redis_service import RedisService

# 创建自定义 Redis 客户端
custom_redis = Redis(host='localhost', port=6379, db=1)

# 使用自定义客户端创建服务
redis_service = RedisService(redis=custom_redis)
```

### 禁用自动序列化

```python
# 存储原始字符串，不序列化
await redis_service.set("key", "value", serialize=False)

# 读取时不反序列化
value = await redis_service.get("key", deserialize=False)
```

## 完整示例

参考 `core/redis_examples.py` 文件查看完整的使用示例。
