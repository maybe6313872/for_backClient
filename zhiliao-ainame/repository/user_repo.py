"""
用户数据仓库模块

本模块提供了用户和邮箱验证码的数据访问层（Repository Pattern）。
封装了所有与用户和验证码相关的数据库操作。

使用异步 SQLAlchemy 进行数据库操作，确保高性能和并发安全。
"""

from models import AsyncSession
from models.user import EmailCode
from sqlalchemy import select, exists
from datetime import datetime, timedelta
from models.user import User
from schemas.user import UserCreateSchema


class UserRepository:
    """
    用户数据仓库类
    
    提供用户相关的数据库操作方法。
    所有方法都是异步的，使用 SQLAlchemy 异步会话。
    
    Attributes:
        session (AsyncSession): SQLAlchemy 异步数据库会话
    """
    
    def __init__(self, session: AsyncSession):
        """
        初始化用户仓库
        
        Args:
            session (AsyncSession): 数据库会话实例
        """
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        """
        根据邮箱查找用户
        
        在数据库中查找指定邮箱的用户。
        
        Args:
            email (str): 用户邮箱地址
            
        Returns:
            User | None: 找到的用户对象，如果不存在则返回 None
        """
        # 查询操作不需要显式事务
        user = await self.session.scalar(
            select(User).where(User.email == email)
        )
        return user

    async def email_is_exist(self, email: str) -> bool:
        """
        检查邮箱是否已存在
        
        使用 exists() 子查询高效检查邮箱是否已被注册。
        
        Args:
            email (str): 要检查的邮箱地址
            
        Returns:
            bool: 邮箱存在返回 True，否则返回 False
            
        Note:
            使用 exists() 比直接查询更高效，因为只需要返回布尔值
        """
        # 查询操作不需要显式事务
        stmt = select(exists().where(User.email == email))
        return await self.session.scalar(stmt)

    async def create(self, user_schema: UserCreateSchema) -> User:
        """
        创建新用户
        
        根据提供的用户信息创建新用户账户。
        密码会自动加密存储。
        
        Args:
            user_schema (UserCreateSchema): 用户创建信息，包括：
                - email: 邮箱地址
                - username: 用户名
                - password: 密码（明文，会自动加密）
                
        Returns:
            User: 创建的用户对象
            
        Note:
            - 密码会在 User 模型初始化时自动加密
            - 需要在外部调用 commit() 才能持久化到数据库
        """
        # 将 schema 转换为字典，然后创建 User 对象
        user = User(**user_schema.model_dump())
        # 添加到会话中
        self.session.add(user)
        # 刷新以获取生成的ID
        await self.session.flush()
        return user


class EmailCodeRepository:
    """
    邮箱验证码数据仓库类
    
    提供邮箱验证码相关的数据库操作方法。
    所有方法都是异步的，使用 SQLAlchemy 异步会话。
    
    Attributes:
        session (AsyncSession): SQLAlchemy 异步数据库会话
    """
    
    def __init__(self, session: AsyncSession):
        """
        初始化验证码仓库
        
        Args:
            session (AsyncSession): 数据库会话实例
        """
        self.session = session

    async def create(self, email: str, code: str) -> EmailCode:
        """
        创建验证码记录
        
        在数据库中保存邮箱和验证码的对应关系。
        
        Args:
            email (str): 接收验证码的邮箱地址
            code (str): 验证码字符串（通常为4位数字）
            
        Returns:
            EmailCode: 创建的验证码记录对象
            
        Note:
            - 需要在外部调用 commit() 才能持久化到数据库
            - 建议定期清理过期的验证码记录
        """
        # 创建验证码记录对象
        email_code = EmailCode(email=email, code=code)
        # 添加到会话中
        self.session.add(email_code)
        # 刷新以获取生成的ID
        await self.session.flush()
        return email_code

    async def check_email_code(self, email: str, code: str) -> bool:
        """
        检查验证码是否正确且有效
        
        验证邮箱和验证码是否匹配，并检查验证码是否在有效期内。
        验证码有效期为10分钟。
        
        Args:
            email (str): 用户邮箱地址
            code (str): 用户输入的验证码
            
        Returns:
            bool: 验证码正确且有效返回 True，否则返回 False
            
        Note:
            - 验证码必须同时匹配邮箱和验证码
            - 验证码必须在10分钟内使用
            - 超过10分钟的验证码自动失效
        """
        # 查询操作不需要显式事务
        stmt = select(EmailCode).where(
            EmailCode.email == email, 
            EmailCode.code == code
        )
        email_code: EmailCode | None = await self.session.scalar(stmt)
        
        # 如果验证码不存在，返回 False
        if email_code is None:
            return False
        
        # 检查验证码是否在有效期内（10分钟）
        if (datetime.now() - email_code.created_time) > timedelta(minutes=10):
            return False
        
        # 验证码正确且有效
        return True
