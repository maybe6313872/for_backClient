from models import AsyncSession
from models.order.company import Company
from models.order.order_product import OrderProduct
from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload
from typing import List, Optional

class CompanyRepository:
    """
    公司数据仓库类
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, name: str, address: str) -> Company:
        """
        创建公司记录
        
        Args:
            name (str): 公司名称
            address (str): 公司地址
            
        Returns:
            Company: 创建的公司对象
        """
        company = Company(name=name, address=address)
        print(company)
        self.session.add(company)
        return company
    
    async def update(self, id: int, name: Optional[str] = None, address: Optional[str] = None) -> Optional[Company]:
        """
        更新公司记录
        
        Args:
            id (int): 公司ID
            name (Optional[str]): 公司名称
            address (Optional[str]): 公司地址
            
        Returns:
            Optional[Company]: 更新后的公司对象
        """
        stmt = update(Company).where(Company.id == id)
        if name is not None:
            stmt = stmt.values(name=name)
        if address is not None:
            stmt = stmt.values(address=address)
        await self.session.execute(stmt)
        return 1
    
    async def query(self) -> List:
        """

            
        Returns:
            Optional[Company]: 公司对象
        """
        stmt = select(Company).order_by(Company.id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def delete(self, id: int) -> int:
        """
        删除公司记录
        
        Args:
            id (int): 公司ID
            
        Returns:
            int: 删除的记录数
        """
        stmt = select(Company).where(Company.id == id).options(selectinload(Company.orders))
        companyItem = await self.session.scalar(stmt)
        order_ids = []
        for order in companyItem.orders:
            order_ids.append(order.id)
        if order_ids.__len__() > 0:
            delete_stmt = delete(OrderProduct).where(OrderProduct.order_id.in_(order_ids))
            await self.session.execute(delete_stmt)
        delete_company_stmt = delete(Company).where(Company.id == id)
        await self.session.execute(delete_company_stmt)
        return 1