<template>
  <aside
    class="fixed left-0 top-16 bottom-0 w-64 bg-white border-r border-gray-100 z-40 transition-transform duration-300"
    :class="{ '-translate-x-full': !open, 'translate-x-0': open }"
  >
    <nav class="p-4 space-y-1">
      <router-link
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-gray-600 hover:bg-brand-50 hover:text-brand-600 transition-all duration-200 group"
        active-class="!bg-brand-50 !text-brand-600 font-semibold shadow-sm"
      >
        <component :is="item.icon" :size="20" class="transition-transform duration-200 group-hover:scale-110" />
        <span class="text-sm">{{ item.label }}</span>
      </router-link>
    </nav>
  </aside>

  <!-- Mobile overlay -->
  <transition name="fade">
    <div
      v-if="open"
      class="fixed inset-0 bg-black/20 backdrop-blur-sm z-30 lg:hidden"
      @click="$emit('close')"
    />
  </transition>
</template>

<script setup>
import { LayoutDashboard, FileText, Users, Phone, BarChart3, Settings } from '@lucide/vue'

defineProps({
  open: { type: Boolean, default: true },
})

defineEmits(['close'])

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/scripts', icon: FileText, label: 'Scripts' },
  { to: '/contacts', icon: Users, label: 'Contacts' },
  { to: '/campaigns', icon: Phone, label: 'Campaigns' },
  { to: '/reports', icon: BarChart3, label: 'Reports' },
  { to: '/settings', icon: Settings, label: 'Settings' },
]
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
