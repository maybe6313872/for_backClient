// @ts-check
const { test, expect } = require('@playwright/test');

const delay = (ms) => new Promise((r) => setTimeout(r, ms));

test.describe.serial('订单列表 OrderList 页面', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/orders/list');
    await page.waitForLoadState('networkidle');
  });

  test('1. 页面加载成功并显示标题', async ({ page }) => {
    await delay(2000);
    await expect(page.getByRole('heading', { name: '订单列表' })).toBeVisible();
    await expect(page.getByText('查看和管理所有订单')).toBeVisible();
    await delay(1500);
  });

  test('2. 接口调用：订单/公司/产品列表接口正常', async ({ page }) => {
    await delay(2000);
    const orderPromise = page.waitForResponse(
      (res) => (res.url().includes('order/query') || res.url().includes('api/order')) && res.status() === 200,
      { timeout: 15000 }
    );
    const companyPromise = page.waitForResponse(
      (res) => (res.url().includes('company/query') || res.url().includes('api/company')) && res.status() === 200,
      { timeout: 15000 }
    );
    const productPromise = page.waitForResponse(
      (res) => (res.url().includes('product/query') || res.url().includes('api/product')) && res.status() === 200,
      { timeout: 15000 }
    );
    await page.goto('/orders/list');
    const [orderRes, companyRes, productRes] = await Promise.all([
      orderPromise,
      companyPromise,
      productPromise,
    ]);
    expect(orderRes.ok()).toBeTruthy();
    expect(companyRes.ok()).toBeTruthy();
    expect(productRes.ok()).toBeTruthy();
    await delay(1500);
  });

  test('3. 表格区域存在：表头与数据或暂无数据', async ({ page }) => {
    await delay(2000);
    await expect(page.locator('table.order-table')).toBeVisible();
    await expect(page.getByRole('columnheader', { name: '订单号' })).toBeVisible();
    await expect(page.getByRole('columnheader', { name: '下单公司' })).toBeVisible();
    const hasData = await page.locator('tbody tr .empty-data').count() === 0;
    const hasEmpty = await page.getByText('暂无数据').isVisible();
    expect(hasData || hasEmpty).toBeTruthy();
    await delay(1500);
  });

  test('4. 点击查询按钮不报错并保持页面正常', async ({ page }) => {
    await delay(2000);
    const queryBtn = page.getByRole('button', { name: '查询' });
    await expect(queryBtn).toBeVisible();
    await queryBtn.click();
    await delay(1500);
    await expect(page.getByRole('heading', { name: '订单列表' })).toBeVisible();
    await delay(1500);
  });

  test('5. 点击新增打开弹窗，弹窗内容与关闭交互正确', async ({ page }) => {
    await delay(2000);
    const addBtn = page.getByRole('button', { name: '新增' });
    await addBtn.click();
    await delay(1000);
    await expect(page.getByRole('heading', { name: '新增订单' })).toBeVisible();
    await expect(page.getByLabel(/订单号/)).toBeVisible();
    await expect(page.getByLabel(/下单公司/)).toBeVisible();
    await delay(1500);
    await page.getByRole('button', { name: '取消' }).click();
    await delay(800);
    await expect(page.getByRole('heading', { name: '新增订单' })).not.toBeVisible();
    await delay(1500);
  });

  test('6. 公司管理按钮跳转到公司管理页', async ({ page }) => {
    await delay(2000);
    await page.getByRole('button', { name: '公司管理' }).click();
    await delay(1500);
    await expect(page).toHaveURL(/\/orders\/company/);
    await delay(1500);
    await page.goto('/orders/list');
    await page.waitForLoadState('networkidle');
    await delay(1500);
  });

  test('7. 产品管理按钮跳转到产品管理页', async ({ page }) => {
    await delay(2000);
    await page.getByRole('button', { name: '产品管理' }).click();
    await delay(1500);
    await expect(page).toHaveURL(/\/orders\/product/);
    await delay(1500);
  });
});
