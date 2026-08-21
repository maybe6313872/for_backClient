<template>
  <div class="chart-card">
    <div class="chart-header">
      <div class="chart-title">{{ title }}</div>
      <div class="chart-subtitle">{{ subtitle }}</div>
    </div>
    <div class="chart-container" ref="chartContainer"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  title: String,
  subtitle: String,
  chartData: Array,
  chartColors: Array,
  yAxisMax: {
    type: Number,
    default: null
  },
  yAxisInterval: {
    type: Number,
    default: null
  }
})

const chartContainer = ref(null)
let chartInstance = null

onMounted(() => {
  if (chartContainer.value) {
    chartInstance = echarts.init(chartContainer.value)
    updateChart()
  }
})

watch(() => props.chartData, () => {
  if (chartInstance) {
    updateChart()
  }
}, { deep: true })

const updateChart = () => {
  if (!chartInstance || !props.chartData) return
  
  const option = {
    grid: {
      left: '10%',
      right: '10%',
      top: '15%',
      bottom: '15%'
    },
    xAxis: {
      type: 'category',
      data: props.chartData.map(item => item.month),
      axisLine: {
        lineStyle: {
          color: '#e0e0e0'
        }
      },
      axisLabel: {
        color: '#666',
        fontSize: 12
      }
    },
    yAxis: {
      type: 'value',
      max: props.yAxisMax,
      interval: props.yAxisInterval,
      axisLine: {
        lineStyle: {
          color: '#e0e0e0'
        }
      },
      axisLabel: {
        color: '#666',
        fontSize: 12
      },
      splitLine: {
        lineStyle: {
          color: '#f0f0f0',
          type: 'dashed'
        }
      }
    },
    series: [{
      data: props.chartData.map(item => item.value),
      type: 'bar',
      itemStyle: {
        color: (params) => {
          return props.chartColors[params.dataIndex % props.chartColors.length]
        },
        borderRadius: [4, 4, 0, 0]
      },
      barWidth: '60%'
    }],
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: 'transparent',
      textStyle: {
        color: '#fff'
      }
    }
  }
  
  chartInstance.setOption(option)
  
  window.addEventListener('resize', () => {
    chartInstance?.resize()
  })
}
</script>

<style scoped>
.chart-card {
  background-color: #ffffff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chart-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.chart-subtitle {
  font-size: 12px;
  color: #999;
}

.chart-container {
  width: 100%;
  height: 300px;
}
</style>
