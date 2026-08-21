<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">班主任列表-{{ route.query.schoolName }}</h1>
    </div>
    
    <div class="page-content">
      <div class="toolbar">
        <button type="button" @click="queryTeachers" class="btn btn-primary">查询</button>
        <button type="button" @click="openAddModal" class="btn btn-success">新增</button>
      </div>
      
      <div class="table-container">
        <table class="teacher-table">
          <thead>
            <tr>
              <th>班主任姓名</th>
              <th>性别</th>
              <th>年龄</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="teacher in teacherList" :key="teacher.id">
              <td>{{ teacher.name }}</td>
              <td>{{ teacher.sex }}</td>
              <td>{{ teacher.age }}</td>
              <td>
                <button type="button" @click="viewStudents(teacher)" class="btn-view">查看学生</button>
                <button type="button" @click="openEditModal(teacher)" class="btn-edit">编辑</button>
                <button type="button" @click="deleteTeacher(teacher)" class="btn-delete">删除</button>
              </td>
            </tr>
            <tr v-if="teacherList.length === 0">
              <td colspan="4" class="empty-data">暂无数据</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 新增/编辑弹窗 -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">{{ isEdit ? '编辑班主任' : '新增班主任' }}</h2>
          <button type="button" class="modal-close" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveTeacher">
            <div class="form-group">
              <label for="teacherName">班主任姓名 <span class="required">*</span></label>
              <input 
                id="teacherName" 
                v-model="formData.name" 
                type="text" 
                placeholder="请输入班主任姓名"
                required
              />
            </div>
            <div class="form-group">
              <label for="teacherGender">性别 <span class="required">*</span></label>
              <select 
                id="teacherGender" 
                v-model="formData.sex" 
                required
                class="form-select"
              >
                <option value="">请选择性别</option>
                <option value="男">男</option>
                <option value="女">女</option>
              </select>
            </div>
            <div class="form-group">
              <label for="teacherAge">年龄 <span class="required">*</span></label>
              <input 
                id="teacherAge" 
                v-model.number="formData.age" 
                type="number" 
                placeholder="请输入年龄"
                min="18"
                max="100"
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
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route = useRoute()

const yourToken = '123123123' || localStorage.getItem('token') || ''

// 班主任列表数据
const teacherList = ref([])

// 弹窗相关数据
const showModal = ref(false)
const isEdit = ref(false)
const formData = ref({
  id: null,
  name: '',
  sex: '',
  age: null
})

// 查询班主任列表
const queryTeachers = async () => {
  try {
    // 这里调用后端API查询班主任数据
    const resp = await axios.get('/api/teacher?school_id=' + (route.query.schoolId + ''), { 
      headers: { Authorization: 'Bearer ' + yourToken } 
    })
    teacherList.value = resp.data.data || resp.data || []
    
    // 模拟数据，实际使用时替换为真实API调用
    // teacherList.value = [
    //   { id: 1, name: '张老师', sex: '男', age: 35 },
    //   { id: 2, name: '李老师', sex: '女', age: 28 },
    //   { id: 3, name: '王老师', sex: '男', age: 42 },
    //   { id: 4, name: '刘老师', sex: '女', age: 31 }
    // ]
    console.log('查询班主任成功')
  } catch (error) {
    console.error('查询班主任失败:', error)
    alert('查询班主任失败')
  }
}

// 打开新增弹窗
const openAddModal = () => {
  isEdit.value = false
  formData.value = {
    id: null,
    name: '',
    sex: '',
    age: null
  }
  showModal.value = true
}

// 打开编辑弹窗
const openEditModal = (teacher) => {
  isEdit.value = true
  formData.value = {
    id: teacher.id,
    name: teacher.name,
    sex: teacher.sex,
    age: teacher.age
  }
  showModal.value = true
}

// 关闭弹窗
const closeModal = () => {
  showModal.value = false
  formData.value = {
    id: null,
    name: '',
    sex: '',
    age: null
  }
}

// 保存班主任（新增或编辑）
const saveTeacher = async () => {
  try {
    if (isEdit.value) {
      // 编辑班主任
      const resp = await axios.put(`/api/teacher/${formData.value.id}`, formData.value, {
        headers: { Authorization: 'Bearer ' + yourToken }
      })
      
      // 模拟更新
      // const index = teacherList.value.findIndex(t => t.id === formData.value.id)
      // if (index !== -1) {
      //   teacherList.value[index] = { ...formData.value }
      // }
      console.log('编辑班主任成功')
      queryTeachers()
    } else {
      // 新增班主任
      const resp = await axios.post('/api/teacher', {
        school_id: route.query.schoolId,
        name: formData.value.name,
        sex: formData.value.sex,
        age: formData.value.age
      }, {
        headers: { Authorization: 'Bearer ' + yourToken }
      })
      queryTeachers()
      // 模拟新增
      // const newId = Math.max(...teacherList.value.map(t => t.id), 0) + 1
      // teacherList.value.push({
      //   id: newId,
      //   name: formData.value.name,
      //   sex: formData.value.sex,
      //   age: formData.value.age
      // })
      console.log('新增班主任成功')
    }
    closeModal()
  } catch (error) {
    console.error('保存班主任失败:', error)
    alert('保存班主任失败')
  }
}

// 查看学生
const viewStudents = (teacher) => {
  router.push({
    name: 'StudentList',
    query: { teacherId: teacher.id, teacherName: teacher.name }
  })
}

// 删除班主任
const deleteTeacher = async (teacher) => {
  if (!confirm(`确定要删除班主任"${teacher.name}"吗？`)) {
    return
  }
  
  try {
    // 这里调用后端API删除班主任
    const resp = await axios.delete(`/api/teacher/${teacher.id}`, {
      headers: { Authorization: 'Bearer ' + yourToken }
    })
    
    // 模拟删除
    // const index = teacherList.value.findIndex(t => t.id === teacher.id)
    // if (index !== -1) {
    //   teacherList.value.splice(index, 1)
    // }
    console.log('删除班主任成功')
    queryTeachers()
  } catch (error) {
    console.error('删除班主任失败:', error)
    alert('删除班主任失败')
  }
}

// 页面加载时自动查询
onMounted(() => {
  queryTeachers()
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

.teacher-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.teacher-table thead {
  background-color: #f8f9fa;
}

.teacher-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #dee2e6;
  white-space: nowrap;
}

.teacher-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #dee2e6;
  color: #666;
}

.teacher-table tbody tr:hover {
  background-color: #f8f9fa;
}

.teacher-table tbody tr:last-child td {
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

.btn-view {
  background-color: #17a2b8;
  color: white;
}

.btn-view:hover {
  background-color: #138496;
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

.form-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-size: 14px;
  background-color: #fff;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
}

.form-select:focus {
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
