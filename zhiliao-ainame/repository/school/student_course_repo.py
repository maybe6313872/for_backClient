"""
学生课程关联数据仓库模块

本模块提供了学生课程关联的数据访问层（Repository Pattern）。
"""

from models import AsyncSession
from models.school.student_course import StudentCourse
from models.school.student import Student
from sqlalchemy import delete, select
from typing import List, Optional


class StudentCourseRepository:
    """
    学生课程关联数据仓库类
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, student_id: int, course_id: int, score: Optional[float] = None) -> StudentCourse:
        """
        创建学生课程关联记录
        
        Args:
            student_id (int): 学生ID
            course_id (int): 课程ID
            score (Optional[float]): 分数
            
        Returns:
            StudentCourse: 创建的关联对象
        """
        student_course = StudentCourse(
            student_id=student_id,
            course_id=course_id,
            score=score
        )
        self.session.add(student_course)
        await self.session.flush()
        return student_course

    async def get_by_id(self, id: int) -> Optional[StudentCourse]:
        """
        根据ID查询关联记录
        
        Args:
            id (int): 关联记录ID
            
        Returns:
            Optional[StudentCourse]: 关联对象
        """
        stmt = select(StudentCourse).where(StudentCourse.id == id)
        return await self.session.scalar(stmt)

    async def get_all(self) -> List[StudentCourse]:
        """
        查询所有关联记录
        
        Returns:
            List[StudentCourse]: 关联对象列表
        """
        stmt = select(StudentCourse).order_by(StudentCourse.id)
        result = await self.session.scalars(stmt)
        return result.all()

    async def get_by_student_id(self, student_id: int) -> List[StudentCourse]:
        """
        根据学生ID查询该学生的所有课程关联
        
        Args:
            student_id (int): 学生ID
            
        Returns:
            List[StudentCourse]: 关联对象列表
        """
        stmt = select(StudentCourse).where(StudentCourse.student_id == student_id).order_by(StudentCourse.id)
        result = await self.session.scalars(stmt)
        return result.all()

    async def get_by_course_id(self, course_id: int) -> List[StudentCourse]:
        """
        根据课程ID查询选修该课程的所有学生关联
        
        Args:
            course_id (int): 课程ID
            
        Returns:
            List[StudentCourse]: 关联对象列表
        """
        stmt = select(StudentCourse).where(StudentCourse.course_id == course_id).order_by(StudentCourse.id)
        result = await self.session.scalars(stmt)
        return result.all()

    async def get_students_by_course_id(self, course_id: int) -> List[dict]:
        """
        根据课程ID查询选修该课程的所有学生信息（包含分数）
        
        Args:
            course_id (int): 课程ID
            
        Returns:
            List[dict]: 学生信息列表，每个元素包含学生信息和分数
        """
        stmt = select(StudentCourse, Student).join(
            Student, StudentCourse.student_id == Student.id
        ).where(StudentCourse.course_id == course_id).order_by(Student.id)
        
        result = await self.session.execute(stmt)
        students_data = []
        for student_course, student in result.all():
            students_data.append({
                "student_id": student.id,
                "student_name": student.name,
                "student_sex": student.sex,
                "student_age": student.age,
                "teacher_id": student.teacher_id,
                "score": student_course.score
            })
        return students_data

    async def get_by_student_and_course(self, student_id: int, course_id: int) -> Optional[StudentCourse]:
        """
        根据学生ID和课程ID查询关联记录
        
        Args:
            student_id (int): 学生ID
            course_id (int): 课程ID
            
        Returns:
            Optional[StudentCourse]: 关联对象
        """
        stmt = select(StudentCourse).where(
            StudentCourse.student_id == student_id,
            StudentCourse.course_id == course_id
        )
        return await self.session.scalar(stmt)

    async def update(self, id: int, score: Optional[float] = None) -> Optional[StudentCourse]:
        """
        更新关联记录（主要是更新分数）
        
        Args:
            id (int): 关联记录ID
            score (Optional[float]): 分数
            
        Returns:
            Optional[StudentCourse]: 更新后的关联对象
        """
        student_course = await self.get_by_id(id)
        if student_course:
            if score is not None:
                student_course.score = score
        return student_course

    async def create_batch(
        self,
        student_id: int,
        course_ids: List[int],
        scores: Optional[List[float]] = None
    ) -> List[StudentCourse]:
        """
        批量创建学生课程关联记录
        
        Args:
            student_id (int): 学生ID
            course_ids (List[int]): 课程ID列表
            scores (Optional[List[float]]): 分数列表（可选，与course_ids一一对应）
            
        Returns:
            List[StudentCourse]: 创建的关联对象列表
        """
        # 检查scores长度是否与course_ids匹配
        if scores is not None and len(scores) != len(course_ids):
            raise ValueError("分数数组长度必须与课程ID数组长度一致")
        
        # 检查是否已存在关联（避免重复选课）
        existing_courses = []
        for course_id in course_ids:
            existing = await self.get_by_student_and_course(student_id, course_id)
            if existing:
                existing_courses.append(course_id)
        
        if existing_courses:
            raise ValueError(f"学生已选修以下课程: {existing_courses}")
        
        # 批量创建关联记录
        student_courses = []
        for idx, course_id in enumerate(course_ids):
            score = scores[idx] if scores is not None else None
            student_course = StudentCourse(
                student_id=student_id,
                course_id=course_id,
                score=score
            )
            self.session.add(student_course)
            student_courses.append(student_course)
        
        await self.session.flush()
        return student_courses

    async def delete(self, id: int) -> int:
        """
        删除关联记录
        
        Args:
            id (int): 关联记录ID
            
        Returns:
            int: 删除的记录数
        """
        stmt = delete(StudentCourse).where(StudentCourse.id == id)
        result = await self.session.execute(stmt)
        return result.rowcount

    async def delete_by_student_id(self, student_id: int) -> int:
        """
        删除指定学生的所有课程关联
        
        Args:
            student_id (int): 学生ID
            
        Returns:
            int: 删除的记录数
        """
        stmt = delete(StudentCourse).where(StudentCourse.student_id == student_id)
        result = await self.session.execute(stmt)
        return result.rowcount

    async def replace_batch(
        self,
        student_id: int,
        course_ids: List[int],
        scores: Optional[List[float]] = None
    ) -> List[StudentCourse]:
        """
        替换学生的所有课程关联（先删除所有已选课程，再批量添加新课程）
        
        Args:
            student_id (int): 学生ID
            course_ids (List[int]): 课程ID列表
            scores (Optional[List[float]]): 分数列表（可选，与course_ids一一对应）
            
        Returns:
            List[StudentCourse]: 创建的关联对象列表
        """
        # 检查scores长度是否与course_ids匹配
        if scores is not None and len(scores) != len(course_ids):
            raise ValueError("分数数组长度必须与课程ID数组长度一致")
        
        # 先删除该学生的所有已选课程
        await self.delete_by_student_id(student_id)
        
        # 如果没有新课程要添加，直接返回空列表
        if not course_ids:
            return []
        
        # 批量创建新的关联记录
        student_courses = []
        for idx, course_id in enumerate(course_ids):
            score = scores[idx] if scores is not None else None
            student_course = StudentCourse(
                student_id=student_id,
                course_id=course_id,
                score=score
            )
            self.session.add(student_course)
            student_courses.append(student_course)
        
        await self.session.flush()
        return student_courses
