<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">订单列表</h1>
      <p class="page-subtitle">查看和管理所有订单</p>
    </div>
    
    <div class="page-content">
      <div class="toolbar">
        <div class="toolbar-left">
          <button type="button" @click="queryOrders" class="btn btn-primary">查询</button>
          <button type="button" @click="openAddModal" class="btn btn-success">新增</button>
        </div>
        <div class="toolbar-right">
          <button type="button" @click="goToCompanyManagement" class="btn btn-secondary">公司管理</button>
          <button type="button" @click="goToProductManagement" class="btn btn-secondary">产品管理</button>
        </div>
      </div>
      
      <div class="table-container">
        <table class="order-table">
          <thead>
            <tr>
              <th>订单号</th>
              <th>下单公司</th>
              <th>产品及数量</th>
              <th>订单总价</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in orderList" :key="order.id">
              <td>{{ order.orderNumber }}</td>
              <td>{{ order.companyName }}</td>
              <td>
                <div v-for="(item, index) in order.products" :key="index" class="product-item">
                  {{ item.name }} × {{ item.quantity }}
                </div>
              </td>
              <td>¥{{ order.totalPrice}}</td>
              <td>
                <button type="button" @click="openEditModal(order)" class="btn-edit">编辑</button>
                <button type="button" @click="deleteOrder(order)" class="btn-delete">删除</button>
              </td>
            </tr>
            <tr v-if="orderList.length === 0">
              <td colspan="5" class="empty-data">暂无数据</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 新增/编辑弹窗 -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">{{ isEdit ? '编辑订单' : '新增订单' }}</h2>
          <button type="button" class="modal-close" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveOrder">
            <div class="form-group">
              <label for="orderNumber">订单号 <span class="required">*</span></label>
              <input 
                id="orderNumber" 
                v-model="formData.orderNumber" 
                type="text" 
                placeholder="请输入订单号"
                required
              />
            </div>
            <div class="form-group">
              <label for="companyName">下单公司 <span class="required">*</span></label>
              <select 
                id="companyName" 
                v-model="formData.companyId" 
                class="form-select"
                required>
                <option value="" disabled>请选择公司</option>
                <option v-for="value in companyList" :key="value.id" :value="value.id">{{ value.name }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>产品及数量 <span class="required">*</span></label>
              <div class="products-list">
                <div v-for="(product, index) in formData.products" :key="index" class="product-row">
                  <select 
                    v-model="product.productId" 
                    @change="onProductChange(index)"
                    class="product-select"
                    required>
                    <option value="" disabled>请选择产品</option>
                    <option v-for="p in productList" :key="p.id" :value="p.id">{{ p.name }}</option>
                  </select>
                  <input 
                    v-model.number="product.quantity" 
                    type="number" 
                    placeholder="数量"
                    min="1"
                    class="product-quantity-input"
                    required
                  />
                  <input 
                    v-model.number="product.price" 
                    type="number" 
                    placeholder="单价"
                    min="0"
                    step="0.01"
                    class="product-price-input"
                    required
                    readonly
                  />
                  <button type="button" @click="removeProduct(index)" class="btn-remove" v-if="formData.products.length > 1">删除</button>
                </div>
                <button type="button" @click="addProduct" class="btn-add-product">添加产品</button>
              </div>
            </div>
            <div class="form-group">
              <label>订单总价</label>
              <div class="total-price">¥{{ calculateTotalPrice().toFixed(2) }}</div>
            </div>
            <div class="modal-footer">
              <button type="button" @click="closeModal" class="btn btn-cancel">取消</button>
              <button type="submit" class="btn btn-submit">{{ isEdit ? '保存' : '新增' }}</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const yourToken = '123123123' || localStorage.getItem('token') || ''

// 订单列表数据
const orderList = ref([])

// 弹窗相关数据
const showModal = ref(false)
const isEdit = ref(false)
const formData = ref({
  id: null,
  orderNumber: '',
  companyName: '',
  companyId: '',
    products: [
      { productId: '', name: '', quantity: 1, price: 0 }
    ],
  totalPrice: 0
})

const companyList = ref([])

// 查询公司列表
const queryCompanies = async () => {
  const resp = await axios.get('/api/company/query', { 
    headers: { Authorization: 'Bearer ' + yourToken } 
  })
  companyList.value = resp.data.data || resp.data || []
}

const productList = ref([])
// 查询产品列表
const queryProducts = async () => {
  try {
    const resp = await axios.get('/api/product/query', { 
      headers: { Authorization: 'Bearer ' + yourToken } 
    })
    productList.value = resp.data.data || resp.data || []
    console.log('查询产品成功')
  } catch (error) {
    console.error('查询产品失败:', error)
    alert('查询产品失败')
  }
}
// 查询订单列表
const queryOrders = async () => {
  try {
    const resp = await axios.get('/api/order/query', { 
      headers: { Authorization: 'Bearer ' + yourToken } 
    })
    const res = resp.data.data || resp.data || []
    orderList.value = res.map(order => ({
      id: order.id,
      orderNumber: order.order_number,
      companyName: order.companyName,
      companyId: order.company_id,
      products: order.product_list.map(p => ({
        productId: p.product_id,
        name: p.product_name,
        quantity: p.number,
        price: p.price || 0
      })),
      totalPrice: order.total_price || 0
    }))
    
    // 计算每个订单的总价
    orderList.value.forEach(order => {
      if (!order.totalPrice && order.products) {
        order.totalPrice = order.products.reduce((sum, p) => sum + (p.price || 0) * (p.quantity || 0), 0)
      }
    })
    
    console.log('查询订单成功')
  } catch (error) {
    console.error('查询订单失败:', error)
    alert('查询订单失败')
  }
}

// 打开新增弹窗
const openAddModal = () => {
  isEdit.value = false
  formData.value = {
    id: null,
    orderNumber: '',
    companyName: '',
    companyId: '',
    products: [
      { productId: '', name: '', quantity: 1, price: 0 }
    ],
    totalPrice: 0
  }
  showModal.value = true
}

// 打开编辑弹窗
const openEditModal = (order) => {
  isEdit.value = true
  // 处理产品数据，如果已有产品数据，需要匹配 productId
  const processedProducts = order.products ? order.products.map(p => {
    // 如果产品有 name，尝试从 productList 中找到对应的 productId
    if (p.name && productList.value.length > 0) {
      const matchedProduct = productList.value.find(prod => prod.name === p.name)
      return {
        productId: matchedProduct ? matchedProduct.id : '',
        name: p.name,
        quantity: p.quantity || 1,
        price: p.price || 0
      }
    }
    return {
      productId: p.productId || '',
      name: p.name || '',
      quantity: p.quantity || 1,
      price: p.price || 0
    }
  }) : [{ productId: '', name: '', quantity: 1, price: 0 }]
  
  formData.value = {
    id: order.id,
    orderNumber: order.orderNumber,
    companyName: order.companyName,
    companyId: order.companyId,
    products: processedProducts,
    totalPrice: order.totalPrice || 0
  }
  showModal.value = true
}

// 关闭弹窗
const closeModal = () => {
  showModal.value = false
  formData.value = {
    id: null,
    orderNumber: '',
    companyName: '',
    companyId: '',
    products: [
      { productId: '', name: '', quantity: 1, price: 0 }
    ],
    totalPrice: 0
  }
}

// 添加产品
const addProduct = () => {
  formData.value.products.push({ productId: '', name: '', quantity: 1, price: 0 })
}

// 产品选择变化处理
const onProductChange = (index) => {
  const selectedProductId = formData.value.products[index].productId
  const selectedProduct = productList.value.find(p => p.id === selectedProductId)
  if (selectedProduct) {
    formData.value.products[index].name = selectedProduct.name
    formData.value.products[index].price = selectedProduct.price || 0
  }
}

// 删除产品
const removeProduct = (index) => {
  formData.value.products.splice(index, 1)
}

// 计算总价
const calculateTotalPrice = () => {
  return formData.value.products.reduce((sum, p) => {
    return sum + (parseFloat(p.price) || 0) * (parseInt(p.quantity) || 0)
  }, 0)
}

// 保存订单（新增或编辑）
const saveOrder = async () => {
  try {
    // 新增订单
    const totalPrice = calculateTotalPrice()
    const orderData = {
      id: formData.value.id,
      company_id: formData.value.companyId,
      order_number: formData.value.orderNumber,
      product_list: formData.value.products.map(p => ({
        id: p.productId,
        number: p.quantity,
      })),
    }
    
    if (isEdit.value) {
      // 编辑订单
      const resp = await axios.put(`/api/order/update`, orderData, {
        headers: { Authorization: 'Bearer ' + yourToken }
      })
      console.log('编辑订单成功')
      queryOrders()
    } else {
      
      const resp = await axios.post('/api/order/create', orderData, {
        headers: { Authorization: 'Bearer ' + yourToken }
      })
      console.log('新增订单成功')
      queryOrders()
    }
    closeModal()
  } catch (error) {
    console.error('保存订单失败:', error)
    alert('保存订单失败')
  }
}

// 删除订单
const deleteOrder = async (order) => {
  if (!confirm(`确定要删除订单"${order.orderNumber}"吗？`)) {
    return
  }
  
  try {
    const resp = await axios.delete(`/api/order/delete?id=${order.id}`, {
      headers: { Authorization: 'Bearer ' + yourToken }
    })
    console.log('删除订单成功')
    queryOrders()
  } catch (error) {
    console.error('删除订单失败:', error)
    alert('删除订单失败')
  }
}

// 跳转到公司管理
const goToCompanyManagement = () => {
  router.push('/orders/company')
}

// 跳转到产品管理
const goToProductManagement = () => {
  router.push('/orders/product')
}

// 页面加载时自动查询
onMounted(() => {
  queryOrders()
  queryCompanies()
  queryProducts()
})
</script>

<style scoped>
.page-container {
  width: 100%;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 14px;
  color: #666;
}

.page-content {
  background-color: #ffffff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  min-height: 400px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0056b3;
  transform: translateY(-1px);
}

.btn-success {
  background-color: #28a745;
  color: white;
}

.btn-success:hover {
  background-color: #218838;
  transform: translateY(-1px);
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
  transform: translateY(-1px);
}

.table-container {
  overflow-x: auto;
}

.order-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.order-table thead {
  background-color: #f8f9fa;
}

.order-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #dee2e6;
  white-space: nowrap;
}

.order-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #dee2e6;
  color: #666;
}

.order-table tbody tr:hover {
  background-color: #f8f9fa;
}

.order-table tbody tr:last-child td {
  border-bottom: none;
}

.product-item {
  margin-bottom: 4px;
}

.product-item:last-child {
  margin-bottom: 0;
}

.empty-data {
  text-align: center;
  color: #999;
  padding: 40px !important;
}

.btn-edit,
.btn-delete {
  padding: 4px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  margin-right: 8px;
  transition: background-color 0.3s ease;
}

.btn-edit {
  background-color: #ffc107;
  color: #333;
}

.btn-edit:hover {
  background-color: #e0a800;
}

.btn-delete {
  background-color: #dc3545;
  color: white;
}

.btn-delete:hover {
  background-color: #c82333;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-content {
  background-color: #ffffff;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  animation: slideUp 0.3s ease;
  max-height: 90vh;
  overflow-y: auto;
}

@keyframes slideUp {
  from {
    transform: translateY(50px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 28px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background-color 0.2s, color 0.2s;
  line-height: 1;
}

.modal-close:hover {
  background-color: #f0f0f0;
  color: #333;
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.required {
  color: #dc3545;
}

.form-group input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.form-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-size: 14px;
  background-color: #fff;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3e%3cpath fill='none' stroke='%23343a40' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M2 5l6 6 6-6'/%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 16px 12px;
  padding-right: 40px;
  appearance: none;
  cursor: pointer;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
  box-sizing: border-box;
}

.form-select:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.form-select option {
  padding: 8px;
}

.product-select {
  flex: 2;
  padding: 10px 12px;
  padding-right: 40px;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-size: 14px;
  background-color: #fff;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3e%3cpath fill='none' stroke='%23343a40' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M2 5l6 6 6-6'/%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 16px 12px;
  appearance: none;
  cursor: pointer;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
  box-sizing: border-box;
}

.product-select:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.product-select option {
  padding: 8px;
}

.products-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.product-row {
  display: flex;
  gap: 8px;
  align-items: center;
}


.product-quantity-input {
  flex: 1;
}

.product-price-input {
  flex: 1;
  background-color: #f8f9fa;
  cursor: not-allowed;
}

.btn-remove {
  padding: 8px 12px;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  white-space: nowrap;
}

.btn-remove:hover {
  background-color: #c82333;
}

.btn-add-product {
  padding: 8px 16px;
  background-color: #17a2b8;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  width: fit-content;
}

.btn-add-product:hover {
  background-color: #138496;
}

.total-price {
  font-size: 18px;
  font-weight: 600;
  color: #007bff;
  padding: 10px 12px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.btn-cancel {
  background-color: #6c757d;
  color: white;
}

.btn-cancel:hover {
  background-color: #5a6268;
}

.btn-submit {
  background-color: #007bff;
  color: white;
}

.btn-submit:hover {
  background-color: #0056b3;
}
</style>
