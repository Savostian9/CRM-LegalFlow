<template>
  <div class="ui-datetime-picker">
    <VDatePicker
      v-model="inner"
      :mode="vcMode"
      :is24hr="true"
      :masks="displayMasks"
      :model-config="modelConfig"
      :popover="{ placement: 'bottom-start' }"
      :hide-time-header="false"
    >
      <template #default="{ inputValue, inputEvents }">
        <input
          class="form-input"
          :placeholder="computedPlaceholder"
          :value="inputValue"
          v-on="inputEvents"
        />
      </template>
    </VDatePicker>
  </div>
</template>

<script>
import { ref, watch, computed } from 'vue'

export default {
  name: 'UiDateTimePicker',
  props: {
    modelValue: { type: [String, null], default: null },
    mode: { type: String, default: 'date' }, // 'date' | 'datetime'
    placeholder: { type: String, default: '' }
  },
  setup(props, { emit }) {
    const inner = ref(props.modelValue || null)

    const isDateTime = computed(() => props.mode === 'datetime')
  const vcMode = computed(() => (isDateTime.value ? 'datetime' : 'date'))

    const displayMasks = computed(() => ({
      input: isDateTime.value ? 'DD/MM/YYYY HH:mm' : 'DD/MM/YYYY'
    }))

    const modelConfig = computed(() => ({
      type: 'string',
      mask: isDateTime.value ? 'YYYY-MM-DD[T]HH:mm' : 'YYYY-MM-DD'
    }))

    const computedPlaceholder = computed(() => (
      props.placeholder || (isDateTime.value ? 'dd/mm/yyyy hh:mm' : 'dd/mm/yyyy')
    ))

    watch(() => props.modelValue, (nv) => {
      inner.value = nv || null
    })

    watch(inner, (nv) => {
      emit('update:modelValue', nv || null)
      emit('change', nv || null)
    })

    return { inner, isDateTime, vcMode, displayMasks, modelConfig, computedPlaceholder }
  }
}
</script>

<style scoped>
.ui-datetime-picker .form-input {
  width: 100%;
  height: 48px;
  border-radius: 8px;
  border: 1px solid var(--form-border, #e2e8f0);
  box-shadow: var(--input-shadow, inset 0 1px 2px rgba(0,0,0,.05));
  padding: 0 12px;
  font-size: 15px;
  background: var(--form-bg, #fff);
}
.ui-datetime-picker .form-input:focus {
  outline: none;
  border-color: var(--form-border-focus, #4A9E80);
  box-shadow: var(--form-focus-ring, 0 0 0 2px rgba(74,158,128,.18));
}
</style>
