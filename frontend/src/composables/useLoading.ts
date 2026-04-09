import { ref } from 'vue'

const loadingMap = new Map<string, number>()

export function useLoading(namespace = 'global') {
  const count = ref(0)

  function start() {
    loadingMap.set(namespace, (loadingMap.get(namespace) || 0) + 1)
    count.value = loadingMap.get(namespace)!
  }

  function stop() {
    const cur = Math.max(0, (loadingMap.get(namespace) || 0) - 1)
    loadingMap.set(namespace, cur)
    count.value = cur
  }

  async function wrap<T>(fn: () => Promise<T>): Promise<T> {
    start()
    try {
      return await fn()
    } finally {
      stop()
    }
  }

  const isLoading = ref(false)

  // convenience: auto-track wrap
  return {
    isLoading,
    start,
    stop,
    wrap,
    get count() { return count.value },
  }
}
