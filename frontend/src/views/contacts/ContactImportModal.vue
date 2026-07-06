<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="card w-full max-w-4xl max-h-[90vh] overflow-y-auto">
      <h2 class="text-xl font-bold mb-4">Import Contacts</h2>

      <!-- Step 1: Upload -->
      <div v-if="step === 1" class="space-y-4">
        <div
          class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors cursor-pointer"
          @dragover.prevent
          @drop.prevent="handleDrop"
          @click="$refs.fileInput.click()"
        >
          <input ref="fileInput" type="file" accept=".xlsx,.xls,.csv,.pdf" class="hidden" @change="handleFileSelect" />
          <div class="text-3xl mb-2">&#128206;</div>
          <p class="text-gray-700 font-medium">{{ fileName || 'Drag & drop or click to browse' }}</p>
          <p class="text-sm text-gray-400 mt-1">Supports CSV, Excel (.xlsx, .xls), and PDF</p>
        </div>

        <div class="bg-gray-50 rounded-lg p-4 text-sm text-gray-600">
          <p class="font-medium mb-2">Expected columns for CSV/Excel:</p>
          <ul class="list-disc list-inside space-y-1">
            <li><strong>phone</strong> (required) — Indian mobile number</li>
            <li><strong>name</strong> (optional)</li>
            <li><strong>email</strong> (optional)</li>
            <li><strong>company</strong> (optional)</li>
          </ul>
          <p class="mt-3 text-gray-500">For PDF: phone numbers are automatically detected from the text. You can edit all fields before importing.</p>
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
            <span class="font-medium">{{ parsedContacts.length }}</span> contact{{ parsedContacts.length !== 1 ? 's' : '' }} found.
            Edit below before importing.
          </p>
          <div class="flex items-center gap-2 text-xs">
            <span class="px-2 py-1 rounded-full bg-green-100 text-green-700">{{ validCount }} valid</span>
            <span v-if="invalidCount > 0" class="px-2 py-1 rounded-full bg-red-100 text-red-700">{{ invalidCount }} invalid</span>
          </div>
        </div>

        <EditableTable
          :columns="contactColumns"
          :rows="parsedContacts"
          :newRowTemplate="newContactTemplate"
          @update:rows="parsedContacts = $event"
          emptyMessage="No contacts to import."
        />
      </div>

      <!-- Step 4: Importing -->
      <div v-else-if="step === 4" class="text-center py-8">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p class="text-gray-500">Importing contacts...</p>
      </div>

      <!-- Step 5: Done -->
      <div v-else-if="step === 5" class="space-y-4">
        <div class="text-center py-4">
          <div class="text-4xl mb-4">&#10003;</div>
          <h3 class="text-lg font-semibold text-green-700 mb-2">Import Complete</h3>
        </div>
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div class="bg-green-50 rounded p-3">
            <p class="text-green-600">Imported</p>
            <p class="text-xl font-bold text-green-700">{{ importResult.imported }}</p>
          </div>
          <div v-if="importResult.duplicates > 0" class="bg-yellow-50 rounded p-3">
            <p class="text-yellow-600">Duplicates Skipped</p>
            <p class="text-xl font-bold text-yellow-700">{{ importResult.duplicates }}</p>
          </div>
        </div>
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

        <button v-if="step === 3" @click="step = 1; parsedContacts = []; file = null" class="btn-secondary">Back</button>
        <button v-if="step === 3" @click="$emit('close')" class="btn-secondary">Cancel</button>
        <button v-if="step === 3" @click="importContacts" class="btn-primary" :disabled="validCount === 0">
          Import {{ validCount }} Contact{{ validCount !== 1 ? 's' : '' }}
        </button>

        <button v-if="step === 5" @click="$emit('close'); $emit('imported')" class="btn-primary">Done</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useContactsStore } from '@/stores/contacts'
import EditableTable from '@/components/common/EditableTable.vue'

const props = defineProps({
  listId: { type: String, required: true },
})

const emit = defineEmits(['close', 'imported'])
const contactsStore = useContactsStore()

const step = ref(1)
const file = ref(null)
const parsing = ref(false)
const error = ref('')
const parsedContacts = ref([])
const importedCount = ref(0)
const importResult = ref({ imported: 0, duplicates: 0 })

const fileName = computed(() => file.value?.name || '')
const validCount = computed(() => parsedContacts.value.filter(c => c._valid && c.phone).length)
const invalidCount = computed(() => parsedContacts.value.filter(c => !c._valid).length)

const contactColumns = [
  { key: 'phone', label: 'Phone', required: true, placeholder: '+91XXXXXXXXXX', width: 'w-44' },
  { key: 'name', label: 'Name', placeholder: 'Contact name' },
  { key: 'email', label: 'Email', placeholder: 'email@example.com' },
  { key: 'company', label: 'Company', placeholder: 'Company name' },
]

function newContactTemplate() {
  return { phone: '', name: '', email: '', company: '', _valid: true, _errors: [] }
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
    const res = await contactsStore.uploadPreview(formData)
    parsedContacts.value = res.rows.map(r => ({ ...r, _valid: r._valid !== false, _errors: r._errors || [] }))
    step.value = 3
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to parse file'
    step.value = 1
  } finally {
    parsing.value = false
  }
}

async function importContacts() {
  const validContacts = parsedContacts.value.filter(c => c._valid && c.phone)
  if (validContacts.length === 0) {
    error.value = 'No valid contacts to import. Ensure each row has a phone number.'
    return
  }
  step.value = 4
  error.value = ''
  try {
    const result = await contactsStore.bulkImportContacts(props.listId, validContacts.map(c => ({
      phone: c.phone,
      name: c.name || null,
      email: c.email || null,
      company: c.company || null,
    })))
    importResult.value = { imported: result.valid_rows, duplicates: result.duplicates_skipped }
    importedCount.value = result.valid_rows
    step.value = 5
  } catch (e) {
    error.value = e.response?.data?.detail || 'Import failed'
    step.value = 3
  }
}
</script>
