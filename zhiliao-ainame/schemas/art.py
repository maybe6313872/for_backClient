"""
文章相关的数据模型模块

本模块定义了文章操作使用的 Pydantic 数据模型。
用于 API 请求和响应的数据验证和序列化。
"""

from pydantic import BaseModel, Field, field_validator
from typing import Annotated, List, Literal, Generic, TypeVar
from datetime import datetime
import base64
from models.art import Art

# 定义泛型类型变量，用于响应模型的 data 字段
T = TypeVar('T')


class ArtIn(BaseModel):
    """
    文章创建请求模型
    
    包含创建文章所需的所有信息。
    
    Attributes:
        username (str): 用户名，最大长度100字符
        sex (str): 性别，最大长度10字符
        artcontent (str): 文章内容，最大长度5000字符
        thumbnail (str): 文章缩略图二进制数据的base64编码字符串
    """
    username: Annotated[
        str,
        Field(max_length=100, description="用户名")
    ]
    sex: Annotated[
        str,
        Field(max_length=10, description="性别")
    ]
    artcontent: Annotated[
        str,
        Field(max_length=5000, description="文章内容")
    ]
    thumbnail: Annotated[
        str,
        Field(description="文章缩略图二进制数据的base64编码字符串")
    ]
    
    def get_thumbnail_bytes(self) -> bytes:
        """
        将base64编码的缩略图字符串转换为二进制数据
        
        Returns:
            bytes: 缩略图的二进制数据
        """
        return base64.b64decode(self.thumbnail)


class ArtOut(BaseModel):
    """
    文章响应模型
    
    用于返回文章信息。
    
    Attributes:
        id (int): 文章唯一标识符
        username (str): 用户名
        sex (str): 性别
        artcontent (str): 文章内容
        thumbnail (str): 文章缩略图二进制数据的base64编码字符串
        created_time (datetime): 创建时间
    """
    id: int
    username: str
    sex: str
    artcontent: str
    # thumbnail: str  # base64编码的字符串
    # created_time: datetime

    model_config = {
        "from_attributes": True  # 替代了v1中的 `orm_mode = True`[1](@ref)
    }
    
    # 如果没有缩略图转为base64，还是用上面那个model_config来转换
    # @classmethod
    # def from_orm_with_thumbnail(cls, art_obj):
    #     """
    #     从ORM对象创建响应模型，将二进制缩略图转换为base64字符串
        
    #     Args:
    #         art_obj: Art ORM对象
            
    #     Returns:
    #         ArtOut: 响应模型实例
    #     """
    #     thumbnail_base64 = base64.b64encode(art_obj.thumbnail).decode('utf-8') if art_obj.thumbnail else ""
    #     return cls(
    #         id=art_obj.id,
    #         username=art_obj.username,
    #         sex=art_obj.sex,
    #         artcontent=art_obj.artcontent,
    #         thumbnail=thumbnail_base64,
    #         created_time=art_obj.created_time
    #     )


class ArtDeleteIn(BaseModel):
    """
    文章批量删除请求模型
    
    包含要删除的文章ID数组。
    
    Attributes:
        idArr (List[int]): 要删除的文章ID数组
    """
    idArr: Annotated[
        List[int],
        Field(..., description="要删除的文章ID数组", min_length=1)
    ]

class ArtChangeIn(BaseModel):
    """
    文章修改请求模型
    
    包含要修改的文章ID和修改后的内容。
    """
    id: Annotated[
        int,
        Field(..., description="文章ID")
    ]
    sex: Annotated[
        str,
        Field(max_length=10, description="性别")
    ]

class ArtQueryIn(BaseModel):
    """
    文章查询请求模型
    
    包含分页查询参数。
    """
    page: Annotated[
        int,
        Field(1, description="页码，默认1", ge=1)
    ]
    size: Annotated[
        int,
        Field(10, description="每页数量，默认10", ge=1, le=100)
    ]
    sex: Annotated[
        str,
        Field(..., max_length=10, description="性别")
    ]


class ArtQueryOut(BaseModel, Generic[T]):
    """
    文章查询响应模型
    
    包含 code、data、message 的标准响应格式。
    如果 data 是 ORM 对象，会自动转换为 Pydantic 响应模型。
    
    Attributes:
        code (int): 响应状态码，默认200
        message (str): 响应消息，默认"查询成功"
        data (T): 查询到的数据，类型由泛型参数决定
    """
    code: Annotated[
        int,
        Field(default=200, description="响应状态码")
    ]
    message: Annotated[
        str,
        Field(default="查询成功", description="响应消息")
    ]
    data: Annotated[
        T,
        Field(description="查询到的数据")
    ]
    
    @field_validator('data', mode='before')
    @classmethod
    def convert_orm_to_pydantic(cls, v):
        """
        如果 data 是 ORM 对象，自动转换为 Pydantic 响应模型
        支持数字、字符串、列表、ORM 对象等多种类型
        
        Args:
            v: data 字段的值（可能是数字、字符串、列表、ORM 对象或 Pydantic 模型）
            
        Returns:
            转换后的数据
        """
        def is_orm_object(obj):
            """检查对象是否是 ORM 对象"""
            # 基本类型（数字、字符串、布尔值）不是 ORM 对象
            if isinstance(obj, (int, float, str, bool, type(None))):
                return False
            # 检查是否是 Art 模型的实例
            if isinstance(obj, Art):
                return True
            # 检查是否有 __tablename__ 属性（SQLAlchemy 模型的特征）
            if hasattr(obj, '__tablename__'):
                return True
            # 检查是否是 BaseModel 实例，如果不是且是对象，可能是 ORM 对象
            if not isinstance(obj, BaseModel) and hasattr(obj, '__class__'):
                # 进一步检查是否有 SQLAlchemy 相关的属性
                if hasattr(obj, 'id') and hasattr(obj, '__mapper__'):
                    return True
            return False
        
        # 基本类型（数字、字符串、布尔值、None）直接返回
        if isinstance(v, (int, float, str, bool, type(None))):
            return v
        
        # 如果是列表
        if isinstance(v, list):
            result = []
            for item in v:
                if is_orm_object(item):
                    # 是 ORM 对象，转换为 ArtOut
                    result.append(ArtOut.model_validate(item, from_attributes=True))
                else:
                    # 已经是 Pydantic 模型、基本类型或其他类型，直接使用
                    result.append(item)
            return result
        
        # 如果是 ORM 对象，转换为 ArtOut
        if is_orm_object(v):
            return ArtOut.model_validate(v, from_attributes=True)
        
        # 其他情况（如 Pydantic 模型、字典等）直接返回
        return v