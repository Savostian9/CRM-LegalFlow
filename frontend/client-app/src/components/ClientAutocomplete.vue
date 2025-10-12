<template>
  <div class="client-autocomplete" ref="root">
    <label v-if="label" class="ca-label">{{ label }}</label>
    <div class="ca-input-wrap" :class="{ open: open, invalid: required && !modelValue }">
      <input
        ref="inputEl"
        type="text"
        class="ca-input"
        :placeholder="placeholder"
        v-model="inputValue"
        @input="onInput"
        @focus="onFocus"
        @keydown.down.prevent="move(1)"
        @keydown.up.prevent="move(-1)"
        @keydown.enter.prevent="enterSelect"
        @keydown.esc.prevent="close"
        :aria-expanded="open ? 'true':'false'"
        autocomplete="off"
      />
      <button v-if="inputValue" type="button" class="clear-btn" @click="clear" aria-label="Clear">×</button>
      <div class="spinner" v-if="loading"></div>
    </div>
    <transition name="fade">
      <ul v-if="open" class="ca-list" role="listbox">
        <li v-if="!loading && !suggestions.length" class="empty">{{ noResultsText }}</li>
        <li v-for="(c,i) in suggestions" :key="c.id" :class="['ca-item', { active: i === index }]" @mousedown.prevent="select(c)" @mousemove="index = i" role="option">
          <span class="name">{{ fullName(c) }}</span>
          <span v-if="c.email" class="email">{{ c.email }}</span>
        </li>
      </ul>
    </transition>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'ClientAutocomplete',
  props: {
    modelValue: [Number, String, null],
    initialLabel: String,
    placeholder: { type: String, default: '' },
    label: String,
    required: { type: Boolean, default: false },
    noResultsText: { type: String, default: 'Не найдено' }
  },
  emits: ['update:modelValue','client-selected'],
  data(){
    return { inputValue: this.initialLabel || '', suggestions: [], loading:false, open:false, index:-1, searchTimer:null }
  },
  watch:{ initialLabel(v){ if(v && !this.inputValue) this.inputValue = v } },
  methods:{
    fullName(c){ return `${c.first_name || ''} ${c.last_name || ''}`.trim() || c.email || ('ID '+c.id) },
    onFocus(){ if(this.inputValue.length>=2) { this.fetch() } },
    onInput(){
      if(!this.inputValue){ this.$emit('update:modelValue', null); this.suggestions=[]; this.open=false; return }
      clearTimeout(this.searchTimer)
      if(this.inputValue.length < 2){ this.suggestions=[]; this.open=false; return }
      this.searchTimer = setTimeout(()=> this.fetch(), 250)
    },
    async fetch(){
      const q = this.inputValue.trim()
      if(q.length < 2) return
      this.loading = true
      const token = localStorage.getItem('user-token')
      try {
        const resp = await axios.get('http://127.0.0.1:8000/api/clients/', { headers:{ Authorization:'Token '+token }, params:{ q } })
        let arr = Array.isArray(resp.data) ? resp.data : []
        const qLower = q.toLowerCase()
        // Frontend fallback filter in case backend ignores ?q=
        arr = arr.filter(c => (`${c.first_name||''} ${c.last_name||''} ${c.email||''}`).toLowerCase().includes(qLower))
        this.suggestions = arr.slice(0,15)
        this.open = true
        this.index = this.suggestions.length ? 0 : -1
      } catch(e){ this.suggestions=[]; this.open=true; this.index=-1 } finally { this.loading=false }
    },
    move(delta){
      if(!this.open){ this.fetch(); return }
      if(!this.suggestions.length) return
      this.index = (this.index + delta + this.suggestions.length) % this.suggestions.length
    },
    enterSelect(){ if(this.index>=0) this.select(this.suggestions[this.index]) },
    select(c){
      this.inputValue = this.fullName(c)
      this.$emit('update:modelValue', c.id)
      this.$emit('client-selected', c)
      this.open = false
    },
    clear(){ this.inputValue=''; this.$emit('update:modelValue', null); this.suggestions=[]; this.open=false; this.index=-1; this.$nextTick(()=> this.$refs.inputEl.focus()) },
    close(){ this.open=false },
    onClickOutside(e){ if(!this.$refs.root) return; if(!this.$refs.root.contains(e.target)) this.close() }
  },
  mounted(){ document.addEventListener('click', this.onClickOutside) },
  beforeUnmount(){ document.removeEventListener('click', this.onClickOutside) }
}
</script>

<style scoped>
.client-autocomplete { position:relative; display:flex; flex-direction:column; gap:6px; }
.ca-label { font-size:13px; font-weight:600; color:#334155; }
.ca-input-wrap { position:relative; display:flex; align-items:center; }
.ca-input { width:100%; border:1px solid var(--form-border,#e2e8f0); border-radius:8px; padding:8px 34px 8px 12px; font:inherit; background:var(--form-bg,#fff); transition:border-color .18s, box-shadow .18s; }
.ca-input:focus { outline:none; border-color:var(--form-border-focus,#4A9E80); box-shadow:var(--form-focus-ring,0 0 0 2px rgba(74,158,128,.18)); }
.ca-input-wrap.invalid .ca-input { border-color:#dc2626; }
.clear-btn { position:absolute; right:6px; top:50%; transform:translateY(-50%); background:transparent; border:none; font-size:18px; line-height:1; cursor:pointer; color:#94a3b8; padding:2px 4px; }
.clear-btn:hover { color:#475569; }
.spinner { position:absolute; right:30px; top:50%; width:14px; height:14px; border:3px solid #cbd5e1; border-top-color:#2563eb; border-radius:50%; animation:spin .7s linear infinite; transform:translateY(-50%); }
@keyframes spin { to { transform:translateY(-50%) rotate(360deg); } }
.ca-list { position:absolute; z-index:3000; left:0; right:0; top:100%; margin:4px 0 0; background:#fff; border:1px solid var(--form-border,#e2e8f0); border-radius:8px; list-style:none; padding:4px 0; box-shadow:0 8px 28px -6px rgba(0,0,0,.18); max-height:260px; overflow:auto; }
.ca-item { padding:8px 12px; display:flex; flex-direction:column; gap:2px; cursor:pointer; font-size:13px; }
.ca-item .email { font-size:11px; color:#64748b; }
.ca-item.active, .ca-item:hover { background:#f1f5f9; }
.empty { padding:10px 12px; font-size:12px; color:#64748b; }
.fade-enter-active, .fade-leave-active { transition: opacity .15s, transform .15s; }
.fade-enter-from, .fade-leave-to { opacity:0; transform:translateY(-4px); }
</style>
