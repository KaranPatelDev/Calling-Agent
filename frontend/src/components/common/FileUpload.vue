<template>
  <div
    class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors cursor-pointer"
    @dragover.prevent="$event.target.classList.add('border-blue-400', 'bg-blue-50')"
    @dragleave.prevent="$event.target.classList.remove('border-blue-400', 'bg-blue-50')"
    @drop.prevent="handleDrop"
    @click="$refs.input.click()"
  >
    <input ref="input" type="file" :accept="accept" class="hidden" @change="handleChange" />
    <slot>
      <p class="text-gray-500">Drag & drop file here or click to browse</p>
      <p class="text-sm text-gray-400 mt-1">{{ accept }}</p>
    </slot>
  </div>
</template>

<script setup>
const props = defineProps({
  accept: { type: String, default: '*/*' },
})

const emit = defineEmits(['file'])

function handleChange(e) {
  const file = e.target.files[0]
  if (file) emit('file', file)
}

function handleDrop(e) {
  e.target.classList.remove('border-blue-400', 'bg-blue-50')
  const file = e.dataTransfer.files[0]
  if (file) emit('file', file)
}
</script>
