import { Router, Request, Response } from 'express';
import { getRedis } from '../lib/redis';

const router = Router();

const PROVINCES_SET = 'region:provinces:set';
const PROVINCE_INFO = (code: string) => `region:province:${code}:info`;
const PROVINCE_CITIES = (code: string) => `region:province:${code}:cities:set`;
const CITY_INFO = (code: string) => `region:city:${code}:info`;
const CITY_DISTRICTS = (code: string) => `region:city:${code}:districts:set`;
const DISTRICT_INFO = (code: string) => `region:district:${code}:info`;

const REGIONS_DATA = {
  provinces: [
    { code: '110000', name: '北京市' },
    { code: '120000', name: '天津市' },
    { code: '130000', name: '河北省' },
    { code: '310000', name: '上海市' },
    { code: '320000', name: '江苏省' },
    { code: '330000', name: '浙江省' },
    { code: '440000', name: '广东省' },
  ],
  cities: {
    '110000': [{ code: '110100', name: '北京市' }],
    '120000': [{ code: '120100', name: '天津市' }],
    '130000': [
      { code: '130100', name: '石家庄市' },
      { code: '130200', name: '唐山市' },
      { code: '130300', name: '秦皇岛市' },
    ],
    '310000': [{ code: '310100', name: '上海市' }],
    '320000': [
      { code: '320100', name: '南京市' },
      { code: '320500', name: '苏州市' },
      { code: '320200', name: '无锡市' },
    ],
    '330000': [
      { code: '330100', name: '杭州市' },
      { code: '330200', name: '宁波市' },
      { code: '330300', name: '温州市' },
    ],
    '440000': [
      { code: '440100', name: '广州市' },
      { code: '440300', name: '深圳市' },
      { code: '440400', name: '珠海市' },
    ],
  },
  districts: {
    '110100': [
      { code: '110101', name: '东城区' },
      { code: '110102', name: '西城区' },
      { code: '110105', name: '朝阳区' },
      { code: '110106', name: '丰台区' },
    ],
    '320100': [
      { code: '320102', name: '玄武区' },
      { code: '320104', name: '秦淮区' },
      { code: '320105', name: '建邺区' },
      { code: '320106', name: '鼓楼区' },
    ],
    '330100': [
      { code: '330102', name: '上城区' },
      { code: '330105', name: '拱墅区' },
      { code: '330106', name: '西湖区' },
      { code: '330108', name: '滨江区' },
    ],
    '440100': [
      { code: '440103', name: '荔湾区' },
      { code: '440104', name: '越秀区' },
      { code: '440105', name: '海珠区' },
      { code: '440106', name: '天河区' },
    ],
  },
};

async function initRegionData(): Promise<void> {
  const redis = getRedis();
  const exists = await redis.exists(PROVINCES_SET);
  if (exists) return;
  const pipe = redis.pipeline();
  for (const p of REGIONS_DATA.provinces) {
    pipe.sadd(PROVINCES_SET, p.code);
    pipe.hset(PROVINCE_INFO(p.code), { code: p.code, name: p.name });
  }
  for (const [provinceCode, cities] of Object.entries(REGIONS_DATA.cities)) {
    for (const c of cities) {
      pipe.hset(CITY_INFO(c.code), { code: c.code, name: c.name });
      pipe.sadd(PROVINCE_CITIES(provinceCode), c.code);
    }
  }
  for (const [cityCode, districts] of Object.entries(REGIONS_DATA.districts)) {
    for (const d of districts) {
      pipe.hset(DISTRICT_INFO(d.code), { code: d.code, name: d.name });
      pipe.sadd(CITY_DISTRICTS(cityCode), d.code);
    }
  }
  await pipe.exec();
}

/** GET /region/provinces */
router.get('/provinces', async (_req: Request, res: Response) => {
  try {
    await initRegionData();
    const redis = getRedis();
    const codes = await redis.smembers(PROVINCES_SET);
    if (!codes.length) {
      res.json({ code: 200, message: '暂无数据', data: [] });
      return;
    }
    const data = await Promise.all(
      codes.sort().map(async (code) => {
        const info = await redis.hgetall(PROVINCE_INFO(code));
        return { code: info.code, name: info.name };
      })
    );
    res.json({ code: 200, message: '查询成功', data });
  } catch (e) {
    console.error(e);
    res.status(500).json({ detail: '获取省份列表失败: ' + String(e) });
  }
});

/** GET /region/cities?province_code= */
router.get('/cities', async (req: Request, res: Response) => {
  const province_code = req.query.province_code as string;
  if (!province_code) {
    res.status(400).json({ detail: '缺少 province_code' });
    return;
  }
  try {
    await initRegionData();
    const redis = getRedis();
    const exists = await redis.sismember(PROVINCES_SET, province_code);
    if (!exists) {
      res.status(404).json({ detail: `省份代码 ${province_code} 不存在` });
      return;
    }
    const codes = await redis.smembers(PROVINCE_CITIES(province_code));
    if (!codes.length) {
      res.json({ code: 200, message: '该省份暂无城市数据', data: [] });
      return;
    }
    const data = await Promise.all(
      codes.sort().map(async (code) => {
        const info = await redis.hgetall(CITY_INFO(code));
        return { code: info.code, name: info.name };
      })
    );
    res.json({ code: 200, message: '查询成功', data });
  } catch (e) {
    console.error(e);
    res.status(500).json({ detail: '获取城市列表失败: ' + String(e) });
  }
});

/** GET /region/districts?city_code= */
router.get('/districts', async (req: Request, res: Response) => {
  const city_code = req.query.city_code as string;
  if (!city_code) {
    res.status(400).json({ detail: '缺少 city_code' });
    return;
  }
  try {
    await initRegionData();
    const redis = getRedis();
    const cityInfo = await redis.hgetall(CITY_INFO(city_code));
    if (!cityInfo || !cityInfo.code) {
      res.status(404).json({ detail: `城市代码 ${city_code} 不存在` });
      return;
    }
    const codes = await redis.smembers(CITY_DISTRICTS(city_code));
    if (!codes.length) {
      res.json({ code: 200, message: '该城市暂无区县数据', data: [] });
      return;
    }
    const data = await Promise.all(
      codes.sort().map(async (code) => {
        const info = await redis.hgetall(DISTRICT_INFO(code));
        return { code: info.code, name: info.name };
      })
    );
    res.json({ code: 200, message: '查询成功', data });
  } catch (e) {
    console.error(e);
    res.status(500).json({ detail: '获取区县列表失败: ' + String(e) });
  }
});

/** POST /region/init */
router.post('/init', async (_req: Request, res: Response) => {
  try {
    await initRegionData();
    res.json({ code: 200, message: '省市区数据初始化成功' });
  } catch (e) {
    console.error(e);
    res.status(500).json({ detail: '初始化数据失败: ' + String(e) });
  }
});

export default router;
