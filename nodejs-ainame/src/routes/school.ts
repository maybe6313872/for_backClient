import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { prisma } from '../lib/prisma';

const router = Router();

const SchoolIn = z.object({ name: z.string().max(100), address: z.string().max(200).optional() });
const SchoolUpdateIn = z.object({
  name: z.string().max(100).optional(),
  address: z.string().max(200).optional(),
});

/** POST /school - 创建学校 */
router.post('/', async (req: Request, res: Response) => {
  const parsed = SchoolIn.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ detail: parsed.error.message });
    return;
  }
  try {
    await prisma.school.create({
      data: { name: parsed.data.name, address: parsed.data.address ?? '' },
    });
    res.json({ result: 'success' });
  } catch (e) {
    console.error(e);
    res.status(500).json({ detail: '创建学校失败: ' + String(e) });
  }
});

/** GET /school - 查询所有学校 */
router.get('/', async (_req: Request, res: Response) => {
  try {
    const list = await prisma.school.findMany({ orderBy: { id: 'asc' } });
    res.json({ code: 200, message: '查询成功', data: list });
  } catch (e) {
    console.error(e);
    res.status(500).json({ detail: '查询学校列表失败: ' + String(e) });
  }
});

/** GET /school/:school_id */
router.get('/:school_id', async (req: Request, res: Response) => {
  const id = parseInt(req.params.school_id, 10);
  if (isNaN(id)) {
    res.status(400).json({ detail: '无效的学校ID' });
    return;
  }
  const school = await prisma.school.findUnique({ where: { id } });
  if (!school) {
    res.status(404).json({ detail: '学校未找到' });
    return;
  }
  res.json(school);
});

/** PUT /school/:school_id */
router.put('/:school_id', async (req: Request, res: Response) => {
  const id = parseInt(req.params.school_id, 10);
  if (isNaN(id)) {
    res.status(400).json({ detail: '无效的学校ID' });
    return;
  }
  const parsed = SchoolUpdateIn.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ detail: parsed.error.message });
    return;
  }
  try {
    await prisma.school.update({
      where: { id },
      data: parsed.data,
    });
    res.json({ result: 'success' });
  } catch (e) {
    res.status(404).json({ detail: '学校未找到' });
  }
});

/** DELETE /school/:school_id */
router.delete('/:school_id', async (req: Request, res: Response) => {
  const id = parseInt(req.params.school_id, 10);
  if (isNaN(id)) {
    res.status(400).json({ detail: '无效的学校ID' });
    return;
  }
  try {
    await prisma.school.delete({ where: { id } });
    res.json({ result: 'success' });
  } catch (e) {
    res.status(404).json({ detail: '学校未找到' });
  }
});

export default router;
