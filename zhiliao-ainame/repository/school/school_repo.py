"""
学校数据仓库模块

本模块提供了学校的数据访问层（Repository Pattern）。
封装了所有与学校相关的数据库操作。
"""

from models import AsyncSession
from models.school.school import School
from models.school.teacher import Teacher
from models.school.student import Student
from models.school.student_course import StudentCourse
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional


class SchoolRepository:
    """
    学校数据仓库类
    
    提供学校相关的数据库操作方法。
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, name: str, address: str) -> School:
        """
        创建学校记录
        
        Args:
            name (str): 校名
            address (str): 学校地址
            
        Returns:
            School: 创建的学校对象
        """
        school = School(name=name, address=address)
        self.session.add(school)
        await self.session.flush()
        return school

    async def get_by_id(self, id: int, load_relations: bool = False) -> Optional[School]:
        """
        根据ID查询学校
        
        Args:
            id (int): 学校ID
            load_relations (bool): 是否加载关联关系（用于级联删除）
            
        Returns:
            Optional[School]: 学校对象，如果不存在返回None
        """
        if load_relations:
            # 加载关联的teachers和students（用于级联删除）
            stmt = select(School).options(
                selectinload(School.teachers).selectinload(Teacher.students)
            ).where(School.id == id)
        else:
            stmt = select(School).where(School.id == id)
        return await self.session.scalar(stmt)

    async def get_all(self) -> List[School]:
        """
        查询所有学校
        
        Returns:
            List[School]: 学校对象列表
        """
        stmt = select(School).order_by(School.id)
        result = await self.session.scalars(stmt)
        return result.all()

    async def update(self, id: int, name: Optional[str] = None, address: Optional[str] = None) -> Optional[School]:
        """
        更新学校记录
        
        Args:
            id (int): 学校ID
            name (Optional[str]): 校名
            address (Optional[str]): 学校地址
            
        Returns:
            Optional[School]: 更新后的学校对象，如果不存在返回None
        """
        school = await self.get_by_id(id)
        if school:
            if name is not None:
                school.name = name
            if address is not None:
                school.address = address
        return school

    async def delete(self, id: int) -> int:
        """
        删除学校记录（级联删除该学校下的所有班主任、学生及其课程关联）
        
        Args:
            id (int): 学校ID
            
        Returns:
            int: 删除的记录数（1表示成功，0表示学校不存在）
        """
        # 加载学校及其所有关联的teachers和students（用于级联删除）
        school = await self.get_by_id(id, load_relations=True)
        if not school:
            return 0
        
        # 收集所有学生的ID（这些学生的课程关联需要删除）
        student_ids = []
        if school.teachers:
            for teacher in school.teachers:
                if teacher.students:
                    student_ids.extend([student.id for student in teacher.students])
        
        # 如果有学生，先删除这些学生的所有课程关联（student_course中间表）
        if student_ids:
            stmt = delete(StudentCourse).where(StudentCourse.student_id.in_(student_ids))
            await self.session.execute(stmt)
        
        # 删除学校对象，SQLAlchemy会自动级联删除所有关联的teachers和students
        # 因为模型中已经配置了 cascade="all, delete-orphan"
        await self.session.delete(school)
        return 1
