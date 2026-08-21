"""
AI 代理相关的数据模型模块

本模块定义了 AI 起名代理使用的数据模型。
用于结构化 AI 响应的格式定义。
"""

from pydantic import BaseModel, Field
from typing import Annotated, List


class NameSchema(BaseModel):
    """
    单个名字的数据模型
    
    表示一个生成的名字及其相关信息。
    用于 AI 代理的结构化输出。
    
    Attributes:
        name (str): 完整的姓名（包含姓氏和名字）
            例如："张子涵"、"李思远"
        reference (str): 名字的出处
            例如："《诗经·小雅》"、"《楚辞·离骚》"、"成语典故"
        moral (str): 名字的寓意说明
            例如："子：有学问、有德行的人；涵：包容、涵养"
            
    Example:
        >>> name = NameSchema(
        ...     name="张子涵",
        ...     reference="《诗经·小雅》",
        ...     moral="子：有学问、有德行的人；涵：包容、涵养"
        ... )
    """
    name: Annotated[str, Field(..., description="姓名")]
    reference: Annotated[str, Field(..., description="出处")]
    moral: Annotated[str, Field(..., description="寓意")]


class NameResultSchema(BaseModel):
    """
    名字生成结果模型
    
    包含 AI 生成的所有名字候选方案。
    用于 LangChain 代理的结构化响应格式。
    
    Attributes:
        names (List[NameSchema]): 生成的名字列表
            通常包含5个候选名字
            
    Note:
        - 此模型用于定义 AI 代理的输出格式
        - LangChain 会确保 AI 返回的数据符合此格式
        - 如果 AI 返回格式不正确，会抛出验证错误
    """
    names: List[NameSchema]