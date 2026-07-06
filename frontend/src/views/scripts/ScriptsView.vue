<template>
  <AppLayout>
    <div class="space-y-6">
      <motion.div
        initial="{ opacity: 0, y: -10 }"
        animate="{ opacity: 1, y: 0 }"
        class="flex justify-between items-center"
      >
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Scripts</h1>
          <p class="text-sm text-gray-500 mt-1">Manage your call scripts and audio files</p>
        </div>
        <div class="flex gap-2">
          <button @click="showImport = true" class="btn-secondary text-sm flex items-center gap-2">
            <Upload :size="16" />
            Import File
          </button>
          <button @click="showCreate = true" class="btn-primary text-sm flex items-center gap-2">
            <Plus :size="16" />
            New Script
          </button>
        </div>
      </motion.div>

      <!-- Loading -->
      <div v-if="loading" class="grid gap-4">
        <div v-for="i in 3" :key="i" class="card">
          <div class="flex items-center justify-between">
            <div class="flex-1">
              <div class="skeleton h-5 w-48 mb-2"></div>
              <div class="skeleton h-4 w-96 mb-2"></div>
              <div class="skeleton h-3 w-32"></div>
            </div>
            <div class="flex gap-2">
              <div class="skeleton h-8 w-20"></div>
              <div class="skeleton h-8 w-20"></div>
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
        <div class="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <FileText :size="32" class="text-blue-600" />
        </div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">No scripts yet</h3>
        <p class="text-gray-500 mb-6 max-w-sm mx-auto">Create a call script with pre-recorded audio or text-to-speech to get started.</p>
        <div class="flex justify-center gap-3">
          <button @click="showImport = true" class="btn-secondary flex items-center gap-2">
            <Upload :size="16" />
            Import from File
          </button>
          <button @click="showCreate = true" class="btn-primary flex items-center gap-2">
            <Plus :size="16" />
            New Script
          </button>
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
              <h3 class="font-semibold text-gray-900">{{ script.name }}</h3>
              <span v-if="script.is_active" class="badge-success">Active</span>
              <span v-if="script.audio_type === 'uploaded'" class="badge-info">Audio Uploaded</span>
              <span v-else class="badge-neutral">TTS</span>
            </div>
            <p class="text-sm text-gray-500 mt-1 truncate">{{ script.content.substring(0, 120) }}...</p>
            <div class="flex items-center gap-4 mt-2 text-xs text-gray-400">
              <span class="flex items-center gap-1"><Globe :size="12" /> {{ script.language }}</span>
              <span>v{{ script.version }}</span>
              <span>{{ new Date(script.updated_at).toLocaleDateString() }}</span>
            </div>
          </div>
          <div class="flex items-center gap-2 ml-4">
            <button v-if="!script.is_active" @click="activate(script.id)" class="btn-success text-xs px-3 py-1.5">Activate</button>
            <label class="btn-secondary text-xs px-3 py-1.5 cursor-pointer flex items-center gap-1">
              <Upload :size="14" />
              Audio
              <input type="file" accept=".mp3,.wav,.ogg" class="hidden" @change="handleUpload($event, script.id)" />
            </label>
            <button @click="editScript = script; showEdit = true" class="btn-ghost text-xs px-2 py-1.5">
              <Pencil :size="14" />
            </button>
            <button @click="handleDelete(script.id)" class="btn-ghost text-xs px-2 py-1.5 text-red-500 hover:text-red-700 hover:bg-red-50">
              <Trash2 :size="14" />
            </button>
          </div>
        </motion.div>
      </div>

      <!-- Create Modal -->
      <transition name="modal">
        <div v-if="showCreate" class="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <motion.div
            initial="{ opacity: 0, scale: 0.95 }"
            animate="{ opacity: 1, scale: 1 }"
            class="card w-full max-w-lg"
          >
            <h2 class="text-xl font-bold text-gray-900 mb-4">New Script</h2>
            <form @submit.prevent="handleCreate" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Script Name</label>
                <input v-model="createForm.name" type="text" required class="input-field" placeholder="e.g. Welcome Call" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Audio Source</label>
                <div class="flex gap-3">
                  <label class="flex-1 flex items-center gap-2 p-3 rounded-xl border cursor-pointer transition-all" :class="createForm.audio_type === 'tts' ? 'border-brand-500 bg-brand-50' : 'border-gray-200 hover:border-gray-300'">
                    <input type="radio" v-model="createForm.audio_type" value="tts" class="sr-only" />
                    <Volume2 :size="18" :class="createForm.audio_type === 'tts' ? 'text-brand-600' : 'text-gray-400'" />
                    <span class="text-sm font-medium" :class="createForm.audio_type === 'tts' ? 'text-brand-700' : 'text-gray-600'">Text-to-Speech</span>
                  </label>
                  <label class="flex-1 flex items-center gap-2 p-3 rounded-xl border cursor-pointer transition-all" :class="createForm.audio_type === 'uploaded' ? 'border-brand-500 bg-brand-50' : 'border-gray-200 hover:border-gray-300'">
                    <input type="radio" v-model="createForm.audio_type" value="uploaded" class="sr-only" />
                    <Upload :size="18" :class="createForm.audio_type === 'uploaded' ? 'text-brand-600' : 'text-gray-400'" />
                    <span class="text-sm font-medium" :class="createForm.audio_type === 'uploaded' ? 'text-brand-700' : 'text-gray-600'">Pre-recorded</span>
                  </label>
                </div>
              </div>
              <div v-if="createForm.audio_type === 'tts'">
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Language</label>
                <select v-model="createForm.language" class="input-field">
                  <option value="hi-IN">Hindi</option>
                  <option value="en-IN">English (India)</option>
                  <option value="ta-IN">Tamil</option>
                  <option value="te-IN">Telugu</option>
                  <option value="bn-IN">Bengali</option>
                  <option value="mr-IN">Marathi</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Script Content</label>
                <textarea v-model="createForm.content" rows="5" required class="input-field" placeholder="Use {customer_name}, {business_name} for variables..."></textarea>
              </div>
              <div class="flex justify-end gap-2 pt-2">
                <button type="button" @click="showCreate = false" class="btn-secondary">Cancel</button>
                <button type="submit" class="btn-primary">Create Script</button>
              </div>
            </form>
          </motion.div>
        </div>
      </transition>

      <!-- Edit Modal -->
      <transition name="modal">
        <div v-if="showEdit" class="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <motion.div
            initial="{ opacity: 0, scale: 0.95 }"
            animate="{ opacity: 1, scale: 1 }"
            class="card w-full max-w-lg"
          >
            <h2 class="text-xl font-bold text-gray-900 mb-4">Edit Script</h2>
            <form @submit.prevent="handleEdit" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Script Name</label>
                <input v-model="editForm.name" type="text" class="input-field" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Audio Source</label>
                <div class="flex gap-3">
                  <label class="flex-1 flex items-center gap-2 p-3 rounded-xl border cursor-pointer transition-all" :class="editForm.audio_type === 'tts' ? 'border-brand-500 bg-brand-50' : 'border-gray-200 hover:border-gray-300'">
                    <input type="radio" v-model="editForm.audio_type" value="tts" class="sr-only" />
                    <Volume2 :size="18" :class="editForm.audio_type === 'tts' ? 'text-brand-600' : 'text-gray-400'" />
                    <span class="text-sm font-medium" :class="editForm.audio_type === 'tts' ? 'text-brand-700' : 'text-gray-600'">Text-to-Speech</span>
                  </label>
                  <label class="flex-1 flex items-center gap-2 p-3 rounded-xl border cursor-pointer transition-all" :class="editForm.audio_type === 'uploaded' ? 'border-brand-500 bg-brand-50' : 'border-gray-200 hover:border-gray-300'">
                    <input type="radio" v-model="editForm.audio_type" value="uploaded" class="sr-only" />
                    <Upload :size="18" :class="editForm.audio_type === 'uploaded' ? 'text-brand-600' : 'text-gray-400'" />
                    <span class="text-sm font-medium" :class="editForm.audio_type === 'uploaded' ? 'text-brand-700' : 'text-gray-600'">Pre-recorded</span>
                  </label>
                </div>
              </div>
              <div v-if="editForm.audio_type === 'tts'">
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Language</label>
                <select v-model="editForm.language" class="input-field">
                  <option value="hi-IN">Hindi</option>
                  <option value="en-IN">English (India)</option>
                  <option value="ta-IN">Tamil</option>
                  <option value="te-IN">Telugu</option>
                  <option value="bn-IN">Bengali</option>
                  <option value="mr-IN">Marathi</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Script Content</label>
                <textarea v-model="editForm.content" rows="5" class="input-field"></textarea>
              </div>
              <div class="flex justify-end gap-2 pt-2">
                <button type="button" @click="showEdit = false" class="btn-secondary">Cancel</button>
                <button type="submit" class="btn-primary">Save Changes</button>
              </div>
            </form>
          </motion.div>
        </div>
      </transition>

      <!-- Import Modal -->
      <ScriptImportModal v-if="showImport" @close="showImport = false" @imported="onImported" />
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { motion } from 'motion-v'
import AppLayout from '@/components/layout/AppLayout.vue'
import ScriptImportModal from './ScriptImportModal.vue'
import { useScriptsStore } from '@/stores/scripts'
import { Plus, Upload, FileText, Globe, Pencil, Trash2, Volume2 } from '@lucide/vue'

const scriptsStore = useScriptsStore()
const { scripts, loading } = scriptsStore

const showCreate = ref(false)
const showEdit = ref(false)
const showImport = ref(false)
const editScript = ref(null)

const createForm = reactive({ name: '', content: '', language: 'hi-IN', audio_type: 'tts' })
const editForm = reactive({ name: '', content: '', language: 'hi-IN', audio_type: 'tts' })

onMounted(() => scriptsStore.fetchScripts())

async function handleCreate() {
  await scriptsStore.createScript(createForm)
  showCreate.value = false
  Object.assign(createForm, { name: '', content: '', language: 'hi-IN', audio_type: 'tts' })
}

async function handleEdit() {
  await scriptsStore.updateScript(editScript.value.id, editForm)
  showEdit.value = false
}

async function activate(id) {
  await scriptsStore.activateScript(id)
}

async function handleDelete(id) {
  if (confirm('Are you sure you want to delete this script?')) {
    await scriptsStore.deleteScript(id)
  }
}

async function handleUpload(event, scriptId) {
  const file = event.target.files[0]
  if (file) {
    await scriptsStore.uploadAudio(scriptId, file)
    alert('Audio uploaded successfully!')
  }
}

function onImported() {
  scriptsStore.fetchScripts()
}
</script>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: all 0.25s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>
