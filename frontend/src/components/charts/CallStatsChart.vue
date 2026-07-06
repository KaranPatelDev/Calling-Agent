<template>
  <div class="card">
    <h3 class="text-lg font-semibold mb-4">{{ title }}</h3>
    <div class="space-y-3">
      <div v-for="(item, idx) in data" :key="idx" class="flex items-center gap-3">
        <div class="w-32 text-sm text-gray-600 truncate">{{ item.label }}</div>
        <div class="flex-1 bg-gray-200 rounded-full h-4 overflow-hidden">
          <div
            class="h-full rounded-full transition-all duration-500"
            :style="{ width: `${getPercent(item.value)}%`, backgroundColor: colors[idx % colors.length] }"
          ></div>
        </div>
        <div class="w-16 text-right text-sm font-medium">{{ item.value }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  title: { type: String, default: 'Statistics' },
  data: { type: Array, default: () => [] },
})

const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899']

function getPercent(value) {
  const max = Math.max(...props.data.map(d => d.value), 1)
  return (value / max) * 100
}
</script>
