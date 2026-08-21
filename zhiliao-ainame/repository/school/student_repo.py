"""
学生数据仓库模块

本模块提供了学生的数据访问层（Repository Pattern）。
"""

from models import AsyncSession
from models.school.student import Student
from models.school.student_course import StudentCourse
from models.school.course import Course
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload, joinedload
from typing import List, Optional


class StudentRepository:
    """
    学生数据仓库类
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, name: str, sex: str, age: int, teacher_id: int) -> Student:
        """
        创建学生记录
        
        Args:
            name (str): 学生姓名
            sex (str): 性别
            age (int): 年龄
            teacher_id (int): 所属班主任ID
            
        Returns:
            Student: 创建的学生对象
        """
        student = Student(name=name, sex=sex, age=age, teacher_id=teacher_id)
        self.session.add(student)
        await self.session.flush()
        return student

    async def get_by_id(self, id: int, load_courses: bool = False) -> Optional[Student]:
        """
        根据ID查询学生
        
        Args:
            id (int): 学生ID
            load_courses (bool): 是否加载课程关联（默认False）
            
        Returns:
            Optional[Student]: 学生对象
        """
        if load_courses:
            # 加载课程关联
            stmt = select(Student).options(
                selectinload(Student.courses)
            ).where(Student.id == id)
        else:
            stmt = select(Student).where(Student.id == id)
        return await self.session.scalar(stmt)

    async def get_all(self, load_courses: bool = False) -> List[Student]:
        """
        查询所有学生
        
        Args:
            load_courses (bool): 是否加载课程关联（默认False）
        
        Returns:
            List[Student]: 学生对象列表
        """
        if load_courses:
            stmt = select(Student).options(
                selectinload(Student.courses)
            ).order_by(Student.id)
        else:
            stmt = select(Student).order_by(Student.id)
        result = await self.session.scalars(stmt)
        return result.all()

    async def get_by_teacher_id(self, teacher_id: int, load_courses: bool = False) -> List[Student]:
        """
        根据班主任ID查询该班主任的所有学生
        
        Args:
            teacher_id (int): 班主任ID
            load_courses (bool): 是否加载课程关联（默认False）
            
        Returns:
            List[Student]: 学生对象列表
        """
        if load_courses:
            stmt = select(Student).options(
                selectinload(Student.courses)
            ).where(Student.teacher_id == teacher_id).order_by(Student.id)
        else:
            stmt = select(Student).where(Student.teacher_id == teacher_id).order_by(Student.id)
        result = await self.session.scalars(stmt)
        return result.all()
    
    async def get_student_courses_with_scores(self, student_id: int) -> List[dict]:
        """
        获取学生的课程信息（包含分数）
        
        Args:
            student_id (int): 学生ID
            
        Returns:
            List[dict]: 课程信息列表，每个元素包含course和score
        """
        stmt = select(StudentCourse, Course).join(
            Course, StudentCourse.course_id == Course.id
        ).where(StudentCourse.student_id == student_id)
        
        result = await self.session.execute(stmt)
        courses_data = []
        for student_course, course in result.all():
            courses_data.append({
                "course": course,
                "score": student_course.score
            })
        return courses_data

    async def update(
        self,
        id: int,
        name: Optional[str] = None,
        sex: Optional[str] = None,
        age: Optional[int] = None,
        teacher_id: Optional[int] = None
    ) -> Optional[Student]:
        """
        更新学生记录
        
        Args:
            id (int): 学生ID
            name (Optional[str]): 学生姓名
            sex (Optional[str]): 性别
            age (Optional[int]): 年龄
            teacher_id (Optional[int]): 所属班主任ID
            
        Returns:
            Optional[Student]: 更新后的学生对象
        """
        student = await self.get_by_id(id)
        if student:
            if name is not None:
                student.name = name
            if sex is not None:
                student.sex = sex
            if age is not None:
                student.age = age
            if teacher_id is not None:
                student.teacher_id = teacher_id
        return student

    async def delete(self, id: int) -> int:
        """
        删除学生记录（同时删除该学生的所有课程关联）
        
        Args:
            id (int): 学生ID
            
        Returns:
            int: 删除的记录数（1表示成功，0表示学生不存在）
        """
        # 先检查学生是否存在
        student = await self.get_by_id(id)
        if not student:
            return 0
        
        # 先删除该学生的所有课程关联（student_course中间表）
        stmt = delete(StudentCourse).where(StudentCourse.student_id == id)
        await self.session.execute(stmt)
        
        # 删除学生记录
        stmt = delete(Student).where(Student.id == id)
        result = await self.session.execute(stmt)
        return result.rowcount
