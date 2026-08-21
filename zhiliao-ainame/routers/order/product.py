from fastapi import APIRouter, Depends, HTTPException, Path, Query
from models import AsyncSession
from dependencies import get_session
from repository.order.product_repo import ProductRepository
from schemas.art import ArtQueryOut
from typing import Optional, Annotated
from pydantic import BaseModel, Field


# 创建公司相关的路由组
router = APIRouter(prefix="/product", tags=["product"])

class ProductIn(BaseModel):
    """
    产品创建请求模型
    
    Attributes:
        name (str): 校名，最大长度100字符
        address (str): 学校地址，最大长度200字符
    """
    id: Annotated[
        int | None,
        Field(description="产品ID")
    ]
    name: Annotated[
        str,
        Field(..., max_length=100, description="校名")
    ]
    price: Annotated[
        float,
        Field(..., description="产品价格")
    ]
    storenum: Annotated[
        int,
        Field(..., description="库存数量")
    ]
    description: Annotated[
        str,
        Field(..., max_length=200, description="产品描述")
    ]
    productno: Annotated[
        str,
        Field(..., max_length=200, description="产品编号")
    ]

@router.post("/create", response_model=ArtQueryOut, summary="创建产品", description="创建一个新产品")
async def create_product(
    data: ProductIn,
    session: AsyncSession = Depends(get_session)
):
    try:
        repo = ProductRepository(session=session)
        company = await repo.create(data.name, data.price, data.storenum, data.description, data.productno)
        await session.commit()
        return ArtQueryOut(data='created successfully')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/query", summary="查询产品", description="根据ID查询产品信息")
async def query_product(
    session: AsyncSession = Depends(get_session)
):
    try:
        repo = ProductRepository(session=session)
        product = await repo.query()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    # await session.commit()
    # return ArtQueryOut(data=product) # 坑哈，这个类里包含了ArtOut,所以报错了
    return {
        "code": 200,
        "message": "查询成功",
        "data": product
    }

@router.put("/update", summary="更新产品", description="根据ID更新产品信息")
async def update_product(
    data: ProductIn,
    session: AsyncSession = Depends(get_session)
):
    try:
        repo = ProductRepository(session=session)
        result = await repo.update(data.id, data.name, data.price, data.storenum, data.description, data.productno)
        await session.commit()
        return {
            "code": 200,
            "message": "更新成功",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/delete", summary="删除公司", description="根据ID删除公司信息")
async def delete_company(
    prduct_id: int = Query(..., description="公司ID"),
    session: AsyncSession = Depends(get_session)
):
    try:
        repo = ProductRepository(session)
        result = await repo.delete(prduct_id)
        await session.commit()
        return {
            "code": 200,
            "message": "删除成功",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))