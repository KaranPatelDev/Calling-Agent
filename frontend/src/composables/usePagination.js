import { ref, computed } from 'vue'

export function usePagination(fetchFn, initialPage = 1, initialLimit = 20) {
  const page = ref(initialPage)
  const limit = ref(initialLimit)
  const total = ref(0)
  const items = ref([])
  const loading = ref(false)

  const pages = computed(() => Math.ceil(total.value / limit.value) || 1)
  const hasNext = computed(() => page.value < pages.value)
  const hasPrev = computed(() => page.value > 1)

  async function fetch() {
    loading.value = true
    try {
      const result = await fetchFn(page.value, limit.value)
      items.value = result.items || []
      total.value = result.total || 0
    } finally {
      loading.value = false
    }
  }

  function nextPage() {
    if (hasNext.value) {
      page.value++
      fetch()
    }
  }

  function prevPage() {
    if (hasPrev.value) {
      page.value--
      fetch()
    }
  }

  function goToPage(p) {
    if (p >= 1 && p <= pages.value) {
      page.value = p
      fetch()
    }
  }

  function reset() {
    page.value = initialPage
    fetch()
  }

  return { page, limit, total, items, loading, pages, hasNext, hasPrev, fetch, nextPage, prevPage, goToPage, reset }
}
