<template>
  <div class="overflow-x-auto">
    <table class="w-full text-sm">
      <thead class="table-header">
        <tr>
          <th
            v-for="col in columns"
            :key="col.key"
            class="px-4 py-3 cursor-pointer hover:bg-gray-100"
            @click="col.sortable && toggleSort(col.key)"
          >
            <div class="flex items-center gap-1">
              {{ col.label }}
              <span v-if="sortKey === col.key" class="text-blue-600">
                {{ sortOrder === 'asc' ? '↑' : '↓' }}
              </span>
            </div>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="!items?.length">
          <td :colspan="columns.length" class="px-4 py-8 text-center text-gray-500">No data</td>
        </tr>
        <tr v-for="(item, idx) in sortedItems" :key="item.id || idx" class="border-t hover:bg-gray-50">
          <td v-for="col in columns" :key="col.key" class="px-4 py-3">
            <slot :name="`cell-${col.key}`" :item="item" :value="item[col.key]">
              {{ item[col.key] }}
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  columns: { type: Array, required: true },
  items: { type: Array, default: () => [] },
})

const sortKey = ref('')
const sortOrder = ref('asc')

function toggleSort(key) {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'asc'
  }
}

const sortedItems = computed(() => {
  if (!sortKey.value) return props.items
  return [...props.items].sort((a, b) => {
    const aVal = a[sortKey.value] ?? ''
    const bVal = b[sortKey.value] ?? ''
    const cmp = String(aVal).localeCompare(String(bVal))
    return sortOrder.value === 'asc' ? cmp : -cmp
  })
})
</script>
