"""
班主任相关路由模块

本模块提供了班主任相关的 API 端点。
"""

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from models import AsyncSession
from dependencies import get_session
from repository.school.teacher_repo import TeacherRepository
from schemas.school.teacher import TeacherIn, TeacherOut, TeacherUpdateIn, TeacherListResponse
from schemas import ResponseOut


# 创建班主任相关的路由组
router = APIRouter(prefix="/teacher", tags=["teacher"])


@router.post("", response_model=ResponseOut, summary="创建班主任", description="创建一位新班主任")
async def create_teacher(
    data: TeacherIn,
    session: AsyncSession = Depends(get_session),
):
    """
    创建班主任接口
    
    Args:
        data (TeacherIn): 班主任信息
        session (AsyncSession): 数据库会话
        
    Returns:
        ResponseOut: 操作结果
    """
    try:
        teacher_repo = TeacherRepository(session=session)
        await teacher_repo.create(data.name, data.sex, data.age, data.school_id)
        await session.commit()
        return ResponseOut(result="success")
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"创建班主任失败: {str(e)}")


@router.get("", response_model=TeacherListResponse, summary="查询所有班主任", description="获取所有班主任列表")
async def get_all_teachers(
    school_id: int | None = Query(None, description="学校ID（可选，用于筛选）"),
    session: AsyncSession = Depends(get_session),
):
    """
    查询所有班主任接口
    
    Args:
        school_id (int | None): 可选，学校ID，用于筛选该学校的班主任
        session (AsyncSession): 数据库会话
        
    Returns:
        TeacherListResponse: 班主任列表
    """
    try:
        teacher_repo = TeacherRepository(session=session)
        if school_id:
            teachers = await teacher_repo.get_by_school_id(school_id)
        else:
            teachers = await teacher_repo.get_all()
        teacher_outs = [TeacherOut.model_validate(teacher, from_attributes=True) for teacher in teachers]
        return TeacherListResponse(code=200, message="查询成功", data=teacher_outs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询班主任列表失败: {str(e)}")


@router.get("/{teacher_id}", response_model=TeacherOut, summary="查询班主任", description="根据ID查询班主任信息")
async def get_teacher(
    teacher_id: int = Path(..., description="班主任ID"),
    session: AsyncSession = Depends(get_session),
):
    """
    根据ID查询班主任接口
    
    Args:
        teacher_id (int): 班主任ID
        session (AsyncSession): 数据库会话
        
    Returns:
        TeacherOut: 班主任信息
        
    Raises:
        HTTPException: 当班主任不存在时
    """
    try:
        teacher_repo = TeacherRepository(session=session)
        teacher = await teacher_repo.get_by_id(teacher_id)
        if not teacher:
            raise HTTPException(status_code=404, detail=f"班主任ID {teacher_id} 不存在")
        return TeacherOut.model_validate(teacher, from_attributes=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询班主任失败: {str(e)}")


@router.put("/{teacher_id}", response_model=ResponseOut, summary="更新班主任", description="更新班主任信息")
async def update_teacher(
    teacher_id: int = Path(..., description="班主任ID"),
    data: TeacherUpdateIn = ...,
    session: AsyncSession = Depends(get_session),
):
    """
    更新班主任接口
    
    Args:
        teacher_id (int): 班主任ID
        data (TeacherUpdateIn): 更新的班主任信息
        session (AsyncSession): 数据库会话
        
    Returns:
        ResponseOut: 操作结果
        
    Raises:
        HTTPException: 当班主任不存在时
    """
    try:
        teacher_repo = TeacherRepository(session=session)
        teacher = await teacher_repo.update(
            teacher_id,
            name=data.name,
            sex=data.sex,
            age=data.age,
            school_id=data.school_id
        )
        if not teacher:
            raise HTTPException(status_code=404, detail=f"班主任ID {teacher_id} 不存在")
        await session.commit()
        return ResponseOut(result="success")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"更新班主任失败: {str(e)}")


@router.delete("/{teacher_id}", response_model=ResponseOut, summary="删除班主任", description="删除班主任")
async def delete_teacher(
    teacher_id: int = Path(..., description="班主任ID"),
    session: AsyncSession = Depends(get_session),
):
    """
    删除班主任接口
    
    Args:
        teacher_id (int): 班主任ID
        session (AsyncSession): 数据库会话
        
    Returns:
        ResponseOut: 操作结果
        
    Raises:
        HTTPException: 当班主任不存在时
    """
    try:
        teacher_repo = TeacherRepository(session=session)
        # 先检查班主任是否存在
        teacher = await teacher_repo.get_by_id(teacher_id)
        if not teacher:
            raise HTTPException(status_code=404, detail=f"班主任ID {teacher_id} 不存在")
        
        count = await teacher_repo.delete(teacher_id)
        await session.commit()
        if count == 0:
            raise HTTPException(status_code=404, detail=f"班主任ID {teacher_id} 不存在")
        return ResponseOut(result="success")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"删除班主任失败: {str(e)}")
