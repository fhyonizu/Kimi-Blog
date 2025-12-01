import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import ArticleDetail from '../views/ArticleDetail.vue'
import Admin from '../views/Admin.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/article/:id', component: ArticleDetail },
  { path: '/admin', component: Admin }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router // <--- 关键点3：必须导出