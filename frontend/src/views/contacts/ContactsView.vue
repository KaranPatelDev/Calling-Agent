<template>
  <AppLayout>
    <div class="space-y-6">
      <motion.div
        initial="{ opacity: 0, y: -10 }"
        animate="{ opacity: 1, y: 0 }"
        class="flex justify-between items-center"
      >
        <div>
          <h1 class="text-2xl font-bold text-surface-900 dark:text-surface-0">Contact Lists</h1>
          <p class="text-sm text-surface-500 mt-1">Manage your contact lists and phone numbers</p>
        </div>
        <Button label="New List" @click="showCreate = true">
          <template #icon><Plus :size="16" /></template>
        </Button>
      </motion.div>

      <!-- Loading -->
      <div v-if="loading" class="grid gap-4">
        <div v-for="i in 3" :key="i" class="card">
          <div class="flex items-center justify-between">
            <div class="flex-1 space-y-2">
              <Skeleton width="10rem" height="1.25rem" />
              <Skeleton width="16rem" height="1rem" />
              <Skeleton width="6rem" height="0.75rem" />
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
        v-else-if="lists.length === 0"
        initial="{ opacity: 0, scale: 0.95 }"
        animate="{ opacity: 1, scale: 1 }"
        class="card text-center py-12"
      >
        <div class="w-16 h-16 bg-purple-100 dark:bg-purple-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <Users :size="32" class="text-purple-600 dark:text-purple-400" />
        </div>
        <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-0 mb-2">No contact lists yet</h3>
        <p class="text-surface-500 mb-6 max-w-sm mx-auto">Create a contact list and add phone numbers to start calling.</p>
        <Button label="New List" @click="showCreate = true">
          <template #icon><Plus :size="16" /></template>
        </Button>
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
            <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-100 to-purple-50 dark:from-purple-500/20 dark:to-purple-500/10 flex items-center justify-center">
              <Users :size="20" class="text-purple-600 dark:text-purple-400" />
            </div>
            <div>
              <h3 class="font-semibold text-surface-900 dark:text-surface-0">{{ list.name }}</h3>
              <p class="text-sm text-surface-500">{{ list.description || 'No description' }}</p>
              <span class="text-xs text-surface-400">{{ list.contact_count }} contacts</span>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <Button label="Import" size="small" severity="secondary" outlined @click="importList = list; showImport = true">
              <template #icon><Upload :size="14" /></template>
            </Button>
            <Button label="View" size="small" severity="secondary" text @click="openDetail(list)">
              <template #icon><Eye :size="14" /></template>
            </Button>
            <Button size="small" severity="danger" text @click="handleDelete(list)">
              <template #icon><Trash2 :size="14" /></template>
            </Button>
          </div>
        </motion.div>
      </div>

      <!-- Create Modal -->
      <Dialog :visible="showCreate" modal header="New Contact List" :style="{ width: '28rem' }" @update:visible="showCreate = $event">
        <form @submit.prevent="handleCreate" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">List Name</label>
            <InputText v-model="createForm.name" required class="w-full" placeholder="e.g. Mumbai Leads" />
          </div>
          <div>
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">Description</label>
            <Textarea v-model="createForm.description" rows="2" class="w-full" placeholder="Optional description" />
          </div>
          <div class="flex justify-end gap-2 pt-2">
            <Button type="button" label="Cancel" severity="secondary" text @click="showCreate = false" />
            <Button type="submit" label="Create" />
          </div>
        </form>
      </Dialog>

      <!-- Detail Modal -->
      <Dialog :visible="showDetail" modal :header="selectedList?.name" :style="{ width: '48rem' }" @update:visible="showDetail = $event">
        <DataTable v-if="!detailLoading" :value="detailContacts" :rows="10" paginator responsive-layout="scroll">
          <template #empty>
            <div class="text-center py-8 text-surface-500">No contacts in this list</div>
          </template>
          <Column field="phone" header="Phone" />
          <Column field="name" header="Name">
            <template #body="{ data }">{{ data.name || '-' }}</template>
          </Column>
          <Column field="email" header="Email">
            <template #body="{ data }">{{ data.email || '-' }}</template>
          </Column>
          <Column header="DND">
            <template #body="{ data }">
              <Tag :value="data.dnd_registered ? 'DND' : 'OK'" :severity="data.dnd_registered ? 'danger' : 'success'" />
            </template>
          </Column>
        </DataTable>
        <div v-else class="space-y-3">
          <Skeleton v-for="i in 5" :key="i" height="2.5rem" />
        </div>
      </Dialog>

      <!-- Import Modal -->
      <ContactImportModal v-if="showImport && importList" :listId="importList.id" @close="showImport = false; importList = null" @imported="onImported" />
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { motion } from 'motion-v'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import AppLayout from '@/components/layout/AppLayout.vue'
import ContactImportModal from './ContactImportModal.vue'
import { useContactsStore } from '@/stores/contacts'
import { Plus, Upload, Users, Eye, Trash2 } from '@lucide/vue'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import Skeleton from 'primevue/skeleton'

const contactsStore = useContactsStore()
const { lists, loading } = storeToRefs(contactsStore)
const confirm = useConfirm()
const toast = useToast()

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
  toast.add({ severity: 'success', summary: 'List created', life: 3000 })
}

async function openDetail(list) {
  selectedList.value = list
  showDetail.value = true
  detailLoading.value = true
  try {
    const data = await contactsStore.getListContacts(list.id)
    detailContacts.value = data.items || []
  } finally {
    detailLoading.value = false
  }
}

function handleDelete(list) {
  confirm.require({
    message: `Delete "${list.name}" and all its contacts?`,
    header: 'Delete contact list',
    acceptProps: { severity: 'danger', label: 'Delete' },
    rejectProps: { severity: 'secondary', outlined: true, label: 'Cancel' },
    accept: async () => {
      await contactsStore.deleteList(list.id)
      toast.add({ severity: 'success', summary: 'List deleted', life: 3000 })
    },
  })
}

function onImported() {
  contactsStore.fetchLists()
}
</script>
