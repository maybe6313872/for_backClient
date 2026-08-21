"""
学校相关的数据模型模块

本模块定义了学校操作使用的 Pydantic 数据模型。
用于 API 请求和响应的数据验证和序列化。
"""

from pydantic import BaseModel, Field
from typing import Annotated, List
from datetime import datetime


class SchoolIn(BaseModel):
    """
    学校创建请求模型
    
    Attributes:
        name (str): 校名，最大长度100字符
        address (str): 学校地址，最大长度200字符
    """
    name: Annotated[
        str,
        Field(..., max_length=100, description="校名")
    ]
    address: Annotated[
        str,
        Field(..., max_length=200, description="学校地址")
    ]


class SchoolOut(BaseModel):
    """
    学校响应模型
    
    Attributes:
        id (int): 学校唯一标识符
        name (str): 校名
        address (str): 学校地址
        created_time (datetime): 创建时间
    """
    id: int
    name: str
    address: str
    created_time: datetime

    model_config = {
        "from_attributes": True
    }


class SchoolUpdateIn(BaseModel):
    """
    学校更新请求模型
    
    Attributes:
        name (str, optional): 校名
        address (str, optional): 学校地址
    """
    name: Annotated[
        str | None,
        Field(None, max_length=100, description="校名")
    ] = None
    address: Annotated[
        str | None,
        Field(None, max_length=200, description="学校地址")
    ] = None


class SchoolListResponse(BaseModel):
    """
    学校列表响应模型
    """
    code: int = Field(default=200, description="响应状态码")
    message: str = Field(default="查询成功", description="响应消息")
    data: List[SchoolOut] = Field(..., description="学校列表")
