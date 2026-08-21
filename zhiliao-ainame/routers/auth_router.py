"""
用户认证相关路由模块

本模块提供了用户注册、登录和邮箱验证码相关的 API 端点。
包括：
- 获取邮箱验证码
- 用户注册
- 用户登录
"""

from fastapi import APIRouter, Query, Depends, HTTPException
from pydantic import EmailStr
from typing import Annotated
from dependencies import get_mail, get_session
from fastapi_mail import FastMail, MessageSchema, MessageType
from models import AsyncSession
import string
import random
from aiosmtplib import SMTPResponseException
from repository.user_repo import EmailCodeRepository, User, UserRepository
from schemas import ResponseOut
from schemas.user import RegisterIn, UserCreateSchema, LoginIn, LoginOut
from core.auth import AuthHandler


# 创建认证相关的路由组
# prefix: 所有路由的前缀为 /auth
# tags: 在 Swagger 文档中分组为 "user"
router = APIRouter(prefix="/auth", tags=["user"])

# 创建认证处理器实例（单例模式）
auth_handler = AuthHandler()


@router.get("/code", response_model=ResponseOut, summary="获取邮箱验证码", description="发送4位数字验证码到指定邮箱")
async def get_email_code(
    email: Annotated[EmailStr, Query(..., description="邮箱地址")],
    mail: FastMail = Depends(get_mail),
    session: AsyncSession = Depends(get_session),
):
    """
    获取邮箱验证码接口
    
    生成一个4位数字的验证码，并通过邮件发送给用户。
    验证码会存储到数据库中，有效期为10分钟。
    
    Args:
        email (EmailStr): 接收验证码的邮箱地址（通过查询参数传入）
        mail (FastMail): 邮件服务实例（通过依赖注入获取）
        session (AsyncSession): 数据库会话（通过依赖注入获取）
        
    Returns:
        ResponseOut: 操作结果响应对象
        
    Raises:
        HTTPException: 当邮件发送失败时返回 500 错误
        
    Note:
        - 验证码为4位随机数字
        - 验证码有效期为10分钟
        - QQ 邮箱在 SMTP 关闭阶段可能返回非标准响应，但邮件已成功发送
    """
    # 1. 生成4位数字的验证码
    # 使用 string.digits (0-9) 重复4次，然后随机选择4个字符
    source = string.digits * 4
    code = "".join(random.sample(source, 4))
    
    # 2. 创建邮件消息对象
    message = MessageSchema(
        subject="【知了课堂】注册验证码",
        recipients=[email],
        body=f"您的验证码为：{code}，五分钟有效！",
        subtype=MessageType.plain  # 纯文本格式
    )
    
    # 创建验证码仓库实例
    email_code_repo = EmailCodeRepository(session=session)
    
    try:
        # 发送邮件
        await mail.send_message(message)
        # 邮件发送成功，将邮箱和验证码存储到数据库中
        await email_code_repo.create(str(email), code)
        # 提交事务
        await session.commit()
    except SMTPResponseException as e:
        # QQ 邮箱在 SMTP 关闭阶段会返回非标准响应，但邮件已成功发送
        # 这里特殊处理，避免误报错误
        if e.code == -1 and b"\\x00\\x00\\x00" in str(e).encode():
            print("⚠️ 忽略 QQ 邮箱 SMTP 关闭阶段的非标准响应（邮件已成功发送）")
            # 将邮箱和验证码存储到数据库中
            await email_code_repo.create(str(email), code)
            # 提交事务
            await session.commit()
        else:
            # 其他错误则回滚事务并抛出异常
            await session.rollback()
            raise HTTPException(500, detail="邮件发送失败！")
    except Exception as e:
        # 其他异常，回滚事务
        await session.rollback()
        raise HTTPException(500, detail=f"操作失败：{str(e)}")
    
    return ResponseOut()


@router.post("/register", response_model=ResponseOut, summary="用户注册", description="使用邮箱、用户名、密码和验证码进行注册")
async def register(
    data: RegisterIn,
    session: AsyncSession = Depends(get_session),
):
    """
    用户注册接口
    
    验证用户提供的注册信息（邮箱、用户名、密码、验证码），
    如果验证通过则创建新用户账户。
    
    Args:
        data (RegisterIn): 注册信息，包括：
            - email: 邮箱地址
            - username: 用户名（3-20个字符）
            - password: 密码（6-20个字符）
            - confirm_password: 确认密码（必须与 password 一致）
            - code: 邮箱验证码（4位数字）
        session (AsyncSession): 数据库会话（通过依赖注入获取）
        
    Returns:
        ResponseOut: 操作结果响应对象
        
    Raises:
        HTTPException: 
            - 400: 邮箱已存在或验证码错误
            - 500: 用户创建失败
            
    Note:
        - 注册前会检查邮箱是否已存在
        - 验证码必须在10分钟内有效
        - 密码会自动加密存储
    """
    # 创建用户仓库实例
    user_repo = UserRepository(session=session)
    
    # 1. 判断邮箱是否已存在
    email_exist = await user_repo.email_is_exist(email=str(data.email))
    if email_exist:
        raise HTTPException(400, detail="该邮箱已经存在！")
    
    # 2. 校验验证码是否正确
    email_code_repo = EmailCodeRepository(session=session)
    email_code_match = email_code_repo.check_email_code(
        email=str(data.email), 
        code=str(data.code)
    )
    if not email_code_match:
        raise HTTPException(400, detail='邮箱或验证码错误！')
    
    # 3. 创建新用户
    try:
        await user_repo.create(UserCreateSchema(
            email=str(data.email), 
            password=data.password, 
            username=data.username
        ))
        # 提交事务
        await session.commit()
    except Exception as e:
        # 捕获所有异常，回滚事务并返回服务器错误
        await session.rollback()
        raise HTTPException(500, detail=str(e))
    
    return ResponseOut()


@router.post('/login', response_model=LoginOut, summary="用户登录", description="使用邮箱和密码登录，返回用户信息和访问令牌")
async def login(
    data: LoginIn,
    session: AsyncSession = Depends(get_session),
):
    """
    用户登录接口
    
    验证用户的邮箱和密码，如果验证通过则返回用户信息和 JWT 访问令牌。
    
    Args:
        data (LoginIn): 登录信息，包括：
            - email: 邮箱地址
            - password: 密码
        session (AsyncSession): 数据库会话（通过依赖注入获取）
        
    Returns:
        LoginOut: 包含用户信息和访问令牌的响应对象：
            - user: 用户信息（id, email, username）
            - token: JWT 访问令牌（用于后续 API 请求的身份验证）
            
    Raises:
        HTTPException:
            - 400: 用户不存在或密码错误
            
    Note:
        - 访问令牌有效期为15天
        - 令牌需要放在请求头的 Authorization 字段中：Bearer {token}
        - 密码验证使用 Argon2 加密算法
    """
    # 1. 创建用户仓库实例
    user_repo = UserRepository(session=session)
    
    # 2. 根据邮箱查找用户
    user: User | None = await user_repo.get_by_email(str(data.email))
    if not user:
        raise HTTPException(400, detail="该用户不存在！")
    
    # 3. 验证密码
    if not user.check_password(data.password):
        raise HTTPException(400, detail="邮箱或密码错误！")
    
    # 4. 生成 JWT 令牌（包括访问令牌和刷新令牌）
    tokens = auth_handler.encode_login_token(user.id)
    
    # 5. 返回用户信息和访问令牌
    return {
        "user": user,
        "token": tokens['access_token']
    }