<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">公司管理</h1>
      <p class="page-subtitle">管理系统中的公司信息</p>
    </div>
    
    <div class="page-content">
      <div class="toolbar">
        <button type="button" @click="queryCompanies" class="btn btn-primary">查询</button>
        <button type="button" @click="openAddModal" class="btn btn-success">新增</button>
      </div>
      
      <div class="table-container">
        <table class="company-table">
          <thead>
            <tr>
              <th>公司名称</th>
              <th>公司地址</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="company in companyList" :key="company.id">
              <td>{{ company.name }}</td>
              <td>{{ company.address }}</td>
              <td>
                <button type="button" @click="openEditModal(company)" class="btn-edit">编辑</button>
                <button type="button" @click="deleteCompany(company)" class="btn-delete">删除</button>
              </td>
            </tr>
            <tr v-if="companyList.length === 0">
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
          <h2 class="modal-title">{{ isEdit ? '编辑公司' : '新增公司' }}</h2>
          <button type="button" class="modal-close" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveCompany">
            <div class="form-group">
              <label for="companyName">公司名称 <span class="required">*</span></label>
              <input 
                id="companyName" 
                v-model="formData.name" 
                type="text" 
                placeholder="请输入公司名称"
                required
              />
            </div>
            <div class="form-group">
              <label for="address">公司地址</label>
              <input 
                id="address" 
                v-model="formData.address" 
                type="text" 
                placeholder="请输入公司地址"
              />
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
import axios from 'axios'

const yourToken = '123123123' || localStorage.getItem('token') || ''

// 公司列表数据
const companyList = ref([])

// 弹窗相关数据
const showModal = ref(false)
const isEdit = ref(false)
const formData = ref({
  id: null,
  name: '',
  address: ''
})

// 查询公司列表
const queryCompanies = async () => {
  try {
    const resp = await axios.get('/api/company/query', { 
      headers: { Authorization: 'Bearer ' + yourToken } 
    })
    companyList.value = resp.data.data || resp.data || []
    
    // 模拟数据
    if (companyList.value.length === 0) {
      companyList.value = [
        {
          id: 1,
          name: '科技有限公司',
          contact: '张三',
          phone: '13800138000',
          address: '北京市朝阳区xxx路xxx号'
        },
        {
          id: 2,
          name: '贸易有限公司',
          contact: '李四',
          phone: '13900139000',
          address: '上海市浦东新区xxx路xxx号'
        }
      ]
    }
    
    console.log('查询公司成功')
  } catch (error) {
    console.error('查询公司失败:', error)
    alert('查询公司失败')
  }
}

// 打开新增弹窗
const openAddModal = () => {
  isEdit.value = false
  formData.value = {
    id: null,
    name: '',
    address: ''
  }
  showModal.value = true
}

// 打开编辑弹窗
const openEditModal = (company) => {
  isEdit.value = true
  formData.value = {
    id: company.id,
    name: company.name,
    address: company.address
  }
  showModal.value = true
}

// 关闭弹窗
const closeModal = () => {
  showModal.value = false
  formData.value = {
    id: null,
    name: '',
    address: ''
  }
}

// 保存公司（新增或编辑）
const saveCompany = async () => {
  try {
    if (isEdit.value) {
      // 编辑公司
      const resp = await axios.put(`/api/company/update`, formData.value, {
        headers: { Authorization: 'Bearer ' + yourToken }
      })
      console.log('编辑公司成功')
      queryCompanies()
    } else {
      // 新增公司
      const resp = await axios.post('/api/company/create', formData.value, {
        headers: { Authorization: 'Bearer ' + yourToken }
      })
      console.log('新增公司成功')
      queryCompanies()
    }
    closeModal()
  } catch (error) {
    console.error('保存公司失败:', error)
    alert('保存公司失败')
  }
}

// 删除公司
const deleteCompany = async (company) => {
  if (!confirm(`确定要删除公司"${company.name}"吗？`)) {
    return
  }
  
  try {
    const resp = await axios.delete(`/api/company/delete?company_id=${company.id}`, {
      headers: { Authorization: 'Bearer ' + yourToken }
    })
    console.log('删除公司成功')
    queryCompanies()
  } catch (error) {
    console.error('删除公司失败:', error)
    alert('删除公司失败')
  }
}

// 页面加载时自动查询
onMounted(() => {
  queryCompanies()
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
  gap: 12px;
  margin-bottom: 20px;
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

.table-container {
  overflow-x: auto;
}

.company-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.company-table thead {
  background-color: #f8f9fa;
}

.company-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #dee2e6;
  white-space: nowrap;
}

.company-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #dee2e6;
  color: #666;
}

.company-table tbody tr:hover {
  background-color: #f8f9fa;
}

.company-table tbody tr:last-child td {
  border-bottom: none;
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
  max-width: 500px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  animation: slideUp 0.3s ease;
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
