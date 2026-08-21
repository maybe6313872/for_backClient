"""
学生课程关联相关路由模块

本模块提供了学生课程关联相关的 API 端点。
"""

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from models import AsyncSession
from dependencies import get_session
from repository.school.student_course_repo import StudentCourseRepository
from schemas.school.student_course import (
    StudentCourseIn,
    StudentCourseOut,
    StudentCourseUpdateIn,
    StudentCourseListResponse,
    StudentCourseBatchIn,
    StudentsByCourseResponse,
    StudentWithScore
)
from schemas import ResponseOut


# 创建学生课程关联相关的路由组
router = APIRouter(prefix="/student-course", tags=["student-course"])


@router.post("", response_model=ResponseOut, summary="批量创建学生课程关联", description="为一个学生批量添加多个课程（批量选课，以入参course_ids为准，会先取消所有已选课程）")
async def create_student_courses_batch(
    data: StudentCourseBatchIn,
    session: AsyncSession = Depends(get_session),
):
    """
    批量创建学生课程关联接口（学生批量选课）
    
    注意：此接口会先删除该学生的所有已选课程，然后根据入参的course_ids数组重新选课。
    这样可以确保学生的选课与入参完全一致。
    
    Args:
        data (StudentCourseBatchIn): 批量选课信息（学生ID + 课程ID数组）
        session (AsyncSession): 数据库会话
        
    Returns:
        ResponseOut: 操作结果
        
    Raises:
        HTTPException: 当参数错误时
    """
    try:
        student_course_repo = StudentCourseRepository(session=session)
        # 使用 replace_batch 方法：先删除所有已选课程，再批量添加新课程
        await student_course_repo.replace_batch(
            data.student_id,
            data.course_ids,
            data.scores
        )
        await session.commit()
        return ResponseOut(result="success")
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"批量创建学生课程关联失败: {str(e)}")


@router.post("/single", response_model=ResponseOut, summary="创建单个学生课程关联", description="为学生添加单个课程（单个选课）")
async def create_student_course(
    data: StudentCourseIn,
    session: AsyncSession = Depends(get_session),
):
    """
    创建单个学生课程关联接口（学生选课）
    
    Args:
        data (StudentCourseIn): 学生课程关联信息
        session (AsyncSession): 数据库会话
        
    Returns:
        ResponseOut: 操作结果
        
    Raises:
        HTTPException: 当关联已存在时
    """
    try:
        student_course_repo = StudentCourseRepository(session=session)
        # 检查是否已存在关联
        existing = await student_course_repo.get_by_student_and_course(data.student_id, data.course_id)
        if existing:
            raise HTTPException(status_code=400, detail="该学生已选修此课程")
        
        await student_course_repo.create(data.student_id, data.course_id, data.score)
        await session.commit()
        return ResponseOut(result="success")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"创建学生课程关联失败: {str(e)}")


@router.get("", response_model=StudentCourseListResponse, summary="查询所有学生课程关联", description="获取所有学生课程关联列表")
async def get_all_student_courses(
    student_id: int | None = Query(None, description="学生ID（可选，用于筛选）"),
    course_id: int | None = Query(None, description="课程ID（可选，用于筛选）"),
    session: AsyncSession = Depends(get_session),
):
    """
    查询所有学生课程关联接口
    
    Args:
        student_id (int | None): 可选，学生ID，用于筛选该学生的课程
        course_id (int | None): 可选，课程ID，用于筛选选修该课程的学生
        session (AsyncSession): 数据库会话
        
    Returns:
        StudentCourseListResponse: 学生课程关联列表
    """
    try:
        student_course_repo = StudentCourseRepository(session=session)
        if student_id:
            student_courses = await student_course_repo.get_by_student_id(student_id)
        elif course_id:
            student_courses = await student_course_repo.get_by_course_id(course_id)
        else:
            student_courses = await student_course_repo.get_all()
        
        student_course_outs = [
            StudentCourseOut.model_validate(sc, from_attributes=True)
            for sc in student_courses
        ]
        return StudentCourseListResponse(code=200, message="查询成功", data=student_course_outs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询学生课程关联列表失败: {str(e)}")


@router.get("/course/{course_id}/students", response_model=StudentsByCourseResponse, summary="根据课程ID查询学生", description="查询所有选中指定课程的学生列表（包含分数）")
async def get_students_by_course(
    course_id: int = Path(..., description="课程ID"),
    session: AsyncSession = Depends(get_session),
):
    """
    根据课程ID查询所有选中该课程的学生接口
    
    Args:
        course_id (int): 课程ID
        session (AsyncSession): 数据库会话
        
    Returns:
        StudentsByCourseResponse: 学生列表（包含分数）
    """
    try:
        student_course_repo = StudentCourseRepository(session=session)
        students_data = await student_course_repo.get_students_by_course_id(course_id)
        
        students_list = [
            StudentWithScore(
                student_id=item["student_id"],
                student_name=item["student_name"],
                student_sex=item["student_sex"],
                student_age=item["student_age"],
                teacher_id=item["teacher_id"],
                score=item["score"]
            )
            for item in students_data
        ]
        
        return StudentsByCourseResponse(code=200, message="查询成功", data=students_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询课程学生列表失败: {str(e)}")


@router.get("/{id}", response_model=StudentCourseOut, summary="查询学生课程关联", description="根据ID查询学生课程关联信息")
async def get_student_course(
    id: int = Path(..., description="关联记录ID"),
    session: AsyncSession = Depends(get_session),
):
    """
    根据ID查询学生课程关联接口
    
    Args:
        id (int): 关联记录ID
        session (AsyncSession): 数据库会话
        
    Returns:
        StudentCourseOut: 学生课程关联信息
        
    Raises:
        HTTPException: 当关联不存在时
    """
    try:
        student_course_repo = StudentCourseRepository(session=session)
        student_course = await student_course_repo.get_by_id(id)
        if not student_course:
            raise HTTPException(status_code=404, detail=f"关联记录ID {id} 不存在")
        return StudentCourseOut.model_validate(student_course, from_attributes=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询学生课程关联失败: {str(e)}")


@router.put("/{id}", response_model=ResponseOut, summary="更新学生课程关联", description="更新学生课程分数")
async def update_student_course(
    id: int = Path(..., description="关联记录ID"),
    data: StudentCourseUpdateIn = ...,
    session: AsyncSession = Depends(get_session),
):
    """
    更新学生课程关联接口（主要用于更新分数）
    
    Args:
        id (int): 关联记录ID
        data (StudentCourseUpdateIn): 更新的信息（主要是分数）
        session (AsyncSession): 数据库会话
        
    Returns:
        ResponseOut: 操作结果
        
    Raises:
        HTTPException: 当关联不存在时
    """
    try:
        student_course_repo = StudentCourseRepository(session=session)
        student_course = await student_course_repo.update(id, score=data.score)
        if not student_course:
            raise HTTPException(status_code=404, detail=f"关联记录ID {id} 不存在")
        await session.commit()
        return ResponseOut(result="success")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"更新学生课程关联失败: {str(e)}")


@router.delete("/{id}", response_model=ResponseOut, summary="删除学生课程关联", description="删除学生课程关联（退课）")
async def delete_student_course(
    id: int = Path(..., description="关联记录ID"),
    session: AsyncSession = Depends(get_session),
):
    """
    删除学生课程关联接口（学生退课）
    
    Args:
        id (int): 关联记录ID
        session (AsyncSession): 数据库会话
        
    Returns:
        ResponseOut: 操作结果
        
    Raises:
        HTTPException: 当关联不存在时
    """
    try:
        student_course_repo = StudentCourseRepository(session=session)
        # 先检查关联是否存在
        student_course = await student_course_repo.get_by_id(id)
        if not student_course:
            raise HTTPException(status_code=404, detail=f"关联记录ID {id} 不存在")
        
        count = await student_course_repo.delete(id)
        await session.commit()
        if count == 0:
            raise HTTPException(status_code=404, detail=f"关联记录ID {id} 不存在")
        return ResponseOut(result="success")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"删除学生课程关联失败: {str(e)}")
