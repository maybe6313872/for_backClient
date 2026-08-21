"""
班主任相关的数据模型模块

本模块定义了班主任操作使用的 Pydantic 数据模型。
"""

from pydantic import BaseModel, Field
from typing import Annotated, List, Optional
from datetime import datetime


class TeacherIn(BaseModel):
    """
    班主任创建请求模型
    
    Attributes:
        name (str): 班主任姓名，最大长度50字符
        sex (str): 性别，最大长度10字符
        age (int): 年龄
        school_id (int): 所属学校ID
    """
    name: Annotated[
        str,
        Field(..., max_length=50, description="班主任姓名")
    ]
    sex: Annotated[
        str,
        Field(..., max_length=10, description="性别")
    ]
    age: Annotated[
        int,
        Field(..., ge=0, le=150, description="年龄")
    ]
    school_id: Annotated[
        int,
        Field(..., description="所属学校ID")
    ]


class TeacherOut(BaseModel):
    """
    班主任响应模型
    
    Attributes:
        id (int): 班主任唯一标识符
        name (str): 班主任姓名
        sex (str): 性别
        age (int): 年龄
        school_id (int): 所属学校ID
        created_time (datetime): 创建时间
    """
    id: int
    name: str
    sex: str
    age: int
    school_id: int
    created_time: datetime

    model_config = {
        "from_attributes": True
    }


class TeacherUpdateIn(BaseModel):
    """
    班主任更新请求模型
    """
    name: Annotated[
        str | None,
        Field(None, max_length=50, description="班主任姓名")
    ] = None
    sex: Annotated[
        str | None,
        Field(None, max_length=10, description="性别")
    ] = None
    age: Annotated[
        int | None,
        Field(None, ge=0, le=150, description="年龄")
    ] = None
    school_id: Annotated[
        int | None,
        Field(None, description="所属学校ID")
    ] = None


class TeacherListResponse(BaseModel):
    """
    班主任列表响应模型
    """
    code: int = Field(default=200, description="响应状态码")
    message: str = Field(default="查询成功", description="响应消息")
    data: List[TeacherOut] = Field(..., description="班主任列表")
