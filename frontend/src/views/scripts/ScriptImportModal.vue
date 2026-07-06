<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="card w-full max-w-4xl max-h-[90vh] overflow-y-auto">
      <h2 class="text-xl font-bold mb-4">Import Scripts</h2>

      <!-- Step 1: Upload -->
      <div v-if="step === 1" class="space-y-4">
        <div
          class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors cursor-pointer"
          @dragover.prevent
          @drop.prevent="handleDrop"
          @click="$refs.fileInput.click()"
        >
          <input ref="fileInput" type="file" accept=".xlsx,.xls,.pdf" class="hidden" @change="handleFileSelect" />
          <div class="text-3xl mb-2">{{ fileIcon }}</div>
          <p class="text-gray-700 font-medium">{{ fileName || 'Drag & drop or click to browse' }}</p>
          <p class="text-sm text-gray-400 mt-1">Supports Excel (.xlsx, .xls) and PDF</p>
        </div>

        <div class="bg-gray-50 rounded-lg p-4 text-sm text-gray-600">
          <p class="font-medium mb-2">Expected format for Excel:</p>
          <ul class="list-disc list-inside space-y-1">
            <li><strong>name</strong> — Script name</li>
            <li><strong>content</strong> — Script text/message</li>
            <li><strong>language</strong> — (optional) hi-IN, en-IN, etc.</li>
          </ul>
          <p class="mt-3 text-gray-500">For PDF: the entire text content becomes one script. You can edit the name after parsing.</p>
        </div>
      </div>

      <!-- Step 2: Parsing -->
      <div v-else-if="step === 2" class="text-center py-8">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p class="text-gray-500">Parsing file...</p>
      </div>

      <!-- Step 3: Review & Edit -->
      <div v-else-if="step === 3" class="space-y-4">
        <div class="flex items-center justify-between">
          <p class="text-sm text-gray-600">
            <span class="font-medium">{{ parsedScripts.length }}</span> script{{ parsedScripts.length !== 1 ? 's' : '' }} found.
            Edit below before importing.
          </p>
          <span class="text-xs px-2 py-1 rounded-full" :class="sourceBadgeClass">
            {{ source === 'pdf' ? 'PDF' : 'Excel' }}
          </span>
        </div>

        <EditableTable
          :columns="scriptColumns"
          :rows="parsedScripts"
          :newRowTemplate="newScriptTemplate"
          @update:rows="parsedScripts = $event"
          emptyMessage="No scripts to import."
        />
      </div>

      <!-- Step 4: Importing -->
      <div v-else-if="step === 4" class="text-center py-8">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p class="text-gray-500">Importing {{ parsedScripts.length }} script{{ parsedScripts.length !== 1 ? 's' : '' }}...</p>
      </div>

      <!-- Step 5: Done -->
      <div v-else-if="step === 5" class="text-center py-8">
        <div class="text-4xl mb-4">&#10003;</div>
        <h3 class="text-lg font-semibold text-green-700 mb-2">Import Complete</h3>
        <p class="text-gray-500 mb-4">{{ importedCount }} script{{ importedCount !== 1 ? 's' : '' }} created successfully.</p>
      </div>

      <!-- Error -->
      <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-3 mt-4">
        <p class="text-red-700 text-sm">{{ error }}</p>
      </div>

      <!-- Actions -->
      <div class="flex justify-end gap-2 mt-6">
        <button v-if="step === 1" @click="$emit('close')" class="btn-secondary">Cancel</button>
        <button v-if="step === 1 && file" @click="parseFile" class="btn-primary" :disabled="parsing">
          {{ parsing ? 'Parsing...' : 'Parse File' }}
        </button>

        <button v-if="step === 3" @click="step = 1; parsedScripts = []; file = null" class="btn-secondary">Back</button>
        <button v-if="step === 3" @click="$emit('close')" class="btn-secondary">Cancel</button>
        <button v-if="step === 3" @click="importScripts" class="btn-primary" :disabled="parsedScripts.length === 0">
          Import {{ parsedScripts.length }} Script{{ parsedScripts.length !== 1 ? 's' : '' }}
        </button>

        <button v-if="step === 5" @click="$emit('close'); $emit('imported')" class="btn-primary">Done</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useScriptsStore } from '@/stores/scripts'
import EditableTable from '@/components/common/EditableTable.vue'

const emit = defineEmits(['close', 'imported'])
const scriptsStore = useScriptsStore()

const step = ref(1)
const file = ref(null)
const parsing = ref(false)
const error = ref('')
const parsedScripts = ref([])
const source = ref('')
const importedCount = ref(0)

const fileName = computed(() => file.value?.name || '')
const fileIcon = computed(() => {
  if (!file.value) return '&#128196;'
  return file.value.name.endsWith('.pdf') ? '&#128196;' : '&#128202;'
})
const sourceBadgeClass = computed(() =>
  source.value === 'pdf' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
)

const scriptColumns = [
  { key: 'name', label: 'Name', required: true, placeholder: 'Script name', width: 'w-48' },
  { key: 'content', label: 'Content', type: 'textarea', required: true, placeholder: 'Script content...' },
  {
    key: 'language', label: 'Language', type: 'select', width: 'w-36',
    options: [
      { value: 'hi-IN', label: 'Hindi' },
      { value: 'en-IN', label: 'English' },
      { value: 'ta-IN', label: 'Tamil' },
      { value: 'te-IN', label: 'Telugu' },
      { value: 'bn-IN', label: 'Bengali' },
      { value: 'mr-IN', label: 'Marathi' },
    ],
  },
]

function newScriptTemplate() {
  return { name: '', content: '', language: 'hi-IN', _valid: true, _errors: [] }
}

function handleFileSelect(e) {
  file.value = e.target.files[0]
}

function handleDrop(e) {
  file.value = e.dataTransfer.files[0]
}

async function parseFile() {
  if (!file.value) return
  parsing.value = true
  error.value = ''
  try {
    const formData = new FormData()
    formData.append('file', file.value)
    const res = await scriptsStore.uploadPreview(formData)
    parsedScripts.value = res.scripts.map(s => ({ ...s, _valid: true, _errors: [] }))
    source.value = res.source
    step.value = 3
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to parse file'
    step.value = 1
  } finally {
    parsing.value = false
  }
}

async function importScripts() {
  const validScripts = parsedScripts.value.filter(s => s._valid && s.name && s.content)
  if (validScripts.length === 0) {
    error.value = 'No valid scripts to import. Ensure each row has a name and content.'
    return
  }
  step.value = 4
  error.value = ''
  try {
    const result = await scriptsStore.bulkImport(validScripts.map(s => ({
      name: s.name,
      content: s.content,
      language: s.language || 'hi-IN',
    })))
    importedCount.value = result.length
    step.value = 5
  } catch (e) {
    error.value = e.response?.data?.detail || 'Import failed'
    step.value = 3
  }
}
</script>
