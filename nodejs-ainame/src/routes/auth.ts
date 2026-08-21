import { Router, Request, Response } from 'express';
import { z } from 'zod';
import argon2 from 'argon2';
import { prisma } from '../lib/prisma';
import { sendMail } from '../lib/mail';
import { encodeLoginToken } from '../middleware/auth';

const router = Router();

const RegisterBody = z.object({
  email: z.string().email(),
  username: z.string().min(3).max(20),
  password: z.string().min(6).max(20),
  confirm_password: z.string().min(6).max(20),
  code: z.string().length(4),
});
RegisterBody.refine((d) => d.password === d.confirm_password, {
  message: '两个密码不一致！',
  path: ['confirm_password'],
});

const LoginBody = z.object({
  email: z.string().email(),
  password: z.string().min(6).max(20),
});

/** GET /auth/code - 发送邮箱验证码 */
router.get('/code', async (req: Request, res: Response) => {
  const email = req.query.email as string;
  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    res.status(400).json({ detail: '邮箱格式无效' });
    return;
  }
  const code = Array.from({ length: 4 }, () => Math.floor(Math.random() * 10)).join('');
  try {
    await sendMail({
      to: email,
      subject: '【知了课堂】注册验证码',
      text: `您的验证码为：${code}，五分钟有效！`,
    });
    await prisma.emailCode.create({
      data: { email, code },
    });
    res.json({ result: 'success' });
  } catch (e) {
    console.error(e);
    res.status(500).json({ detail: '邮件发送失败！' });
  }
});

/** POST /auth/register - 用户注册 */
router.post('/register', async (req: Request, res: Response) => {
  const parsed = RegisterBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ detail: parsed.error.errors.map((e) => e.message).join('; ') });
    return;
  }
  const { email, username, password, code } = parsed.data;
  const exist = await prisma.user.findUnique({ where: { email } });
  if (exist) {
    res.status(400).json({ detail: '该邮箱已经存在！' });
    return;
  }
  const tenMinAgo = new Date(Date.now() - 10 * 60 * 1000);
  const record = await prisma.emailCode.findFirst({
    where: { email, code, createdTime: { gte: tenMinAgo } },
    orderBy: { createdTime: 'desc' },
  });
  if (!record) {
    res.status(400).json({ detail: '邮箱或验证码错误！' });
    return;
  }
  const hashed = await argon2.hash(password);
  try {
    await prisma.user.create({
      data: { email, username, password: hashed },
    });
    res.json({ result: 'success' });
  } catch (e) {
    console.error(e);
    res.status(500).json({ detail: String(e) });
  }
});

/** POST /auth/login - 用户登录 */
router.post('/login', async (req: Request, res: Response) => {
  const parsed = LoginBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ detail: '参数错误' });
    return;
  }
  const { email, password } = parsed.data;
  const user = await prisma.user.findUnique({ where: { email } });
  if (!user) {
    res.status(400).json({ detail: '该用户不存在！' });
    return;
  }
  const ok = await argon2.verify(user.password, password);
  if (!ok) {
    res.status(400).json({ detail: '邮箱或密码错误！' });
    return;
  }
  const tokens = encodeLoginToken(user.id);
  res.json({
    user: { id: user.id, email: user.email, username: user.username },
    token: tokens.access_token,
  });
});

export default router;
