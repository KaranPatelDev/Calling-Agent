<template>
  <Dialog :visible="true" modal header="Import Scripts" :style="{ width: '48rem' }" :closable="step < 4" @update:visible="$emit('close')">
    <!-- Step 1: Upload -->
    <div v-if="step === 1" class="space-y-4">
      <div
        class="border-2 border-dashed border-surface-300 dark:border-surface-600 rounded-lg p-8 text-center hover:border-primary-400 transition-colors cursor-pointer"
        @dragover.prevent
        @drop.prevent="handleDrop"
        @click="$refs.fileInput.click()"
      >
        <input ref="fileInput" type="file" accept=".xlsx,.xls,.pdf" class="hidden" @change="handleFileSelect" />
        <FileIcon :size="32" class="mx-auto text-surface-400 mb-2" />
        <p class="text-surface-700 dark:text-surface-200 font-medium">{{ fileName || 'Drag & drop or click to browse' }}</p>
        <p class="text-sm text-surface-400 mt-1">Supports Excel (.xlsx, .xls) and PDF</p>
      </div>

      <div class="bg-surface-50 dark:bg-surface-800 rounded-lg p-4 text-sm text-surface-600 dark:text-surface-300">
        <p class="font-medium mb-2">Expected format for Excel:</p>
        <ul class="list-disc list-inside space-y-1">
          <li><strong>name</strong> — Script name</li>
          <li><strong>content</strong> — Script text/message</li>
          <li><strong>language</strong> — (optional) hi-IN, en-IN, etc.</li>
        </ul>
        <p class="mt-3 text-surface-500">For PDF: the entire text content becomes one script. You can edit the name after parsing.</p>
      </div>
    </div>

    <!-- Step 2: Parsing -->
    <div v-else-if="step === 2" class="text-center py-8">
      <ProgressSpinner style="width: 2.5rem; height: 2.5rem" stroke-width="4" />
      <p class="text-surface-500 mt-4">Parsing file...</p>
    </div>

    <!-- Step 3: Review & Edit -->
    <div v-else-if="step === 3" class="space-y-4">
      <div class="flex items-center justify-between">
        <p class="text-sm text-surface-600 dark:text-surface-300">
          <span class="font-medium">{{ parsedScripts.length }}</span> script{{ parsedScripts.length !== 1 ? 's' : '' }} found.
          Edit below before importing.
        </p>
        <Tag :value="source === 'pdf' ? 'PDF' : 'Excel'" :severity="source === 'pdf' ? 'danger' : 'success'" />
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
      <ProgressSpinner style="width: 2.5rem; height: 2.5rem" stroke-width="4" />
      <p class="text-surface-500 mt-4">Importing {{ parsedScripts.length }} script{{ parsedScripts.length !== 1 ? 's' : '' }}...</p>
    </div>

    <!-- Step 5: Done -->
    <div v-else-if="step === 5" class="text-center py-8">
      <CheckCircle2 :size="48" class="mx-auto text-emerald-500 mb-4" />
      <h3 class="text-lg font-semibold text-emerald-700 dark:text-emerald-400 mb-2">Import Complete</h3>
      <p class="text-surface-500 mb-4">{{ importedCount }} script{{ importedCount !== 1 ? 's' : '' }} created successfully.</p>
    </div>

    <Message v-if="error" severity="error" :closable="false" class="mt-4">{{ error }}</Message>

    <template #footer>
      <Button v-if="step === 1" label="Cancel" severity="secondary" text @click="$emit('close')" />
      <Button v-if="step === 1 && file" :label="parsing ? 'Parsing...' : 'Parse File'" :loading="parsing" @click="parseFile" />

      <Button v-if="step === 3" label="Back" severity="secondary" text @click="step = 1; parsedScripts = []; file = null" />
      <Button v-if="step === 3" label="Cancel" severity="secondary" text @click="$emit('close')" />
      <Button v-if="step === 3" :label="`Import ${parsedScripts.length} Script${parsedScripts.length !== 1 ? 's' : ''}`" :disabled="parsedScripts.length === 0" @click="importScripts" />

      <Button v-if="step === 5" label="Done" @click="$emit('close'); $emit('imported')" />
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useScriptsStore } from '@/stores/scripts'
import EditableTable from '@/components/common/EditableTable.vue'
import { FileText as FileIcon, CheckCircle2 } from '@lucide/vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import Message from 'primevue/message'
import ProgressSpinner from 'primevue/progressspinner'

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
