<template>
  <AppLayout>
    <div class="space-y-6">
      <div class="flex justify-between items-center">
        <div class="flex items-center gap-2">
          <router-link to="/scripts" class="text-surface-500 hover:text-surface-700 dark:hover:text-surface-300">Scripts</router-link>
          <span class="text-surface-400">/</span>
          <h1 class="text-2xl font-bold text-surface-900 dark:text-surface-0">{{ isEdit ? 'Edit Script' : 'New Script' }}</h1>
        </div>
      </div>

      <form @submit.prevent="handleSave" class="card space-y-6">
        <div>
          <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1">Script Name</label>
          <InputText v-model="form.name" required class="w-full" placeholder="e.g. Summer Sale Pitch" />
        </div>

        <div>
          <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-2">Audio Source</label>
          <div class="flex gap-4">
            <div class="flex items-center gap-2">
              <RadioButton v-model="form.audio_type" input-id="audio-tts" value="tts" />
              <label for="audio-tts" class="cursor-pointer">Text-to-Speech</label>
            </div>
            <div class="flex items-center gap-2">
              <RadioButton v-model="form.audio_type" input-id="audio-uploaded" value="uploaded" />
              <label for="audio-uploaded" class="cursor-pointer">Pre-recorded Audio</label>
            </div>
          </div>
        </div>

        <div v-if="form.audio_type === 'tts'" class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1">Language</label>
            <Select v-model="form.language" :options="languageOptions" option-label="label" option-value="value" class="w-full" />
          </div>
          <div>
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1">Voice</label>
            <Select v-model="form.tts_voice" :options="voiceOptions" option-label="label" option-value="value" class="w-full" />
          </div>
        </div>

        <div v-if="form.audio_type === 'uploaded'">
          <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1">Upload Audio File</label>
          <div
            class="border-2 border-dashed border-surface-300 dark:border-surface-600 rounded-lg p-6 text-center hover:border-primary-400 transition-colors cursor-pointer"
            @dragover.prevent
            @drop.prevent="handleDrop"
            @click="$refs.fileInput.click()"
          >
            <input ref="fileInput" type="file" accept=".mp3,.wav,.ogg" class="hidden" @change="handleFileSelect" />
            <div v-if="uploading" class="text-primary-600">Uploading...</div>
            <div v-else-if="uploadedFile" class="text-emerald-600 dark:text-emerald-400">
              <p class="font-medium">{{ uploadedFile.name }}</p>
              <p class="text-sm">{{ (uploadedFile.size / 1024).toFixed(1) }} KB</p>
            </div>
            <div v-else>
              <p class="text-surface-500">Drag & drop audio file here or click to browse</p>
              <p class="text-sm text-surface-400 mt-1">Supported: MP3, WAV, OGG (max 10MB)</p>
            </div>
          </div>
          <audio v-if="audioPreviewUrl" :src="audioPreviewUrl" controls class="mt-3 w-full" />
        </div>

        <div>
          <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1">Script Content</label>
          <Textarea
            v-model="form.content"
            rows="6"
            required
            class="w-full"
            placeholder="Use {customer_name}, {business_name} for variables..."
          />
          <p class="text-xs text-surface-400 mt-1">Use curly braces for variables: {'{customer_name}'}, {'{business_name}'}</p>
        </div>

        <Message v-if="error" severity="error" :closable="false">{{ error }}</Message>

        <div class="flex justify-end gap-2">
          <Button as="router-link" to="/scripts" label="Cancel" severity="secondary" text />
          <Button type="submit" :loading="saving" :label="isEdit ? 'Save Changes' : 'Create Script'" />
        </div>
      </form>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useScriptsStore } from '@/stores/scripts'
import api from '@/api/client'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Select from 'primevue/select'
import RadioButton from 'primevue/radiobutton'
import Button from 'primevue/button'
import Message from 'primevue/message'

const route = useRoute()
const router = useRouter()
const scriptsStore = useScriptsStore()
const toast = useToast()

const isEdit = computed(() => !!route.params.id)
const saving = ref(false)
const uploading = ref(false)
const uploadedFile = ref(null)
const audioPreviewUrl = ref('')
const error = ref('')

const languageOptions = [
  { label: 'Hindi', value: 'hi-IN' },
  { label: 'English (India)', value: 'en-IN' },
  { label: 'Tamil', value: 'ta-IN' },
  { label: 'Telugu', value: 'te-IN' },
  { label: 'Bengali', value: 'bn-IN' },
  { label: 'Marathi', value: 'mr-IN' },
]

const voiceOptions = [
  { label: 'Wavenet A (Female)', value: 'hi-IN-Wavenet-A' },
  { label: 'Wavenet B (Male)', value: 'hi-IN-Wavenet-B' },
  { label: 'Wavenet C (Female)', value: 'hi-IN-Wavenet-C' },
  { label: 'Wavenet D (Male)', value: 'hi-IN-Wavenet-D' },
]

const form = reactive({
  name: '',
  content: '',
  language: 'hi-IN',
  tts_voice: 'hi-IN-Wavenet-A',
  audio_type: 'tts',
})

onMounted(async () => {
  if (isEdit.value) {
    try {
      const res = await api.get(`/scripts/${route.params.id}`)
      Object.assign(form, {
        name: res.data.name,
        content: res.data.content,
        language: res.data.language || 'hi-IN',
        tts_voice: res.data.tts_voice || 'hi-IN-Wavenet-A',
        audio_type: res.data.audio_type || 'tts',
      })
      if (res.data.audio_file_path) {
        audioPreviewUrl.value = `/uploads/${res.data.audio_file_path}`
      }
    } catch {
      router.push('/scripts')
    }
  }
})

function handleFileSelect(e) {
  const file = e.target.files[0]
  if (file) uploadFile(file)
}

function handleDrop(e) {
  const file = e.dataTransfer.files[0]
  if (file) uploadFile(file)
}

async function uploadFile(file) {
  if (file.size > 10 * 1024 * 1024) {
    error.value = 'File too large. Maximum 10MB.'
    return
  }
  uploadedFile.value = file
  audioPreviewUrl.value = URL.createObjectURL(file)
}

async function handleSave() {
  saving.value = true
  error.value = ''
  try {
    if (isEdit.value) {
      await scriptsStore.updateScript(route.params.id, form)
      if (uploadedFile.value) {
        await scriptsStore.uploadAudio(route.params.id, uploadedFile.value)
      }
    } else {
      const created = await scriptsStore.createScript(form)
      if (uploadedFile.value) {
        await scriptsStore.uploadAudio(created.id, uploadedFile.value)
      }
    }
    toast.add({ severity: 'success', summary: isEdit.value ? 'Script updated' : 'Script created', life: 3000 })
    router.push('/scripts')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to save script'
  } finally {
    saving.value = false
  }
}
</script>
