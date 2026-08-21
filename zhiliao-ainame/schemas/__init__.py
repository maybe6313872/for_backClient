"""
通用响应模型模块

本模块定义了通用的 API 响应数据模型。
用于不需要返回具体数据的操作（如注册、删除等）。
"""

from pydantic import BaseModel, Field
from typing import Annotated, Literal


class ResponseOut(BaseModel):
    """
    通用操作结果响应模型
    
    用于一些视图函数，只需要返回操作成功或失败的结果。
    不需要返回具体的数据内容。
    
    Attributes:
        result (Literal["success", "failure"]): 操作结果，默认为 "success"
            - "success": 操作成功
            - "failure": 操作失败
            
    Example:
        >>> response = ResponseOut()
        >>> response.result
        'success'
        
        >>> response = ResponseOut(result="failure")
        >>> response.result
        'failure'
    """
    result: Annotated[
        Literal["success", "failure"], 
        Field(default="success", description="操作的结果！")
    ]