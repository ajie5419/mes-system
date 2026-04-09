import type { App } from 'vue'
import { usePermissionStore } from '../stores/permission'

export default {
  install(app: App) {
    app.directive('permission', {
      mounted(el: HTMLElement, binding) {
        const permStore = usePermissionStore()
        if (!permStore.hasPermission(binding.value)) {
          el.parentNode?.removeChild(el)
        }
      },
      updated(el: HTMLElement, binding) {
        const permStore = usePermissionStore()
        if (!permStore.hasPermission(binding.value)) {
          el.parentNode?.removeChild(el)
        }
      },
    })
  },
}
