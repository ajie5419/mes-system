import { ElMessageBox } from 'element-plus'

interface ConfirmOptions {
  title?: string
  message: string
  type?: 'warning' | 'error' | 'info' | 'success'
  confirmText?: string
  cancelText?: string
}

export function useConfirm() {
  async function confirm(options: ConfirmOptions): Promise<boolean> {
    const {
      title = '确认操作',
      message,
      type = 'warning',
      confirmText = '确认',
      cancelText = '取消',
    } = options
    try {
      await ElMessageBox.confirm(message, title, {
        type,
        confirmButtonText: confirmText,
        cancelButtonText: cancelText,
        closeOnClickModal: false,
      })
      return true
    } catch {
      return false
    }
  }

  async function confirmDelete(itemName: string): Promise<boolean> {
    return confirm({
      title: '危险操作',
      message: `确认删除「${itemName}」？此操作不可恢复。`,
      type: 'error',
      confirmText: '确认删除',
      cancelText: '取消',
    })
  }

  return { confirm, confirmDelete }
}
