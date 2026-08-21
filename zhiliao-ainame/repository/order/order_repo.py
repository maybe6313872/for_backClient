from models import AsyncSession
from models.order.order import Order
from models.order.order_product import OrderProduct
from models.order.company import Company
from models.order.product import Product
from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload
from typing import List, Optional

class OrderRepository:
    """
    产品数据仓库类
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, order_number: str, company_id: int, product_list: list):
        """
        创建订单记录

        Args:
            order_number (str): 订单编号
            company_id (int): 公司ID
            product_list (list): 产品列表

        Returns:
            Order: 创建的订单对象
        """
        order = Order(order_number=order_number, company_id=company_id)
        self.session.add(order)
        await self.session.flush()  # Ensure order.id is populated
        order_id = order.id
        for product in product_list:
            order_product = OrderProduct(order_id=order_id, product_id=product['id'], number=product['number'])
            self.session.add(order_product)

        return order
    
    async def query(self) -> List:
        """
        查询所有订单记录

        Returns:
            List: 订单列表
        """

        stmt_order = select(Order).order_by(Order.id)
        result = await self.session.execute(stmt_order)
        arr = result.scalars().all()
        for item in arr:
            stmt_company = select(Company).where(Company.id == item.company_id)
            result_company = await self.session.execute(stmt_company)
            company = result_company.scalars().first()
            item.companyName = company.name if company else None
            stmt_order_product = select(OrderProduct).where(OrderProduct.order_id == item.id)
            result_order_product = await self.session.execute(stmt_order_product)
            order_products = result_order_product.scalars().all()
            item.product_list = []
            item.total_price = 0
            for op in order_products:
                stmt_product = select(Product).where(Product.id == op.product_id)
                result_product = await self.session.execute(stmt_product)
                product = result_product.scalars().first()
                item.product_list.append({
                    "product_id": op.product_id,
                    "product_name": product.name if product else None,
                    "number": op.number,
                    "price": product.price if product else 0
                })
                item.total_price += (product.price * op.number) if product else 0
        return arr
    
    async def update(self, id: int, order_number: str, company_id: int, product_list: list):
        """
        更新订单记录

        Args:
            order_number (str): 订单编号
            company_id (int): 公司ID
            product_list (list): 产品列表

        Returns:
            Order: 创建的订单对象
        """
        stmt = update(Order).where(Order.id == id)
        if order_number is not None:
            stmt = stmt.values(order_number=order_number)
        if company_id is not None:
            stmt = stmt.values(company_id=company_id)
        await self.session.execute(stmt)
        stmt_middle = delete(OrderProduct).where(OrderProduct.order_id == id)
        await self.session.execute(stmt_middle)
        await self.session.flush()
        stmt_sel = select(Order).where(Order.id == id)
        order_sel = await self.session.scalar(stmt_sel)
        order_id = order_sel.id
        for product in product_list:
            order_product = OrderProduct(order_id=order_id, product_id=product['id'], number=product['number'])
            self.session.add(order_product)

        return 1
    
    async def delete(self, id: int):
        """
        删除订单记录

        Args:
            id (int): 订单ID

        Returns:
            int: 删除的订单ID
        """
        stmt_middle = delete(OrderProduct).where(OrderProduct.order_id == id)
        await self.session.execute(stmt_middle)
        stmt = delete(Order).where(Order.id == id)
        await self.session.execute(stmt)
        return id