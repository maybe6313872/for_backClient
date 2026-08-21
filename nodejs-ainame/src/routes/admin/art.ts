import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { prisma } from '../../lib/prisma';
import { authAccess } from '../../middleware/auth';

const router = Router();

const ArtDeleteBody = z.object({ idArr: z.array(z.number()).min(1) });
const ArtChangeBody = z.object({ id: z.number(), sex: z.string().max(10) });
const ArtQueryBody = z.object({
  page: z.number().min(1).default(1),
  size: z.number().min(1).max(100).default(10),
  sex: z.string().max(10),
});

/** POST /admin/insertArt - 插入文章（multipart: username, sex, artcontent, file） */
router.post('/insertArt', async (req: Request, res: Response) => {
  const upload = (req as Request & { file?: Express.Multer.File }).file;
  const body = (req as Request & { body?: Record<string, string> }).body || {};
  const username = body.username;
  const sex = body.sex;
  const artcontent = body.artcontent;
  if (!username || !sex || !artcontent || !upload?.buffer) {
    res.status(400).json({ detail: '缺少 username、sex、artcontent 或 file' });
    return;
  }
  const maxSize = 100 * 1024 * 1024;
  if (upload.buffer.length > maxSize) {
    res.status(413).json({ detail: `文件大小超过限制，最大允许 ${maxSize / 1024 / 1024}MB` });
    return;
  }
  try {
    await prisma.art.create({
      data: {
        username,
        sex,
        artcontent,
        thumbnail: upload.buffer,
      },
    });
    res.json({ result: 'success' });
  } catch (e) {
    console.error(e);
    res.status(500).json({ detail: String(e) });
  }
});

/** POST /admin/delArt - 批量删除文章 */
router.post('/delArt', async (req: Request, res: Response) => {
  const parsed = ArtDeleteBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ detail: 'ID数组不能为空' });
    return;
  }
  const result = await prisma.art.deleteMany({ where: { id: { in: parsed.data.idArr } } });
  if (result.count === 0) {
    res.status(400).json({ detail: '未找到要删除的文章记录' });
    return;
  }
  res.json(result.count);
});

/** POST /admin/changeArt - 修改文章 */
router.post('/changeArt', async (req: Request, res: Response) => {
  const parsed = ArtChangeBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ detail: '参数错误' });
    return;
  }
  await prisma.art.update({
    where: { id: parsed.data.id },
    data: { sex: parsed.data.sex },
  });
  res.json({ code: 200, message: '修改成功', data: parsed.data.id });
});

/** POST /admin/queryArt - 查询文章（需 JWT） */
router.post('/queryArt', authAccess, async (req: Request, res: Response) => {
  const parsed = ArtQueryBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ detail: '参数错误' });
    return;
  }
  const { page, size, sex } = parsed.data;
  const list = await prisma.art.findMany({
    where: { sex },
    orderBy: { createdTime: 'desc' },
    skip: (page - 1) * size,
    take: size,
    select: { id: true, username: true, sex: true, artcontent: true, createdTime: true },
  });
  res.json(list);
});

/** POST /admin/queryArtOut - 查询文章（标准包装） */
router.post('/queryArtOut', async (req: Request, res: Response) => {
  const parsed = ArtQueryBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ detail: '参数错误' });
    return;
  }
  const { page, size, sex } = parsed.data;
  const list = await prisma.art.findMany({
    where: { sex },
    orderBy: { createdTime: 'desc' },
    skip: (page - 1) * size,
    take: size,
    select: { id: true, username: true, sex: true, artcontent: true, createdTime: true },
  });
  res.json({ code: 200, message: '查询成功', data: list });
});

export { router as artRouter };
