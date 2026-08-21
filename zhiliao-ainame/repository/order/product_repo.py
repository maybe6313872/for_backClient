from models import AsyncSession
from models.order.product import Product
from models.order.order_product import OrderProduct
from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload
from typing import List, Optional

class ProductRepository:
    """
    产品数据仓库类
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, name: str, price: float, storenum: int, description: str, productno: str) -> Product:
        """
        创建公司记录
        
        Args:
            name (str): 公司名称
            address (str): 公司地址
            
        Returns:
            Product: 创建的产品对象
        """
        product = Product(name=name, price=price, storenum=storenum, description=description, productno=productno)
        self.session.add(product)
        return product

    async def update(self, id: int, name: Optional[str] = None, price: Optional[float] = None, storenum: Optional[int] = None, description: Optional[str] = None, productno: Optional[str] = None) -> Optional[Product]:
        """
        更新公司记录
        
        Args:
            id (int): 公司ID
            name (Optional[str]): 公司名称
            address (Optional[str]): 公司地址
            
        Returns:
            Optional[Product]: 更新后的产品对象
        """
        stmt = update(Product).where(Product.id == id)
        if name is not None:
            stmt = stmt.values(name=name)
        if price is not None:
            stmt = stmt.values(price=price)
        if storenum is not None:
            stmt = stmt.values(storenum=storenum)
        if description is not None:
            stmt = stmt.values(description=description)
        if productno is not None:
            stmt = stmt.values(productno=productno)
        await self.session.execute(stmt)
        return 1
    
    async def query(self) -> List:
        """

            
        Returns:
            Optional[Product]: 产品对象
        """
        stmt = select(Product).order_by(Product.id)
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
        stmt = select(Product).where(Product.id == id).options(selectinload(Product.orders))
        productItem = await self.session.scalar(stmt)
        order_ids = []
        for order in productItem.orders:
            order_ids.append(order.id)
        if order_ids.__len__() > 0:
            delete_stmt = delete(OrderProduct).where(OrderProduct.order_id.in_(order_ids))
            await self.session.execute(delete_stmt)
        delete_product_stmt = delete(Product).where(Product.id == id)
        await self.session.execute(delete_product_stmt)
        return 1