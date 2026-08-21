"""
文章相关路由模块

本模块提供了文章相关的 API 端点。
"""

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from models import AsyncSession
from dependencies import get_session
from repository.art_repo import ArtRepository
from schemas import ResponseOut
from schemas.art import ArtDeleteIn, ArtChangeIn, ArtQueryIn, ArtOut, ArtQueryOut
from core.auth import AuthHandler


# 创建文章相关的路由组
# prefix: 所有路由的前缀为 /admin
# tags: 在 Swagger 文档中分组为 "admin"
router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/insertArt", response_model=ResponseOut, summary="插入文章", description="插入一条文章数据")
async def insert_art(
    username: str = Form(..., description="用户名"),
    sex: str = Form(..., description="性别"),
    artcontent: str = Form(..., description="文章内容"),
    file: UploadFile = File(..., description="文章缩略图文件"),
    session: AsyncSession = Depends(get_session),
):
    """
    插入文章接口
    
    在数据库中插入一条文章记录。
    
    Args:
        username (str): 用户名
        sex (str): 性别
        artcontent (str): 文章内容
        file (UploadFile): 文章缩略图文件（formdata中的file字段）
        session (AsyncSession): 数据库会话（通过依赖注入获取）
        
    Returns:
        ResponseOut: 操作结果响应对象
        
    Raises:
        HTTPException: 
            - 500: 文章创建失败
    """
    # 创建文章仓库实例
    art_repo = ArtRepository(session=session)
    
    try:
        # 读取文件内容为二进制数据
        thumbnail_bytes = await file.read()
        
        # 检查文件大小（限制为100MB）
        max_size = 100 * 1024 * 1024  # 100MB
        if len(thumbnail_bytes) > max_size:
            raise HTTPException(413, detail=f"文件大小超过限制，最大允许 {max_size / 1024 / 1024}MB")
        
        # 创建文章
        await art_repo.create(
            username=username,
            sex=sex,
            artcontent=artcontent,
            thumbnail=thumbnail_bytes
        )
        # 提交事务
        await session.commit()
    except HTTPException:
        # HTTP异常直接抛出
        raise
    except Exception as e:
        # 捕获所有异常，回滚事务并返回服务器错误
        await session.rollback()
        raise HTTPException(500, detail=str(e))
    
    return ResponseOut()


@router.post("/delArt", response_model=int, summary="批量删除文章", description="根据ID数组批量删除文章")
async def del_art(
    data: ArtDeleteIn,
    session: AsyncSession = Depends(get_session),
):
    """
    批量删除文章接口
    
    根据ID数组批量删除文章记录。
    
    Args:
        data (ArtDeleteIn): 删除请求，包含：
            - idArr: 要删除的文章ID数组
        session (AsyncSession): 数据库会话（通过依赖注入获取）
        
    Returns:
        ResponseOut: 操作结果响应对象
        
    Raises:
        HTTPException: 
            - 400: ID数组为空
            - 500: 删除失败
    """
    # 创建文章仓库实例
    art_repo = ArtRepository(session=session)
    
    try:
        # 验证ID数组不为空
        if not data.idArr:
            raise HTTPException(400, detail="ID数组不能为空")
        
        # 批量删除文章
        deleted_count = await art_repo.delete_by_ids(data.idArr)
        
        # 如果删除的记录数为0，说明没有找到对应的记录
        if deleted_count == 0:
            raise HTTPException(400, detail="未找到要删除的文章记录")
        
        # 提交事务
        await session.commit()
    except HTTPException:
        # HTTP异常直接抛出
        await session.rollback()
        raise
    except Exception as e:
        # 捕获所有异常，回滚事务并返回服务器错误
        await session.rollback()
        raise HTTPException(500, detail=f"删除失败：{str(e)}")
    
    return deleted_count

@router.post("/changeArt", response_model=ArtQueryOut, summary="修改文章", description="修改文章")
async def change_art(
    data: ArtChangeIn,
    session: AsyncSession = Depends(get_session),
):
    """
    修改文章接口
    
    修改文章记录。
    """
    art_repo = ArtRepository(session=session)
    # 哪怕是通过
    artId = await art_repo.change_by_id(data.id, data.sex)

    await session.commit()
    return ArtQueryOut(
        code=200,
        message="修改成功",
        data=artId
    )
# 创建认证处理器实例（单例模式）
auth_handler = AuthHandler()
@router.post("/queryArt", response_model=list[ArtOut], summary="查询文章", description="查询文章")
async def query_art(
    data: ArtQueryIn,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(auth_handler.auth_access_dependency)
):
    """
    查询文章接口

    查询文章记录。
    """
    art_repo = ArtRepository(session=session)
    artList = await art_repo.query_by_sex(data.page, data.size, data.sex)

    # 将 ORM 对象转换为 Pydantic 响应模型
    # result = [ArtOut.from_orm_with_thumbnail(art) for art in artList]

    await session.commit()
    return artList

@router.post("/queryArtOut", response_model=ArtQueryOut, summary="查询文章", description="查询文章")
async def query_art_out(
    data: ArtQueryIn,
    session: AsyncSession = Depends(get_session),
):
    """
    查询文章接口

    查询文章记录，返回标准格式的响应（包含 code、data、message）。
    ArtQueryOut 会自动将 ORM 对象转换为 Pydantic 响应模型。
    """
    art_repo = ArtRepository(session=session)
    artList = await art_repo.query_by_sex(data.page, data.size, data.sex)

    # 将 ORM 对象转换为 Pydantic 响应模型
    # result = [ArtOut.model_validate(art, from_attributes=True) for art in artList]
    await session.commit()
    
    # 返回标准格式的响应，ArtQueryOut 会自动转换 ORM 对象
    return ArtQueryOut(
        code=200,
        message="查询成功",
        data=artList  # 直接传入 ORM 对象列表，ArtQueryOut 会自动转换
    )