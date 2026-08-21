"""
学生相关路由模块

本模块提供了学生相关的 API 端点。
"""

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from models import AsyncSession
from dependencies import get_session
from repository.school.student_repo import StudentRepository
from schemas.school.student import StudentIn, StudentOut, StudentUpdateIn, StudentListResponse, CourseWithScore
from schemas.school.course import CourseOut
from schemas import ResponseOut


# 创建学生相关的路由组
router = APIRouter(prefix="/student", tags=["student"])


@router.post("", response_model=ResponseOut, summary="创建学生", description="创建一位新学生")
async def create_student(
    data: StudentIn,
    session: AsyncSession = Depends(get_session),
):
    """
    创建学生接口
    
    Args:
        data (StudentIn): 学生信息
        session (AsyncSession): 数据库会话
        
    Returns:
        ResponseOut: 操作结果
    """
    try:
        student_repo = StudentRepository(session=session)
        await student_repo.create(data.name, data.sex, data.age, data.teacher_id)
        await session.commit()
        return ResponseOut(result="success")
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"创建学生失败: {str(e)}")


@router.get("", response_model=StudentListResponse, summary="查询所有学生", description="获取所有学生列表（包含所选课程）")
async def get_all_students(
    teacher_id: int | None = Query(None, description="班主任ID（可选，用于筛选）"),
    session: AsyncSession = Depends(get_session),
):
    """
    查询所有学生接口（包含所选课程信息）
    
    Args:
        teacher_id (int | None): 可选，班主任ID，用于筛选该班主任的学生
        session (AsyncSession): 数据库会话
        
    Returns:
        StudentListResponse: 学生列表（包含所选课程）
    """
    try:
        student_repo = StudentRepository(session=session)
        if teacher_id:
            students = await student_repo.get_by_teacher_id(teacher_id, load_courses=True)
        else:
            students = await student_repo.get_all(load_courses=True)
        
        # 构建学生响应列表，包含课程信息
        student_outs = []
        for student in students:
            # 获取该学生的课程信息（包含分数）
            courses_with_scores = await student_repo.get_student_courses_with_scores(student.id)
            courses_data = [
                CourseWithScore(
                    course=CourseOut.model_validate(item["course"], from_attributes=True),
                    score=item["score"]
                )
                for item in courses_with_scores
            ]
            
            student_out = StudentOut(
                id=student.id,
                name=student.name,
                sex=student.sex,
                age=student.age,
                teacher_id=student.teacher_id,
                created_time=student.created_time,
                courses=courses_data
            )
            student_outs.append(student_out)
        
        return StudentListResponse(code=200, message="查询成功", data=student_outs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询学生列表失败: {str(e)}")


@router.get("/{student_id}", response_model=StudentOut, summary="查询学生", description="根据ID查询学生信息（包含所选课程）")
async def get_student(
    student_id: int = Path(..., description="学生ID"),
    session: AsyncSession = Depends(get_session),
):
    """
    根据ID查询学生接口（包含所选课程信息）
    
    Args:
        student_id (int): 学生ID
        session (AsyncSession): 数据库会话
        
    Returns:
        StudentOut: 学生信息（包含所选课程）
        
    Raises:
        HTTPException: 当学生不存在时
    """
    try:
        student_repo = StudentRepository(session=session)
        student = await student_repo.get_by_id(student_id, load_courses=True)
        if not student:
            raise HTTPException(status_code=404, detail=f"学生ID {student_id} 不存在")
        
        # 获取该学生的课程信息（包含分数）
        courses_with_scores = await student_repo.get_student_courses_with_scores(student_id)
        courses_data = [
            CourseWithScore(
                course=CourseOut.model_validate(item["course"], from_attributes=True),
                score=item["score"]
            )
            for item in courses_with_scores
        ]
        
        student_out = StudentOut(
            id=student.id,
            name=student.name,
            sex=student.sex,
            age=student.age,
            teacher_id=student.teacher_id,
            created_time=student.created_time,
            courses=courses_data
        )
        return student_out
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询学生失败: {str(e)}")


@router.put("/{student_id}", response_model=ResponseOut, summary="更新学生", description="更新学生信息")
async def update_student(
    student_id: int = Path(..., description="学生ID"),
    data: StudentUpdateIn = ...,
    session: AsyncSession = Depends(get_session),
):
    """
    更新学生接口
    
    Args:
        student_id (int): 学生ID
        data (StudentUpdateIn): 更新的学生信息
        session (AsyncSession): 数据库会话
        
    Returns:
        ResponseOut: 操作结果
        
    Raises:
        HTTPException: 当学生不存在时
    """
    try:
        student_repo = StudentRepository(session=session)
        student = await student_repo.update(
            student_id,
            name=data.name,
            sex=data.sex,
            age=data.age,
            teacher_id=data.teacher_id
        )
        if not student:
            raise HTTPException(status_code=404, detail=f"学生ID {student_id} 不存在")
        await session.commit()
        return ResponseOut(result="success")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"更新学生失败: {str(e)}")


@router.delete("/{student_id}", response_model=ResponseOut, summary="删除学生", description="删除学生")
async def delete_student(
    student_id: int = Path(..., description="学生ID"),
    session: AsyncSession = Depends(get_session),
):
    """
    删除学生接口
    
    Args:
        student_id (int): 学生ID
        session (AsyncSession): 数据库会话
        
    Returns:
        ResponseOut: 操作结果
        
    Raises:
        HTTPException: 当学生不存在时
    """
    try:
        student_repo = StudentRepository(session=session)
        # 先检查学生是否存在
        student = await student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(status_code=404, detail=f"学生ID {student_id} 不存在")
        
        count = await student_repo.delete(student_id)
        await session.commit()
        if count == 0:
            raise HTTPException(status_code=404, detail=f"学生ID {student_id} 不存在")
        return ResponseOut(result="success")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"删除学生失败: {str(e)}")
