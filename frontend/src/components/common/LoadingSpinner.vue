<template>
  <div class="flex items-center justify-center gap-2">
    <ProgressSpinner :style="{ width: sizePx, height: sizePx }" stroke-width="4" />
    <span v-if="text" class="text-surface-500">{{ text }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import ProgressSpinner from 'primevue/progressspinner'

const props = defineProps({
  size: { type: String, default: 'md' },
  text: { type: String, default: '' },
})

const sizePx = computed(() => ({
  sm: '1rem',
  md: '2rem',
  lg: '3rem',
}[props.size]))
</script>
