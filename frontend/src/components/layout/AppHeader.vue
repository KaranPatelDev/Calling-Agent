<template>
  <header class="fixed top-0 left-0 right-0 z-50 h-16 bg-surface-0/80 dark:bg-surface-900/80 backdrop-blur-xl border-b border-surface-200 dark:border-surface-700">
    <div class="flex items-center justify-between h-full px-4 lg:px-6">
      <div class="flex items-center gap-3">
        <button @click="$emit('toggleSidebar')" class="lg:hidden p-2 rounded-lg hover:bg-surface-100 dark:hover:bg-surface-800 transition-colors">
          <MenuIcon :size="20" />
        </button>
        <router-link to="/dashboard" class="flex items-center gap-2">
          <div class="w-8 h-8 bg-gradient-to-br from-primary-500 to-purple-600 rounded-lg flex items-center justify-center">
            <Phone :size="16" class="text-white" />
          </div>
          <span class="text-lg font-bold gradient-text hidden sm:block">Calling Agent</span>
        </router-link>
      </div>

      <div class="flex items-center gap-2">
        <Button
          text
          rounded
          severity="secondary"
          :aria-label="themeStore.isDark ? 'Switch to light mode' : 'Switch to dark mode'"
          @click="themeStore.toggleTheme"
        >
          <template #icon>
            <Sun v-if="themeStore.isDark" :size="18" />
            <Moon v-else :size="18" />
          </template>
        </Button>

        <button class="relative p-2 rounded-lg hover:bg-surface-100 dark:hover:bg-surface-800 transition-colors">
          <Bell :size="20" class="text-surface-500" />
          <span class="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>

        <button
          @click="toggleMenu"
          class="flex items-center gap-2 p-1.5 rounded-xl hover:bg-surface-100 dark:hover:bg-surface-800 transition-colors"
        >
          <Avatar :label="initials" shape="circle" class="!bg-gradient-to-br !from-primary-400 !to-primary-600 !text-white" />
          <span class="text-sm font-medium text-surface-700 dark:text-surface-200 hidden md:block">{{ authStore.user?.full_name || 'User' }}</span>
          <ChevronDown :size="16" class="text-surface-400 hidden md:block" />
        </button>

        <Menu ref="menu" :model="menuItems" :popup="true">
          <template #start>
            <div class="px-4 py-2 border-b border-surface-200 dark:border-surface-700">
              <p class="text-sm font-medium text-surface-900 dark:text-surface-0">{{ authStore.user?.full_name }}</p>
              <p class="text-xs text-surface-500">{{ authStore.user?.email }}</p>
            </div>
          </template>
          <template #item="{ item, props }">
            <a v-bind="props.action" class="flex items-center gap-3" :class="item.danger ? '!text-red-600' : ''">
              <component :is="item.iconComponent" :size="16" />
              <span>{{ item.label }}</span>
            </a>
          </template>
        </Menu>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { Menu as MenuIcon, Phone, Bell, ChevronDown, Settings, LogOut, Sun, Moon } from '@lucide/vue'
import Avatar from 'primevue/avatar'
import Button from 'primevue/button'
import Menu from 'primevue/menu'

defineEmits(['toggleSidebar'])

const authStore = useAuthStore()
const themeStore = useThemeStore()
const router = useRouter()
const menu = ref(null)

const initials = computed(() => {
  const name = authStore.user?.full_name || 'U'
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
})

const menuItems = [
  { label: 'Settings', iconComponent: Settings, command: () => router.push('/settings') },
  { label: 'Sign out', iconComponent: LogOut, danger: true, command: handleLogout },
]

function toggleMenu(event) {
  menu.value.toggle(event)
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>
