"""
省市区相关路由模块（基于 Redis）

本模块提供了基于 Redis 的省市区查询功能。
使用 RedisService 封装类简化 Redis 操作。
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel, Field
from core.redis_service import get_redis_service_dependency, RedisService


# 创建省市区相关的路由组
router = APIRouter(prefix="/region", tags=["region"])


# ==================== 数据模型 ====================

class RegionInfo(BaseModel):
    """
    地区信息模型
    """
    code: str = Field(..., description="地区代码")
    name: str = Field(..., description="地区名称")


class RegionListResponse(BaseModel):
    """
    地区列表响应模型
    """
    code: int = Field(default=200, description="响应状态码")
    message: str = Field(default="查询成功", description="响应消息")
    data: List[RegionInfo] = Field(..., description="地区列表")


# ==================== Redis Key 常量 ====================

PROVINCES_SET_KEY = "region:provinces:set"
PROVINCE_INFO_KEY = "region:province:{code}:info"
PROVINCE_CITIES_KEY = "region:province:{code}:cities:set"
CITY_INFO_KEY = "region:city:{code}:info"
CITY_DISTRICTS_KEY = "region:city:{code}:districts:set"
DISTRICT_INFO_KEY = "region:district:{code}:info"


# ==================== 辅助函数 ====================

async def init_region_data(redis_service: RedisService):
    """
    初始化省市区数据到 Redis
    
    这里使用简化的中国省市区数据作为示例。
    实际项目中，可以从数据库或数据文件加载完整数据。
    
    Args:
        redis_service (RedisService): Redis 服务实例
    """
    # 检查数据是否已初始化
    exists = await redis_service.exists(PROVINCES_SET_KEY)
    if exists:
        return  # 数据已存在，跳过初始化
    
    # 示例数据（部分省份）
    regions_data = {
        "provinces": [
            {"code": "110000", "name": "北京市"},
            {"code": "120000", "name": "天津市"},
            {"code": "130000", "name": "河北省"},
            {"code": "310000", "name": "上海市"},
            {"code": "320000", "name": "江苏省"},
            {"code": "330000", "name": "浙江省"},
            {"code": "440000", "name": "广东省"},
        ],
        "cities": {
            "110000": [  # 北京
                {"code": "110100", "name": "北京市"},
            ],
            "120000": [  # 天津
                {"code": "120100", "name": "天津市"},
            ],
            "130000": [  # 河北
                {"code": "130100", "name": "石家庄市"},
                {"code": "130200", "name": "唐山市"},
                {"code": "130300", "name": "秦皇岛市"},
            ],
            "310000": [  # 上海
                {"code": "310100", "name": "上海市"},
            ],
            "320000": [  # 江苏
                {"code": "320100", "name": "南京市"},
                {"code": "320500", "name": "苏州市"},
                {"code": "320200", "name": "无锡市"},
            ],
            "330000": [  # 浙江
                {"code": "330100", "name": "杭州市"},
                {"code": "330200", "name": "宁波市"},
                {"code": "330300", "name": "温州市"},
            ],
            "440000": [  # 广东
                {"code": "440100", "name": "广州市"},
                {"code": "440300", "name": "深圳市"},
                {"code": "440400", "name": "珠海市"},
            ],
        },
        "districts": {
            "110100": [  # 北京
                {"code": "110101", "name": "东城区"},
                {"code": "110102", "name": "西城区"},
                {"code": "110105", "name": "朝阳区"},
                {"code": "110106", "name": "丰台区"},
            ],
            "320100": [  # 南京
                {"code": "320102", "name": "玄武区"},
                {"code": "320104", "name": "秦淮区"},
                {"code": "320105", "name": "建邺区"},
                {"code": "320106", "name": "鼓楼区"},
            ],
            "330100": [  # 杭州
                {"code": "330102", "name": "上城区"},
                {"code": "330105", "name": "拱墅区"},
                {"code": "330106", "name": "西湖区"},
                {"code": "330108", "name": "滨江区"},
            ],
            "440100": [  # 广州
                {"code": "440103", "name": "荔湾区"},
                {"code": "440104", "name": "越秀区"},
                {"code": "440105", "name": "海珠区"},
                {"code": "440106", "name": "天河区"},
            ],
        }
    }
    
    # 使用管道批量操作提高性能
    pipe = await redis_service.pipeline()
    
    # 初始化省份
    for province in regions_data["provinces"]:
        code = province["code"]
        name = province["name"]
        # 添加到省份集合
        pipe.sadd(PROVINCES_SET_KEY, code)
        # 存储省份信息（使用 hmset 批量设置，更简洁）
        province_key = PROVINCE_INFO_KEY.format(code=code)
        pipe.hmset(province_key, {"code": code, "name": name})
    
    # 初始化城市
    for province_code, cities in regions_data["cities"].items():
        for city in cities:
            code = city["code"]
            name = city["name"]
            # 存储城市信息（使用 hmset 批量设置）
            city_key = CITY_INFO_KEY.format(code=code)
            pipe.hmset(city_key, {"code": code, "name": name})
            # 添加到对应省份的城市集合
            pipe.sadd(PROVINCE_CITIES_KEY.format(code=province_code), code)
    
    # 初始化区县
    for city_code, districts in regions_data["districts"].items():
        for district in districts:
            code = district["code"]
            name = district["name"]
            # 存储区县信息（使用 hmset 批量设置）
            district_key = DISTRICT_INFO_KEY.format(code=code)
            pipe.hmset(district_key, {"code": code, "name": name})
            # 添加到对应城市的区县集合
            pipe.sadd(CITY_DISTRICTS_KEY.format(code=city_code), code)
    
    # 执行批量操作
    await pipe.execute()


# ==================== API 接口 ====================

@router.get("/provinces", response_model=RegionListResponse, summary="获取省份列表", description="获取所有省份列表")
async def get_provinces(redis_service: RedisService = Depends(get_redis_service_dependency)):
    """
    获取所有省份列表
    
    Args:
        redis_service (RedisService): Redis 服务实例（依赖注入）
    
    Returns:
        RegionListResponse: 包含省份列表的响应
    """
    try:
        # 初始化数据（如果尚未初始化）
        await init_region_data(redis_service)
        
        # 获取所有省份代码
        province_codes = await redis_service.smembers(PROVINCES_SET_KEY)
        
        if not province_codes:
            return RegionListResponse(code=200, message="暂无数据", data=[])
        
        # 批量获取省份信息
        pipe = await redis_service.pipeline()
        for code in province_codes:
            pipe.hgetall(PROVINCE_INFO_KEY.format(code=code))
        province_infos = await pipe.execute()
        
        # 转换为响应格式
        provinces = [
            RegionInfo(code=info["code"], name=info["name"])
            for info in province_infos if info
        ]
        
        # 按代码排序
        provinces.sort(key=lambda x: x.code)
        
        return RegionListResponse(code=200, message="查询成功", data=provinces)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取省份列表失败: {str(e)}")


@router.get("/cities", response_model=RegionListResponse, summary="获取城市列表", description="根据省份代码获取城市列表")
async def get_cities(
    province_code: str = Query(..., description="省份代码", example="110000"),
    redis_service: RedisService = Depends(get_redis_service_dependency)
):
    """
    根据省份代码获取该省份下的城市列表
    
    Args:
        province_code (str): 省份代码
        redis_service (RedisService): Redis 服务实例（依赖注入）
        
    Returns:
        RegionListResponse: 包含城市列表的响应
        
    Raises:
        HTTPException: 当省份代码不存在时
    """
    try:
        # 初始化数据（如果尚未初始化）
        await init_region_data(redis_service)
        
        # 验证省份是否存在
        province_exists = await redis_service.sismember(PROVINCES_SET_KEY, province_code)
        if not province_exists:
            raise HTTPException(status_code=404, detail=f"省份代码 {province_code} 不存在")
        
        # 获取该省份下的城市代码集合
        city_codes = await redis_service.smembers(PROVINCE_CITIES_KEY.format(code=province_code))
        
        if not city_codes:
            return RegionListResponse(code=200, message="该省份暂无城市数据", data=[])
        
        # 批量获取城市信息
        pipe = await redis_service.pipeline()
        for code in city_codes:
            pipe.hgetall(CITY_INFO_KEY.format(code=code))
        city_infos = await pipe.execute()
        
        # 转换为响应格式
        cities = [
            RegionInfo(code=info["code"], name=info["name"])
            for info in city_infos if info
        ]
        
        # 按代码排序
        cities.sort(key=lambda x: x.code)
        
        return RegionListResponse(code=200, message="查询成功", data=cities)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取城市列表失败: {str(e)}")


@router.get("/districts", response_model=RegionListResponse, summary="获取区县列表", description="根据城市代码获取区县列表")
async def get_districts(
    city_code: str = Query(..., description="城市代码", example="110100"),
    redis_service: RedisService = Depends(get_redis_service_dependency)
):
    """
    根据城市代码获取该城市下的区县列表
    
    Args:
        city_code (str): 城市代码
        redis_service (RedisService): Redis 服务实例（依赖注入）
        
    Returns:
        RegionListResponse: 包含区县列表的响应
        
    Raises:
        HTTPException: 当城市代码不存在时
    """
    try:
        # 初始化数据（如果尚未初始化）
        await init_region_data(redis_service)
        
        # 验证城市是否存在（通过检查城市信息是否存在）
        city_info = await redis_service.hgetall(CITY_INFO_KEY.format(code=city_code))
        if not city_info:
            raise HTTPException(status_code=404, detail=f"城市代码 {city_code} 不存在")
        
        # 获取该城市下的区县代码集合
        district_codes = await redis_service.smembers(CITY_DISTRICTS_KEY.format(code=city_code))
        
        if not district_codes:
            return RegionListResponse(code=200, message="该城市暂无区县数据", data=[])
        
        # 批量获取区县信息
        pipe = await redis_service.pipeline()
        for code in district_codes:
            pipe.hgetall(DISTRICT_INFO_KEY.format(code=code))
        district_infos = await pipe.execute()
        
        # 转换为响应格式
        districts = [
            RegionInfo(code=info["code"], name=info["name"])
            for info in district_infos if info
        ]
        
        # 按代码排序
        districts.sort(key=lambda x: x.code)
        
        return RegionListResponse(code=200, message="查询成功", data=districts)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取区县列表失败: {str(e)}")


@router.post("/init", summary="初始化省市区数据", description="手动初始化省市区数据到Redis（如果数据已存在则跳过）")
async def init_regions(redis_service: RedisService = Depends(get_redis_service_dependency)):
    """
    手动初始化省市区数据
    
    如果数据已经存在，则跳过初始化。
    
    Args:
        redis_service (RedisService): Redis 服务实例（依赖注入）
        
    Returns:
        dict: 操作结果
    """
    try:
        await init_region_data(redis_service)
        return {"code": 200, "message": "省市区数据初始化成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"初始化数据失败: {str(e)}")
