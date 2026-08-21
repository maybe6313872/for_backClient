<template>
  <div class="layout">
    <Sidebar />
    <Header />
    <div class="main-content">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import Sidebar from './Sidebar.vue'
import Header from './Header.vue'
</script>

<style scoped>
.layout {
  display: flex;
  width: 100%;
  height: 100vh;
  background-color: #f5f5f5;
}

.main-content {
  margin-left: 240px;
  margin-top: 60px;
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  height: calc(100vh - 60px);
}
</style>
