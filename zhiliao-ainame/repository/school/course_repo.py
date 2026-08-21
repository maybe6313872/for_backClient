"""
课程数据仓库模块

本模块提供了课程的数据访问层（Repository Pattern）。
"""

from models import AsyncSession
from models.school.course import Course
from sqlalchemy import delete, select
from typing import List, Optional


class CourseRepository:
    """
    课程数据仓库类
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, name: str, credit: float) -> Course:
        """
        创建课程记录
        
        Args:
            name (str): 课程名
            credit (float): 学分
            
        Returns:
            Course: 创建的课程对象
        """
        course = Course(name=name, credit=credit)
        self.session.add(course)
        await self.session.flush()
        return course

    async def get_by_id(self, id: int) -> Optional[Course]:
        """
        根据ID查询课程
        
        Args:
            id (int): 课程ID
            
        Returns:
            Optional[Course]: 课程对象
        """
        stmt = select(Course).where(Course.id == id)
        return await self.session.scalar(stmt)

    async def get_all(self) -> List[Course]:
        """
        查询所有课程
        
        Returns:
            List[Course]: 课程对象列表
        """
        stmt = select(Course).order_by(Course.id)
        result = await self.session.scalars(stmt)
        return result.all()

    async def update(self, id: int, name: Optional[str] = None, credit: Optional[float] = None) -> Optional[Course]:
        """
        更新课程记录
        
        Args:
            id (int): 课程ID
            name (Optional[str]): 课程名
            credit (Optional[float]): 学分
            
        Returns:
            Optional[Course]: 更新后的课程对象
        """
        course = await self.get_by_id(id)
        if course:
            if name is not None:
                course.name = name
            if credit is not None:
                course.credit = credit
        return course

    async def delete(self, id: int) -> int:
        """
        删除课程记录
        
        Args:
            id (int): 课程ID
            
        Returns:
            int: 删除的记录数
        """
        stmt = delete(Course).where(Course.id == id)
        result = await self.session.execute(stmt)
        return result.rowcount
