<template>
  <div class="header">
    <div class="header-left">
      <span class="close-icon">✕</span>
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input type="text" placeholder="搜索菜单、功能..." class="search-input" />
      </div>
    </div>
    
    <div class="header-right">
      <div class="notification-icon">
        <span>🔔</span>
        <span class="notification-dot"></span>
      </div>
      <div class="user-info">
        <span class="user-avatar">👤</span>
        <div class="user-details">
          <span class="user-name">管理员</span>
          <span class="user-email">admin@example.com</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.header {
  height: 60px;
  background-color: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: fixed;
  top: 0;
  left: 240px;
  right: 0;
  z-index: 100;
  border-bottom: 1px solid #e0e0e0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.close-icon {
  font-size: 18px;
  color: #666;
  cursor: pointer;
}

.search-box {
  display: flex;
  align-items: center;
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 8px 12px;
  gap: 8px;
  min-width: 300px;
}

.search-icon {
  font-size: 16px;
  color: #999;
}

.search-input {
  border: none;
  outline: none;
  flex: 1;
  font-size: 14px;
  color: #333;
}

.search-input::placeholder {
  color: #999;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 24px;
}

.notification-icon {
  position: relative;
  cursor: pointer;
  font-size: 20px;
}

.notification-dot {
  position: absolute;
  top: -2px;
  right: -2px;
  width: 8px;
  height: 8px;
  background-color: #ff4444;
  border-radius: 50%;
  border: 2px solid #f5f5f5;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  font-size: 24px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #e0e0e0;
  border-radius: 50%;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.user-email {
  font-size: 12px;
  color: #999;
}
</style>
