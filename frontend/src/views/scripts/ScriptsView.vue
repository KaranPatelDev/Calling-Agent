<template>
  <AppLayout>
    <div class="space-y-6">
      <motion.div
        initial="{ opacity: 0, y: -10 }"
        animate="{ opacity: 1, y: 0 }"
        class="flex justify-between items-center"
      >
        <div>
          <h1 class="text-2xl font-bold text-surface-900 dark:text-surface-0">Scripts</h1>
          <p class="text-sm text-surface-500 mt-1">Manage your call scripts and audio files</p>
        </div>
        <div class="flex gap-2">
          <Button label="Import File" severity="secondary" outlined @click="showImport = true">
            <template #icon><Upload :size="16" /></template>
          </Button>
          <Button label="New Script" @click="showCreate = true">
            <template #icon><Plus :size="16" /></template>
          </Button>
        </div>
      </motion.div>

      <!-- Loading -->
      <div v-if="loading" class="grid gap-4">
        <div v-for="i in 3" :key="i" class="card">
          <div class="flex items-center justify-between">
            <div class="flex-1 space-y-2">
              <Skeleton width="12rem" height="1.25rem" />
              <Skeleton width="24rem" height="1rem" />
              <Skeleton width="8rem" height="0.75rem" />
            </div>
            <div class="flex gap-2">
              <Skeleton width="5rem" height="2rem" />
              <Skeleton width="5rem" height="2rem" />
            </div>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <motion.div
        v-else-if="scripts.length === 0"
        initial="{ opacity: 0, scale: 0.95 }"
        animate="{ opacity: 1, scale: 1 }"
        class="card text-center py-12"
      >
        <div class="w-16 h-16 bg-blue-100 dark:bg-blue-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <FileText :size="32" class="text-blue-600 dark:text-blue-400" />
        </div>
        <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-0 mb-2">No scripts yet</h3>
        <p class="text-surface-500 mb-6 max-w-sm mx-auto">Create a call script with pre-recorded audio or text-to-speech to get started.</p>
        <div class="flex justify-center gap-3">
          <Button label="Import from File" severity="secondary" outlined @click="showImport = true">
            <template #icon><Upload :size="16" /></template>
          </Button>
          <Button label="New Script" @click="showCreate = true">
            <template #icon><Plus :size="16" /></template>
          </Button>
        </div>
      </motion.div>

      <!-- Scripts list -->
      <div v-else class="space-y-3">
        <motion.div
          v-for="(script, idx) in scripts"
          :key="script.id"
          initial="{ opacity: 0, y: 10 }"
          animate="{ opacity: 1, y: 0 }"
          transition="{ duration: 0.2, delay: idx * 0.05 }"
          class="card-hover flex items-center justify-between"
        >
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <h3 class="font-semibold text-surface-900 dark:text-surface-0">{{ script.name }}</h3>
              <Tag v-if="script.is_active" value="Active" severity="success" />
              <Tag v-if="script.audio_type === 'uploaded'" value="Audio Uploaded" severity="info" />
              <Tag v-else value="TTS" severity="secondary" />
            </div>
            <p class="text-sm text-surface-500 mt-1 truncate">{{ script.content.substring(0, 120) }}...</p>
            <div class="flex items-center gap-4 mt-2 text-xs text-surface-400">
              <span class="flex items-center gap-1"><Globe :size="12" /> {{ script.language }}</span>
              <span>v{{ script.version }}</span>
              <span>{{ new Date(script.updated_at).toLocaleDateString() }}</span>
            </div>
          </div>
          <div class="flex items-center gap-2 ml-4">
            <Button v-if="!script.is_active" label="Activate" size="small" severity="success" @click="activate(script.id)" />
            <Button label="Audio" size="small" severity="secondary" outlined @click="triggerAudioInput(script.id)">
              <template #icon><Upload :size="14" /></template>
            </Button>
            <input :id="`audio-input-${script.id}`" type="file" accept=".mp3,.wav,.ogg" class="hidden" @change="handleUpload($event, script.id)" />
            <Button size="small" severity="secondary" text @click="openEdit(script)">
              <template #icon><Pencil :size="14" /></template>
            </Button>
            <Button size="small" severity="danger" text @click="handleDelete(script)">
              <template #icon><Trash2 :size="14" /></template>
            </Button>
          </div>
        </motion.div>
      </div>

      <!-- Create Modal -->
      <Dialog :visible="showCreate" modal header="New Script" :style="{ width: '32rem' }" @update:visible="showCreate = $event">
        <form @submit.prevent="handleCreate" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">Script Name</label>
            <InputText v-model="createForm.name" required class="w-full" placeholder="e.g. Welcome Call" />
          </div>
          <div>
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">Audio Source</label>
            <AudioSourceToggle v-model="createForm.audio_type" />
          </div>
          <div v-if="createForm.audio_type === 'tts'">
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">Language</label>
            <Select v-model="createForm.language" :options="languageOptions" option-label="label" option-value="value" class="w-full" />
          </div>
          <div>
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">Script Content</label>
            <Textarea v-model="createForm.content" rows="5" required class="w-full" placeholder="Use {customer_name}, {business_name} for variables..." />
          </div>
          <div class="flex justify-end gap-2 pt-2">
            <Button type="button" label="Cancel" severity="secondary" text @click="showCreate = false" />
            <Button type="submit" label="Create Script" />
          </div>
        </form>
      </Dialog>

      <!-- Edit Modal -->
      <Dialog :visible="showEdit" modal header="Edit Script" :style="{ width: '32rem' }" @update:visible="showEdit = $event">
        <form @submit.prevent="handleEdit" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">Script Name</label>
            <InputText v-model="editForm.name" class="w-full" />
          </div>
          <div>
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">Audio Source</label>
            <AudioSourceToggle v-model="editForm.audio_type" />
          </div>
          <div v-if="editForm.audio_type === 'tts'">
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">Language</label>
            <Select v-model="editForm.language" :options="languageOptions" option-label="label" option-value="value" class="w-full" />
          </div>
          <div>
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">Script Content</label>
            <Textarea v-model="editForm.content" rows="5" class="w-full" />
          </div>
          <div class="flex justify-end gap-2 pt-2">
            <Button type="button" label="Cancel" severity="secondary" text @click="showEdit = false" />
            <Button type="submit" label="Save Changes" />
          </div>
        </form>
      </Dialog>

      <!-- Import Modal -->
      <ScriptImportModal v-if="showImport" @close="showImport = false" @imported="onImported" />
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, reactive, onMounted, h } from 'vue'
import { storeToRefs } from 'pinia'
import { motion } from 'motion-v'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import AppLayout from '@/components/layout/AppLayout.vue'
import ScriptImportModal from './ScriptImportModal.vue'
import { useScriptsStore } from '@/stores/scripts'
import { Plus, Upload, FileText, Globe, Pencil, Trash2, Volume2 } from '@lucide/vue'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import Skeleton from 'primevue/skeleton'

const scriptsStore = useScriptsStore()
const { scripts, loading } = storeToRefs(scriptsStore)
const confirm = useConfirm()
const toast = useToast()

const showCreate = ref(false)
const showEdit = ref(false)
const showImport = ref(false)
const editScript = ref(null)

const languageOptions = [
  { label: 'Hindi', value: 'hi-IN' },
  { label: 'English (India)', value: 'en-IN' },
  { label: 'Tamil', value: 'ta-IN' },
  { label: 'Telugu', value: 'te-IN' },
  { label: 'Bengali', value: 'bn-IN' },
  { label: 'Marathi', value: 'mr-IN' },
]

const createForm = reactive({ name: '', content: '', language: 'hi-IN', audio_type: 'tts' })
const editForm = reactive({ name: '', content: '', language: 'hi-IN', audio_type: 'tts' })

// Simple inline component for the "Text-to-Speech / Pre-recorded" toggle used in both modals
const AudioSourceToggle = {
  props: { modelValue: String },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const options = [
      { value: 'tts', label: 'Text-to-Speech', icon: Volume2 },
      { value: 'uploaded', label: 'Pre-recorded', icon: Upload },
    ]
    return () => h('div', { class: 'flex gap-3' }, options.map(opt =>
      h('label', {
        key: opt.value,
        class: [
          'flex-1 flex items-center gap-2 p-3 rounded-xl border cursor-pointer transition-all',
          props.modelValue === opt.value
            ? 'border-primary-500 bg-primary-50 dark:bg-primary-500/10'
            : 'border-surface-200 dark:border-surface-600 hover:border-surface-300',
        ],
        onClick: () => emit('update:modelValue', opt.value),
      }, [
        h(opt.icon, { size: 18, class: props.modelValue === opt.value ? 'text-primary-600' : 'text-surface-400' }),
        h('span', {
          class: ['text-sm font-medium', props.modelValue === opt.value ? 'text-primary-700 dark:text-primary-400' : 'text-surface-600 dark:text-surface-300'],
        }, opt.label),
      ])
    ))
  },
}

onMounted(() => scriptsStore.fetchScripts())

async function handleCreate() {
  await scriptsStore.createScript(createForm)
  showCreate.value = false
  Object.assign(createForm, { name: '', content: '', language: 'hi-IN', audio_type: 'tts' })
  toast.add({ severity: 'success', summary: 'Script created', life: 3000 })
}

function openEdit(script) {
  editScript.value = script
  Object.assign(editForm, { name: script.name, content: script.content, language: script.language, audio_type: script.audio_type })
  showEdit.value = true
}

async function handleEdit() {
  await scriptsStore.updateScript(editScript.value.id, editForm)
  showEdit.value = false
  toast.add({ severity: 'success', summary: 'Script updated', life: 3000 })
}

async function activate(id) {
  await scriptsStore.activateScript(id)
  toast.add({ severity: 'success', summary: 'Script activated', life: 3000 })
}

function handleDelete(script) {
  confirm.require({
    message: `Delete "${script.name}"? This cannot be undone.`,
    header: 'Delete script',
    acceptProps: { severity: 'danger', label: 'Delete' },
    rejectProps: { severity: 'secondary', outlined: true, label: 'Cancel' },
    accept: async () => {
      await scriptsStore.deleteScript(script.id)
      toast.add({ severity: 'success', summary: 'Script deleted', life: 3000 })
    },
  })
}

function triggerAudioInput(scriptId) {
  document.getElementById(`audio-input-${scriptId}`)?.click()
}

async function handleUpload(event, scriptId) {
  const file = event.target.files[0]
  if (file) {
    await scriptsStore.uploadAudio(scriptId, file)
    toast.add({ severity: 'success', summary: 'Audio uploaded', life: 3000 })
  }
}

function onImported() {
  scriptsStore.fetchScripts()
}
</script>
