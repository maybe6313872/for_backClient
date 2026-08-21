from fastapi import APIRouter, Depends, HTTPException, Path, Query
from models import AsyncSession
from dependencies import get_session
from repository.order.company_repo import CompanyRepository
from schemas.art import ArtQueryOut
from typing import Optional, Annotated
from pydantic import BaseModel, Field


# 创建公司相关的路由组
router = APIRouter(prefix="/company", tags=["company"])

class CompanyIn(BaseModel):
    """
    学校创建请求模型
    
    Attributes:
        name (str): 校名，最大长度100字符
        address (str): 学校地址，最大长度200字符
    """
    name: Annotated[
        str,
        Field(..., max_length=100, description="校名")
    ]
    address: Annotated[
        str,
        Field(..., max_length=200, description="学校地址")
    ]

@router.post("/create", response_model=ArtQueryOut, summary="创建公司", description="创建一所新公司")
async def create_company(
    data: CompanyIn,
    session: AsyncSession = Depends(get_session)
):
    try:
        repo = CompanyRepository(session=session)
        company = await repo.create(data.name, data.address)
        await session.commit()
        return ArtQueryOut(data='created successfully')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/query", summary="查询公司", description="根据ID查询公司信息")
async def query_company(
    session: AsyncSession = Depends(get_session)
):
    try:
        repo = CompanyRepository(session)
        company = await repo.query()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    # await session.commit()
    if not company:
        raise HTTPException(status_code=404, detail="公司未找到")
    # return ArtQueryOut(data=company) # 坑哈，这个类里包含了ArtOut,所以报错了
    return {
        "code": 200,
        "message": "查询成功",
        "data": company
    }

class CompanyUpdateIn(BaseModel):
    """
    学校创建请求模型
    
    Attributes:
        name (str): 校名，最大长度100字符
        address (str): 学校地址，最大长度200字符
    """
    id: Annotated[
        int,
        Field(..., description="公司ID")
    ]
    name: Annotated[
        str,
        Field(..., max_length=100, description="校名")
    ]
    address: Annotated[
        str,
        Field(..., max_length=200, description="学校地址")
    ]
@router.put("/update", summary="更新公司", description="根据ID更新公司信息")
async def update_company(
    data: CompanyUpdateIn,
    session: AsyncSession = Depends(get_session)
):
    try:
        repo = CompanyRepository(session)
        result = await repo.update(data.id, data.name, data.address)
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
    company_id: int = Query(..., description="公司ID"),
    session: AsyncSession = Depends(get_session)
):
    try:
        repo = CompanyRepository(session)
        result = await repo.delete(company_id)
        await session.commit()
        return {
            "code": 200,
            "message": "删除成功",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))