"""
学生课程关联相关的数据模型模块

本模块定义了学生课程关联操作使用的 Pydantic 数据模型。
"""

from pydantic import BaseModel, Field
from typing import Annotated, List, Optional
from datetime import datetime


class StudentCourseIn(BaseModel):
    """
    学生课程关联创建请求模型
    
    Attributes:
        student_id (int): 学生ID
        course_id (int): 课程ID
        score (float, optional): 分数
    """
    student_id: Annotated[
        int,
        Field(..., description="学生ID")
    ]
    course_id: Annotated[
        int,
        Field(..., description="课程ID")
    ]
    score: Annotated[
        float | None,
        Field(None, ge=0, le=100, description="分数")
    ] = None


class StudentCourseOut(BaseModel):
    """
    学生课程关联响应模型
    
    Attributes:
        id (int): 关联记录唯一标识符
        student_id (int): 学生ID
        course_id (int): 课程ID
        score (float): 分数
        created_time (datetime): 创建时间
    """
    id: int
    student_id: int
    course_id: int
    score: float | None
    created_time: datetime

    model_config = {
        "from_attributes": True
    }


class StudentCourseUpdateIn(BaseModel):
    """
    学生课程关联更新请求模型
    """
    score: Annotated[
        float | None,
        Field(None, ge=0, le=100, description="分数")
    ] = None


class StudentCourseBatchIn(BaseModel):
    """
    学生批量选课请求模型
    
    Attributes:
        student_id (int): 学生ID
        course_ids (List[int]): 课程ID数组
        scores (List[float], optional): 分数数组（可选，与course_ids一一对应）
    """
    student_id: Annotated[
        int,
        Field(..., description="学生ID")
    ]
    course_ids: Annotated[
        List[int],
        Field(..., min_length=1, description="课程ID数组")
    ]
    scores: Annotated[
        List[float] | None,
        Field(None, description="分数数组（可选，与course_ids一一对应）")
    ] = None


class StudentWithScore(BaseModel):
    """
    带分数的学生信息模型
    
    Attributes:
        student_id (int): 学生ID
        student_name (str): 学生姓名
        student_sex (str): 学生性别
        student_age (int): 学生年龄
        teacher_id (int): 所属班主任ID
        score (float | None): 分数
    """
    student_id: int
    student_name: str
    student_sex: str
    student_age: int
    teacher_id: int
    score: float | None = None


class StudentCourseListResponse(BaseModel):
    """
    学生课程关联列表响应模型
    """
    code: int = Field(default=200, description="响应状态码")
    message: str = Field(default="查询成功", description="响应消息")
    data: List[StudentCourseOut] = Field(..., description="学生课程关联列表")


class StudentsByCourseResponse(BaseModel):
    """
    根据课程ID查询学生的响应模型
    """
    code: int = Field(default=200, description="响应状态码")
    message: str = Field(default="查询成功", description="响应消息")
    data: List[StudentWithScore] = Field(..., description="学生列表（包含分数）")
