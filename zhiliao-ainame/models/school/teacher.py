"""
班主任相关数据库模型模块

本模块定义了班主任（Teacher）的数据库模型。
"""

from models import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey
from datetime import datetime


class Teacher(Base):
    """
    班主任模型
    
    存储班主任相关信息。
    
    Attributes:
        id (int): 班主任唯一标识符，主键，自增
        name (str): 班主任姓名，最大长度50字符
        sex (str): 性别，最大长度10字符
        age (int): 年龄
        school_id (int): 所属学校ID（外键）
        created_time (datetime): 创建时间，默认当前时间
        school (School): 所属学校（多对一关系）
        students (List[Student]): 该班主任的学生列表（一对多关系）
    """
    __tablename__ = 'teacher'
    
    # 班主任 ID，主键，自增
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # 班主任姓名
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # 性别
    sex: Mapped[str] = mapped_column(String(10), nullable=False)
    
    # 年龄
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # 所属学校ID（外键）
    school_id: Mapped[int] = mapped_column(Integer, ForeignKey('school.id'), nullable=False)
    
    # 创建时间，默认当前时间
    created_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    # 多对一关系：多个班主任属于一个学校
    school: Mapped["School"] = relationship("School", back_populates="teachers")
    
    # 一对多关系：一个班主任有多个学生
    students: Mapped[list["Student"]] = relationship(
        "Student",
        back_populates="teacher",
        cascade="all, delete-orphan"
    )
