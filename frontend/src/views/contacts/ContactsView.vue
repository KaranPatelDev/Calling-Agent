<template>
  <AppLayout>
    <div class="space-y-6">
      <motion.div
        initial="{ opacity: 0, y: -10 }"
        animate="{ opacity: 1, y: 0 }"
        class="flex justify-between items-center"
      >
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Contact Lists</h1>
          <p class="text-sm text-gray-500 mt-1">Manage your contact lists and phone numbers</p>
        </div>
        <button @click="showCreate = true" class="btn-primary text-sm flex items-center gap-2">
          <Plus :size="16" />
          New List
        </button>
      </motion.div>

      <!-- Loading -->
      <div v-if="loading" class="grid gap-4">
        <div v-for="i in 3" :key="i" class="card">
          <div class="flex items-center justify-between">
            <div class="flex-1">
              <div class="skeleton h-5 w-40 mb-2"></div>
              <div class="skeleton h-4 w-64 mb-2"></div>
              <div class="skeleton h-3 w-24"></div>
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
        v-else-if="lists.length === 0"
        initial="{ opacity: 0, scale: 0.95 }"
        animate="{ opacity: 1, scale: 1 }"
        class="card text-center py-12"
      >
        <div class="w-16 h-16 bg-purple-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <Users :size="32" class="text-purple-600" />
        </div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">No contact lists yet</h3>
        <p class="text-gray-500 mb-6 max-w-sm mx-auto">Create a contact list and add phone numbers to start calling.</p>
        <button @click="showCreate = true" class="btn-primary flex items-center gap-2 mx-auto">
          <Plus :size="16" />
          New List
        </button>
      </motion.div>

      <!-- Lists -->
      <div v-else class="space-y-3">
        <motion.div
          v-for="(list, idx) in lists"
          :key="list.id"
          initial="{ opacity: 0, y: 10 }"
          animate="{ opacity: 1, y: 0 }"
          transition="{ duration: 0.2, delay: idx * 0.05 }"
          class="card-hover flex items-center justify-between"
        >
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-100 to-purple-50 flex items-center justify-center">
              <Users :size="20" class="text-purple-600" />
            </div>
            <div>
              <h3 class="font-semibold text-gray-900">{{ list.name }}</h3>
              <p class="text-sm text-gray-500">{{ list.description || 'No description' }}</p>
              <span class="text-xs text-gray-400">{{ list.contact_count }} contacts</span>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button @click="importList = list; showImport = true" class="btn-secondary text-xs px-3 py-1.5 flex items-center gap-1">
              <Upload :size="14" />
              Import
            </button>
            <button @click="selectedList = list; showDetail = true" class="btn-ghost text-xs px-3 py-1.5 flex items-center gap-1">
              <Eye :size="14" />
              View
            </button>
            <button @click="handleDelete(list.id)" class="btn-ghost text-xs px-2 py-1.5 text-red-500 hover:text-red-700 hover:bg-red-50">
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
            class="card w-full max-w-md"
          >
            <h2 class="text-xl font-bold text-gray-900 mb-4">New Contact List</h2>
            <form @submit.prevent="handleCreate" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">List Name</label>
                <input v-model="createForm.name" type="text" required class="input-field" placeholder="e.g. Mumbai Leads" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Description</label>
                <textarea v-model="createForm.description" rows="2" class="input-field" placeholder="Optional description"></textarea>
              </div>
              <div class="flex justify-end gap-2 pt-2">
                <button type="button" @click="showCreate = false" class="btn-secondary">Cancel</button>
                <button type="submit" class="btn-primary">Create</button>
              </div>
            </form>
          </motion.div>
        </div>
      </transition>

      <!-- Detail Modal -->
      <transition name="modal">
        <div v-if="showDetail && selectedList" class="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <motion.div
            initial="{ opacity: 0, scale: 0.95 }"
            animate="{ opacity: 1, scale: 1 }"
            class="card w-full max-w-2xl max-h-[80vh] overflow-y-auto"
          >
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-xl font-bold text-gray-900">{{ selectedList.name }}</h2>
              <button @click="showDetail = false" class="p-2 rounded-lg hover:bg-gray-100 transition-colors">
                <X :size="20" />
              </button>
            </div>
            <div v-if="detailLoading" class="space-y-3">
              <div v-for="i in 5" :key="i" class="skeleton h-10 w-full"></div>
            </div>
            <div v-else-if="detailContacts.length === 0" class="text-center py-8 text-gray-500">No contacts in this list</div>
            <table v-else class="w-full text-sm">
              <thead class="table-header">
                <tr>
                  <th class="px-4 py-2">Phone</th>
                  <th class="px-4 py-2">Name</th>
                  <th class="px-4 py-2">Email</th>
                  <th class="px-4 py-2">DND</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-50">
                <tr v-for="c in detailContacts" :key="c.id" class="hover:bg-gray-50/50">
                  <td class="px-4 py-2.5 font-medium">{{ c.phone }}</td>
                  <td class="px-4 py-2.5">{{ c.name || '-' }}</td>
                  <td class="px-4 py-2.5 text-gray-500">{{ c.email || '-' }}</td>
                  <td class="px-4 py-2.5">
                    <span v-if="c.dnd_registered" class="badge-danger">DND</span>
                    <span v-else class="badge-success">OK</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </motion.div>
        </div>
      </transition>

      <!-- Import Modal -->
      <ContactImportModal v-if="showImport && importList" :listId="importList.id" @close="showImport = false; importList = null" @imported="onImported" />
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { motion } from 'motion-v'
import AppLayout from '@/components/layout/AppLayout.vue'
import ContactImportModal from './ContactImportModal.vue'
import { useContactsStore } from '@/stores/contacts'
import { Plus, Upload, Users, Eye, Trash2, X } from '@lucide/vue'

const contactsStore = useContactsStore()
const { lists, loading } = contactsStore

const showCreate = ref(false)
const showDetail = ref(false)
const showImport = ref(false)
const selectedList = ref(null)
const importList = ref(null)
const detailContacts = ref([])
const detailLoading = ref(false)
const createForm = reactive({ name: '', description: '' })

onMounted(() => contactsStore.fetchLists())

async function handleCreate() {
  await contactsStore.createList(createForm)
  showCreate.value = false
  Object.assign(createForm, { name: '', description: '' })
}

async function handleDelete(id) {
  if (confirm('Delete this contact list and all its contacts?')) {
    await contactsStore.deleteList(id)
  }
}

function onImported() {
  contactsStore.fetchLists()
}
</script>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: all 0.25s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>
