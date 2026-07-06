<template>
  <header class="fixed top-0 left-0 right-0 z-50 h-16 bg-white/80 backdrop-blur-xl border-b border-gray-100">
    <div class="flex items-center justify-between h-full px-4 lg:px-6">
      <div class="flex items-center gap-3">
        <button @click="$emit('toggleSidebar')" class="lg:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors">
          <Menu :size="20" />
        </button>
        <router-link to="/dashboard" class="flex items-center gap-2">
          <div class="w-8 h-8 bg-gradient-to-br from-brand-500 to-purple-600 rounded-lg flex items-center justify-center">
            <Phone :size="16" class="text-white" />
          </div>
          <span class="text-lg font-bold gradient-text hidden sm:block">Calling Agent</span>
        </router-link>
      </div>

      <div class="flex items-center gap-2">
        <button class="relative p-2 rounded-lg hover:bg-gray-100 transition-colors">
          <Bell :size="20" class="text-gray-500" />
          <span class="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>

        <div class="relative" ref="dropdownRef">
          <button
            @click="showDropdown = !showDropdown"
            class="flex items-center gap-2 p-1.5 rounded-xl hover:bg-gray-100 transition-colors"
          >
            <div class="w-8 h-8 bg-gradient-to-br from-brand-400 to-brand-600 rounded-full flex items-center justify-center text-white text-sm font-semibold">
              {{ initials }}
            </div>
            <span class="text-sm font-medium text-gray-700 hidden md:block">{{ authStore.user?.full_name || 'User' }}</span>
            <ChevronDown :size="16" class="text-gray-400 hidden md:block" />
          </button>

          <transition name="dropdown">
            <div
              v-if="showDropdown"
              class="absolute right-0 top-full mt-2 w-56 bg-white rounded-xl shadow-glass-lg border border-gray-100 py-2 z-50"
            >
              <div class="px-4 py-2 border-b border-gray-100">
                <p class="text-sm font-medium text-gray-900">{{ authStore.user?.full_name }}</p>
                <p class="text-xs text-gray-500">{{ authStore.user?.email }}</p>
              </div>
              <router-link to="/settings" class="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors" @click="showDropdown = false">
                <Settings :size="16" />
                Settings
              </router-link>
              <button @click="handleLogout" class="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 transition-colors">
                <LogOut :size="16" />
                Sign out
              </button>
            </div>
          </transition>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Menu, Phone, Bell, ChevronDown, Settings, LogOut } from '@lucide/vue'

defineEmits(['toggleSidebar'])

const authStore = useAuthStore()
const router = useRouter()
const showDropdown = ref(false)
const dropdownRef = ref(null)

const initials = computed(() => {
  const name = authStore.user?.full_name || 'U'
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
})

function handleLogout() {
  authStore.logout()
  router.push('/login')
  showDropdown.value = false
}

function handleClickOutside(e) {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target)) {
    showDropdown.value = false
  }
}

onMounted(() => document.addEventListener('click', handleClickOutside))
onUnmounted(() => document.removeEventListener('click', handleClickOutside))
</script>

<style scoped>
.dropdown-enter-active, .dropdown-leave-active {
  transition: all 0.2s ease;
}
.dropdown-enter-from, .dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.95);
}
</style>
