<template>
  <div class="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
    <div class="card w-full max-w-lg">
      <h2 class="text-xl font-bold text-gray-900 mb-4">Bulk Upload Contacts</h2>

      <div v-if="!file" class="space-y-4">
        <div
          class="border-2 border-dashed border-gray-200 rounded-xl p-8 text-center hover:border-brand-400 hover:bg-brand-50/30 transition-all duration-200 cursor-pointer"
          @dragover.prevent
          @drop.prevent="handleDrop"
          @click="$refs.fileInput.click()"
        >
          <input ref="fileInput" type="file" accept=".csv,.xlsx,.xls" class="hidden" @change="handleFileSelect" />
          <Upload :size="32" class="mx-auto text-gray-400 mb-3" />
          <p class="text-gray-700 font-medium">Drag & drop or click to browse</p>
          <p class="text-sm text-gray-400 mt-1">CSV, XLSX, XLS</p>
        </div>

        <div class="bg-gray-50 rounded-xl p-4 text-sm text-gray-600">
          <p class="font-medium mb-2">Expected columns:</p>
          <ul class="space-y-1">
            <li class="flex items-center gap-2"><span class="w-1.5 h-1.5 rounded-full bg-brand-500"></span><strong>phone</strong> (required)</li>
            <li class="flex items-center gap-2"><span class="w-1.5 h-1.5 rounded-full bg-gray-300"></span><strong>name</strong> (optional)</li>
            <li class="flex items-center gap-2"><span class="w-1.5 h-1.5 rounded-full bg-gray-300"></span><strong>email</strong> (optional)</li>
            <li class="flex items-center gap-2"><span class="w-1.5 h-1.5 rounded-full bg-gray-300"></span><strong>company</strong> (optional)</li>
          </ul>
        </div>
      </div>

      <div v-else-if="validating" class="text-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-600 mx-auto mb-3"></div>
        <p class="text-gray-500">Validating file...</p>
      </div>

      <div v-else-if="result" class="space-y-4">
        <div class="grid grid-cols-2 gap-3 text-sm">
          <div class="bg-gray-50 rounded-xl p-3">
            <p class="text-gray-500 text-xs">Total rows</p>
            <p class="text-xl font-bold text-gray-900">{{ result.total_rows }}</p>
          </div>
          <div class="bg-emerald-50 rounded-xl p-3">
            <p class="text-emerald-600 text-xs">Valid</p>
            <p class="text-xl font-bold text-emerald-700">{{ result.valid_rows }}</p>
          </div>
          <div v-if="result.invalid_rows" class="bg-red-50 rounded-xl p-3">
            <p class="text-red-600 text-xs">Invalid</p>
            <p class="text-xl font-bold text-red-700">{{ result.invalid_rows }}</p>
          </div>
          <div v-if="result.duplicates_skipped" class="bg-amber-50 rounded-xl p-3">
            <p class="text-amber-600 text-xs">Duplicates</p>
            <p class="text-xl font-bold text-amber-700">{{ result.duplicates_skipped }}</p>
          </div>
        </div>

        <div v-if="result.errors?.length" class="max-h-40 overflow-y-auto text-sm">
          <p class="font-medium text-red-600 mb-2">Errors:</p>
          <div v-for="err in result.errors" :key="err.row" class="text-red-500 text-xs">
            Row {{ err.row }}: {{ err.errors.join(', ') }}
          </div>
        </div>
      </div>

      <div class="flex justify-end gap-2 mt-6">
        <button @click="$emit('close')" class="btn-secondary">Cancel</button>
        <button v-if="file && !result" @click="handleUpload" class="btn-primary" :disabled="validating">
          {{ validating ? 'Validating...' : 'Upload' }}
        </button>
        <button v-if="result" @click="$emit('close')" class="btn-primary">Done</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useContactsStore } from '@/stores/contacts'
import { Upload } from '@lucide/vue'

const props = defineProps({ listId: { type: String, required: true } })
const emit = defineEmits(['close', 'uploaded'])

const contactsStore = useContactsStore()
const file = ref(null)
const validating = ref(false)
const result = ref(null)

function handleFileSelect(e) {
  file.value = e.target.files[0]
}

function handleDrop(e) {
  file.value = e.dataTransfer.files[0]
}

async function handleUpload() {
  if (!file.value) return
  validating.value = true
  try {
    const uploadResult = await contactsStore.bulkUpload(props.listId, file.value)
    result.value = uploadResult
    emit('uploaded', uploadResult)
  } catch (e) {
    alert(e.response?.data?.detail || 'Upload failed')
  } finally {
    validating.value = false
  }
}
</script>
