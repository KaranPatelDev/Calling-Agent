<template>
  <Dialog :visible="true" modal header="Import Contacts" :style="{ width: '48rem' }" :closable="step < 4" @update:visible="$emit('close')">
    <!-- Step 1: Upload -->
    <div v-if="step === 1" class="space-y-4">
      <div
        class="border-2 border-dashed border-surface-300 dark:border-surface-600 rounded-lg p-8 text-center hover:border-primary-400 transition-colors cursor-pointer"
        @dragover.prevent
        @drop.prevent="handleDrop"
        @click="$refs.fileInput.click()"
      >
        <input ref="fileInput" type="file" accept=".xlsx,.xls,.csv,.pdf" class="hidden" @change="handleFileSelect" />
        <FileText :size="32" class="mx-auto text-surface-400 mb-2" />
        <p class="text-surface-700 dark:text-surface-200 font-medium">{{ fileName || 'Drag & drop or click to browse' }}</p>
        <p class="text-sm text-surface-400 mt-1">Supports CSV, Excel (.xlsx, .xls), and PDF</p>
      </div>

      <div class="bg-surface-50 dark:bg-surface-800 rounded-lg p-4 text-sm text-surface-600 dark:text-surface-300">
        <p class="font-medium mb-2">Expected columns for CSV/Excel:</p>
        <ul class="list-disc list-inside space-y-1">
          <li><strong>phone</strong> (required) — Indian mobile number</li>
          <li><strong>name</strong> (optional)</li>
          <li><strong>email</strong> (optional)</li>
          <li><strong>company</strong> (optional)</li>
        </ul>
        <p class="mt-3 text-surface-500">For PDF: phone numbers are automatically detected from the text. You can edit all fields before importing.</p>
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
          <span class="font-medium">{{ parsedContacts.length }}</span> contact{{ parsedContacts.length !== 1 ? 's' : '' }} found.
          Edit below before importing.
        </p>
        <div class="flex items-center gap-2">
          <Tag :value="`${validCount} valid`" severity="success" />
          <Tag v-if="invalidCount > 0" :value="`${invalidCount} invalid`" severity="danger" />
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
      <ProgressSpinner style="width: 2.5rem; height: 2.5rem" stroke-width="4" />
      <p class="text-surface-500 mt-4">Importing contacts...</p>
    </div>

    <!-- Step 5: Done -->
    <div v-else-if="step === 5" class="space-y-4">
      <div class="text-center py-4">
        <CheckCircle2 :size="48" class="mx-auto text-emerald-500 mb-4" />
        <h3 class="text-lg font-semibold text-emerald-700 dark:text-emerald-400 mb-2">Import Complete</h3>
      </div>
      <div class="grid grid-cols-2 gap-4 text-sm">
        <div class="bg-emerald-50 dark:bg-emerald-500/10 rounded p-3">
          <p class="text-emerald-600 dark:text-emerald-400">Imported</p>
          <p class="text-xl font-bold text-emerald-700 dark:text-emerald-300">{{ importResult.imported }}</p>
        </div>
        <div v-if="importResult.duplicates > 0" class="bg-amber-50 dark:bg-amber-500/10 rounded p-3">
          <p class="text-amber-600 dark:text-amber-400">Duplicates Skipped</p>
          <p class="text-xl font-bold text-amber-700 dark:text-amber-300">{{ importResult.duplicates }}</p>
        </div>
      </div>
    </div>

    <Message v-if="error" severity="error" :closable="false" class="mt-4">{{ error }}</Message>

    <template #footer>
      <Button v-if="step === 1" label="Cancel" severity="secondary" text @click="$emit('close')" />
      <Button v-if="step === 1 && file" :label="parsing ? 'Parsing...' : 'Parse File'" :loading="parsing" @click="parseFile" />

      <Button v-if="step === 3" label="Back" severity="secondary" text @click="step = 1; parsedContacts = []; file = null" />
      <Button v-if="step === 3" label="Cancel" severity="secondary" text @click="$emit('close')" />
      <Button v-if="step === 3" :label="`Import ${validCount} Contact${validCount !== 1 ? 's' : ''}`" :disabled="validCount === 0" @click="importContacts" />

      <Button v-if="step === 5" label="Done" @click="$emit('close'); $emit('imported')" />
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useContactsStore } from '@/stores/contacts'
import EditableTable from '@/components/common/EditableTable.vue'
import { FileText, CheckCircle2 } from '@lucide/vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import Message from 'primevue/message'
import ProgressSpinner from 'primevue/progressspinner'

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
