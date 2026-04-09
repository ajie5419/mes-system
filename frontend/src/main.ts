import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import 'element-plus/dist/index.css'
import './style.css'
import App from './App.vue'

const app = createApp(App)
const pinia = createPinia()

// 注册所有图标，确保侧边栏和看板图标正常显示
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

import permissionDirective from './directives/permission'

app.use(pinia)
app.use(ElementPlus)
app.use(permissionDirective)
app.mount('#app')
