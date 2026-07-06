<template>
  <span :class="badgeClass">{{ label }}</span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, required: true },
})

const statusConfig = {
  completed: { label: 'Completed', class: 'bg-green-100 text-green-800' },
  successful: { label: 'Successful', class: 'bg-green-100 text-green-800' },
  running: { label: 'Running', class: 'bg-blue-100 text-blue-800' },
  in_progress: { label: 'In Progress', class: 'bg-blue-100 text-blue-800' },
  'in-progress': { label: 'In Progress', class: 'bg-blue-100 text-blue-800' },
  dialing: { label: 'Dialing', class: 'bg-yellow-100 text-yellow-800' },
  ringing: { label: 'Ringing', class: 'bg-yellow-100 text-yellow-800' },
  queued: { label: 'Queued', class: 'bg-gray-100 text-gray-800' },
  paused: { label: 'Paused', class: 'bg-orange-100 text-orange-800' },
  draft: { label: 'Draft', class: 'bg-gray-100 text-gray-600' },
  scheduled: { label: 'Scheduled', class: 'bg-purple-100 text-purple-800' },
  failed: { label: 'Failed', class: 'bg-red-100 text-red-800' },
  'no-answer': { label: 'No Answer', class: 'bg-orange-100 text-orange-800' },
  busy: { label: 'Busy', class: 'bg-yellow-100 text-yellow-800' },
  cancelled: { label: 'Cancelled', class: 'bg-gray-100 text-gray-600' },
}

const label = computed(() => statusConfig[props.status]?.label || props.status)
const badgeClass = computed(() => {
  const base = 'px-2 py-1 rounded-full text-xs font-medium'
  const cfg = statusConfig[props.status]
  return cfg ? `${base} ${cfg.class}` : `${base} bg-gray-100 text-gray-600`
})
</script>
