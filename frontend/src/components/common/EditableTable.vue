<template>
  <div class="space-y-3">
    <div class="flex items-center justify-between">
      <span class="text-sm text-gray-500">{{ rows.length }} row{{ rows.length !== 1 ? 's' : '' }}</span>
      <button v-if="allowAdd" @click="addRow" class="text-sm text-brand-600 hover:text-brand-700 font-medium flex items-center gap-1">
        <Plus :size="14" />
        Add Row
      </button>
    </div>

    <div class="overflow-x-auto border border-gray-200 rounded-xl">
      <table class="w-full text-sm">
        <thead class="bg-gray-50/80 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
          <tr>
            <th v-if="allowDelete" class="w-10 px-3 py-2.5"></th>
            <th v-for="col in columns" :key="col.key" class="px-3 py-2.5" :class="col.width || ''">
              {{ col.label }}
              <span v-if="col.required" class="text-red-500">*</span>
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="(row, idx) in rows" :key="idx" class="hover:bg-gray-50/50 transition-colors">
            <td v-if="allowDelete" class="px-3 py-2">
              <button @click="removeRow(idx)" class="p-1 rounded-lg text-gray-400 hover:text-red-600 hover:bg-red-50 transition-all">
                <X :size="14" />
              </button>
            </td>
            <td v-for="col in columns" :key="col.key" class="px-2 py-1.5">
              <select
                v-if="col.type === 'select'"
                :value="row[col.key]"
                @input="updateCell(idx, col.key, $event.target.value)"
                class="w-full px-2.5 py-1.5 border border-gray-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all"
                :class="{ 'border-red-300 bg-red-50': !row._valid && col.required }"
              >
                <option v-for="opt in col.options" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
              </select>
              <textarea
                v-else-if="col.type === 'textarea'"
                :value="row[col.key]"
                @input="updateCell(idx, col.key, $event.target.value)"
                rows="2"
                class="w-full px-2.5 py-1.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 resize-y transition-all"
                :class="{ 'border-red-300 bg-red-50': !row._valid && col.required }"
                :placeholder="col.placeholder || ''"
              ></textarea>
              <input
                v-else
                type="text"
                :value="row[col.key]"
                @input="updateCell(idx, col.key, $event.target.value)"
                class="w-full px-2.5 py-1.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all"
                :class="{ 'border-red-300 bg-red-50': !row._valid && col.required }"
                :placeholder="col.placeholder || ''"
              />
              <p v-if="!row._valid && row._errors?.length" class="text-xs text-red-500 mt-1">
                {{ row._errors.join('; ') }}
              </p>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="rows.length === 0" class="text-center py-8 text-gray-400 text-sm">
      {{ emptyMessage }}
    </div>
  </div>
</template>

<script setup>
import { Plus, X } from '@lucide/vue'

const props = defineProps({
  columns: { type: Array, required: true },
  rows: { type: Array, required: true },
  allowAdd: { type: Boolean, default: true },
  allowDelete: { type: Boolean, default: true },
  emptyMessage: { type: String, default: 'No rows yet. Add one to get started.' },
  newRowTemplate: { type: Function, default: () => ({}) },
})

const emit = defineEmits(['update:rows'])

function updateCell(idx, key, value) {
  const updated = [...props.rows]
  updated[idx] = { ...updated[idx], [key]: value }
  emit('update:rows', updated)
}

function addRow() {
  const newRow = { ...props.newRowTemplate(), _valid: true, _errors: [] }
  emit('update:rows', [...props.rows, newRow])
}

function removeRow(idx) {
  const updated = props.rows.filter((_, i) => i !== idx)
  emit('update:rows', updated)
}
</script>
