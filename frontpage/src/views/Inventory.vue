<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">学校列表</h1>
    </div>
    
    <div class="page-content">
      <div class="toolbar">
        <button type="button" @click="querySchools" class="btn btn-primary">查询</button>
        <button type="button" @click="openAddModal" class="btn btn-success">新增</button>
      </div>
      
      <div class="table-container">
        <table class="school-table">
          <thead>
            <tr>
              <th>学校名称</th>
              <th>学校地址</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="school in schoolList" :key="school.id">
              <td>{{ school.name }}</td>
              <td>{{ school.address }}</td>
              <td>
                <button type="button" @click="viewTeachers(school)" class="btn-view">查看班主任</button>
                <button type="button" @click="openEditModal(school)" class="btn-edit">编辑</button>
                <button type="button" @click="deleteSchool(school)" class="btn-delete">删除</button>
              </td>
            </tr>
            <tr v-if="schoolList.length === 0">
              <td colspan="3" class="empty-data">暂无数据</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 新增/编辑弹窗 -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">{{ isEdit ? '编辑学校' : '新增学校' }}</h2>
          <button type="button" class="modal-close" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveSchool">
            <div class="form-group">
              <label for="schoolName">学校名称 <span class="required">*</span></label>
              <input 
                id="schoolName" 
                v-model="formData.name" 
                type="text" 
                placeholder="请输入学校名称"
                required
              />
            </div>
            <div class="form-group">
              <label for="schoolAddress">学校地址 <span class="required">*</span></label>
              <input 
                id="schoolAddress" 
                v-model="formData.address" 
                type="text" 
                placeholder="请输入学校地址"
                required
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
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const yourToken = '123123123' || localStorage.getItem('token') || ''

// 学校列表数据
const schoolList = ref([])

// 弹窗相关数据
const showModal = ref(false)
const isEdit = ref(false)
const formData = ref({
  id: null,
  name: '',
  address: ''
})

// 查询学校列表
const querySchools = async () => {
  try {
    // 这里调用后端API查询学校数据
    const resp = await axios.get('/api/school', { 
      headers: { Authorization: 'Bearer ' + yourToken } 
    })
    schoolList.value = resp.data.data || resp.data || resp || []
    
    // 模拟数据，实际使用时替换为真实API调用
    // schoolList.value = [
    //   { id: 1, name: '北京大学', address: '北京市海淀区颐和园路5号' },
    //   { id: 2, name: '清华大学', address: '北京市海淀区清华园1号' },
    //   { id: 3, name: '复旦大学', address: '上海市杨浦区邯郸路220号' },
    //   { id: 4, name: '上海交通大学', address: '上海市闵行区东川路800号' }
    // ]
    console.log('查询学校成功')
  } catch (error) {
    console.error('查询学校失败:', error)
    alert('查询学校失败')
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
const openEditModal = (school) => {
  isEdit.value = true
  formData.value = {
    id: school.id,
    name: school.name,
    address: school.address
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

// 保存学校（新增或编辑）
const saveSchool = async () => {
  try {
    if (isEdit.value) {
      // 编辑学校
      const resp = await axios.put(`/api/school/${formData.value.id}`, formData.value, {
        headers: { Authorization: 'Bearer ' + yourToken }
      })
      
      // 模拟更新
      // const index = schoolList.value.findIndex(s => s.id === formData.value.id)
      // if (index !== -1) {
      //   schoolList.value[index] = { ...formData.value }
      // }
      console.log('编辑学校成功')
      querySchools()
    } else {
      // 新增学校
      const resp = await axios.post('/api/school', formData.value, {
        headers: { Authorization: 'Bearer ' + yourToken }
      })
      
      // 模拟新增
      // const newId = Math.max(...schoolList.value.map(s => s.id), 0) + 1
      // schoolList.value.push({
      //   id: newId,
      //   name: formData.value.name,
      //   address: formData.value.address
      // })
      console.log('新增学校成功')
      querySchools()
    }
    closeModal()
    // 如果需要，可以重新查询列表
    // querySchools()
  } catch (error) {
    console.error('保存学校失败:', error)
    alert('保存学校失败')
  }
}

// 查看班主任
const viewTeachers = (school) => {
  router.push({
    name: 'TeacherList',
    query: { schoolId: school.id, schoolName: school.name }
  })
}

// 删除学校
const deleteSchool = async (school) => {
  if (!confirm(`确定要删除学校"${school.name}"吗？`)) {
    return
  }
  
  try {
    // 这里调用后端API删除学校
    const resp = await axios.delete(`/api/school/${school.id}`, {
      headers: { Authorization: 'Bearer ' + yourToken }
    })
    
    // 模拟删除
    // const index = schoolList.value.findIndex(s => s.id === school.id)
    // if (index !== -1) {
    //   schoolList.value.splice(index, 1)
    // }
    console.log('删除学校成功')
    querySchools()
  } catch (error) {
    console.error('删除学校失败:', error)
    alert('删除学校失败')
  }
}

// 页面加载时自动查询
onMounted(() => {
  querySchools()
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
  margin: 0;
}

.page-content {
  background-color: #ffffff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
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

.school-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.school-table thead {
  background-color: #f8f9fa;
}

.school-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #dee2e6;
  white-space: nowrap;
}

.school-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #dee2e6;
  color: #666;
}

.school-table tbody tr:hover {
  background-color: #f8f9fa;
}

.school-table tbody tr:last-child td {
  border-bottom: none;
}

.empty-data {
  text-align: center;
  color: #999;
  padding: 40px !important;
}

.btn-view,
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

.btn-view {
  background-color: #17a2b8;
  color: white;
}

.btn-view:hover {
  background-color: #138496;
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
