"""
用户相关数据库模型模块

本模块定义了用户和邮箱验证码的数据库模型。
使用 pwdlib 库进行密码加密（Argon2 算法）。

依赖包：pwdlib[argon2] (pip install "pwdlib[argon2]")
"""

from . import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, String, DateTime
from pwdlib import PasswordHash

from datetime import datetime

# 创建密码哈希器实例
# 使用推荐的 Argon2 算法进行密码加密
# Argon2 是密码哈希竞赛的获胜者，安全性高，抗暴力破解能力强
password_hash = PasswordHash.recommended()


class User(Base):
    """
    用户模型
    
    表示系统中的用户账户信息。
    密码使用 Argon2 算法加密存储，不存储明文密码。
    
    Attributes:
        id (int): 用户唯一标识符，主键，自增
        email (str): 用户邮箱地址，唯一，最大长度100字符
        username (str): 用户名，最大长度100字符
        _password (str): 加密后的密码，最大长度200字符（私有属性）
        
    Methods:
        password (property): 密码属性，设置时自动加密
        check_password(raw_password): 验证密码是否正确
    """
    __tablename__ = 'user'
    
    # 用户 ID，主键，自增
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # 邮箱地址，唯一约束
    email: Mapped[str] = mapped_column(String(100), unique=True)
    
    # 用户名
    username: Mapped[str] = mapped_column(String(100))
    
    # 加密后的密码（私有属性，通过 password 属性访问）
    _password: Mapped[str] = mapped_column(String(200))

    def __init__(self, *args, **kwargs):
        """
        初始化用户对象
        
        从关键字参数中提取 password，然后调用父类初始化。
        如果提供了 password，会自动加密存储。
        
        Args:
            *args: 位置参数
            **kwargs: 关键字参数，可能包含 password
        """
        # 提取 password 参数（如果存在）
        password = kwargs.pop('password', None)
        
        # 调用父类初始化
        super().__init__(*args, **kwargs)
        
        # 如果提供了密码，则设置密码（会自动加密）
        if password:
            self.password = password

    @property
    def password(self) -> str:
        """
        获取加密后的密码（只读属性）
        
        Returns:
            str: 加密后的密码哈希值
        """
        return self._password

    @password.setter
    def password(self, raw_password: str):
        """
        设置密码（自动加密）
        
        当设置密码时，会自动使用 Argon2 算法加密存储。
        不存储明文密码，提高安全性。
        
        Args:
            raw_password (str): 原始密码（明文）
        """
        self._password = password_hash.hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """
        验证密码是否正确
        
        使用 Argon2 算法验证提供的密码是否与存储的哈希值匹配。
        
        Args:
            raw_password (str): 要验证的原始密码（明文）
            
        Returns:
            bool: 密码正确返回 True，否则返回 False
            
        Note:
            - 使用安全的密码验证方法，防止时序攻击
            - 即使密码错误，验证时间也保持一致
        """
        return password_hash.verify(raw_password, self.password)


class EmailCode(Base):
    """
    邮箱验证码模型
    
    存储发送给用户的邮箱验证码信息。
    用于用户注册时的邮箱验证。
    
    Attributes:
        id (int): 验证码记录唯一标识符，主键，自增
        email (str): 接收验证码的邮箱地址，最大长度100字符
        code (str): 验证码字符串，最大长度10字符
        created_time (datetime): 验证码创建时间，默认当前时间
        
    Note:
        - 验证码通常为4位数字
        - 验证码有效期为10分钟（在 repository 中检查）
        - 建议定期清理过期的验证码记录
    """
    __tablename__ = 'email_code'
    
    # 验证码记录 ID，主键，自增
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # 接收验证码的邮箱地址
    email: Mapped[str] = mapped_column(String(100))
    
    # 验证码字符串（通常为4位数字）
    code: Mapped[str] = mapped_column(String(10))
    
    # 验证码创建时间，默认当前时间
    created_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # 测试修改数据库结构并同步更新
    type: Mapped[str] = mapped_column(String(10), default="test")
