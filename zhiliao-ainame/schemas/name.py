"""
名字生成相关的数据模型模块

本模块定义了起名服务的请求和响应数据模型。
用于 API 请求和响应的数据验证和序列化。
"""

from pydantic import BaseModel, Field
from typing import Annotated, Literal, List
from .agent import NameSchema


class NameIn(BaseModel):
    """
    起名请求模型
    
    包含生成名字所需的所有要求信息。
    
    Attributes:
        surname (str): 姓氏，例如 "张"、"李"、"王"
        gender (Literal): 性别要求，可选值：
            - "不限": 不限制性别
            - "男": 男性名字
            - "女": 女性名字
        length (Literal): 名字字数要求，可选值：
            - "不限": 不限制字数
            - "单字": 单字名
            - "两字": 两字名
        other (str, optional): 其他要求，例如：
            - "希望名字有文化内涵"
            - "希望名字儒雅大气"
            - "希望名字清丽脱俗"
            默认为空字符串
        exclude (List[str], optional): 要排除的名字列表
            例如：["张三", "李四"]
            默认为空列表
            
    Example:
        >>> name_in = NameIn(
        ...     surname="张",
        ...     gender="男",
        ...     length="两字",
        ...     other="希望名字有文化内涵",
        ...     exclude=["张伟", "张强"]
        ... )
    """
    surname: Annotated[str, Field(..., description="姓氏")]
    gender: Annotated[
        Literal["不限", "男", "女"], 
        Field(..., description="性别")
    ]
    length: Annotated[
        Literal["不限", "单字", "两字"], 
        Field(..., description="字数")
    ]
    other: Annotated[
        str | None, 
        Field(default="", description="其他要求")
    ]
    exclude: Annotated[
        List[str], 
        Field(default=[], description="排除的名字")
    ]


class NameOut(BaseModel):
    """
    起名响应模型
    
    包含 AI 生成的名字列表。
    每个名字都包含完整的姓名、出处和寓意说明。
    
    Attributes:
        names (List[NameSchema]): 生成的名字列表
            通常包含5个候选名字，每个名字包含：
            - name: 完整的姓名
            - reference: 名字的出处（典籍来源或文化意象）
            - moral: 名字的寓意说明
            
    Example:
        >>> name_out = NameOut(names=[
        ...     NameSchema(
        ...         name="张子涵",
        ...         reference="《诗经》",
        ...         moral="子：有学问、有德行的人；涵：包容、涵养"
        ...     )
        ... ])
    """
    names: List[NameSchema]