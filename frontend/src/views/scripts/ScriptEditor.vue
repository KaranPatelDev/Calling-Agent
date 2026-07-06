<template>
  <AppLayout>
    <div class="space-y-6">
      <div class="flex justify-between items-center">
        <div class="flex items-center gap-2">
          <router-link to="/scripts" class="text-gray-500 hover:text-gray-700">Scripts</router-link>
          <span class="text-gray-400">/</span>
          <h1 class="text-2xl font-bold">{{ isEdit ? 'Edit Script' : 'New Script' }}</h1>
        </div>
      </div>

      <form @submit.prevent="handleSave" class="card space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Script Name</label>
          <input v-model="form.name" type="text" required class="input-field" placeholder="e.g. Summer Sale Pitch" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Audio Source</label>
          <div class="flex gap-4">
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="radio" v-model="form.audio_type" value="tts" class="text-blue-600" />
              <span>Text-to-Speech</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="radio" v-model="form.audio_type" value="uploaded" class="text-blue-600" />
              <span>Pre-recorded Audio</span>
            </label>
          </div>
        </div>

        <div v-if="form.audio_type === 'tts'" class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Language</label>
            <select v-model="form.language" class="input-field">
              <option value="hi-IN">Hindi</option>
              <option value="en-IN">English (India)</option>
              <option value="ta-IN">Tamil</option>
              <option value="te-IN">Telugu</option>
              <option value="bn-IN">Bengali</option>
              <option value="mr-IN">Marathi</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Voice</label>
            <select v-model="form.tts_voice" class="input-field">
              <option value="hi-IN-Wavenet-A">Wavenet A (Female)</option>
              <option value="hi-IN-Wavenet-B">Wavenet B (Male)</option>
              <option value="hi-IN-Wavenet-C">Wavenet C (Female)</option>
              <option value="hi-IN-Wavenet-D">Wavenet D (Male)</option>
            </select>
          </div>
        </div>

        <div v-if="form.audio_type === 'uploaded'">
          <label class="block text-sm font-medium text-gray-700 mb-1">Upload Audio File</label>
          <div
            class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors cursor-pointer"
            @dragover.prevent
            @drop.prevent="handleDrop"
            @click="$refs.fileInput.click()"
          >
            <input ref="fileInput" type="file" accept=".mp3,.wav,.ogg" class="hidden" @change="handleFileSelect" />
            <div v-if="uploading" class="text-blue-600">Uploading...</div>
            <div v-else-if="uploadedFile" class="text-green-600">
              <p class="font-medium">{{ uploadedFile.name }}</p>
              <p class="text-sm">{{ (uploadedFile.size / 1024).toFixed(1) }} KB</p>
            </div>
            <div v-else>
              <p class="text-gray-500">Drag & drop audio file here or click to browse</p>
              <p class="text-sm text-gray-400 mt-1">Supported: MP3, WAV, OGG (max 10MB)</p>
            </div>
          </div>
          <audio v-if="audioPreviewUrl" :src="audioPreviewUrl" controls class="mt-3 w-full" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Script Content</label>
          <textarea
            v-model="form.content"
            rows="6"
            required
            class="input-field"
            placeholder="Use {customer_name}, {business_name} for variables..."
          ></textarea>
          <p class="text-xs text-gray-400 mt-1">Use curly braces for variables: {'{customer_name}'}, {'{business_name}'}</p>
        </div>

        <div class="flex justify-end gap-2">
          <router-link to="/scripts" class="btn-secondary">Cancel</router-link>
          <button type="submit" class="btn-primary" :disabled="saving">
            {{ saving ? 'Saving...' : (isEdit ? 'Save Changes' : 'Create Script') }}
          </button>
        </div>
      </form>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useScriptsStore } from '@/stores/scripts'
import api from '@/api/client'

const route = useRoute()
const router = useRouter()
const scriptsStore = useScriptsStore()

const isEdit = computed(() => !!route.params.id)
const saving = ref(false)
const uploading = ref(false)
const uploadedFile = ref(null)
const audioPreviewUrl = ref('')

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
    alert('File too large. Maximum 10MB.')
    return
  }
  uploadedFile.value = file
  audioPreviewUrl.value = URL.createObjectURL(file)
}

async function handleSave() {
  saving.value = true
  try {
    if (isEdit.value) {
      const updated = await scriptsStore.updateScript(route.params.id, form)
      if (uploadedFile.value) {
        await scriptsStore.uploadAudio(route.params.id, uploadedFile.value)
      }
    } else {
      const created = await scriptsStore.createScript(form)
      if (uploadedFile.value) {
        await scriptsStore.uploadAudio(created.id, uploadedFile.value)
      }
    }
    router.push('/scripts')
  } catch (e) {
    alert(e.response?.data?.detail || 'Failed to save script')
  } finally {
    saving.value = false
  }
}
</script>
