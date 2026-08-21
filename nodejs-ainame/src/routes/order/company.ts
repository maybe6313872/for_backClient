import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { prisma } from '../../lib/prisma';

const router = Router();

const CompanyIn = z.object({ name: z.string().max(100), address: z.string().max(200).optional() });
const CompanyUpdateIn = z.object({
  id: z.number(),
  name: z.string().max(100),
  address: z.string().max(200).optional(),
});

/** POST /company/create - 创建公司 */
router.post('/create', async (req: Request, res: Response) => {
  const parsed = CompanyIn.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ detail: parsed.error.message });
    return;
  }
  try {
    await prisma.company.create({
      data: { name: parsed.data.name, address: parsed.data.address ?? '' },
    });
    res.json({ code: 200, message: '创建成功', data: 'created successfully' });
  } catch (e) {
    console.error(e);
    res.status(500).json({ detail: String(e) });
  }
});

/** GET /company/query - 查询公司列表 */
router.get('/query', async (_req: Request, res: Response) => {
  try {
    const list = await prisma.company.findMany({ orderBy: { id: 'asc' } });
    res.json({ code: 200, message: '查询成功', data: list });
  } catch (e) {
    console.error(e);
    res.status(500).json({ detail: String(e) });
  }
});

/** PUT /company/update - 更新公司 */
router.put('/update', async (req: Request, res: Response) => {
  const parsed = CompanyUpdateIn.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ detail: '参数错误' });
    return;
  }
  try {
    await prisma.company.update({
      where: { id: parsed.data.id },
      data: { name: parsed.data.name, address: parsed.data.address },
    });
    res.json({ code: 200, message: '更新成功' });
  } catch (e) {
    res.status(404).json({ detail: '公司未找到' });
  }
});

/** DELETE /company/delete?company_id= */
router.delete('/delete', async (req: Request, res: Response) => {
  const company_id = parseInt(req.query.company_id as string, 10);
  if (isNaN(company_id)) {
    res.status(400).json({ detail: '缺少 company_id' });
    return;
  }
  try {
    await prisma.company.delete({ where: { id: company_id } });
    res.json({ code: 200, message: '删除成功' });
  } catch (e) {
    res.status(404).json({ detail: '公司未找到' });
  }
});

export default router;
