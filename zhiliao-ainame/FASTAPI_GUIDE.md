# FastAPI 详细介绍

## 目录
1. [什么是 FastAPI](#什么是-fastapi)
2. [核心特性](#核心特性)
3. [基本 API 使用](#基本-api-使用)
4. [路由系统](#路由系统)
5. [依赖注入（Dependency Injection）](#依赖注入dependency-injection)
6. [请求和响应处理](#请求和响应处理)
7. [中间件和异常处理](#中间件和异常处理)
8. [应用场景](#应用场景)
9. [项目中的实际应用](#项目中的实际应用)
10. [最佳实践](#最佳实践)

---

## 什么是 FastAPI

**FastAPI** 是一个现代、快速（高性能）的 Web 框架，用于构建基于 Python 的 API。它基于标准 Python 类型提示，使用 Pydantic 进行数据验证，并自动生成交互式 API 文档。

### 核心特点
- ⚡ **高性能**：与 NodeJS 和 Go 相当，是 Python 框架中最快的之一
- 🚀 **快速开发**：开发速度提升约 200% 到 300%
- 📝 **自动文档**：自动生成交互式 API 文档（Swagger UI 和 ReDoc）
- 🔒 **类型安全**：基于 Python 类型提示，减少错误
- ✅ **数据验证**：使用 Pydantic 自动验证请求和响应数据
- 🔄 **异步支持**：原生支持异步/等待（async/await）
- 📦 **标准兼容**：基于（并完全兼容）OpenAPI 和 JSON Schema

---

## 核心特性

### 1. 自动 API 文档生成

FastAPI 自动生成两种交互式 API 文档：

- **Swagger UI**：访问 `/docs`（默认路径）
- **ReDoc**：访问 `/redoc`（默认路径）

**项目中的配置**（`main.py`）：
```python
app = FastAPI(
    title="知了AI起名 API",
    description="一个基于AI的起名服务API",
    version="1.0.0",
    docs_url="/docs",          # Swagger UI 文档路径
    redoc_url="/redoc",        # ReDoc 文档路径
    openapi_url="/openapi.json"  # OpenAPI JSON 规范路径
)
```

### 2. 基于类型提示的数据验证

FastAPI 使用 Python 类型提示和 Pydantic 自动验证请求数据：

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.post("/items/")
async def create_item(item: Item):  # 自动验证 item 数据
    return item
```

### 3. 异步支持

FastAPI 原生支持异步操作，可以处理大量并发请求：

```python
@app.get("/")
async def read_root():  # 使用 async/await
    return {"message": "Hello World"}
```

### 4. 高性能

FastAPI 基于 Starlette 和 Pydantic，性能优异：
- 比 Flask 快约 2-3 倍
- 与 NodeJS 和 Go 相当
- 支持异步操作，可以处理大量并发

---

## 基本 API 使用

### 1. 创建 FastAPI 应用

```python
from fastapi import FastAPI

app = FastAPI(
    title="我的 API",
    description="API 描述",
    version="1.0.0"
)
```

**项目中的实际例子**（`main.py`）：
```python
app = FastAPI(
    title="知了AI起名 API",
    description="一个基于AI的起名服务API，提供用户注册、登录和智能起名功能",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)
```

### 2. 定义路由端点

#### GET 请求

```python
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
```

**项目中的实际例子**（`main.py`）：
```python
@app.get("/")
async def root():
    """根路径端点，用于测试 API 服务是否正常运行"""
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    """根据传入的名字参数返回个性化的问候消息"""
    return {"message": f"Hello {name}"}
```

#### POST 请求

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float

@app.post("/items/")
async def create_item(item: Item):
    return item
```

**项目中的实际例子**（`routers/auth_router.py`）：
```python
@router.post("/register", response_model=ResponseOut)
async def register(data: RegisterIn):
    # 处理注册逻辑
    return ResponseOut()
```

#### PUT、DELETE 等请求

```python
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}

@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    return {"message": f"Item {item_id} deleted"}
```

### 3. 路径参数

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):  # 自动转换为 int 类型
    return {"user_id": user_id}
```

### 4. 查询参数

```python
@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}
```

**项目中的实际例子**（`routers/auth_router.py`）：
```python
@router.get("/code")
async def get_email_code(
    email: Annotated[EmailStr, Query(..., description="邮箱地址")]
):
    # 处理验证码逻辑
    pass
```

### 5. 请求体（Request Body）

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str

@app.post("/users/")
async def create_user(user: User):
    return user
```

**项目中的实际例子**（`routers/auth_router.py`）：
```python
@router.post("/register")
async def register(data: RegisterIn):  # RegisterIn 是 Pydantic 模型
    # data 已经自动验证
    email = data.email
    username = data.username
    # ...
```

### 6. 响应模型（Response Model）

```python
class UserOut(BaseModel):
    id: int
    name: str
    email: str

@app.post("/users/", response_model=UserOut)
async def create_user(user: UserIn):
    # 返回的数据会自动转换为 UserOut 格式
    return {"id": 1, "name": user.name, "email": user.email}
```

**项目中的实际例子**（`routers/auth_router.py`）：
```python
@router.post('/login', response_model=LoginOut)
async def login(data: LoginIn):
    # 返回的数据会自动序列化为 LoginOut 格式
    return {
        "user": user,
        "token": tokens['access_token']
    }
```

---

## 路由系统

### 1. 使用 APIRouter 组织路由

将相关的路由组织到不同的模块中：

```python
from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login")
async def login():
    pass

@router.post("/register")
async def register():
    pass
```

**项目中的实际例子**（`routers/auth_router.py`）：
```python
router = APIRouter(prefix="/auth", tags=["user"])

@router.get("/code")
async def get_email_code(...):
    pass

@router.post("/register")
async def register(...):
    pass

@router.post('/login')
async def login(...):
    pass
```

### 2. 注册路由到主应用

```python
from routers.auth_router import router as auth_router

app.include_router(auth_router)
```

**项目中的实际例子**（`main.py`）：
```python
from routers.auth_router import router as auth_router
from routers.name_router import router as name_router

app.include_router(auth_router)
app.include_router(name_router)
```

### 3. 路由标签（Tags）

用于在 API 文档中分组：

```python
router = APIRouter(prefix="/auth", tags=["user"])
```

### 4. 路由前缀（Prefix）

为所有路由添加统一前缀：

```python
router = APIRouter(prefix="/api/v1")
```

---

## 依赖注入（Dependency Injection）

FastAPI 的依赖注入系统非常强大，可以用于：
- 共享数据库连接
- 身份验证
- 权限检查
- 共享业务逻辑

### 1. 基本依赖注入

```python
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/")
async def get_users(db = Depends(get_db)):
    # 使用 db
    pass
```

**项目中的实际例子**（`dependencies.py`）：
```python
async def get_session() -> AsyncSession:
    """获取数据库会话的依赖注入函数"""
    session = AsyncSessionFactory()
    try:
        yield session
    finally:
        await session.close()

# 在路由中使用
@router.post("/register")
async def register(
    data: RegisterIn,
    session: AsyncSession = Depends(get_session)
):
    # 使用 session 访问数据库
    pass
```

### 2. 依赖链（Dependency Chains）

依赖可以依赖其他依赖：

```python
def get_db():
    pass

def get_user(db = Depends(get_db)):
    pass

@app.get("/items/")
async def get_items(user = Depends(get_user)):
    pass
```

**项目中的实际例子**（`routers/name_router.py`）：
```python
@router.post("/")
async def take_names(
    data: NameIn,
    user_id: int = Depends(auth_handler.auth_access_dependency)
):
    # auth_access_dependency 内部会验证 JWT 令牌
    # 并返回用户 ID
    pass
```

### 3. 类作为依赖

```python
class AuthHandler:
    def verify_token(self, token: str):
        pass

auth_handler = AuthHandler()

def get_current_user(token: str = Depends(oauth2_scheme)):
    return auth_handler.verify_token(token)
```

**项目中的实际例子**（`routers/name_router.py`）：
```python
auth_handler = AuthHandler()

@router.post("/")
async def take_names(
    user_id: int = Depends(auth_handler.auth_access_dependency)
):
    # auth_handler.auth_access_dependency 是一个方法
    # 用于验证 JWT 令牌并返回用户 ID
    pass
```

---

## 请求和响应处理

### 1. 请求验证

FastAPI 使用 Pydantic 自动验证请求数据：

```python
from pydantic import BaseModel, EmailStr

class RegisterIn(BaseModel):
    email: EmailStr
    username: str
    password: str

@app.post("/register")
async def register(data: RegisterIn):
    # data 已经自动验证
    # 如果验证失败，FastAPI 自动返回 422 错误
    pass
```

### 2. 响应序列化

使用 `response_model` 指定响应格式：

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get("/users/{user_id}", response_model=UserOut)
async def get_user(user_id: int):
    return {"id": user_id, "name": "John"}
```

### 3. 状态码

```python
from fastapi import status

@app.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserIn):
    return user
```

### 4. 异常处理

```python
from fastapi import HTTPException

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    return users[user_id]
```

**项目中的实际例子**（`routers/auth_router.py`）：
```python
@router.post("/register")
async def register(data: RegisterIn, session: AsyncSession = Depends(get_session)):
    email_exist = await user_repo.email_is_exist(email=str(data.email))
    if email_exist:
        raise HTTPException(400, detail="该邮箱已经存在！")
    
    email_code_match = email_code_repo.check_email_code(...)
    if not email_code_match:
        raise HTTPException(400, detail='邮箱或验证码错误！')
```

### 5. 响应头

```python
from fastapi import Response

@app.get("/")
async def root(response: Response):
    response.headers["X-Custom-Header"] = "custom-value"
    return {"message": "Hello World"}
```

---

## 中间件和异常处理

### 1. 添加中间件

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. 自定义中间件

```python
from fastapi import Request
import time

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### 3. 全局异常处理

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"message": str(exc)}
    )
```

---

## 应用场景

### 1. RESTful API 开发

FastAPI 非常适合构建 RESTful API：

- ✅ 自动生成 API 文档
- ✅ 数据验证和序列化
- ✅ 类型安全
- ✅ 高性能

**适用场景**：
- 后端 API 服务
- 微服务架构
- 移动应用后端
- 前端应用后端

### 2. 实时应用

FastAPI 支持 WebSocket，适合实时应用：

```python
from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
```

**适用场景**：
- 实时聊天应用
- 实时数据推送
- 在线游戏
- 实时协作工具

### 3. 数据科学和机器学习 API

FastAPI 适合部署机器学习模型：

```python
import pickle

model = pickle.load(open("model.pkl", "rb"))

@app.post("/predict")
async def predict(data: PredictionInput):
    result = model.predict(data.features)
    return {"prediction": result}
```

**适用场景**：
- 机器学习模型服务
- 数据分析和处理 API
- AI 服务接口

### 4. 企业级应用

FastAPI 适合构建企业级应用：

- ✅ 安全性（OAuth2、JWT）
- ✅ 依赖注入
- ✅ 中间件支持
- ✅ 异步支持

**适用场景**：
- 企业内部系统
- SaaS 应用
- 电商平台
- 内容管理系统

### 5. 微服务架构

FastAPI 轻量级，适合微服务：

- ✅ 快速启动
- ✅ 低资源消耗
- ✅ 易于部署
- ✅ 服务间通信

**适用场景**：
- 微服务架构
- 容器化部署（Docker、Kubernetes）
- 云原生应用

---

## 项目中的实际应用

### 1. 应用初始化（`main.py`）

```python
app = FastAPI(
    title="知了AI起名 API",
    description="一个基于AI的起名服务API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 注册路由
app.include_router(auth_router)
app.include_router(name_router)
```

### 2. 路由组织

**认证路由**（`routers/auth_router.py`）：
```python
router = APIRouter(prefix="/auth", tags=["user"])

@router.get("/code")  # GET /auth/code
async def get_email_code(...):
    pass

@router.post("/register")  # POST /auth/register
async def register(...):
    pass

@router.post("/login")  # POST /auth/login
async def login(...):
    pass
```

**起名路由**（`routers/name_router.py`）：
```python
router = APIRouter(prefix="/name", tags=["name"])

@router.post("/")  # POST /name/
async def take_names(...):
    pass
```

### 3. 依赖注入使用

**数据库会话依赖**（`dependencies.py`）：
```python
async def get_session() -> AsyncSession:
    session = AsyncSessionFactory()
    try:
        yield session
    finally:
        await session.close()

# 在路由中使用
@router.post("/register")
async def register(
    data: RegisterIn,
    session: AsyncSession = Depends(get_session)
):
    # 使用 session 访问数据库
    pass
```

**认证依赖**（`routers/name_router.py`）：
```python
@router.post("/")
async def take_names(
    data: NameIn,
    user_id: int = Depends(auth_handler.auth_access_dependency)
):
    # auth_access_dependency 验证 JWT 令牌
    # 如果验证失败，自动返回 401 错误
    # 如果验证成功，返回用户 ID
    pass
```

### 4. 请求和响应模型

**请求模型**：
```python
@router.post("/register")
async def register(data: RegisterIn):  # 自动验证
    # data.email 是 EmailStr，已验证格式
    # data.username 已验证长度 3-20
    # data.password 已验证长度 6-20
    pass
```

**响应模型**：
```python
@router.post('/login', response_model=LoginOut)
async def login(data: LoginIn):
    return {
        "user": user,
        "token": tokens['access_token']
    }
    # 自动序列化为 LoginOut 格式
```

### 5. 异常处理

```python
@router.post("/register")
async def register(data: RegisterIn, session: AsyncSession = Depends(get_session)):
    email_exist = await user_repo.email_is_exist(email=str(data.email))
    if email_exist:
        raise HTTPException(400, detail="该邮箱已经存在！")
    
    email_code_match = email_code_repo.check_email_code(...)
    if not email_code_match:
        raise HTTPException(400, detail='邮箱或验证码错误！')
```

---

## 最佳实践

### 1. 使用路由模块组织代码

**推荐**：
```python
# routers/auth_router.py
router = APIRouter(prefix="/auth", tags=["user"])

# main.py
app.include_router(auth_router)
```

**不推荐**：把所有路由写在 `main.py` 中

### 2. 分离请求和响应模型

**推荐**：
```python
class UserCreate(BaseModel):  # 请求模型
    email: EmailStr
    username: str
    password: str

class UserResponse(BaseModel):  # 响应模型
    id: int
    email: EmailStr
    username: str
    # 不包含 password

@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate):
    pass
```

### 3. 使用依赖注入管理资源

**推荐**：
```python
async def get_session() -> AsyncSession:
    session = AsyncSessionFactory()
    try:
        yield session
    finally:
        await session.close()
```

### 4. 使用类型提示

**推荐**：
```python
@app.get("/users/{user_id}")
async def get_user(user_id: int) -> UserResponse:
    pass
```

### 5. 添加详细的文档字符串

**推荐**：
```python
@router.post("/register", summary="用户注册", description="使用邮箱、用户名、密码和验证码进行注册")
async def register(data: RegisterIn):
    """
    用户注册接口
    
    验证用户提供的注册信息，如果验证通过则创建新用户账户。
    """
    pass
```

### 6. 使用适当的 HTTP 状态码

```python
from fastapi import status

@app.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserIn):
    pass

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    pass
```

### 7. 使用环境变量管理配置

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 8. 使用异步操作提高性能

**推荐**：
```python
@app.get("/users/")
async def get_users(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User))
    return result.scalars().all()
```

### 9. 添加 CORS 中间件（如果需要）

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 10. 使用路由标签组织 API 文档

```python
router = APIRouter(prefix="/auth", tags=["user"])
router = APIRouter(prefix="/name", tags=["name"])
```

---

## 总结

FastAPI 在你的项目中主要发挥以下作用：

1. ✅ **API 框架**：提供完整的 Web API 开发框架
2. ✅ **自动文档**：自动生成 Swagger UI 和 ReDoc 文档
3. ✅ **数据验证**：与 Pydantic 配合，自动验证请求和响应数据
4. ✅ **依赖注入**：管理数据库会话、认证等依赖
5. ✅ **路由组织**：使用 APIRouter 模块化组织路由
6. ✅ **异步支持**：支持异步操作，提高性能
7. ✅ **类型安全**：基于 Python 类型提示，提高代码质量

通过使用 FastAPI，你的 API 更加健壮、类型安全，并且具有自动生成的交互式文档，大大提高了开发效率和代码质量！

---

## 快速参考

### 启动应用

```bash
uvicorn main:app --reload
```

### 访问文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

### 常用装饰器

```python
@app.get("/")      # GET 请求
@app.post("/")     # POST 请求
@app.put("/")      # PUT 请求
@app.delete("/")   # DELETE 请求
@app.patch("/")    # PATCH 请求
```

### 常用依赖

```python
from fastapi import Depends, Query, Path, Header, Cookie

@app.get("/items/")
async def read_items(
    q: str = Query(..., description="查询参数"),
    item_id: int = Path(..., description="路径参数"),
    user_agent: str = Header(..., description="请求头"),
    session_id: str = Cookie(..., description="Cookie")
):
    pass
```
