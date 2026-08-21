<template>
  <div class="sidebar">
    <div class="sidebar-header">
      <span class="logo-icon">⚡</span>
      <span class="logo-text">后台管理</span>
    </div>
    
    <nav class="sidebar-nav">
      <template v-for="item in menuItems" :key="item.path">
        <!-- 一级菜单 -->
        <div 
          class="nav-item" 
          :class="{ active: isActive(item.path) }"
          @click="toggleMenu(item.path)"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-text">{{ item.title }}</span>
          <span 
            class="nav-arrow" 
            v-if="item.children && item.children.length > 0"
            :class="{ rotated: expandedMenus[item.path] }"
          >▶</span>
        </div>
        
        <!-- 二级菜单 -->
        <div 
          v-if="item.children && expandedMenus[item.path]" 
          class="nav-submenu"
        >
          <template v-for="subItem in item.children" :key="subItem.path">
            <div 
              class="nav-subitem"
              :class="{ active: isActive(subItem.path) }"
              @click.stop="toggleSubMenu(subItem.path)"
              v-if="!subItem.children || subItem.children.length === 0"
            >
              <router-link :to="subItem.path" class="nav-link">
                {{ subItem.title }}
              </router-link>
            </div>
            <div 
              v-else
              class="nav-subitem"
              @click.stop="toggleSubMenu(subItem.path)"
            >
              <span>{{ subItem.title }}</span>
              <span 
                class="nav-arrow"
                :class="{ rotated: expandedMenus[subItem.path] }"
              >▶</span>
            </div>
            
            <!-- 三级菜单 -->
            <div 
              v-if="subItem.children && expandedMenus[subItem.path]" 
              class="nav-submenu-level2"
            >
              <div 
                v-for="thirdItem in subItem.children" 
                :key="thirdItem.path"
                class="nav-subitem"
                :class="{ active: isActive(thirdItem.path) }"
                @click.stop="$router.push(thirdItem.path)"
              >
                <router-link :to="thirdItem.path" class="nav-link">
                  {{ thirdItem.title }}
                </router-link>
              </div>
            </div>
          </template>
        </div>
      </template>
    </nav>
    
    <div class="sidebar-footer">
      版本 v1.0.0
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

// 菜单数据
const menuItems = ref([
  {
    path: '/',
    title: '仪表盘',
    icon: '☷',
    children: []
  },
  {
    path: '/products',
    title: '商品管理',
    icon: '🛒',
    children: [
      {
        path: '/products/list',
        title: '商品列表',
        children: []
      },
      {
        path: '/products/category',
        title: '商品分类',
        children: [
          {
            path: '/products/category/main',
            title: '主分类',
            children: []
          },
          {
            path: '/products/category/sub',
            title: '子分类',
            children: []
          }
        ]
      },
      {
        path: '/products/tags',
        title: '标签管理',
        children: []
      }
    ]
  },
  {
    path: '/inventory',
    title: '库存管理',
    icon: '📦',
    children: []
  },
  {
    path: '/orders',
    title: '订单管理',
    icon: '🛒',
    children: [
      {
        path: '/orders/list',
        title: '订单列表',
        children: []
      },
      {
        path: '/orders/refund',
        title: '退款管理',
        children: []
      }
    ]
  },
  {
    path: '/users',
    title: '用户管理',
    icon: '👤',
    children: [
      {
        path: '/users/list',
        title: '用户列表',
        children: []
      },
      {
        path: '/users/roles',
        title: '角色管理',
        children: []
      }
    ]
  },
  {
    path: '/content',
    title: '内容管理',
    icon: '📄',
    children: [
      {
        path: '/content/articles',
        title: '文章管理',
        children: []
      },
      {
        path: '/content/categories',
        title: '内容分类',
        children: []
      }
    ]
  },
  {
    path: '/analytics',
    title: '数据分析',
    icon: '📊',
    children: [
      {
        path: '/analytics/sales',
        title: '销售分析',
        children: []
      },
      {
        path: '/analytics/users',
        title: '用户分析',
        children: []
      }
    ]
  },
  {
    path: '/settings',
    title: '系统设置',
    icon: '⚙️',
    children: [
      {
        path: '/settings/basic',
        title: '基础设置',
        children: []
      },
      {
        path: '/settings/permissions',
        title: '权限管理',
        children: []
      }
    ]
  }
])

// 展开状态管理
const expandedMenus = reactive({})

// 切换菜单展开/收起
const toggleMenu = (path) => {
  const menu = findMenuByPath(menuItems.value, path)
  if (menu && menu.children && menu.children.length > 0) {
    expandedMenus[path] = !expandedMenus[path]
  } else {
    // 没有子菜单，直接跳转
    router.push(path)
  }
}

// 切换二级菜单展开/收起
const toggleSubMenu = (path) => {
  const menu = findSubMenuByPath(menuItems.value, path)
  if (menu && menu.children && menu.children.length > 0) {
    expandedMenus[path] = !expandedMenus[path]
  } else {
    router.push(path)
  }
}

// 查找菜单项
const findMenuByPath = (items, path) => {
  for (const item of items) {
    if (item.path === path) {
      return item
    }
  }
  return null
}

// 查找子菜单项
const findSubMenuByPath = (items, path) => {
  for (const item of items) {
    if (item.children) {
      for (const subItem of item.children) {
        if (subItem.path === path) {
          return subItem
        }
        if (subItem.children) {
          for (const thirdItem of subItem.children) {
            if (thirdItem.path === path) {
              return thirdItem
            }
          }
        }
      }
    }
  }
  return null
}

// 判断当前路由是否激活
const isActive = (path) => {
  return route.path === path || route.path.startsWith(path + '/')
}

// 初始化展开状态（根据当前路由自动展开）
const initExpandedMenus = () => {
  const currentPath = route.path
  menuItems.value.forEach(item => {
    if (item.children && item.children.length > 0) {
      // 检查当前路径是否在该菜单的子项中
      const hasActiveChild = item.children.some(subItem => {
        if (subItem.path === currentPath || currentPath.startsWith(subItem.path + '/')) {
          expandedMenus[item.path] = true
          return true
        }
        if (subItem.children) {
          return subItem.children.some(thirdItem => {
            if (thirdItem.path === currentPath) {
              expandedMenus[item.path] = true
              expandedMenus[subItem.path] = true
              return true
            }
            return false
          })
        }
        return false
      })
    }
  })
}

// 监听路由变化，自动展开对应菜单
watch(() => route.path, () => {
  initExpandedMenus()
}, { immediate: true })

// 初始化
initExpandedMenus()
</script>

<style scoped>
.sidebar {
  width: 240px;
  height: 100vh;
  background-color: #1e3a5f;
  color: #ffffff;
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  overflow-y: auto;
}

.sidebar-header {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-icon {
  font-size: 24px;
}

.sidebar-nav {
  flex: 1;
  padding: 10px 0;
}

.nav-item {
  padding: 12px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: background-color 0.2s;
  position: relative;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-item.active {
  background-color: #2a4d7a;
}

.nav-icon {
  font-size: 18px;
  width: 20px;
  text-align: center;
}

.nav-text {
  flex: 1;
  font-size: 14px;
}

.nav-arrow {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.6);
  transition: transform 0.3s;
}

.nav-arrow.rotated {
  transform: rotate(90deg);
}

.nav-submenu {
  background-color: rgba(0, 0, 0, 0.2);
  padding-left: 0;
  max-height: 1000px;
  overflow: hidden;
  transition: max-height 0.3s ease;
}

.nav-subitem {
  padding: 10px 20px;
  padding-left: 52px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: background-color 0.2s;
}

.nav-subitem:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-subitem.active {
  background-color: rgba(42, 77, 122, 0.5);
  color: #ffffff;
}

.nav-link {
  color: inherit;
  text-decoration: none;
  flex: 1;
}

.nav-submenu-level2 {
  background-color: rgba(0, 0, 0, 0.3);
  padding-left: 0;
  max-height: 1000px;
  overflow: hidden;
  transition: max-height 0.3s ease;
}

.nav-submenu-level2 .nav-subitem {
  padding-left: 72px;
}

.sidebar-footer {
  padding: 20px;
  text-align: center;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}
</style>
