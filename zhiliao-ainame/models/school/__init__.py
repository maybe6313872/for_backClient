"""
学校管理系统模型模块

本模块包含学校管理系统的所有数据库模型。
"""

from models import Base
from .school import School
from .teacher import Teacher
from .student import Student
from .course import Course
from .student_course import StudentCourse

__all__ = ["School", "Teacher", "Student", "Course", "StudentCourse"]
