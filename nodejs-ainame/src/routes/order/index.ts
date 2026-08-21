import { Router } from 'express';
import companyRouter from './company';
import productRouter from './product';
import orderRouter from './order';

const router = Router();
router.use('/company', companyRouter);
router.use('/product', productRouter);
router.use('/order', orderRouter);

export default router;
