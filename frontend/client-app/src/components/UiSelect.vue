<template>
  <div class="ui-select" ref="root">
    <button
      class="ui-select__trigger"
      type="button"
      :aria-expanded="open ? 'true' : 'false'"
      :aria-haspopup="'listbox'"
      @click="toggle"
      @keydown.down.prevent="openAndFocus(1)"
      @keydown.up.prevent="openAndFocus(-1)"
      @keydown.enter.prevent="toggle"
      @keydown.space.prevent="toggle"
    >
      <span class="ui-select__label">{{ labelForValue(modelValue) || placeholder }}</span>
      <svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M7 10l5 5 5-5H7z"/></svg>
    </button>

    <teleport to="body">
      <div v-if="open" class="ui-select__dropdown" :style="dropdownStyle" @keydown.escape.stop.prevent="close">
        <ul class="ui-select__list" role="listbox" :aria-label="ariaLabel">
          <li
            v-for="(opt, i) in options"
            :key="String(opt.value)"
            class="ui-select__option"
            :class="{ selected: isSelected(opt), focused: focusedIndex === i }"
            role="option"
            :aria-selected="isSelected(opt) ? 'true' : 'false'"
            @click.stop="select(opt)"
            @mouseenter="focusedIndex = i"
          >
            <slot name="option" :option="opt">{{ opt.label }}</slot>
          </li>
        </ul>
      </div>
    </teleport>
  </div>
</template>

<script>
export default {
  name: 'UiSelect',
  props: {
    modelValue: [String, Number, Boolean],
    options: { type: Array, default: () => [] }, // [{value, label}]
    placeholder: { type: String, default: '' },
    ariaLabel: { type: String, default: 'select' },
  },
  emits: ['update:modelValue', 'change'],
  data(){
    return { open: false, rect: { top: 0, left: 0, width: 0, height: 0 }, focusedIndex: -1 };
  },
  computed:{
    dropdownStyle(){
      // Position fixed is relative to viewport; do NOT add window scroll offsets.
      let top = Math.round(this.rect.top + this.rect.height + 8);
      const left = Math.round(this.rect.left);
      const minWidth = Math.max(200, this.rect.width);
      // Clamp within viewport so list doesn't fly off-screen
      const estimatedH = Math.min(360, ((this.options || []).length * 32) + 12);
      const maxTop = (typeof window !== 'undefined' ? (window.innerHeight - estimatedH - 8) : top);
      if (top > maxTop) top = Math.max(8, maxTop);
      if (top < 8) top = 8;
      return { top: top + 'px', left: left + 'px', minWidth: minWidth + 'px' };
    }
  },
  methods:{
    updateRect(){
      try { const r = this.$refs.root.getBoundingClientRect(); this.rect = { top: r.top, left: r.left, width: r.width, height: r.height }; } catch(e){ /* ignore */ }
    },
    toggle(){ this.open ? this.close() : this.openDropdown(); },
    openDropdown(){
      this.updateRect();
      this.open = true;
      this.$nextTick(()=>{
        window.addEventListener('click', this.onWinClick, { capture: true });
        window.addEventListener('resize', this.updateRect);
        window.addEventListener('scroll', this.updateRect, true);
      });
    },
    close(){
      this.open = false;
      window.removeEventListener('click', this.onWinClick, { capture: true });
      window.removeEventListener('resize', this.updateRect);
      window.removeEventListener('scroll', this.updateRect, true);
      this.focusedIndex = -1;
    },
    onWinClick(e){
      const inRoot = this.$refs.root && this.$refs.root.contains(e.target);
      const inDrop = e.target.closest && e.target.closest('.ui-select__dropdown');
      if (!inRoot && !inDrop) this.close();
    },
    select(opt){
      this.$emit('update:modelValue', opt.value);
      this.$emit('change', opt.value);
      this.close();
    },
    isSelected(opt){ return String(opt.value) === String(this.modelValue || ''); },
    labelForValue(val){
      const m = (this.options || []).find(o => String(o.value) === String(val || ''));
      return m ? m.label : '';
    },
    openAndFocus(dir){
      if (!this.open) this.openDropdown();
      const len = (this.options || []).length;
      if (!len) return;
      let i = this.focusedIndex;
      i = i < 0 ? (dir > 0 ? 0 : len - 1) : (i + dir + len) % len;
      this.focusedIndex = i;
    }
  },
  beforeUnmount(){ this.close(); }
}
</script>

<style scoped>
.ui-select { display: inline-block; position: relative; }
.ui-select__trigger{
  display:inline-flex; align-items:center; gap:8px;
  padding:8px 10px; border-radius:8px; border:1px solid #e2e8f0;
  background: var(--input-bg,#fff); color:#334155; cursor:pointer; min-width:160px;
  transition:border-color .18s, box-shadow .18s, background-color .25s;
}
.ui-select__trigger:hover{ background:#f7f9fc; }
.ui-select__trigger:focus{ outline:none; border-color:#4A9E80; box-shadow:0 0 0 2px rgba(74,158,128,.18); }
.ui-select__label{ flex: 1; text-align: left; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.ui-select__dropdown{
  position:fixed; z-index:5000;
  background: var(--card-bg,#fff); border:1px solid #e2e8f0; border-radius:8px;
  box-shadow:0 16px 40px rgba(0,0,0,0.18); padding:4px 0; max-height:60vh; overflow:auto;
}
.ui-select__list{ list-style: none; margin: 0; padding: 0; }
.ui-select__option{
  padding:8px 10px; cursor:pointer; display:block; white-space:nowrap; text-overflow:ellipsis; overflow:hidden; font-size:14px; transition:background .16s ease, color .16s ease;
}
/* Hover/focus: лёгкий светлый фон (не тёмный) */
.ui-select__option:hover, .ui-select__option.focused{ background:#f0f4f7; }
/* Selected: фирменный зеленоватый фон + жирный текст */
.ui-select__option.selected{ background:#e8f4f0; color:#2f7f66; font-weight:600; }
/* Когда элемент и выбран и наведен — не затемнять */
.ui-select__option.selected:hover{ background:#e8f4f0; }
</style>
