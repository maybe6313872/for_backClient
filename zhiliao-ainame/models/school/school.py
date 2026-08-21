"""
学校相关数据库模型模块

本模块定义了学校（School）的数据库模型。
"""

from models import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey
from datetime import datetime


class School(Base):
    """
    学校模型
    
    存储学校相关信息。
    
    Attributes:
        id (int): 学校唯一标识符，主键，自增
        name (str): 校名，最大长度100字符
        address (str): 学校地址，最大长度200字符
        created_time (datetime): 创建时间，默认当前时间
        teachers (List[Teacher]): 该学校的班主任列表（一对多关系）
    """
    __tablename__ = 'school'
    
    # 学校 ID，主键，自增
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # 校名
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # 学校地址
    address: Mapped[str] = mapped_column(String(200), nullable=False)
    
    # 创建时间，默认当前时间
    created_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    # 一对多关系：一个学校有多个班主任
    teachers: Mapped[list["Teacher"]] = relationship(  # pyright: ignore[reportUndefinedVariable]
        "Teacher",
        back_populates="school",
        cascade="all, delete-orphan"
    )
