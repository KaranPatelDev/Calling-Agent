<template>
  <div class="card">
    <h3 class="text-lg font-semibold mb-4">{{ title }}</h3>
    <div class="flex items-center justify-center">
      <div class="relative">
        <svg width="200" height="200" viewBox="0 0 200 200">
          <circle
            v-for="(segment, idx) in segments"
            :key="idx"
            cx="100"
            cy="100"
            r="80"
            fill="none"
            :stroke="segment.color"
            stroke-width="30"
            :stroke-dasharray="segment.dasharray"
            :stroke-dashoffset="segment.offset"
            :transform="`rotate(${segment.rotation} 100 100)`"
          />
        </svg>
        <div class="absolute inset-0 flex items-center justify-center">
          <div class="text-center">
            <p class="text-2xl font-bold">{{ totalValue }}</p>
            <p class="text-xs text-gray-500">Total</p>
          </div>
        </div>
      </div>
    </div>
    <div class="flex justify-center gap-4 mt-4">
      <div v-for="(item, idx) in data" :key="idx" class="flex items-center gap-2 text-sm">
        <div class="w-3 h-3 rounded-full" :style="{ backgroundColor: colors[idx % colors.length] }"></div>
        <span class="text-gray-600">{{ item.label }}</span>
        <span class="font-medium">{{ item.value }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: { type: String, default: 'Success Rate' },
  data: { type: Array, default: () => [] },
})

const colors = ['#10B981', '#EF4444', '#F59E0B', '#6B7280', '#3B82F6']

const totalValue = computed(() => props.data.reduce((sum, d) => sum + d.value, 0))

const segments = computed(() => {
  const total = totalValue.value || 1
  const circumference = 2 * Math.PI * 80
  let accumulatedOffset = 0
  const circumference2 = 2 * Math.PI * 80

  return props.data.map((item, idx) => {
    const percent = item.value / total
    const dashLength = percent * circumference
    const gapLength = circumference - dashLength
    const rotation = (accumulatedOffset / circumference) * 360 - 90
    accumulatedOffset += dashLength

    return {
      color: colors[idx % colors.length],
      dasharray: `${dashLength} ${gapLength}`,
      offset: 0,
      rotation,
    }
  })
})
</script>
