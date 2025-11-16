<template>
  <div class="alt-datetime-picker">
    <DatePicker
      :value="inner"
      :type="dpType"
      :format="displayFormat"
      :value-type="valueType"
      :disabled-date="disabledDate"
      :disabled="disabled"
      :editable="false"
      :clearable="true"
      :placeholder="computedPlaceholder"
      :append-to-body="true"
      popup-class="lf-dp-popup"
      @change="onChange"
      @open="onOpen"
      @close="onClose"
    />
  </div>
  </template>

<script>
import { ref, watch, computed } from 'vue'
import DatePicker from 'vue-datepicker-next'
import 'vue-datepicker-next/index.css'

export default {
  name: 'AltDateTimePicker',
  components: { DatePicker },
  props: {
    modelValue: { type: [String, null], default: null },
    mode: { type: String, default: 'date' }, // 'date' | 'datetime'
    placeholder: { type: String, default: '' },
    // When true, disallow selecting any past date/time (relative to now)
    minNow: { type: Boolean, default: false },
    disabled: { type: Boolean, default: false }
  },
  setup(props, { emit }) {
    const inner = ref(props.modelValue || null)
    const draft = ref(props.modelValue || null)
    const isOpen = ref(false)
    const isDateTime = computed(() => props.mode === 'datetime')
    const dpType = computed(() => (isDateTime.value ? 'datetime' : 'date'))
    const displayFormat = computed(() => (isDateTime.value ? 'DD/MM/YYYY HH:mm' : 'DD/MM/YYYY'))
    const valueType = computed(() => (isDateTime.value ? 'YYYY-MM-DD[T]HH:mm' : 'YYYY-MM-DD'))
    const computedPlaceholder = computed(() => props.placeholder || (isDateTime.value ? 'dd/mm/yyyy hh:mm' : 'dd/mm/yyyy'))

    // Disable past calendar days (coarse prevention)
    const disabledDate = (date) => {
      if (!props.minNow || !date) return false
      try {
        const today = new Date()
        const todayStart = new Date(today.getFullYear(), today.getMonth(), today.getDate())
        return date < todayStart
      } catch { return false }
    }

    function parseLocal(val) {
      if (!val) return null
      try {
        if (isDateTime.value) {
          const [d, t = '00:00'] = String(val).split('T')
          const [Y, M, D] = d.split('-').map(n => Number(n))
          const [h, m] = t.split(':').map(n => Number(n))
          return new Date(Y, (M || 1) - 1, D || 1, h || 0, m || 0, 0, 0)
        } else {
          const [Y, M, D] = String(val).split('-').map(n => Number(n))
          return new Date(Y, (M || 1) - 1, D || 1, 0, 0, 0, 0)
        }
      } catch { return null }
    }

    watch(() => props.modelValue, (nv) => { inner.value = nv || null; draft.value = nv || null })
    function onChange(val) {
      // Always update local draft and v-model so UI reflects selection while popup is open
      draft.value = val || null
      inner.value = draft.value
      emit('update:modelValue', inner.value)
      // Do NOT emit invalid here to avoid early errors (e.g., hour picked, minute not yet)
      emit('change', inner.value)
    }
    function onOpen() { isOpen.value = true }
    function onClose() {
      isOpen.value = false
      if (props.minNow && inner.value) {
        const picked = parseLocal(inner.value)
        const now = new Date()
        const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate())
        // Compare with minute precision so 16:25 selected at 16:25:xx is allowed
        const roundedNow = new Date(now.getFullYear(), now.getMonth(), now.getDate(), now.getHours(), now.getMinutes(), 0, 0)
        const invalid = isDateTime.value ? (picked && picked < roundedNow) : (picked && picked < todayStart)
        if (invalid) {
          inner.value = null
          draft.value = null
          emit('update:modelValue', null)
          emit('invalid', { reason: 'past', attempted: null })
        }
      }
      emit('close')
    }
    return { inner, dpType, displayFormat, valueType, computedPlaceholder, disabledDate, onChange, onOpen, onClose }
  }
}
</script>

<style scoped>
.alt-datetime-picker :deep(.mx-input) {
  width: 100%;
  height: 48px;
  border-radius: 8px;
  border: 1px solid var(--form-border, #e2e8f0);
  box-shadow: var(--input-shadow, inset 0 1px 2px rgba(0,0,0,.05));
  padding: 0 12px;
  font-size: 15px;
  background: var(--form-bg, #fff);
}
.alt-datetime-picker :deep(.mx-input:focus) {
  outline: none;
  border-color: var(--form-border-focus, #4A9E80);
  box-shadow: var(--form-focus-ring, 0 0 0 2px rgba(74,158,128,.18));
}
</style>

<!-- Global style for teleported popup (appended to body) -->
<style>
.lf-dp-popup { z-index: 5000 !important; }
</style>
