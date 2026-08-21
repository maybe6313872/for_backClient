import { Router, Request, Response } from 'express';
import { z } from 'zod';

const router = Router();

const NameBody = z.object({
  surname: z.string(),
  gender: z.enum(['不限', '男', '女']),
  length: z.enum(['不限', '单字', '两字']),
  other: z.string().optional().default(''),
  exclude: z.array(z.string()).optional().default([]),
});

/** POST /name - AI 起名（当前返回示例数据） */
router.post('/', (req: Request, res: Response) => {
  const parsed = NameBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ detail: parsed.error.message });
    return;
  }
  // 可在此接入 DeepSeek 等 AI 生成名字，目前返回示例
  res.json({
    names: [
      {
        name: '张子涵',
        reference: '《诗经·小雅》',
        moral: '子：有学问、有德行的人；涵：包容、涵养',
      },
    ],
  });
});

export default router;
