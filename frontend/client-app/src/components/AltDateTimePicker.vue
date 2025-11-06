<template>
  <div class="alt-datetime-picker">
    <DatePicker
      :value="inner"
      :type="dpType"
      :format="displayFormat"
      :value-type="valueType"
      :editable="false"
      :clearable="true"
      :placeholder="computedPlaceholder"
      :append-to-body="true"
      popup-class="lf-dp-popup"
      @change="onChange"
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
    placeholder: { type: String, default: '' }
  },
  setup(props, { emit }) {
    const inner = ref(props.modelValue || null)
    const isDateTime = computed(() => props.mode === 'datetime')
    const dpType = computed(() => (isDateTime.value ? 'datetime' : 'date'))
    const displayFormat = computed(() => (isDateTime.value ? 'DD/MM/YYYY HH:mm' : 'DD/MM/YYYY'))
    const valueType = computed(() => (isDateTime.value ? 'YYYY-MM-DD[T]HH:mm' : 'YYYY-MM-DD'))
    const computedPlaceholder = computed(() => props.placeholder || (isDateTime.value ? 'dd/mm/yyyy hh:mm' : 'dd/mm/yyyy'))

    watch(() => props.modelValue, (nv) => { inner.value = nv || null })
    function onChange(val) {
      inner.value = val || null
      emit('update:modelValue', inner.value)
      emit('change', inner.value)
    }
    return { inner, dpType, displayFormat, valueType, computedPlaceholder, onChange }
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
