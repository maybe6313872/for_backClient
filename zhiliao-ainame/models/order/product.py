"""
课程相关数据库模型模块

本模块定义了课程（Course）的数据库模型。
"""

from models import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, String, DateTime, Float
from datetime import datetime


class Product(Base):
    """
    课程模型
    
    存储课程相关信息。
    
    Attributes:
        id (int): 课程唯一标识符，主键，自增
        name (str): 课程名，最大长度100字符
        credit (float): 学分
        created_time (datetime): 创建时间，默认当前时间
        students (List[Student]): 选修该课程的学生列表（多对多关系，通过 StudentCourse）
    """
    __tablename__ = 'product'
    
    # 产品ID，主键，自增
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # 产品名
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # 价格
    price: Mapped[float] = mapped_column(Float, nullable=False)

    # 库存数量
    storenum: Mapped[int] = mapped_column(Integer, nullable=False)

    # 产品描述
    description: Mapped[str] = mapped_column(String(200), nullable=False)

    # 产品编号
    productno: Mapped[str] = mapped_column(String(200), nullable=False)
    
    # 创建时间，默认当前时间
    created_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    # 多对多关系：一个订单多个产品,也能多个产品一个订单
    orders: Mapped[list["Order"]] = relationship(
        "Order",
        secondary="order_product",
        back_populates="products"
    )
