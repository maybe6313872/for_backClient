import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { prisma } from '../lib/prisma';

const router = Router();

const StudentCourseIn = z.object({
  student_id: z.number(),
  course_id: z.number(),
  score: z.number().min(0).max(100).nullable().optional(),
});
const StudentCourseBatchIn = z.object({
  student_id: z.number(),
  course_ids: z.array(z.number()).min(1),
  scores: z.array(z.number().min(0).max(100)).optional(),
});
const StudentCourseUpdateIn = z.object({
  score: z.number().min(0).max(100).nullable().optional(),
});

/** POST /student-course - 批量选课（先清空该学生已选，再按 course_ids 添加） */
router.post('/', async (req: Request, res: Response) => {
  const parsed = StudentCourseBatchIn.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ detail: parsed.error.message });
    return;
  }
  const { student_id, course_ids, scores } = parsed.data;
  if (scores != null && scores.length !== course_ids.length) {
    res.status(400).json({ detail: '分数数组长度必须与课程ID数组长度一致' });
    return;
  }
  try {
    await prisma.$transaction(async (tx) => {
      await tx.studentCourse.deleteMany({ where: { studentId: student_id } });
      for (let i = 0; i < course_ids.length; i++) {
        const score = scores != null ? scores[i] : null;
        await tx.studentCourse.create({
          data: {
            studentId: student_id,
            courseId: course_ids[i],
            score: score != null ? Math.round(score) : null,
          },
        });
      }
    });
    res.json({ result: 'success' });
  } catch (e) {
    console.error(e);
    res.status(500).json({ detail: '批量创建学生课程关联失败: ' + String(e) });
  }
});

/** POST /student-course/single - 单条选课 */
router.post('/single', async (req: Request, res: Response) => {
  const parsed = StudentCourseIn.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ detail: parsed.error.message });
    return;
  }
  const { student_id, course_id, score } = parsed.data;
  const existing = await prisma.studentCourse.findUnique({
    where: {
      studentId_courseId: { studentId: student_id, courseId: course_id },
    },
  });
  if (existing) {
    res.status(400).json({ detail: '该学生已选修此课程' });
    return;
  }
  try {
    await prisma.studentCourse.create({
      data: {
        studentId: student_id,
        courseId: course_id,
        score: score != null ? Math.round(score) : null,
      },
    });
    res.json({ result: 'success' });
  } catch (e) {
    console.error(e);
    res.status(500).json({ detail: '创建学生课程关联失败: ' + String(e) });
  }
});

/** GET /student-course?student_id=&course_id= - 列表（可选按学生或课程筛选） */
router.get('/', async (req: Request, res: Response) => {
  const student_id = req.query.student_id ? parseInt(req.query.student_id as string, 10) : undefined;
  const course_id = req.query.course_id ? parseInt(req.query.course_id as string, 10) : undefined;
  try {
    const list = await prisma.studentCourse.findMany({
      where: {
        ...(student_id ? { studentId: student_id } : {}),
        ...(course_id ? { courseId: course_id } : {}),
      },
      orderBy: { id: 'asc' },
      include: { student: true, course: true },
    });
    const data = list.map((sc) => ({
      id: sc.id,
      student_id: sc.studentId,
      course_id: sc.courseId,
      score: sc.score,
      created_time: sc.createdAt,
    }));
    res.json({ code: 200, message: '查询成功', data });
  } catch (e) {
    console.error(e);
    res.status(500).json({ detail: '查询学生课程关联列表失败: ' + String(e) });
  }
});

/** GET /student-course/course/:course_id/students - 某课程下的学生列表（含分数） */
router.get('/course/:course_id/students', async (req: Request, res: Response) => {
  const course_id = parseInt(req.params.course_id, 10);
  if (isNaN(course_id)) {
    res.status(400).json({ detail: '无效的课程ID' });
    return;
  }
  try {
    const list = await prisma.studentCourse.findMany({
      where: { courseId: course_id },
      include: { student: true },
    });
    const data = list.map((sc) => ({
      student_id: sc.student.id,
      student_name: sc.student.name,
      student_sex: sc.student.sex,
      student_age: sc.student.age,
      teacher_id: sc.student.teacherId,
      score: sc.score,
    }));
    res.json({ code: 200, message: '查询成功', data });
  } catch (e) {
    console.error(e);
    res.status(500).json({ detail: '查询课程学生列表失败: ' + String(e) });
  }
});

/** GET /student-course/:id */
router.get('/:id', async (req: Request, res: Response) => {
  const id = parseInt(req.params.id, 10);
  if (isNaN(id)) {
    res.status(400).json({ detail: '无效的关联ID' });
    return;
  }
  const sc = await prisma.studentCourse.findUnique({ where: { id } });
  if (!sc) {
    res.status(404).json({ detail: `关联记录ID ${id} 不存在` });
    return;
  }
  res.json({
    id: sc.id,
    student_id: sc.studentId,
    course_id: sc.courseId,
    score: sc.score,
    created_time: sc.createdAt,
  });
});

/** PUT /student-course/:id - 更新（主要更新分数） */
router.put('/:id', async (req: Request, res: Response) => {
  const id = parseInt(req.params.id, 10);
  if (isNaN(id)) {
    res.status(400).json({ detail: '无效的关联ID' });
    return;
  }
  const parsed = StudentCourseUpdateIn.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ detail: parsed.error.message });
    return;
  }
  try {
    await prisma.studentCourse.update({
      where: { id },
      data: { score: parsed.data.score != null ? Math.round(parsed.data.score) : undefined },
    });
    res.json({ result: 'success' });
  } catch (e) {
    res.status(404).json({ detail: `关联记录ID ${id} 不存在` });
  }
});

/** DELETE /student-course/:id */
router.delete('/:id', async (req: Request, res: Response) => {
  const id = parseInt(req.params.id, 10);
  if (isNaN(id)) {
    res.status(400).json({ detail: '无效的关联ID' });
    return;
  }
  try {
    await prisma.studentCourse.delete({ where: { id } });
    res.json({ result: 'success' });
  } catch (e) {
    res.status(404).json({ detail: `关联记录ID ${id} 不存在` });
  }
});

export default router;
