"""
学校相关路由模块

本模块提供了学校相关的 API 端点。
"""

from fastapi import APIRouter, Depends, HTTPException, Path
from models import AsyncSession
from dependencies import get_session
from repository.school.school_repo import SchoolRepository
from schemas.school.school import SchoolIn, SchoolOut, SchoolUpdateIn, SchoolListResponse
from schemas import ResponseOut


# 创建学校相关的路由组
router = APIRouter(prefix="/school", tags=["school"])


@router.post("", response_model=ResponseOut, summary="创建学校", description="创建一所新学校")
async def create_school(
    data: SchoolIn,
    session: AsyncSession = Depends(get_session),
):
    """
    创建学校接口
    
    Args:
        data (SchoolIn): 学校信息
        session (AsyncSession): 数据库会话
        
    Returns:
        ResponseOut: 操作结果
    """
    try:
        school_repo = SchoolRepository(session=session)
        await school_repo.create(data.name, data.address)
        await session.commit()
        return ResponseOut(result="success")
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"创建学校失败: {str(e)}")


@router.get("", response_model=SchoolListResponse, summary="查询所有学校", description="获取所有学校列表")
async def get_all_schools(
    session: AsyncSession = Depends(get_session),
):
    """
    查询所有学校接口
    
    Args:
        session (AsyncSession): 数据库会话
        
    Returns:
        SchoolListResponse: 学校列表
    """
    try:
        school_repo = SchoolRepository(session=session)
        schools = await school_repo.get_all()
        school_outs = [SchoolOut.model_validate(school, from_attributes=True) for school in schools]
        return SchoolListResponse(code=200, message="查询成功", data=school_outs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询学校列表失败: {str(e)}")


@router.get("/{school_id}", response_model=SchoolOut, summary="查询学校", description="根据ID查询学校信息")
async def get_school(
    school_id: int = Path(..., description="学校ID"),
    session: AsyncSession = Depends(get_session),
):
    """
    根据ID查询学校接口
    
    Args:
        school_id (int): 学校ID
        session (AsyncSession): 数据库会话
        
    Returns:
        SchoolOut: 学校信息
        
    Raises:
        HTTPException: 当学校不存在时
    """
    try:
        school_repo = SchoolRepository(session=session)
        school = await school_repo.get_by_id(school_id)
        if not school:
            raise HTTPException(status_code=404, detail=f"学校ID {school_id} 不存在")
        return SchoolOut.model_validate(school, from_attributes=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询学校失败: {str(e)}")


@router.put("/{school_id}", response_model=ResponseOut, summary="更新学校", description="更新学校信息")
async def update_school(
    school_id: int = Path(..., description="学校ID"),
    data: SchoolUpdateIn = ...,
    session: AsyncSession = Depends(get_session),
):
    """
    更新学校接口
    
    Args:
        school_id (int): 学校ID
        data (SchoolUpdateIn): 更新的学校信息
        session (AsyncSession): 数据库会话
        
    Returns:
        ResponseOut: 操作结果
        
    Raises:
        HTTPException: 当学校不存在时
    """
    try:
        school_repo = SchoolRepository(session=session)
        school = await school_repo.update(
            school_id,
            name=data.name,
            address=data.address
        )
        if not school:
            raise HTTPException(status_code=404, detail=f"学校ID {school_id} 不存在")
        await session.commit()
        return ResponseOut(result="success")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"更新学校失败: {str(e)}")


@router.delete("/{school_id}", response_model=ResponseOut, summary="删除学校", description="删除学校")
async def delete_school(
    school_id: int = Path(..., description="学校ID"),
    session: AsyncSession = Depends(get_session),
):
    """
    删除学校接口
    
    Args:
        school_id (int): 学校ID
        session (AsyncSession): 数据库会话
        
    Returns:
        ResponseOut: 操作结果
        
    Raises:
        HTTPException: 当学校不存在时
    """
    try:
        school_repo = SchoolRepository(session=session)
        # 先检查学校是否存在
        school = await school_repo.get_by_id(school_id)
        if not school:
            raise HTTPException(status_code=404, detail=f"学校ID {school_id} 不存在")
        
        count = await school_repo.delete(school_id)
        await session.commit()
        if count == 0:
            raise HTTPException(status_code=404, detail=f"学校ID {school_id} 不存在")
        return ResponseOut(result="success")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"删除学校失败: {str(e)}")
