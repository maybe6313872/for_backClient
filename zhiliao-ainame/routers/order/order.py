from fastapi import APIRouter, Depends, HTTPException, Path, Query
from models import AsyncSession
from dependencies import get_session
from repository.order.order_repo import OrderRepository
from schemas.art import ArtQueryOut
from typing import Optional, Annotated
from pydantic import BaseModel, Field

router = APIRouter(prefix="/order", tags=["order"])

class OrderIn(BaseModel):
    """
    订单创建请求模型
    
    Attributes:
        name (str): 校名，最大长度100字符
        address (str): 学校地址，最大长度200字符
    """
    id: Annotated[
        int | None,
        Field(description="产品ID")
    ]
    order_number: Annotated[
        str,
        Field(..., max_length=100, description="订单编号")
    ]
    company_id: Annotated[
        int,
        Field(..., description="公司ID")
    ]
    product_list: Annotated[
        list,
        Field(..., description="库存数量")
    ]

@router.post("/create", response_model=ArtQueryOut, summary="创建订单", description="创建一个新订单")
async def create_order(
    data: OrderIn,
    session: AsyncSession = Depends(get_session)
):
    try:
        repo = OrderRepository(session=session)
        company = await repo.create(data.order_number, data.company_id, data.product_list)
        await session.commit()
        return ArtQueryOut(data='created successfully')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update", response_model=ArtQueryOut, summary="更新订单", description="更新一个订单")
async def update_order(
    data: OrderIn,
    session: AsyncSession = Depends(get_session)
):
    try:
        repo = OrderRepository(session=session)
        company = await repo.update(data.id, data.order_number, data.company_id, data.product_list)
        await session.commit()
        return ArtQueryOut(data='updated successfully')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/query", summary="查询订单", description="根据ID查询订单信息")
async def query_order(
    session: AsyncSession = Depends(get_session)
):
    try:
        repo = OrderRepository(session=session)
        orderArr = await repo.query()
        await session.commit()
        return {
            "code": 200,
            "data": orderArr,
            "msg": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/delete", response_model=ArtQueryOut, summary="删除订单", description="根据ID删除订单")
async def delete_order(
    id: Annotated[int, Query(..., description="订单ID")],
    session: AsyncSession = Depends(get_session)
):
    try:
        repo = OrderRepository(session=session)
        await repo.delete(id)
        await session.commit()
        return ArtQueryOut(data='deleted successfully')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))