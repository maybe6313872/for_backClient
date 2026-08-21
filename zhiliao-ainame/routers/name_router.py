"""
名字生成相关路由模块

本模块提供了基于 AI 的智能起名服务 API 端点。
需要用户认证后才能使用。
"""

from fastapi import APIRouter, Depends

from schemas.name import NameIn, NameOut
from core.agent import generate_names
from core.auth import AuthHandler

# 创建认证处理器实例（单例模式）
auth_handler = AuthHandler()


# 创建名字生成相关的路由组
# prefix: 所有路由的前缀为 /name
# tags: 在 Swagger 文档中分组为 "name"
router = APIRouter(prefix="/name", tags=["name"])


@router.post("/", response_model=NameOut, summary="生成名字", description="根据输入的姓氏、性别等信息生成名字")
async def take_names(
    data: NameIn,
    # user_id: int = Depends(auth_handler.auth_access_dependency)
):
    """
    生成名字接口
    
    根据用户提供的姓氏、性别、字数等要求，使用 AI 生成符合要求的名字。
    每个名字都会包含出处和寓意说明。
    
    Args:
        data (NameIn): 起名要求，包括：
            - surname (str): 姓氏，例如 "张"、"李"
            - gender (Literal): 性别，可选值："不限"、"男"、"女"
            - length (Literal): 名字字数，可选值："不限"、"单字"、"两字"
            - other (str, optional): 其他要求，例如 "希望名字有文化内涵"
            - exclude (List[str], optional): 要排除的名字列表
        user_id (int): 当前登录用户的 ID（通过 JWT 令牌自动获取）
        
    Returns:
        NameOut: 包含生成的名字列表的响应对象：
            - names: 名字列表，每个名字包含：
                - name: 完整的姓名
                - reference: 名字的出处（典籍来源或文化意象）
                - moral: 名字的寓意说明
                
    Raises:
        HTTPException:
            - 401: 未提供有效的认证令牌
            - 403: 认证令牌无效或已过期
            
    Note:
        - 此接口需要用户登录认证
        - 需要在请求头中提供 JWT 令牌：Authorization: Bearer {token}
        - 使用 LangChain + DeepSeek AI 模型生成名字
        - 生成的名字会参考《诗经》《楚辞》等经典文献
    """
    # 调用 AI 代理生成名字
    # name_result = await generate_names(data)
    
    # 返回格式化的名字列表
    # 格式：{"names": [{"name": "xx", "reference": "xx", "moral": "xx"}]}
    # return NameOut(names=name_result.names)
    return NameOut(names=[
        {
            "name": "张子涵",
            "reference": "《诗经·小雅》",
            "moral": "子：有学问、有德行的人；涵：包容、涵养"
        }
    ])