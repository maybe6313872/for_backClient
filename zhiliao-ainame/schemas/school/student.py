"""
学生相关的数据模型模块

本模块定义了学生操作使用的 Pydantic 数据模型。
"""

from pydantic import BaseModel, Field
from typing import Annotated, List, Optional
from datetime import datetime
from schemas.school.course import CourseOut


class StudentIn(BaseModel):
    """
    学生创建请求模型
    
    Attributes:
        name (str): 学生姓名，最大长度50字符
        sex (str): 性别，最大长度10字符
        age (int): 年龄
        teacher_id (int): 所属班主任ID
    """
    name: Annotated[
        str,
        Field(..., max_length=50, description="学生姓名")
    ]
    sex: Annotated[
        str,
        Field(..., max_length=10, description="性别")
    ]
    age: Annotated[
        int,
        Field(..., ge=0, le=150, description="年龄")
    ]
    teacher_id: Annotated[
        int,
        Field(..., description="所属班主任ID")
    ]


class CourseWithScore(BaseModel):
    """
    带分数的课程信息模型
    
    Attributes:
        course (CourseOut): 课程信息
        score (float | None): 分数
    """
    course: CourseOut
    score: float | None = None

    model_config = {
        "from_attributes": True
    }


class StudentOut(BaseModel):
    """
    学生响应模型
    
    Attributes:
        id (int): 学生唯一标识符
        name (str): 学生姓名
        sex (str): 性别
        age (int): 年龄
        teacher_id (int): 所属班主任ID
        created_time (datetime): 创建时间
        courses (List[CourseWithScore]): 所选课程列表（包含分数）
    """
    id: int
    name: str
    sex: str
    age: int
    teacher_id: int
    created_time: datetime
    courses: List[CourseWithScore] = []

    model_config = {
        "from_attributes": True
    }


class StudentUpdateIn(BaseModel):
    """
    学生更新请求模型
    """
    name: Annotated[
        str | None,
        Field(None, max_length=50, description="学生姓名")
    ] = None
    sex: Annotated[
        str | None,
        Field(None, max_length=10, description="性别")
    ] = None
    age: Annotated[
        int | None,
        Field(None, ge=0, le=150, description="年龄")
    ] = None
    teacher_id: Annotated[
        int | None,
        Field(None, description="所属班主任ID")
    ] = None


class StudentListResponse(BaseModel):
    """
    学生列表响应模型
    """
    code: int = Field(default=200, description="响应状态码")
    message: str = Field(default="查询成功", description="响应消息")
    data: List[StudentOut] = Field(..., description="学生列表")
