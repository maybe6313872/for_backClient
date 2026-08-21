"""
课程相关数据库模型模块

本模块定义了课程（Course）的数据库模型。
"""

from models import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, String, DateTime, Float
from datetime import datetime


class Course(Base):
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
    __tablename__ = 'course'
    
    # 课程 ID，主键，自增
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # 课程名
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # 学分
    credit: Mapped[float] = mapped_column(Float, nullable=False)
    
    # 创建时间，默认当前时间
    created_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    # 多对多关系：一门课程可以被多个学生选修（通过 StudentCourse 中间表）
    students: Mapped[list["Student"]] = relationship(
        "Student",
        secondary="student_course",
        back_populates="courses"
    )
