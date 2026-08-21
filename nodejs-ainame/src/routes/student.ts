import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { prisma } from '../lib/prisma';

const router = Router();

const StudentIn = z.object({
  name: z.string().max(50),
  sex: z.string().max(10),
  age: z.number().min(0).max(150),
  teacher_id: z.number(),
});
const StudentUpdateIn = z.object({
  name: z.string().max(50).optional(),
  sex: z.string().max(10).optional(),
  age: z.number().min(0).max(150).optional(),
  teacher_id: z.number().optional(),
});

async function studentToOut(s: {
  id: number;
  name: string;
  sex: string | null;
  age: number | null;
  teacherId: number;
  createdAt: Date | null;
  courses?: { course: { id: number; name: string; credit: number | null; createdAt: Date | null }; score: number | null }[];
}) {
  const courses = (s.courses ?? []).map((sc) => ({
    course: {
      id: sc.course.id,
      name: sc.course.name,
      credit: sc.course.credit ?? 0,
      created_time: sc.course.createdAt,
    },
    score: sc.score != null ? sc.score : null,
  }));
  return {
    id: s.id,
    name: s.name,
    sex: s.sex,
    age: s.age,
    teacher_id: s.teacherId,
    created_time: s.createdAt,
    courses,
  };
}

/** POST /student - 创建学生 */
router.post('/', async (req: Request, res: Response) => {
  const parsed = StudentIn.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ detail: parsed.error.message });
    return;
  }
  try {
    await prisma.student.create({
      data: {
        name: parsed.data.name,
        sex: parsed.data.sex,
        age: parsed.data.age,
        teacherId: parsed.data.teacher_id,
      },
    });
    res.json({ result: 'success' });
  } catch (e) {
    console.error(e);
    res.status(500).json({ detail: '创建学生失败: ' + String(e) });
  }
});

/** GET /student?teacher_id= - 查询学生列表（含选课与分数，可选按班主任筛选） */
router.get('/', async (req: Request, res: Response) => {
  const teacher_id = req.query.teacher_id ? parseInt(req.query.teacher_id as string, 10) : undefined;
  try {
    const list = await prisma.student.findMany({
      where: teacher_id ? { teacherId: teacher_id } : undefined,
      orderBy: { id: 'asc' },
      include: {
        courses: {
          include: {
            course: true,
          },
        },
      },
    });
    const data = await Promise.all(list.map((s) => studentToOut(s)));
    res.json({ code: 200, message: '查询成功', data });
  } catch (e) {
    console.error(e);
    res.status(500).json({ detail: '查询学生列表失败: ' + String(e) });
  }
});

/** GET /student/:student_id */
router.get('/:student_id', async (req: Request, res: Response) => {
  const id = parseInt(req.params.student_id, 10);
  if (isNaN(id)) {
    res.status(400).json({ detail: '无效的学生ID' });
    return;
  }
  const student = await prisma.student.findUnique({
    where: { id },
    include: {
      courses: {
        include: { course: true },
      },
    },
  });
  if (!student) {
    res.status(404).json({ detail: `学生ID ${id} 不存在` });
    return;
  }
  res.json(await studentToOut(student));
});

/** PUT /student/:student_id */
router.put('/:student_id', async (req: Request, res: Response) => {
  const id = parseInt(req.params.student_id, 10);
  if (isNaN(id)) {
    res.status(400).json({ detail: '无效的学生ID' });
    return;
  }
  const parsed = StudentUpdateIn.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ detail: parsed.error.message });
    return;
  }
  const updateData: { name?: string; sex?: string; age?: number; teacherId?: number } = {};
  if (parsed.data.name !== undefined) updateData.name = parsed.data.name;
  if (parsed.data.sex !== undefined) updateData.sex = parsed.data.sex;
  if (parsed.data.age !== undefined) updateData.age = parsed.data.age;
  if (parsed.data.teacher_id !== undefined) updateData.teacherId = parsed.data.teacher_id;
  try {
    await prisma.student.update({ where: { id }, data: updateData });
    res.json({ result: 'success' });
  } catch (e) {
    res.status(404).json({ detail: `学生ID ${id} 不存在` });
  }
});

/** DELETE /student/:student_id */
router.delete('/:student_id', async (req: Request, res: Response) => {
  const id = parseInt(req.params.student_id, 10);
  if (isNaN(id)) {
    res.status(400).json({ detail: '无效的学生ID' });
    return;
  }
  try {
    await prisma.student.delete({ where: { id } });
    res.json({ result: 'success' });
  } catch (e) {
    res.status(404).json({ detail: `学生ID ${id} 不存在` });
  }
});

export default router;
