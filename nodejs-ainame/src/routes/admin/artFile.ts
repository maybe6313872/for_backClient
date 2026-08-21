import { Router, Request, Response } from 'express';
import * as XLSX from 'xlsx';
import { prisma } from '../../lib/prisma';
import { z } from 'zod';

const router = Router();

const ArtQueryBody = z.object({
  page: z.number().min(1).default(1),
  size: z.number().min(1).max(100).default(10),
  sex: z.string().max(10),
});

/** POST /admin/queryArtExcel - 导出文章为 Excel */
router.post('/queryArtExcel', async (req: Request, res: Response) => {
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
    select: { id: true, username: true, sex: true, artcontent: true },
  });
  const headers = ['ID', '用户名', '性别', '文章内容'];
  const rows = list.map((a) => [a.id, a.username, a.sex, a.artcontent]);
  const wb = XLSX.utils.book_new();
  const ws = XLSX.utils.aoa_to_sheet([headers, ...rows]);
  XLSX.utils.book_append_sheet(wb, ws, '文章列表');
  const buf = XLSX.write(wb, { type: 'buffer', bookType: 'xlsx' });
  const timestamp = new Date().toISOString().replace(/[-:T]/g, '').slice(0, 15);
  const filename = `文章列表_${timestamp}.xlsx`;
  res.setHeader(
    'Content-Disposition',
    `attachment; filename*=UTF-8''${encodeURIComponent(filename)}`
  );
  res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
  res.send(buf);
});

/** POST /admin/insertArtByExcel - 从 Excel 批量导入文章 */
router.post('/insertArtByExcel', async (req: Request, res: Response) => {
  const upload = (req as Request & { file?: Express.Multer.File }).file;
  if (!upload?.buffer) {
    res.status(400).json({ detail: '请上传 Excel 文件' });
    return;
  }
  if (!upload.originalname.match(/\.(xlsx|xls)$/i)) {
    res.status(400).json({ detail: '文件格式错误，仅支持 .xlsx 或 .xls 格式' });
    return;
  }
  let workbook: XLSX.WorkBook;
  try {
    workbook = XLSX.read(upload.buffer, { type: 'buffer' });
  } catch (e) {
    res.status(400).json({ detail: 'Excel 解析失败' });
    return;
  }
  const sheet = workbook.Sheets[workbook.SheetNames[0]];
  const data = XLSX.utils.sheet_to_json<string[]>(sheet, { header: 1 }) as string[][];
  if (!data.length) {
    res.status(400).json({ detail: 'Excel文件为空或没有数据行' });
    return;
  }
  const headerRow = data[0].map((h) => String(h || '').trim());
  const col = (name: string, aliases: string[]) => {
    const i = headerRow.findIndex((h) => aliases.some((a) => h.includes(a) || h === a));
    return i >= 0 ? i : null;
  };
  const usernameCol = col('username', ['用户名', 'username', '用户']);
  const sexCol = col('sex', ['性别', 'sex']);
  const artcontentCol = col('artcontent', ['文章内容', 'artcontent', '内容', 'content']);
  const thumbnailCol = col('thumbnail', ['缩略图', 'thumbnail', '图片', 'image']);
  if (usernameCol == null || sexCol == null || artcontentCol == null) {
    res.status(400).json({ detail: "Excel 中缺少必需列：用户名、性别、文章内容" });
    return;
  }
  let successCount = 0;
  const errors: string[] = [];
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    const username = String((row[usernameCol] ?? '')).trim();
    const sex = String((row[sexCol] ?? '')).trim();
    const artcontent = String((row[artcontentCol] ?? '')).trim();
    if (!username || !sex || !artcontent) {
      errors.push(`第${i + 1}行：缺少必需字段`);
      continue;
    }
    if (username.length > 100 || sex.length > 10 || artcontent.length > 5000) {
      errors.push(`第${i + 1}行：字段长度超限`);
      continue;
    }
    let thumbnail: Buffer = Buffer.alloc(0);
    if (thumbnailCol != null && row[thumbnailCol]) {
      try {
        thumbnail = Buffer.from(String(row[thumbnailCol]).trim(), 'base64');
      } catch {
        // 忽略单行 base64 错误
      }
    }
    try {
      await prisma.art.create({
        data: { username, sex, artcontent, thumbnail },
      });
      successCount++;
    } catch (e) {
      errors.push(`第${i + 1}行: ${String(e)}`);
    }
  }
  if (successCount === 0) {
    res.status(400).json({
      detail: `批量导入失败，共${errors.length}条错误。${errors.slice(0, 5).join('; ')}`,
    });
    return;
  }
  res.json({ result: 'success' });
});

export { router as artFileRouter };
