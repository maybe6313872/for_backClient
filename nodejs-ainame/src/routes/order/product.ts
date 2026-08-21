import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { prisma } from '../../lib/prisma';

const router = Router();

const ProductIn = z.object({
  name: z.string().max(100),
  price: z.number(),
  storenum: z.number(),
  description: z.string().max(500).optional(),
  productno: z.string().max(50).optional(),
});
const ProductUpdateIn = z.object({
  id: z.number(),
  name: z.string().max(100).optional(),
  price: z.number().optional(),
  storenum: z.number().optional(),
  description: z.string().max(500).optional(),
  productno: z.string().max(50).optional(),
});

/** POST /product/create - 创建产品 */
router.post('/create', async (req: Request, res: Response) => {
  const parsed = ProductIn.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ detail: parsed.error.message });
    return;
  }
  try {
    await prisma.product.create({
      data: {
        name: parsed.data.name,
        price: parsed.data.price,
        storenum: parsed.data.storenum,
        description: parsed.data.description ?? '',
        productno: parsed.data.productno ?? '',
      },
    });
    res.json({ code: 200, message: '创建成功', data: 'created successfully' });
  } catch (e) {
    console.error(e);
    res.status(500).json({ detail: String(e) });
  }
});

/** GET /product/query - 查询产品列表 */
router.get('/query', async (_req: Request, res: Response) => {
  try {
    const list = await prisma.product.findMany({ orderBy: { id: 'asc' } });
    res.json({ code: 200, message: '查询成功', data: list });
  } catch (e) {
    console.error(e);
    res.status(500).json({ detail: String(e) });
  }
});

/** PUT /product/update - 更新产品 */
router.put('/update', async (req: Request, res: Response) => {
  const parsed = ProductUpdateIn.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ detail: '参数错误' });
    return;
  }
  const { id, ...data } = parsed.data;
  try {
    await prisma.product.update({ where: { id }, data });
    res.json({ code: 200, message: '更新成功' });
  } catch (e) {
    res.status(404).json({ detail: '产品未找到' });
  }
});

/** DELETE /product/delete?prduct_id= (保持与原 API 拼写一致) */
router.delete('/delete', async (req: Request, res: Response) => {
  const id = parseInt((req.query.prduct_id || req.query.product_id) as string, 10);
  if (isNaN(id)) {
    res.status(400).json({ detail: '缺少 prduct_id 或 product_id' });
    return;
  }
  try {
    await prisma.product.delete({ where: { id } });
    res.json({ code: 200, message: '删除成功' });
  } catch (e) {
    res.status(404).json({ detail: '产品未找到' });
  }
});

export default router;
