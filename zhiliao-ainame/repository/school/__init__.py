"""
学校管理系统数据仓库模块

本模块包含学校管理系统的所有数据访问层。
"""

from .school_repo import SchoolRepository
from .teacher_repo import TeacherRepository
from .student_repo import StudentRepository
from .course_repo import CourseRepository
from .student_course_repo import StudentCourseRepository

__all__ = [
    "SchoolRepository",
    "TeacherRepository",
    "StudentRepository",
    "CourseRepository",
    "StudentCourseRepository",
]
