"""
课程相关的数据模型模块

本模块定义了课程操作使用的 Pydantic 数据模型。
"""

from pydantic import BaseModel, Field
from typing import Annotated, List
from datetime import datetime


class CourseIn(BaseModel):
    """
    课程创建请求模型
    
    Attributes:
        name (str): 课程名，最大长度100字符
        credit (float): 学分
    """
    name: Annotated[
        str,
        Field(..., max_length=100, description="课程名")
    ]
    credit: Annotated[
        float,
        Field(..., ge=0, description="学分")
    ]


class CourseOut(BaseModel):
    """
    课程响应模型
    
    Attributes:
        id (int): 课程唯一标识符
        name (str): 课程名
        credit (float): 学分
        created_time (datetime): 创建时间
    """
    id: int
    name: str
    credit: float
    created_time: datetime

    model_config = {
        "from_attributes": True
    }


class CourseUpdateIn(BaseModel):
    """
    课程更新请求模型
    """
    name: Annotated[
        str | None,
        Field(None, max_length=100, description="课程名")
    ] = None
    credit: Annotated[
        float | None,
        Field(None, ge=0, description="学分")
    ] = None


class CourseListResponse(BaseModel):
    """
    课程列表响应模型
    """
    code: int = Field(default=200, description="响应状态码")
    message: str = Field(default="查询成功", description="响应消息")
    data: List[CourseOut] = Field(..., description="课程列表")
