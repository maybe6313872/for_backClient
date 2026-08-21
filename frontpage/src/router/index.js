import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../components/Layout.vue'
import Dashboard from '../views/Dashboard.vue'
import Inventory from '../views/Inventory.vue'
import TeacherList from '../views/TeacherList.vue'
import StudentList from '../views/StudentList.vue'

// 商品管理
import ProductList from '../views/products/ProductList.vue'
import CategoryMain from '../views/products/CategoryMain.vue'
import CategorySub from '../views/products/CategorySub.vue'
import ProductTags from '../views/products/ProductTags.vue'

// 订单管理
import OrderList from '../views/orders/OrderList.vue'
import OrderRefund from '../views/orders/OrderRefund.vue'
import CompanyManagement from '../views/orders/CompanyManagement.vue'
import ProductManagement from '../views/orders/ProductManagement.vue'

// 用户管理
import UserList from '../views/users/UserList.vue'
import UserRoles from '../views/users/UserRoles.vue'

// 内容管理
import ContentArticles from '../views/content/ContentArticles.vue'
import ContentCategories from '../views/content/ContentCategories.vue'

// 数据分析
import AnalyticsSales from '../views/analytics/AnalyticsSales.vue'
import AnalyticsUsers from '../views/analytics/AnalyticsUsers.vue'

// 系统设置
import SettingsBasic from '../views/settings/SettingsBasic.vue'
import SettingsPermissions from '../views/settings/SettingsPermissions.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: Dashboard
      },
      {
        path: '/inventory',
        name: 'Inventory',
        component: Inventory
      },
      {
        path: '/teachers',
        name: 'TeacherList',
        component: TeacherList
      },
      {
        path: '/students',
        name: 'StudentList',
        component: StudentList
      },
      // 商品管理
      {
        path: '/products/list',
        name: 'ProductList',
        component: ProductList
      },
      {
        path: '/products/category/main',
        name: 'CategoryMain',
        component: CategoryMain
      },
      {
        path: '/products/category/sub',
        name: 'CategorySub',
        component: CategorySub
      },
      {
        path: '/products/tags',
        name: 'ProductTags',
        component: ProductTags
      },
      // 订单管理
      {
        path: '/orders/list',
        name: 'OrderList',
        component: OrderList
      },
      {
        path: '/orders/refund',
        name: 'OrderRefund',
        component: OrderRefund
      },
      {
        path: '/orders/company',
        name: 'CompanyManagement',
        component: CompanyManagement
      },
      {
        path: '/orders/product',
        name: 'ProductManagement',
        component: ProductManagement
      },
      // 用户管理
      {
        path: '/users/list',
        name: 'UserList',
        component: UserList
      },
      {
        path: '/users/roles',
        name: 'UserRoles',
        component: UserRoles
      },
      // 内容管理
      {
        path: '/content/articles',
        name: 'ContentArticles',
        component: ContentArticles
      },
      {
        path: '/content/categories',
        name: 'ContentCategories',
        component: ContentCategories
      },
      // 数据分析
      {
        path: '/analytics/sales',
        name: 'AnalyticsSales',
        component: AnalyticsSales
      },
      {
        path: '/analytics/users',
        name: 'AnalyticsUsers',
        component: AnalyticsUsers
      },
      // 系统设置
      {
        path: '/settings/basic',
        name: 'SettingsBasic',
        component: SettingsBasic
      },
      {
        path: '/settings/permissions',
        name: 'SettingsPermissions',
        component: SettingsPermissions
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
