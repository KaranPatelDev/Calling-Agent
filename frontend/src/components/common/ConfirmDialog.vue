<template>
  <div v-if="show" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="card w-full max-w-md">
      <h2 class="text-xl font-bold mb-2">{{ title }}</h2>
      <p class="text-gray-600 mb-6">{{ message }}</p>
      <div class="flex justify-end gap-2">
        <button @click="$emit('cancel')" class="btn-secondary">Cancel</button>
        <button @click="$emit('confirm')" :class="dangerMode ? 'btn-danger' : 'btn-primary'">
          {{ confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  show: { type: Boolean, default: false },
  title: { type: String, default: 'Confirm' },
  message: { type: String, default: 'Are you sure?' },
  confirmText: { type: String, default: 'Confirm' },
  dangerMode: { type: Boolean, default: false },
})

defineEmits(['confirm', 'cancel'])
</script>
