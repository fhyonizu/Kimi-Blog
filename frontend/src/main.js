import { createApp } from 'vue'
import './style.css'  // 一定要引入 tailwind 的样式
import App from './App.vue'
import router from './router' // <--- 关键点1：引入路由文件

const app = createApp(App)

app.use(router) // <--- 关键点2：告诉 Vue 使用路由插件
app.mount('#app')