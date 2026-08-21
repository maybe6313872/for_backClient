# Pydantic 详细介绍

## 目录
1. [什么是 Pydantic](#什么是-pydantic)
2. [核心作用](#核心作用)
3. [基本用法](#基本用法)
4. [高级特性](#高级特性)
5. [项目中的实际应用](#项目中的实际应用)
6. [最佳实践](#最佳实践)

---

## 什么是 Pydantic

**Pydantic** 是一个使用 Python 类型注解进行数据验证和设置管理的库。它通过 Python 的类型提示（Type Hints）来自动验证数据，确保数据的正确性和一致性。

### 核心特点
- ✅ **类型安全**：基于 Python 类型注解
- ✅ **自动验证**：自动验证数据类型和约束条件
- ✅ **易于使用**：简洁的 API，学习曲线平缓
- ✅ **性能优秀**：使用 Rust 编写的核心验证引擎（Pydantic v2）
- ✅ **与 FastAPI 完美集成**：FastAPI 的默认数据验证库

---

## 核心作用

### 1. **数据验证（Data Validation）**
自动验证输入数据是否符合预期的类型和约束条件。

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    age: int  # 必须是整数
    email: str  # 必须是字符串

# 自动验证
user = User(age=25, email="test@example.com")  # ✅ 正确
user = User(age="25", email="test@example.com")  # ✅ 自动转换 "25" -> 25
user = User(age="abc", email="test@example.com")  # ❌ 抛出 ValidationError
```

### 2. **数据序列化（Serialization）**
将 Python 对象转换为字典或 JSON 格式。

```python
user = User(age=25, email="test@example.com")
print(user.model_dump())  # {'age': 25, 'email': 'test@example.com'}
print(user.model_dump_json())  # '{"age":25,"email":"test@example.com"}'
```

### 3. **数据反序列化（Deserialization）**
将字典或 JSON 数据转换为 Python 对象。

```python
data = {"age": 25, "email": "test@example.com"}
user = User(**data)  # 从字典创建
user = User.model_validate_json('{"age":25,"email":"test@example.com"}')  # 从 JSON 创建
```

### 4. **API 文档生成**
与 FastAPI 配合，自动生成 OpenAPI/Swagger 文档。

---

## 基本用法

### 1. 定义模型（继承 BaseModel）

```python
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int
```

### 2. 创建实例

```python
# 方式1：直接传参
person = Person(name="张三", age=25)

# 方式2：从字典创建
data = {"name": "张三", "age": 25}
person = Person(**data)

# 方式3：从 JSON 创建
json_str = '{"name":"张三","age":25}'
person = Person.model_validate_json(json_str)
```

### 3. 访问数据

```python
person = Person(name="张三", age=25)
print(person.name)  # "张三"
print(person.age)   # 25
```

### 4. 转换为字典/JSON

```python
person = Person(name="张三", age=25)

# 转换为字典
print(person.model_dump())  # {'name': '张三', 'age': 25}

# 转换为 JSON 字符串
print(person.model_dump_json())  # '{"name":"张三","age":25}'
```

---

## 高级特性

### 1. 字段验证（Field）

使用 `Field` 添加验证规则和描述：

```python
from pydantic import BaseModel, Field
from typing import Annotated

class User(BaseModel):
    # 方式1：使用 Annotated（推荐，Python 3.9+）
    username: Annotated[
        str, 
        Field(min_length=3, max_length=20, description="用户名")
    ]
    
    # 方式2：直接使用 Field（旧方式，仍然支持）
    password: str = Field(min_length=6, max_length=20, description="密码")
    
    # 可选字段
    email: str | None = Field(default=None, description="邮箱")
```

**项目中的实际例子**（`schemas/user.py`）：
```python
UsernameStr = Annotated[
    str, 
    Field(min_length=3, max_length=20, description="用户名")
]

PasswordStr = Annotated[
    str, 
    Field(min_length=6, max_length=20, description="密码")
]

class RegisterIn(BaseModel):
    email: EmailStr
    username: UsernameStr  # 自动验证长度
    password: PasswordStr  # 自动验证长度
```

### 2. 特殊类型

#### EmailStr（邮箱验证）
```python
from pydantic import EmailStr

class User(BaseModel):
    email: EmailStr  # 自动验证邮箱格式

user = User(email="test@example.com")  # ✅ 正确
user = User(email="invalid-email")  # ❌ 抛出验证错误
```

#### Literal（字面量类型）
限制字段只能取特定的值：

```python
from typing import Literal

class NameIn(BaseModel):
    gender: Literal["不限", "男", "女"]  # 只能是这三个值之一
    length: Literal["不限", "单字", "两字"]
```

**项目中的实际例子**（`schemas/name.py`）：
```python
gender: Annotated[
    Literal["不限", "男", "女"], 
    Field(..., description="性别")
]
```

### 3. 嵌套模型

```python
class Address(BaseModel):
    city: str
    street: str

class Person(BaseModel):
    name: str
    address: Address  # 嵌套模型

person = Person(
    name="张三",
    address=Address(city="北京", street="长安街")
)
```

**项目中的实际例子**（`schemas/agent.py`）：
```python
class NameSchema(BaseModel):
    name: str
    reference: str
    moral: str

class NameResultSchema(BaseModel):
    names: List[NameSchema]  # 嵌套列表
```

### 4. 列表和可选字段

```python
from typing import List, Optional

class NameIn(BaseModel):
    exclude: List[str] = Field(default=[], description="排除的名字")
    other: str | None = Field(default="", description="其他要求")
```

### 5. 自定义验证器（Validators）

#### model_validator（模型级验证）
验证整个模型的数据：

```python
from pydantic import BaseModel, model_validator

class RegisterIn(BaseModel):
    password: str
    confirm_password: str
    
    @model_validator(mode="after")
    def password_is_match(self):
        """验证密码和确认密码是否一致"""
        if self.password != self.confirm_password:
            raise ValueError("两个密码不一致！")
        return self
```

**项目中的实际例子**（`schemas/user.py`）：
```python
class RegisterIn(BaseModel):
    password: PasswordStr
    confirm_password: PasswordStr
    
    @model_validator(mode="after")
    def password_is_math(self):
        if self.password != self.confirm_password:
            raise ValueError("两个密码不一致！")
        return self
```

#### field_validator（字段级验证）
验证单个字段：

```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    email: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('邮箱格式不正确')
        return v.lower()  # 转换为小写
```

### 6. 配置选项（Config）

```python
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    model_config = ConfigDict(
        # 禁止额外字段
        extra='forbid',
        # 使用枚举值而不是名称
        use_enum_values=True,
        # 验证赋值
        validate_assignment=True,
    )
    
    name: str
    age: int
```

---

## 项目中的实际应用

### 1. API 请求验证（Request Validation）

在 FastAPI 中，Pydantic 模型自动验证请求数据：

```python
# routers/auth_router.py
@router.post("/register")
async def register(data: RegisterIn):  # FastAPI 自动验证 RegisterIn
    # data 已经是验证过的 RegisterIn 实例
    email = data.email  # EmailStr，已验证格式
    username = data.username  # 已验证长度 3-20
    password = data.password  # 已验证长度 6-20
    # ...
```

**工作流程**：
1. 客户端发送 JSON 请求
2. FastAPI 自动将 JSON 转换为 `RegisterIn` 对象
3. Pydantic 验证数据（类型、长度、格式等）
4. 如果验证失败，自动返回 422 错误
5. 如果验证通过，路由函数接收到已验证的数据

### 2. API 响应序列化（Response Serialization）

```python
# routers/auth_router.py
@router.post('/login', response_model=LoginOut)
async def login(data: LoginIn):
    # ...
    return {
        "user": user,
        "token": tokens['access_token']
    }
    # FastAPI 自动将返回值序列化为 LoginOut 格式
```

**工作流程**：
1. 路由函数返回字典或对象
2. FastAPI 使用 `response_model=LoginOut` 验证和序列化
3. 自动转换为 JSON 响应
4. 只包含 `LoginOut` 中定义的字段

### 3. 数据模型定义（Schema Definition）

项目中定义了多个 Schema：

- **`schemas/user.py`**：用户相关的数据模型
  - `RegisterIn`：注册请求
  - `LoginIn`：登录请求
  - `UserSchema`：用户信息响应
  - `LoginOut`：登录响应

- **`schemas/name.py`**：起名相关的数据模型
  - `NameIn`：起名请求
  - `NameOut`：起名响应

- **`schemas/agent.py`**：AI 代理的数据模型
  - `NameSchema`：单个名字的结构
  - `NameResultSchema`：名字列表结构

### 4. 类型别名（Type Aliases）

使用 `Annotated` 创建可复用的类型别名：

```python
# schemas/user.py
UsernameStr = Annotated[
    str, 
    Field(min_length=3, max_length=20, description="用户名")
]

# 在多个模型中复用
class RegisterIn(BaseModel):
    username: UsernameStr  # 自动应用验证规则

class LoginIn(BaseModel):
    username: UsernameStr  # 同样的验证规则
```

---

## 最佳实践

### 1. 使用 Annotated 而不是直接 Field

**推荐**（Python 3.9+）：
```python
from typing import Annotated
from pydantic import Field

username: Annotated[str, Field(min_length=3, max_length=20)]
```

**不推荐**（旧方式）：
```python
username: str = Field(min_length=3, max_length=20)
```

### 2. 分离请求和响应模型

```python
# 请求模型：包含所有输入字段
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

# 响应模型：不包含敏感信息
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    # 不包含 password
```

### 3. 使用类型别名提高复用性

```python
# 定义可复用的类型
UsernameStr = Annotated[str, Field(min_length=3, max_length=20)]
PasswordStr = Annotated[str, Field(min_length=6, max_length=20)]

# 在多个模型中使用
class RegisterIn(BaseModel):
    username: UsernameStr
    password: PasswordStr

class LoginIn(BaseModel):
    username: UsernameStr
    password: PasswordStr
```

### 4. 添加详细的文档字符串

```python
class RegisterIn(BaseModel):
    """
    用户注册请求模型
    
    包含用户注册所需的所有信息。
    密码和确认密码必须一致。
    """
    email: EmailStr
    username: UsernameStr
    password: PasswordStr
```

### 5. 使用 Literal 限制选项

```python
# 明确限制可选值
gender: Literal["不限", "男", "女"]

# 而不是
gender: str  # 不够明确
```

### 6. 合理使用可选字段

```python
# 有默认值的可选字段
other: str | None = Field(default="", description="其他要求")

# 没有默认值的可选字段
optional_field: str | None = None
```

---

## 常见错误处理

### 1. ValidationError

当数据验证失败时，Pydantic 会抛出 `ValidationError`：

```python
from pydantic import ValidationError

try:
    user = User(age="abc")  # 不是整数
except ValidationError as e:
    print(e.errors())  # 查看所有错误
```

### 2. 在 FastAPI 中自动处理

FastAPI 会自动捕获 `ValidationError` 并返回 422 错误：

```json
{
  "detail": [
    {
      "loc": ["body", "age"],
      "msg": "value is not a valid integer",
      "type": "type_error.integer"
    }
  ]
}
```

---

## 总结

Pydantic 在你的项目中主要发挥以下作用：

1. ✅ **API 请求验证**：确保客户端发送的数据符合要求
2. ✅ **API 响应序列化**：确保返回的数据格式一致
3. ✅ **类型安全**：利用 Python 类型注解提高代码可读性和安全性
4. ✅ **自动文档生成**：与 FastAPI 配合生成 API 文档
5. ✅ **数据转换**：自动进行类型转换和验证

通过使用 Pydantic，你的 API 更加健壮、类型安全，并且减少了大量的手动验证代码！
