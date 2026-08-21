<template>
  <div class="dashboard">
    <div class="content-header">
      <h1 class="page-title">仪表盘概览</h1>
      <p class="page-subtitle">欢迎回来,这是您的数据概览</p>
    </div>
        <div class="form-section">
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label for="account">账号</label>
            <input id="account" v-model="account" type="text">
          </div>
          <div class="form-group">
            <label for="password">密码</label>
            <input id="password" v-model="password" type="password">
          </div>
          <div class="form-group">
            <label for="code">验证码</label>
            <div class="input-with-button">
              <input id="code" v-model="code" type="text" class="input-x">
              <button type="button" @click="getCode">获取验证码</button>
            </div>
          </div>
          
          <button type="submit">提交</button>
        </form>
        <button @click="getAiName" style="margin-top: 20px;">获取AIname</button>
        <div class="action-buttons" style="margin-top:12px; display:flex; gap:12px;">
          <button type="button" @click="onAdd">增加</button>
          <button type="button" @click="onDelete">删除</button>
          <button type="button" @click="onEdit">修改</button>
          <button type="button" @click="onQuery">查询</button>
        </div>
        <div class="action-buttons" style="margin-top:12px; display:flex; gap:12px;">
          <button type="button" @click="queryOut">统一出参格式</button>
          <button type="button" @click="queryExcel">导出excel</button>
          <button type="button" @click="testRedis">redis尝试</button>
          <button type="button" style="opacity: 0;" @click="onQuery">查询</button>
        </div>
        <div class="file-upload" style="margin-top:12px; display:flex; gap:12px; align-items:center;">
          <input type="file" @change="onFileChange" ref="fileInput">
          <button type="button" @click="uploadFile">批量插入</button>
        </div>
        
      </div>
      
      <div class="stats-grid">
        <StatCard
          title="总销售额"
          value="¥128,456"
          change="+12.5%"
          :is-positive="true"
        />
        <StatCard
          title="新增用户"
          value="2,345"
          change="+8.2%"
          :is-positive="true"
        />
        <StatCard
          title="订单数量"
          value="1,234"
          change="-3.1%"
          :is-positive="false"
        />
        <StatCard
          title="访问量"
          value="45,678"
          change="+15.3%"
          :is-positive="true"
        />
      </div>
      
      <div class="charts-grid">
        <ChartCard
          title="销售趋势"
          subtitle="最近7天的销售数据"
          :chart-data="salesData"
          :chart-colors="salesColors"
          :y-axis-max="4000"
          :y-axis-interval="1000"
        />
        <ChartCard
          title="用户增长"
          subtitle="用户注册趋势"
          :chart-data="userGrowthData"
          :chart-colors="userGrowthColors"
          :y-axis-max="3000"
          :y-axis-interval="500"
        />
      </div>
      
      <div class="orders-card">
        <div class="card-header">
          <div class="card-title">最新订单</div>
          <div class="card-subtitle">最近的订单记录</div>
        </div>
        <div class="orders-content">
          <!-- 订单列表内容为空，如原图所示 -->
        </div>
      </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import StatCard from '../components/StatCard.vue'
import ChartCard from '../components/ChartCard.vue'

const account = ref('')
const password = ref('')
const code = ref('')
const yourToken = '123123123' || localStorage.getItem('token') || ''
const selectedFile = ref(null)
const fileInput = ref(null)

const getCode = async () => {
  // 模拟获取验证码
  const getResponse = await axios.get('/api/auth/code?email=liuxun@envicool.com')
  console.log('GET Response:', getResponse.data)
  alert(`GET 请求返回: ${getResponse.data.message}`)
}

const handleSubmit = async () => {
  try {
    // GET 示例
    // const url = '/api/' + 'hello/lx'
    // const url = '/api' + '/mail/test?email=liuxun@envicool.com' // 测试邮箱
    // const getResponse = await axios.get(url)
    // console.log('GET Response:', getResponse.data)
    // alert(`GET 请求返回: ${getResponse.data.message}`)

    // POST 示例
    const postData = {
      email: '360999519@qq.com',
      username: account.value,
      password: password.value,
      confirm_password: password.value,
      code: code.value
    }
    // const url = '/api' + '/auth/register' // 注册用户
    const url = '/api' + '/auth/login' // 登录用户
    // const postResponse = await axios.post(url, postData)
    const postResponse = await axios.post(url, {
      email: '360999519@qq.com',
      password: '111111'
    })
    console.log('POST Response:', postResponse.data)
  } catch (error) {
    console.error('Error:', error)
  }
}

const getAiName = async () => {
  try {
    const url = '/api/name/'
    const response = await axios.post(url, {
      surname: "张",
      gender: "男",
      length: "两字",
      other: "希望名字有文化内涵",
      exclude: ["张伟", "张强"]
    }, { headers: { Authorization: 'Bearer ' + yourToken } })
    console.log('AI Name Response:', response.data)
    alert(`AI Name: ${response.data.name}`)
  } catch (error) {
    console.error('Error fetching AI name:', error)
  }
}

const onAdd = async () => {
  const form = new FormData()
  form.append('username', '测试用户')
  form.append('sex', '男')
  form.append('artcontent', '这是测试文章内容')
  form.append('file', selectedFile.value)
  const resp = await axios.post('/api/admin/insertArt', form, { headers: { Authorization: 'Bearer ' + yourToken
    , 'Content-Type': 'multipart/form-data'
  } })
  alert(resp)
}

const onDelete = async () => {
  const resp = await axios.post('/api/admin/delArt', {
    idArr: [2]
  }, { headers: { Authorization: 'Bearer ' + yourToken } })
  console.log('删除')
  alert('删除')
}

const onEdit = async () => {
  const resp = await axios.post('/api/admin/changeArt', {
    id:11,
    sex: '女',
  }, { headers: { Authorization: 'Bearer ' + yourToken } })
  console.log('修改')
  alert('修改')
}

const onQuery = async () => {
  const resp = await axios.post('/api/admin/queryArt', {
    page: 1,
    size: 10,
    sex: '女',
  }, { headers: { Authorization: 'Bearer ' + yourToken } })
  console.log('查询')
  alert('查询')
}

const queryOut = async () => {
  const resp = await axios.post('/api/admin/queryArtOut', {
    page: 1,
    size: 10,
    sex: '女',
  }, { headers: { Authorization: 'Bearer ' + yourToken } })
  console.log('统一出参格式查询结果:', resp) 
}

const queryExcel = async () => {
    try {
      const resp = await axios.post('/api/admin/queryArtExcel', {
        page: 1,
        size: 10,
        sex: '女',
      }, {
        headers: { Authorization: 'Bearer ' + yourToken, Accept: 'application/octet-stream' },
        responseType: 'blob'
      })

      // 从响应头中解析文件名（如果服务器返回了 Content-Disposition）
      const contentDisposition = resp.headers && (resp.headers['content-disposition'] || resp.headers['Content-Disposition'])
      let filename = 'export.xlsx'
      if (contentDisposition) {
        const match = contentDisposition.match(/filename\*=UTF-8''([^;\n]+)|filename="?([^;\n"]+)"?/) 
        if (match) filename = decodeURIComponent(match[1] || match[2])
      }

      const blob = new Blob([resp.data], { type: resp.headers['content-type'] || 'application/octet-stream' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
      console.log('导出Excel成功:', filename)
    } catch (err) {
      console.error('导出Excel失败:', err)
      alert('导出失败')
    }
}

const testRedis = async () => {
    const res = await axios.post('/api/region/init')
    const resp = await axios.get('/api/region/provinces')
    const resc = await axios.get('/api/region/cities?province_code=440000')
    const resd = await axios.get('/api/region/districts?city_code=440100')
}

const onFileChange = (event) => {
  const files = event.target.files || []
  selectedFile.value = files[0] || null
  console.log('Selected file:', selectedFile.value)
}

const uploadFile = async () => {
  if (!selectedFile.value) {
    alert('请先选择文件')
    return
  }
  try {
    const form = new FormData()
    form.append('username', '备用用户')
    form.append('file', selectedFile.value)
    const resp = await axios.post('/api/admin/insertArtByExcel', form, { headers: { Authorization: 'Bearer ' + yourToken
      , 'Content-Type': 'multipart/form-data'
    } })
    // 清空文件选择
    if (fileInput.value) fileInput.value.value = null
    selectedFile.value = null
  } catch (err) {
    console.error('Upload error:', err)
    alert('上传失败')
  }
}

const salesData = ref([
  { month: '1月', value: 3200 },
  { month: '2月', value: 2800 },
  { month: '3月', value: 3500 },
  { month: '4月', value: 2900 },
  { month: '5月', value: 3800 },
  { month: '6月', value: 3400 },
  { month: '7月', value: 3600 }
])

const salesColors = ['#8b5cf6', '#60a5fa', '#ef4444', '#60a5fa', '#8b5cf6', '#f97316', '#22c55e']

const userGrowthData = ref([
  { month: '1月', value: 1200 },
  { month: '2月', value: 1800 },
  { month: '3月', value: 2000 },
  { month: '4月', value: 1500 },
  { month: '5月', value: 2500 },
  { month: '6月', value: 2200 },
  { month: '7月', value: 2800 }
])

const userGrowthColors = ['#ef4444', '#60a5fa', '#60a5fa', '#eab308', '#8b5cf6', '#f97316', '#22c55e']
</script>

<style scoped>
.dashboard {
  width: 100%;
}

.content-header {
  margin-bottom: 24px;
}

.form-section {
  background-color: #ffffff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
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

.form-group input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 6px;
  font-size: 16px;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
  background-color: #fafbfc;
}

.form-group input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
  background-color: #ffffff;
}

button {
  padding: 12px 24px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: background-color 0.3s ease, transform 0.2s ease;
  width: 100%;
}

button:hover {
  background-color: #0056b3;
  transform: translateY(-1px);
}

button:active {
  transform: translateY(0);
}

.input-with-button {
  display: flex;
  flex: 1;
  gap: 12px;
}

.input-with-button .input {
  flex: 1;
}

.input-with-button button {
  width: 120px;
  flex-shrink: 0;
  padding: 12px 16px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.input-with-button button:hover {
  background-color: #218838;
  transform: translateY(-1px);
}

.input-with-button button:active {
  transform: translateY(0);
}

.button-row {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.button-row button {
  width: auto;
  flex: 1;
  padding: 10px 16px;
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.orders-card {
  background-color: #ffffff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 16px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.card-subtitle {
  font-size: 12px;
  color: #999;
}

.orders-content {
  min-height: 200px;
}

@media (max-width: 1400px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
