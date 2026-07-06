<template>
  <div>
    <div
      v-if="!audioSrc"
      class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors cursor-pointer"
      @dragover.prevent
      @drop.prevent="handleDrop"
      @click="$refs.input.click()"
    >
      <input ref="input" type="file" accept=".mp3,.wav,.ogg" class="hidden" @change="handleChange" />
      <p class="text-gray-500">Drag & drop audio file here</p>
      <p class="text-sm text-gray-400 mt-1">MP3, WAV, OGG (max 10MB)</p>
    </div>

    <div v-else class="space-y-2">
      <audio :src="audioSrc" controls class="w-full" />
      <div class="flex items-center justify-between text-sm">
        <span class="text-gray-500">{{ fileName }}</span>
        <button @click="removeFile" class="text-red-600 hover:text-red-800">Remove</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: [File, String], default: null },
})

const emit = defineEmits(['update:modelValue'])

const audioSrc = ref('')
const fileName = ref('')

watch(() => props.modelValue, (val) => {
  if (val instanceof File) {
    audioSrc.value = URL.createObjectURL(val)
    fileName.value = val.name
  } else if (typeof val === 'string' && val) {
    audioSrc.value = val
    fileName.value = val.split('/').pop()
  } else {
    audioSrc.value = ''
    fileName.value = ''
  }
}, { immediate: true })

function handleChange(e) {
  const file = e.target.files[0]
  if (file) emitFile(file)
}

function handleDrop(e) {
  const file = e.dataTransfer.files[0]
  if (file) emitFile(file)
}

function emitFile(file) {
  if (file.size > 10 * 1024 * 1024) {
    alert('File too large. Maximum 10MB.')
    return
  }
  emit('update:modelValue', file)
}

function removeFile() {
  audioSrc.value = ''
  fileName.value = ''
  emit('update:modelValue', null)
}
</script>
