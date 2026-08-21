"""
学生课程关联表模型模块

本模块定义了学生和课程的关联表（StudentCourse）的数据库模型。
"""

from models import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, Float, DateTime, ForeignKey, UniqueConstraint
from datetime import datetime


class StudentCourse(Base):
    """
    学生课程关联表模型
    
    存储学生和课程的关联关系，以及学生的课程分数。
    
    Attributes:
        id (int): 关联记录唯一标识符，主键，自增
        student_id (int): 学生ID（外键）
        course_id (int): 课程ID（外键）
        score (float): 分数
        created_time (datetime): 创建时间，默认当前时间
        
    Constraints:
        - 学生和课程的组合必须唯一（一个学生对同一门课程只能有一条记录）
    """
    __tablename__ = 'student_course'
    
    # 关联记录 ID，主键，自增
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # 学生ID（外键）
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey('student.id'), nullable=False)
    
    # 课程ID（外键）
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey('course.id'), nullable=False)
    
    # 分数
    score: Mapped[float] = mapped_column(Float, nullable=True)
    
    # 创建时间，默认当前时间
    created_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    # 唯一约束：确保一个学生对同一门课程只能有一条记录
    __table_args__ = (
        UniqueConstraint('student_id', 'course_id', name='uq_student_course'),
    )
    