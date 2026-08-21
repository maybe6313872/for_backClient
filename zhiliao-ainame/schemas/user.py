"""
用户相关的数据模型模块

本模块定义了用户注册、登录等操作使用的 Pydantic 数据模型。
用于 API 请求和响应的数据验证和序列化。
"""

from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Annotated

from models.user import User

# 用户名类型别名：3-20个字符
UsernameStr = Annotated[
    str, 
    Field(min_length=3, max_length=20, description="用户名")
]

# 密码类型别名：6-20个字符
PasswordStr = Annotated[
    str, 
    Field(min_length=6, max_length=20, description="密码")
]


class RegisterIn(BaseModel):
    """
    用户注册请求模型
    
    包含用户注册所需的所有信息。
    密码和确认密码必须一致。
    
    Attributes:
        email (EmailStr): 用户邮箱地址（必须符合邮箱格式）
        username (UsernameStr): 用户名（3-20个字符）
        password (PasswordStr): 密码（6-20个字符）
        confirm_password (PasswordStr): 确认密码（必须与 password 一致）
        code (str): 邮箱验证码（4位数字）
        
    Validators:
        password_is_math: 验证密码和确认密码是否一致
        
    Raises:
        ValueError: 当密码和确认密码不一致时
    """
    email: EmailStr
    username: UsernameStr
    password: PasswordStr
    confirm_password: PasswordStr
    code: Annotated[
        str, 
        Field(min_length=4, max_length=4, description="邮箱验证码")
    ]

    @model_validator(mode="after")
    def password_is_math(self):
        """
        验证密码和确认密码是否一致
        
        Returns:
            self: 验证通过返回自身
            
        Raises:
            ValueError: 密码不一致时抛出异常
        """
        if self.password != self.confirm_password:
            raise ValueError("两个密码不一致！")
        return self


class UserCreateSchema(BaseModel):
    """
    用户创建数据模型
    
    用于创建新用户时的数据传递。
    不包含确认密码和验证码，这些在注册接口中验证。
    
    Attributes:
        email (EmailStr): 用户邮箱地址
        username (UsernameStr): 用户名（3-20个字符）
        password (PasswordStr): 密码（6-20个字符，明文，会在模型中加密）
    """
    email: EmailStr
    username: UsernameStr
    password: PasswordStr


class LoginIn(BaseModel):
    """
    用户登录请求模型
    
    包含用户登录所需的信息。
    
    Attributes:
        email (EmailStr): 用户邮箱地址
        password (PasswordStr): 用户密码（明文）
    """
    email: EmailStr
    password: PasswordStr


class UserSchema(BaseModel):
    """
    用户信息响应模型
    
    用于返回用户的基本信息，不包含敏感信息（如密码）。
    
    Attributes:
        id (int): 用户唯一标识符
        email (EmailStr): 用户邮箱地址
        username (UsernameStr): 用户名
    """
    id: Annotated[int, Field(...)]
    email: EmailStr
    username: UsernameStr


class LoginOut(BaseModel):
    """
    用户登录响应模型
    
    包含登录成功后的用户信息和访问令牌。
    
    Attributes:
        user (UserSchema): 用户基本信息
        token (str): JWT 访问令牌，用于后续 API 请求的身份验证
        
    Note:
        - token 需要放在请求头的 Authorization 字段中
        - 格式：Authorization: Bearer {token}
        - 访问令牌有效期为15天
    """
    user: UserSchema
    token: str