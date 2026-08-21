"""
学校相关数据库模型模块

本模块定义了学校（School）的数据库模型。
"""

from models import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey
from datetime import datetime


class Order(Base):
    """
    订单模型
    
    订单相关信息。
    
    Attributes:
        id (int): 学校唯一标识符，主键，自增
        name (str): 校名，最大长度100字符
        address (str): 学校地址，最大长度200字符
        created_time (datetime): 创建时间，默认当前时间
        teachers (List[Teacher]): 该学校的班主任列表（一对多关系）
    """
    __tablename__ = 'order'
    
    # 学校 ID，主键，自增
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # 订单号
    order_number: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # 下单公司
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey('company.id'), nullable=False)

    # 创建时间，默认当前时间
    created_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # 多对一关系：多个公司属于一个
    company: Mapped["Company"] = relationship("Company", back_populates="orders")

    # 一对多关系：一个学校有多个班主任
    products: Mapped[list["Product"]] = relationship(
        "Product",
        secondary="order_product",
        back_populates="orders"
    )
