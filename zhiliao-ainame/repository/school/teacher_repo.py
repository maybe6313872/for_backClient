"""
班主任数据仓库模块

本模块提供了班主任的数据访问层（Repository Pattern）。
"""

from models import AsyncSession
from models.school.teacher import Teacher
from models.school.student import Student
from models.school.student_course import StudentCourse
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional


class TeacherRepository:
    """
    班主任数据仓库类
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, name: str, sex: str, age: int, school_id: int) -> Teacher:
        """
        创建班主任记录
        
        Args:
            name (str): 班主任姓名
            sex (str): 性别
            age (int): 年龄
            school_id (int): 所属学校ID
            
        Returns:
            Teacher: 创建的班主任对象
        """
        teacher = Teacher(name=name, sex=sex, age=age, school_id=school_id)
        self.session.add(teacher)
        await self.session.flush()
        return teacher

    async def get_by_id(self, id: int, load_relations: bool = False) -> Optional[Teacher]:
        """
        根据ID查询班主任
        
        Args:
            id (int): 班主任ID
            load_relations (bool): 是否加载关联关系（用于级联删除）
            
        Returns:
            Optional[Teacher]: 班主任对象
        """
        if load_relations:
            # 加载关联的students（用于级联删除）
            stmt = select(Teacher).options(
                selectinload(Teacher.students)
            ).where(Teacher.id == id)
        else:
            stmt = select(Teacher).where(Teacher.id == id)
        return await self.session.scalar(stmt)

    async def get_all(self) -> List[Teacher]:
        """
        查询所有班主任
        
        Returns:
            List[Teacher]: 班主任对象列表
        """
        stmt = select(Teacher).order_by(Teacher.id)
        result = await self.session.scalars(stmt)
        return result.all()

    async def get_by_school_id(self, school_id: int) -> List[Teacher]:
        """
        根据学校ID查询该学校的所有班主任
        
        Args:
            school_id (int): 学校ID
            
        Returns:
            List[Teacher]: 班主任对象列表
        """
        stmt = select(Teacher).where(Teacher.school_id == school_id).order_by(Teacher.id)
        result = await self.session.scalars(stmt)
        return result.all()

    async def update(
        self,
        id: int,
        name: Optional[str] = None,
        sex: Optional[str] = None,
        age: Optional[int] = None,
        school_id: Optional[int] = None
    ) -> Optional[Teacher]:
        """
        更新班主任记录
        
        Args:
            id (int): 班主任ID
            name (Optional[str]): 班主任姓名
            sex (Optional[str]): 性别
            age (Optional[int]): 年龄
            school_id (Optional[int]): 所属学校ID
            
        Returns:
            Optional[Teacher]: 更新后的班主任对象
        """
        teacher = await self.get_by_id(id)
        if teacher:
            if name is not None:
                teacher.name = name
            if sex is not None:
                teacher.sex = sex
            if age is not None:
                teacher.age = age
            if school_id is not None:
                teacher.school_id = school_id
        return teacher

    async def delete(self, id: int) -> int:
        """
        删除班主任记录（级联删除该班主任下的所有学生及其课程关联）
        
        Args:
            id (int): 班主任ID
            
        Returns:
            int: 删除的记录数（1表示成功，0表示班主任不存在）
        """
        # 加载班主任及其所有关联的students（用于级联删除）
        teacher = await self.get_by_id(id, load_relations=True)
        if not teacher:
            return 0
        
        # 先删除所有学生的课程关联（student_course中间表）
        if teacher.students:
            student_ids = [student.id for student in teacher.students]
            if student_ids:
                # 删除这些学生的所有课程关联
                stmt = delete(StudentCourse).where(StudentCourse.student_id.in_(student_ids))
                await self.session.execute(stmt)
        
        # 删除班主任对象，SQLAlchemy会自动级联删除所有关联的students
        # 因为模型中已经配置了 cascade="all, delete-orphan"
        await self.session.delete(teacher)
        return 1
