"""
学校管理系统数据模式模块

本模块包含学校管理系统的所有 Pydantic 数据模型。
"""

from .school import SchoolIn, SchoolOut, SchoolUpdateIn, SchoolListResponse
from .teacher import TeacherIn, TeacherOut, TeacherUpdateIn, TeacherListResponse
from .student import StudentIn, StudentOut, StudentUpdateIn, StudentListResponse
from .course import CourseIn, CourseOut, CourseUpdateIn, CourseListResponse
from .student_course import (
    StudentCourseIn,
    StudentCourseOut,
    StudentCourseUpdateIn,
    StudentCourseListResponse,
    StudentCourseBatchIn
)

__all__ = [
    "SchoolIn",
    "SchoolOut",
    "SchoolUpdateIn",
    "SchoolListResponse",
    "TeacherIn",
    "TeacherOut",
    "TeacherUpdateIn",
    "TeacherListResponse",
    "StudentIn",
    "StudentOut",
    "StudentUpdateIn",
    "StudentListResponse",
    "CourseIn",
    "CourseOut",
    "CourseUpdateIn",
    "CourseListResponse",
    "StudentCourseIn",
    "StudentCourseOut",
    "StudentCourseUpdateIn",
    "StudentCourseListResponse",
    "StudentCourseBatchIn",
]
