"""
课程相关路由模块

本模块提供了课程相关的 API 端点。
"""

from fastapi import APIRouter, Depends, HTTPException, Path
from models import AsyncSession
from dependencies import get_session
from repository.school.course_repo import CourseRepository
from schemas.school.course import CourseIn, CourseOut, CourseUpdateIn, CourseListResponse
from schemas import ResponseOut


# 创建课程相关的路由组
router = APIRouter(prefix="/course", tags=["course"])


@router.post("", response_model=ResponseOut, summary="创建课程", description="创建一门新课程")
async def create_course(
    data: CourseIn,
    session: AsyncSession = Depends(get_session),
):
    """
    创建课程接口
    
    Args:
        data (CourseIn): 课程信息
        session (AsyncSession): 数据库会话
        
    Returns:
        ResponseOut: 操作结果
    """
    try:
        course_repo = CourseRepository(session=session)
        await course_repo.create(data.name, data.credit)
        await session.commit()
        return ResponseOut(result="success")
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"创建课程失败: {str(e)}")


@router.get("", response_model=CourseListResponse, summary="查询所有课程", description="获取所有课程列表")
async def get_all_courses(
    session: AsyncSession = Depends(get_session),
):
    """
    查询所有课程接口
    
    Args:
        session (AsyncSession): 数据库会话
        
    Returns:
        CourseListResponse: 课程列表
    """
    try:
        course_repo = CourseRepository(session=session)
        courses = await course_repo.get_all()
        course_outs = [CourseOut.model_validate(course, from_attributes=True) for course in courses]
        return CourseListResponse(code=200, message="查询成功", data=course_outs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询课程列表失败: {str(e)}")


@router.get("/{course_id}", response_model=CourseOut, summary="查询课程", description="根据ID查询课程信息")
async def get_course(
    course_id: int = Path(..., description="课程ID"),
    session: AsyncSession = Depends(get_session),
):
    """
    根据ID查询课程接口
    
    Args:
        course_id (int): 课程ID
        session (AsyncSession): 数据库会话
        
    Returns:
        CourseOut: 课程信息
        
    Raises:
        HTTPException: 当课程不存在时
    """
    try:
        course_repo = CourseRepository(session=session)
        course = await course_repo.get_by_id(course_id)
        if not course:
            raise HTTPException(status_code=404, detail=f"课程ID {course_id} 不存在")
        return CourseOut.model_validate(course, from_attributes=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询课程失败: {str(e)}")


@router.put("/{course_id}", response_model=ResponseOut, summary="更新课程", description="更新课程信息")
async def update_course(
    course_id: int = Path(..., description="课程ID"),
    data: CourseUpdateIn = ...,
    session: AsyncSession = Depends(get_session),
):
    """
    更新课程接口
    
    Args:
        course_id (int): 课程ID
        data (CourseUpdateIn): 更新的课程信息
        session (AsyncSession): 数据库会话
        
    Returns:
        ResponseOut: 操作结果
        
    Raises:
        HTTPException: 当课程不存在时
    """
    try:
        course_repo = CourseRepository(session=session)
        course = await course_repo.update(
            course_id,
            name=data.name,
            credit=data.credit
        )
        if not course:
            raise HTTPException(status_code=404, detail=f"课程ID {course_id} 不存在")
        await session.commit()
        return ResponseOut(result="success")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"更新课程失败: {str(e)}")


@router.delete("/{course_id}", response_model=ResponseOut, summary="删除课程", description="删除课程")
async def delete_course(
    course_id: int = Path(..., description="课程ID"),
    session: AsyncSession = Depends(get_session),
):
    """
    删除课程接口
    
    Args:
        course_id (int): 课程ID
        session (AsyncSession): 数据库会话
        
    Returns:
        ResponseOut: 操作结果
        
    Raises:
        HTTPException: 当课程不存在时
    """
    try:
        course_repo = CourseRepository(session=session)
        # 先检查课程是否存在
        course = await course_repo.get_by_id(course_id)
        if not course:
            raise HTTPException(status_code=404, detail=f"课程ID {course_id} 不存在")
        
        count = await course_repo.delete(course_id)
        await session.commit()
        if count == 0:
            raise HTTPException(status_code=404, detail=f"课程ID {course_id} 不存在")
        return ResponseOut(result="success")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"删除课程失败: {str(e)}")
