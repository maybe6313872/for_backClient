import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { prisma } from '../../lib/prisma';

const router = Router();

const OrderCreateIn = z.object({
  order_number: z.string().max(100),
  company_id: z.number(),
  product_list: z.array(
    z.object({ product_id: z.number(), number: z.number().min(1).optional().default(1) })
  ),
});
const OrderUpdateIn = OrderCreateIn.extend({ id: z.number() });

/** POST /order/create - 创建订单 */
router.post('/create', async (req: Request, res: Response) => {
  const parsed = OrderCreateIn.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ detail: parsed.error.message });
    return;
  }
  try {
    const order = await prisma.order.create({
      data: {
        orderNumber: parsed.data.order_number,
        companyId: parsed.data.company_id,
        products: {
          create: parsed.data.product_list.map((p) => ({
            productId: p.product_id,
            number: p.number ?? 1,
          })),
        },
      },
    });
    res.json({ code: 200, message: '创建成功', data: order.id });
  } catch (e) {
    console.error(e);
    res.status(500).json({ detail: String(e) });
  }
});

/** PUT /order/update - 更新订单 */
router.put('/update', async (req: Request, res: Response) => {
  const parsed = OrderUpdateIn.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ detail: parsed.error.message });
    return;
  }
  try {
    await prisma.orderProduct.deleteMany({ where: { orderId: parsed.data.id } });
    await prisma.order.update({
      where: { id: parsed.data.id },
      data: {
        orderNumber: parsed.data.order_number,
        companyId: parsed.data.company_id,
        products: {
          create: parsed.data.product_list.map((p) => ({
            productId: p.product_id,
            number: p.number ?? 1,
          })),
        },
      },
    });
    res.json({ code: 200, message: 'updated successfully' });
  } catch (e) {
    res.status(500).json({ detail: String(e) });
  }
});

/** GET /order/query - 查询订单列表 */
router.get('/query', async (_req: Request, res: Response) => {
  try {
    const list = await prisma.order.findMany({
      include: { company: true, products: { include: { product: true } } },
      orderBy: { id: 'asc' },
    });
    res.json({ code: 200, data: list, msg: 'success' });
  } catch (e) {
    console.error(e);
    res.status(500).json({ detail: String(e) });
  }
});

/** DELETE /order/delete?id= */
router.delete('/delete', async (req: Request, res: Response) => {
  const id = parseInt(req.query.id as string, 10);
  if (isNaN(id)) {
    res.status(400).json({ detail: '缺少 id' });
    return;
  }
  try {
    await prisma.order.delete({ where: { id } });
    res.json({ code: 200, message: '删除成功' });
  } catch (e) {
    res.status(404).json({ detail: '订单未找到' });
  }
});

export default router;
