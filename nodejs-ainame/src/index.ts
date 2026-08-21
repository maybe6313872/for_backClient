/**
 * 知了AI起名 API - Node.js 实现
 * 基于 Express + TypeScript，与 FastAPI 版功能对齐
 */
import 'dotenv/config';

import express from 'express';
import cors from 'cors';
import authRouter from './routes/auth';
import nameRouter from './routes/name';
import regionRouter from './routes/region';
import schoolRouter from './routes/school';
import teacherRouter from './routes/teacher';
import studentRouter from './routes/student';
import courseRouter from './routes/course';
import studentCourseRouter from './routes/student-course';
import orderRouter from './routes/order';
import { artRouter } from './routes/admin/art';
import { artFileRouter } from './routes/admin/artFile';
import { upload } from './middleware/upload';
import { sendMail } from './lib/mail';
import { getRedis } from './lib/redis';

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// ---------- 根路由 ----------
app.get('/', (_req, res) => {
  res.json({ message: 'Hello World' });
});

app.get('/hello/:name', (req, res) => {
  res.json({ message: `Hello ${req.params.name}` });
});

/** GET /mail/test?email= - 邮件测试 */
app.get('/mail/test', async (req, res) => {
  const email = req.query.email as string;
  if (!email) {
    res.status(400).json({ detail: '缺少 email 参数' });
    return;
  }
  try {
    await sendMail({
      to: email,
      subject: 'hello',
      text: `hello ${email}`,
    });
    res.json({ message: '邮件发送成功！' });
  } catch (e) {
    console.error(e);
    res.status(500).json({ detail: '邮件发送失败' });
  }
});

// ---------- 业务路由 ----------
app.use('/auth', authRouter);
app.use('/name', nameRouter);
app.use('/region', regionRouter);
app.use('/school', schoolRouter);
app.use('/teacher', teacherRouter);
app.use('/student', studentRouter);
app.use('/course', courseRouter);
app.use('/student-course', studentCourseRouter);
app.use('/', orderRouter); // /company, /product, /order

// Admin：文章接口需 multipart 的单独用 upload
app.use('/admin', upload.single('file'), (req, res, next) => {
  next();
});
app.use('/admin', artRouter);
app.use('/admin', artFileRouter);

// ---------- 启动 ----------
const PORT = process.env.PORT ? parseInt(process.env.PORT, 10) : 8000;

async function main() {
  // 预连 Redis（可选，首次请求时也会连）
  try {
    const redis = getRedis();
    await redis.ping();
  } catch (e) {
    console.warn('Redis 未连接，region 接口可能不可用:', (e as Error).message);
  }

  app.listen(PORT, () => {
    console.log(`知了AI起名 API 运行在 http://localhost:${PORT}`);
    console.log(`文档可参考原 FastAPI 项目 /docs 的接口说明`);
  });
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
