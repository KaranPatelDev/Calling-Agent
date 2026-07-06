import { defineStore } from 'pinia'
import { ref } from 'vue'
import { DARK_MODE_SELECTOR } from '@/theme/preset'

function getInitialDarkMode() {
  const stored = localStorage.getItem('theme')
  if (stored === 'dark') return true
  if (stored === 'light') return false
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(getInitialDarkMode())

  function applyDarkClass() {
    document.documentElement.classList.toggle(DARK_MODE_SELECTOR.slice(1), isDark.value)
  }

  function toggleTheme() {
    isDark.value = !isDark.value
    localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
    applyDarkClass()
  }

  applyDarkClass()

  return { isDark, toggleTheme }
})
