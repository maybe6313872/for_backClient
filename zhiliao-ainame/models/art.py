"""
文章相关数据库模型模块

本模块定义了文章（Art）的数据库模型。
"""

from . import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.dialects.mysql import LONGBLOB
from datetime import datetime


class Art(Base):
    """
    文章模型
    
    存储文章相关信息。
    
    Attributes:
        id (int): 文章唯一标识符，主键，自增
        username (str): 用户名，最大长度100字符
        sex (str): 性别，最大长度10字符
        artcontent (str): 文章内容，最大长度5000字符
        thumbnail (bytes): 文章缩略图二进制数据（BLOB类型）
        created_time (datetime): 创建时间，默认当前时间
    """
    __tablename__ = 'art'
    
    # 文章 ID，主键，自增
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # 用户名
    username: Mapped[str] = mapped_column(String(100))
    
    # 性别
    sex: Mapped[str] = mapped_column(String(10))
    
    # 文章内容
    artcontent: Mapped[str] = mapped_column(String(5000))
    
    # 文章缩略图二进制数据（LONGBLOB类型，最大支持4GB）
    thumbnail: Mapped[bytes] = mapped_column(LONGBLOB)
    
    # 创建时间，默认当前时间
    created_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
