"""
学校管理系统路由模块

本模块包含学校管理系统的所有 API 路由。
"""

from .school import router as school_router
from .teacher import router as teacher_router
from .student import router as student_router
from .course import router as course_router
from .student_course import router as student_course_router

__all__ = [
    "school_router",
    "teacher_router",
    "student_router",
    "course_router",
    "student_course_router",
]
