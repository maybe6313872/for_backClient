import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { prisma } from '../lib/prisma';

const router = Router();

const TeacherIn = z.object({
  name: z.string().max(50),
  sex: z.string().max(10),
  age: z.number().min(0).max(150),
  school_id: z.number(),
});
const TeacherUpdateIn = z.object({
  name: z.string().max(50).optional(),
  sex: z.string().max(10).optional(),
  age: z.number().min(0).max(150).optional(),
  school_id: z.number().optional(),
});

/** POST /teacher - 创建班主任 */
router.post('/', async (req: Request, res: Response) => {
  const parsed = TeacherIn.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ detail: parsed.error.message });
    return;
  }
  try {
    await prisma.teacher.create({
      data: {
        name: parsed.data.name,
        sex: parsed.data.sex,
        age: parsed.data.age,
        schoolId: parsed.data.school_id,
      },
    });
    res.json({ result: 'success' });
  } catch (e) {
    console.error(e);
    res.status(500).json({ detail: '创建班主任失败: ' + String(e) });
  }
});

/** GET /teacher?school_id= - 查询班主任列表（可选按学校筛选） */
router.get('/', async (req: Request, res: Response) => {
  const school_id = req.query.school_id ? parseInt(req.query.school_id as string, 10) : undefined;
  try {
    const list = await prisma.teacher.findMany({
      where: school_id ? { schoolId: school_id } : undefined,
      orderBy: { id: 'asc' },
    });
    const data = list.map((t) => ({
      id: t.id,
      name: t.name,
      sex: t.sex,
      age: t.age,
      school_id: t.schoolId,
      created_time: t.createdAt,
    }));
    res.json({ code: 200, message: '查询成功', data });
  } catch (e) {
    console.error(e);
    res.status(500).json({ detail: '查询班主任列表失败: ' + String(e) });
  }
});

/** GET /teacher/:teacher_id */
router.get('/:teacher_id', async (req: Request, res: Response) => {
  const id = parseInt(req.params.teacher_id, 10);
  if (isNaN(id)) {
    res.status(400).json({ detail: '无效的班主任ID' });
    return;
  }
  const teacher = await prisma.teacher.findUnique({ where: { id } });
  if (!teacher) {
    res.status(404).json({ detail: `班主任ID ${id} 不存在` });
    return;
  }
  res.json({
    id: teacher.id,
    name: teacher.name,
    sex: teacher.sex,
    age: teacher.age,
    school_id: teacher.schoolId,
    created_time: teacher.createdAt,
  });
});

/** PUT /teacher/:teacher_id */
router.put('/:teacher_id', async (req: Request, res: Response) => {
  const id = parseInt(req.params.teacher_id, 10);
  if (isNaN(id)) {
    res.status(400).json({ detail: '无效的班主任ID' });
    return;
  }
  const parsed = TeacherUpdateIn.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ detail: parsed.error.message });
    return;
  }
  const updateData: { name?: string; sex?: string; age?: number; schoolId?: number } = {};
  if (parsed.data.name !== undefined) updateData.name = parsed.data.name;
  if (parsed.data.sex !== undefined) updateData.sex = parsed.data.sex;
  if (parsed.data.age !== undefined) updateData.age = parsed.data.age;
  if (parsed.data.school_id !== undefined) updateData.schoolId = parsed.data.school_id;
  try {
    await prisma.teacher.update({ where: { id }, data: updateData });
    res.json({ result: 'success' });
  } catch (e) {
    res.status(404).json({ detail: `班主任ID ${id} 不存在` });
  }
});

/** DELETE /teacher/:teacher_id */
router.delete('/:teacher_id', async (req: Request, res: Response) => {
  const id = parseInt(req.params.teacher_id, 10);
  if (isNaN(id)) {
    res.status(400).json({ detail: '无效的班主任ID' });
    return;
  }
  try {
    await prisma.teacher.delete({ where: { id } });
    res.json({ result: 'success' });
  } catch (e) {
    res.status(404).json({ detail: `班主任ID ${id} 不存在` });
  }
});

export default router;
