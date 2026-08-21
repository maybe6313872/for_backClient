"""
学生相关数据库模型模块

本模块定义了学生（Student）的数据库模型。
"""

from models import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey
from datetime import datetime


class Student(Base):
    """
    学生模型
    
    存储学生相关信息。
    
    Attributes:
        id (int): 学生唯一标识符，主键，自增
        name (str): 学生姓名，最大长度50字符
        sex (str): 性别，最大长度10字符
        age (int): 年龄
        teacher_id (int): 所属班主任ID（外键）
        created_time (datetime): 创建时间，默认当前时间
        teacher (Teacher): 所属班主任（多对一关系）
        courses (List[Course]): 该学生选修的课程列表（多对多关系，通过 StudentCourse）
    """
    __tablename__ = 'student'
    
    # 学生 ID，主键，自增
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # 学生姓名
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # 性别
    sex: Mapped[str] = mapped_column(String(10), nullable=False)
    
    # 年龄
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # 所属班主任ID（外键）
    teacher_id: Mapped[int] = mapped_column(Integer, ForeignKey('teacher.id'), nullable=False)
    
    # 创建时间，默认当前时间
    created_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    # 多对一关系：多个学生属于一个班主任
    teacher: Mapped["Teacher"] = relationship("Teacher", back_populates="students")  # pyright: ignore[reportUndefinedVariable]
    
    # 多对多关系：一个学生可以选修多门课程（通过 StudentCourse 中间表）
    courses: Mapped[list["Course"]] = relationship(  # pyright: ignore[reportUndefinedVariable]
        "Course",
        secondary="student_course",
        back_populates="students"
    )
