import { createApp } from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { createPinia } from 'pinia'
import { createRouter, createWebHashHistory } from 'vue-router'

// 导入组件
import Auth from './components/Auth.vue'
import Home from './components/Home.vue'
import UserManagement from './components/UserManagement.vue'

// 路由配置
const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    component: Auth,
    name: 'login'
  },
  {
    path: '/home',
    component: Home,
    name: 'home'
  },
  {
    path: '/users',
    component: UserManagement,
    name: 'users'
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

const app = createApp(App)
app.use(ElementPlus)
app.use(createPinia())
app.use(router)
app.mount('#app')
