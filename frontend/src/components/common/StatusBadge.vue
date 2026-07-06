<template>
  <Tag :value="label" :severity="severity" rounded />
</template>

<script setup>
import { computed } from 'vue'
import Tag from 'primevue/tag'

const props = defineProps({
  status: { type: String, required: true },
})

const statusConfig = {
  completed: { label: 'Completed', severity: 'success' },
  successful: { label: 'Successful', severity: 'success' },
  running: { label: 'Running', severity: 'info' },
  in_progress: { label: 'In Progress', severity: 'info' },
  'in-progress': { label: 'In Progress', severity: 'info' },
  dialing: { label: 'Dialing', severity: 'warn' },
  ringing: { label: 'Ringing', severity: 'warn' },
  queued: { label: 'Queued', severity: 'secondary' },
  paused: { label: 'Paused', severity: 'warn' },
  draft: { label: 'Draft', severity: 'secondary' },
  scheduled: { label: 'Scheduled', severity: 'contrast' },
  failed: { label: 'Failed', severity: 'danger' },
  'no-answer': { label: 'No Answer', severity: 'warn' },
  busy: { label: 'Busy', severity: 'warn' },
  cancelled: { label: 'Cancelled', severity: 'secondary' },
}

const label = computed(() => statusConfig[props.status]?.label || props.status)
const severity = computed(() => statusConfig[props.status]?.severity || 'secondary')
</script>
