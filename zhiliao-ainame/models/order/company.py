"""
学校相关数据库模型模块

本模块定义了学校（School）的数据库模型。
"""

from models import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey
from datetime import datetime


class Company(Base):
    """
    公司模型

    存储公司相关信息。

    Attributes:
        id (int): 公司唯一标识符，主键，自增
        name (str): 公司名称，最大长度100字符
        address (str): 公司地址，最大长度200字符
        created_time (datetime): 创建时间，默认当前时间
        orders (List[Order]): 该公司的订单列表（一对多关系）
    """
    __tablename__ = 'company'
    
    # 公司 ID，主键，自增
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # 公司名称
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # 公司地址
    address: Mapped[str] = mapped_column(String(200), nullable=False)
    
    # 创建时间，默认当前时间
    created_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # 一对多关系：一个公司有多个订单
    orders: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="company",
        cascade="all, delete-orphan"
    )
