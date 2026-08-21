<template>
  <div class="stat-card">
    <div class="stat-title">{{ title }}</div>
    <div class="stat-value">{{ value }}</div>
    <div class="stat-change" :class="changeClass">
      <span class="change-arrow">{{ changeArrow }}</span>
      <span class="change-text">{{ change }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: String,
  value: String,
  change: String,
  isPositive: {
    type: Boolean,
    default: true
  }
})

const changeClass = computed(() => {
  return props.isPositive ? 'positive' : 'negative'
})

const changeArrow = computed(() => {
  return props.isPositive ? '↑' : '↓'
})
</script>

<style scoped>
.stat-card {
  background-color: #ffffff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stat-title {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: #333;
}

.stat-change {
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-change.positive {
  color: #52c41a;
}

.stat-change.negative {
  color: #ff4d4f;
}

.change-arrow {
  font-size: 12px;
}
</style>
