import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { prisma } from '../lib/prisma';

const router = Router();

const CourseIn = z.object({
  name: z.string().max(100),
  credit: z.number().min(0),
});
const CourseUpdateIn = z.object({
  name: z.string().max(100).optional(),
  credit: z.number().min(0).optional(),
});

/** POST /course - 创建课程 */
router.post('/', async (req: Request, res: Response) => {
  const parsed = CourseIn.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ detail: parsed.error.message });
    return;
  }
  try {
    await prisma.course.create({
      data: {
        name: parsed.data.name,
        credit: Math.round(parsed.data.credit),
      },
    });
    res.json({ result: 'success' });
  } catch (e) {
    console.error(e);
    res.status(500).json({ detail: '创建课程失败: ' + String(e) });
  }
});

/** GET /course - 查询所有课程 */
router.get('/', async (_req: Request, res: Response) => {
  try {
    const list = await prisma.course.findMany({ orderBy: { id: 'asc' } });
    const data = list.map((c) => ({
      id: c.id,
      name: c.name,
      credit: c.credit ?? 0,
      created_time: c.createdAt,
    }));
    res.json({ code: 200, message: '查询成功', data });
  } catch (e) {
    console.error(e);
    res.status(500).json({ detail: '查询课程列表失败: ' + String(e) });
  }
});

/** GET /course/:course_id */
router.get('/:course_id', async (req: Request, res: Response) => {
  const id = parseInt(req.params.course_id, 10);
  if (isNaN(id)) {
    res.status(400).json({ detail: '无效的课程ID' });
    return;
  }
  const course = await prisma.course.findUnique({ where: { id } });
  if (!course) {
    res.status(404).json({ detail: `课程ID ${id} 不存在` });
    return;
  }
  res.json({
    id: course.id,
    name: course.name,
    credit: course.credit ?? 0,
    created_time: course.createdAt,
  });
});

/** PUT /course/:course_id */
router.put('/:course_id', async (req: Request, res: Response) => {
  const id = parseInt(req.params.course_id, 10);
  if (isNaN(id)) {
    res.status(400).json({ detail: '无效的课程ID' });
    return;
  }
  const parsed = CourseUpdateIn.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ detail: parsed.error.message });
    return;
  }
  const updateData: { name?: string; credit?: number } = {};
  if (parsed.data.name !== undefined) updateData.name = parsed.data.name;
  if (parsed.data.credit !== undefined) updateData.credit = Math.round(parsed.data.credit);
  try {
    await prisma.course.update({ where: { id }, data: updateData });
    res.json({ result: 'success' });
  } catch (e) {
    res.status(404).json({ detail: `课程ID ${id} 不存在` });
  }
});

/** DELETE /course/:course_id */
router.delete('/:course_id', async (req: Request, res: Response) => {
  const id = parseInt(req.params.course_id, 10);
  if (isNaN(id)) {
    res.status(400).json({ detail: '无效的课程ID' });
    return;
  }
  try {
    await prisma.course.delete({ where: { id } });
    res.json({ result: 'success' });
  } catch (e) {
    res.status(404).json({ detail: `课程ID ${id} 不存在` });
  }
});

export default router;
