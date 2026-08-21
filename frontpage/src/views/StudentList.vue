<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">学生列表-{{ route.query.teacherName }}</h1>
      <button type="button" @click="queryRelation" class="btn btn-primary">查询关联关系表</button>
    </div>
    
    <div class="page-content">
      <div class="toolbar">
        <button type="button" @click="queryStudents" class="btn btn-primary">查询</button>
        <button type="button" @click="openAddModal" class="btn btn-success">新增</button>
      </div>
      
      <div class="table-container">
        <table class="student-table">
          <thead>
            <tr>
              <th>学生名字</th>
              <th>性别</th>
              <th>年龄</th>
              <th>已选课程</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="student in studentList" :key="student.id">
              <td>{{ student.name }}</td>
              <td>{{ student.sex }}</td>
              <td>{{ student.age }}</td>
              <td>
                <span v-if="student.courses && student.courses.length > 0">
                  {{ student.courses.map(c => c.course.name).join('、') }}
                </span>
                <span v-else class="no-course">未选课程</span>
              </td>
              <td>
                <button type="button" @click="openAssignCourseModal(student)" class="btn-assign">分配课程</button>
                <button type="button" @click="openEditModal(student)" class="btn-edit">编辑</button>
                <button type="button" @click="deleteStudent(student)" class="btn-delete">删除</button>
              </td>
            </tr>
            <tr v-if="studentList.length === 0">
              <td colspan="5" class="empty-data">暂无数据</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 课程列表维护区域 -->
    <div class="course-section">
      <div class="section-header">
        <h2 class="section-title">课程列表维护</h2>
      </div>
      <div class="toolbar">
        <button type="button" @click="queryCourses" class="btn btn-primary">查询</button>
        <button type="button" @click="openAddCourseModal" class="btn btn-success">新增</button>
      </div>
      
      <div class="table-container">
        <table class="course-table">
          <thead>
            <tr>
              <th>课程名</th>
              <th>学分</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="course in courseList" :key="course.id">
              <td>{{ course.name }}</td>
              <td>{{ course.credit }}</td>
              <td>
                <button type="button" @click="viewCourseStudents(course)" class="btn-view">查看选中学生</button>
                <button type="button" @click="openEditCourseModal(course)" class="btn-edit">编辑</button>
                <button type="button" @click="deleteCourse(course)" class="btn-delete">删除</button>
              </td>
            </tr>
            <tr v-if="courseList.length === 0">
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
          <h2 class="modal-title">{{ isEdit ? '编辑学生' : '新增学生' }}</h2>
          <button type="button" class="modal-close" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveStudent">
            <div class="form-group">
              <label for="studentName">学生名字 <span class="required">*</span></label>
              <input 
                id="studentName" 
                v-model="formData.name" 
                type="text" 
                placeholder="请输入学生名字"
                required
              />
            </div>
            <div class="form-group">
              <label for="studentGender">性别 <span class="required">*</span></label>
              <select 
                id="studentGender" 
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
              <label for="studentAge">年龄 <span class="required">*</span></label>
              <input 
                id="studentAge" 
                v-model.number="formData.age" 
                type="number" 
                placeholder="请输入年龄"
                min="6"
                max="30"
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

    <!-- 课程新增/编辑弹窗 -->
    <div v-if="showCourseModal" class="modal-overlay" @click="closeCourseModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">{{ isCourseEdit ? '编辑课程' : '新增课程' }}</h2>
          <button type="button" class="modal-close" @click="closeCourseModal">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveCourse">
            <div class="form-group">
              <label for="courseName">课程名 <span class="required">*</span></label>
              <input 
                id="courseName" 
                v-model="courseFormData.name" 
                type="text" 
                placeholder="请输入课程名"
                required
              />
            </div>
            <div class="form-group">
              <label for="courseCredits">学分 <span class="required">*</span></label>
              <input 
                id="courseCredits" 
                v-model.number="courseFormData.credit" 
                type="number" 
                placeholder="请输入学分"
                min="1"
                max="10"
                required
              />
            </div>
            <div class="modal-footer">
              <button type="button" @click="closeCourseModal" class="btn btn-cancel">取消</button>
              <button type="submit" class="btn btn-submit">{{ isCourseEdit ? '保存' : '新增' }}</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 分配课程弹窗 -->
    <div v-if="showAssignCourseModal" class="modal-overlay" @click="closeAssignCourseModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">{{ currentStudent?.name }} - 分配课程</h2>
          <button type="button" class="modal-close" @click="closeAssignCourseModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>选择课程 <span class="required">*</span></label>
            <div class="course-checkboxes">
              {{ selectedCourseIds }}
              <label 
                v-for="course in courseList" 
                :key="course.id"
                class="checkbox-label"
              >
                <input 
                  type="checkbox" 
                  :value="course.id"
                  v-model="selectedCourseIds"
                />
                <span>{{ course.name }}（{{ course.credit }}学分）</span>
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" @click="closeAssignCourseModal" class="btn btn-cancel">取消</button>
            <button type="button" @click="saveAssignCourse" class="btn btn-submit">保存</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 查看课程学生弹窗 -->
    <div v-if="showCourseStudentsModal" class="modal-overlay" @click="closeCourseStudentsModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">{{ currentCourse?.name }} - 选中学生列表</h2>
          <button type="button" class="modal-close" @click="closeCourseStudentsModal">×</button>
        </div>
        <div class="modal-body">
          <div class="table-container">
            <table class="student-list-table">
              <thead>
                <tr>
                  <th>学生名字</th>
                  <th>性别</th>
                  <th>年龄</th>
                  <th>分数</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="student in courseStudentsList" :key="student.id">
                  <td>{{ student.name }}</td>
                  <td>{{ student.gender }}</td>
                  <td>{{ student.age }}</td>
                  <td>{{ student.score || '-' }}</td>
                </tr>
                <tr v-if="courseStudentsList.length === 0">
                  <td colspan="4" class="empty-data">暂无学生选择该课程</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="modal-footer">
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

// 学生列表数据
const studentList = ref([])

// 弹窗相关数据
const showModal = ref(false)
const isEdit = ref(false)
const formData = ref({
  id: null,
  name: '',
  sex: '',
  age: null
})

// 课程列表数据
const courseList = ref([])

// 课程弹窗相关数据
const showCourseModal = ref(false)
const isCourseEdit = ref(false)
const courseFormData = ref({
  id: null,
  name: '',
  credit: null
})

// 分配课程弹窗相关数据
const showAssignCourseModal = ref(false)
const currentStudent = ref(null)
const selectedCourseIds = ref([])

// 查看课程学生弹窗相关数据
const showCourseStudentsModal = ref(false)
const currentCourse = ref(null)
const courseStudentsList = ref([])

// 查询关联关系表
const queryRelation = async () => {
  try {
    const resp = await axios.get('/api/student-course', { 
      headers: { Authorization: 'Bearer ' + yourToken } 
    })
  } catch (error) {
    console.error('查询关联关系表失败:', error)
  }

}
// 查询学生列表
const queryStudents = async () => {
  try {
    // 这里调用后端API查询学生数据
    const resp = await axios.get('/api/student?teacher_id=' + route.query.teacherId, { 
      headers: { Authorization: 'Bearer ' + yourToken } 
    })
    studentList.value = resp.data.data || resp.data || []
    
    // 模拟数据，实际使用时替换为真实API调用
    // studentList.value = [
    //   { id: 1, name: '张三', sex: '男', age: 15, selectedCourses: [] },
    //   { id: 2, name: '李四', sex: '女', age: 16, selectedCourses: [] },
    //   { id: 3, name: '王五', sex: '男', age: 14, selectedCourses: [] },
    //   { id: 4, name: '赵六', sex: '女', age: 15, selectedCourses: [] }
    // ]
    console.log('查询学生成功')
  } catch (error) {
    console.error('查询学生失败:', error)
    alert('查询学生失败')
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
const openEditModal = (student) => {
  isEdit.value = true
  formData.value = {
    id: student.id,
    name: student.name,
    sex: student.sex,
    age: student.age
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

// 保存学生（新增或编辑）
const saveStudent = async () => {
  try {
    if (isEdit.value) {
      // 编辑学生
      const resp = await axios.put(`/api/student/${formData.value.id}`, {
        ...formData.value,
        teacher_id: route.query.teacherId
      }, {
        headers: { Authorization: 'Bearer ' + yourToken }
      })
      
      // 模拟更新
      // const index = studentList.value.findIndex(s => s.id === formData.value.id)
      // if (index !== -1) {
      //   studentList.value[index] = { ...formData.value }
      // }
      console.log('编辑学生成功')
      queryStudents()
    } else {
      // 新增学生
      const resp = await axios.post('/api/student', {
        ...formData.value,
        teacher_id: route.query.teacherId
      }, {
        headers: { Authorization: 'Bearer ' + yourToken }
      })
      
      // 模拟新增
      // const newId = Math.max(...studentList.value.map(s => s.id), 0) + 1
      // studentList.value.push({
      //   id: newId,
      //   name: formData.value.name,
      //   sex: formData.value.sex,
      //   age: formData.value.age
      // })
      console.log('新增学生成功')
      queryStudents()
    }
    closeModal()
  } catch (error) {
    console.error('保存学生失败:', error)
    alert('保存学生失败')
  }
}

// 删除学生
const deleteStudent = async (student) => {
  if (!confirm(`确定要删除学生"${student.name}"吗？`)) {
    return
  }
  
  try {
    // 这里调用后端API删除学生
    const resp = await axios.delete(`/api/student/${student.id}`, {
      headers: { Authorization: 'Bearer ' + yourToken }
    })
    
    // 模拟删除
    // const index = studentList.value.findIndex(s => s.id === student.id)
    // if (index !== -1) {
    //   studentList.value.splice(index, 1)
    // }
    console.log('删除学生成功')
    queryStudents()
  } catch (error) {
    console.error('删除学生失败:', error)
    alert('删除学生失败')
  }
}

// 查询课程列表
const queryCourses = async () => {
  try {
    // 这里调用后端API查询课程数据
    const resp = await axios.get('/api/course', { 
      headers: { Authorization: 'Bearer ' + yourToken } 
    })
    courseList.value = resp.data.data || resp.data || []
    
    // 模拟数据，实际使用时替换为真实API调用
    // courseList.value = [
    //   { id: 1, name: '数学', credit: 4 },
    //   { id: 2, name: '语文', credit: 3 },
    //   { id: 3, name: '英语', credit: 3 },
    //   { id: 4, name: '物理', credit: 2 }
    // ]
    console.log('查询课程成功')
  } catch (error) {
    console.error('查询课程失败:', error)
    alert('查询课程失败')
  }
}

// 打开课程新增弹窗
const openAddCourseModal = () => {
  isCourseEdit.value = false
  courseFormData.value = {
    id: null,
    name: '',
    credit: null
  }
  showCourseModal.value = true
}

// 打开课程编辑弹窗
const openEditCourseModal = (course) => {
  isCourseEdit.value = true
  courseFormData.value = {
    id: course.id,
    name: course.name,
    credit: course.credit
  }
  showCourseModal.value = true
}

// 关闭课程弹窗
const closeCourseModal = () => {
  showCourseModal.value = false
  courseFormData.value = {
    id: null,
    name: '',
    credit: null
  }
}

// 保存课程（新增或编辑）
const saveCourse = async () => {
  try {
    if (isCourseEdit.value) {
      // 编辑课程
      const resp = await axios.put(`/api/course/${courseFormData.value.id}`, courseFormData.value, {
        headers: { Authorization: 'Bearer ' + yourToken }
      })
      
      // 模拟更新
      // const index = courseList.value.findIndex(c => c.id === courseFormData.value.id)
      // if (index !== -1) {
      //   courseList.value[index] = { ...courseFormData.value }
      // }
      console.log('编辑课程成功')
      queryCourses()
    } else {
      // 新增课程
      const resp = await axios.post('/api/course', courseFormData.value, {
        headers: { Authorization: 'Bearer ' + yourToken }
      })
      
      // 模拟新增
      // const newId = Math.max(...courseList.value.map(c => c.id), 0) + 1
      // courseList.value.push({
      //   id: newId,
      //   name: courseFormData.value.name,
      //   credit: courseFormData.value.credit
      // })
      console.log('新增课程成功')
      queryCourses()
    }
    closeCourseModal()
  } catch (error) {
    console.error('保存课程失败:', error)
    alert('保存课程失败')
  }
}

// 删除课程
const deleteCourse = async (course) => {
  if (!confirm(`确定要删除课程"${course.name}"吗？`)) {
    return
  }
  
  try {
    // 这里调用后端API删除课程
    const resp = await axios.delete(`/api/course/${course.id}`, {
      headers: { Authorization: 'Bearer ' + yourToken }
    })
    
    // 模拟删除
    // const index = courseList.value.findIndex(c => c.id === course.id)
    // if (index !== -1) {
    //   courseList.value.splice(index, 1)
    // }
    console.log('删除课程成功')
    queryCourses()
  } catch (error) {
    console.error('删除课程失败:', error)
    alert('删除课程失败')
  }
}

// 打开分配课程弹窗
const openAssignCourseModal = (student) => {
  currentStudent.value = student
  // 初始化已选课程ID
  selectedCourseIds.value = student.courses 
    ? student.courses.map(c => c.course.id) 
    : []

  showAssignCourseModal.value = true
}

// 关闭分配课程弹窗
const closeAssignCourseModal = () => {
  showAssignCourseModal.value = false
  currentStudent.value = null
  selectedCourseIds.value = []
}

// 保存分配课程
const saveAssignCourse = async () => {
  if (!currentStudent.value) return
  
  try {
    // 这里调用后端API保存分配课程
    const resp = await axios.post(`/api/student-course`, {
      student_id: currentStudent.value.id,
      course_ids: selectedCourseIds.value,
      scores: selectedCourseIds.value.map(c => 80)
    }, { headers: { Authorization: 'Bearer ' + yourToken } })
    
    // 模拟保存
    // const selectedCourses = courseList.value.filter(c => 
    //   selectedCourseIds.value.includes(c.id)
    // )
    
    // const index = studentList.value.findIndex(s => s.id === currentStudent.value.id)
    // if (index !== -1) {
    //   studentList.value[index].selectedCourses = selectedCourses
    // }
    
    console.log('分配课程成功')
    queryStudents()
    closeAssignCourseModal()
  } catch (error) {
    console.error('分配课程失败:', error)
    alert('分配课程失败')
  }
}

// 查看课程学生
const viewCourseStudents = async (course) => {
  currentCourse.value = course
  showCourseStudentsModal.value = true
  courseStudentsList.value = []
  
  try {
    // 这里调用后端API查询选中该课程的学生
    const resp = await axios.get(`/api/student-course/course/${course.id}/students`, {
      headers: { Authorization: 'Bearer ' + yourToken }
    })
    courseStudentsList.value = (resp.data.data || resp.data || []).map(item => {
      return {
        id: item.id,
        name: item.student_name,
        gender: item.student_sex,
        age: item.student_age,
        score: item.score
      }
    })
    
    // 模拟数据：从学生列表中筛选出选择了该课程的学生
    // const studentsWithCourse = studentList.value.filter(student => {
    //   return student.courses && student.courses.some(sc => sc.course.id === course.id)
    // })
    
    // courseStudentsList.value = studentsWithCourse.map(student => {
    //   const courseRelation = student.courses.find(sc => sc.course.id === course.id)
    //   return {
    //     id: student.id,
    //     name: student.name,
    //     gender: student.gender,
    //     age: student.age,
    //     score: courseRelation ? courseRelation.score : null
    //   }
    // })
    
    console.log('查询课程学生成功:', courseStudentsList.value)
  } catch (error) {
    console.error('查询课程学生失败:', error)
    alert('查询课程学生失败')
  }
}

// 关闭查看课程学生弹窗
const closeCourseStudentsModal = () => {
  showCourseStudentsModal.value = false
  currentCourse.value = null
  courseStudentsList.value = []
}

// 页面加载时自动查询
onMounted(() => {
  queryStudents()
  queryCourses()
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
  margin-bottom: 24px;
}

.course-section {
  background-color: #ffffff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.section-header {
  margin-bottom: 20px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
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

.student-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.student-table thead {
  background-color: #f8f9fa;
}

.student-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #dee2e6;
  white-space: nowrap;
}

.student-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #dee2e6;
  color: #666;
}

.student-table tbody tr:hover {
  background-color: #f8f9fa;
}

.student-table tbody tr:last-child td {
  border-bottom: none;
}

.course-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.course-table thead {
  background-color: #f8f9fa;
}

.course-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #dee2e6;
  white-space: nowrap;
}

.course-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #dee2e6;
  color: #666;
}

.course-table tbody tr:hover {
  background-color: #f8f9fa;
}

.course-table tbody tr:last-child td {
  border-bottom: none;
}

.empty-data {
  text-align: center;
  color: #999;
  padding: 40px !important;
}

.no-course {
  color: #999;
  font-style: italic;
}

.btn-assign,
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

.btn-assign {
  background-color: #17a2b8;
  color: white;
}

.btn-assign:hover {
  background-color: #138496;
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

.course-checkboxes {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
  padding: 12px;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  background-color: #f8f9fa;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-weight: normal;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.checkbox-label:hover {
  background-color: #e9ecef;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  margin: 0;
  cursor: pointer;
}

.checkbox-label span {
  flex: 1;
  color: #333;
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

.student-list-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.student-list-table thead {
  background-color: #f8f9fa;
}

.student-list-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #dee2e6;
  white-space: nowrap;
}

.student-list-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #dee2e6;
  color: #666;
}

.student-list-table tbody tr:hover {
  background-color: #f8f9fa;
}

.student-list-table tbody tr:last-child td {
  border-bottom: none;
}
</style>
