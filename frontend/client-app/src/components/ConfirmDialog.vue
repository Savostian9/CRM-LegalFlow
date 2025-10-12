<template>
  <div v-if="modelValue" class="cd-mask" @click.self="cancel">
    <div class="cd-panel" role="dialog" aria-modal="true">
      <header class="cd-header">
        <h4>{{ title }}</h4>
        <button class="cd-close" @click="cancel">×</button>
      </header>
      <div class="cd-body">
        <slot>
          <p class="cd-message">{{ message }}</p>
        </slot>
      </div>
      <footer class="cd-footer">
        <button class="btn" @click="cancel" :disabled="loading">{{ cancelText }}</button>
        <button :class="['btn', danger? 'danger':'primary']" @click="confirm" :disabled="loading">
          <span v-if="!loading">{{ confirmText }}</span>
          <span v-else class="spinner"></span>
        </button>
      </footer>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ConfirmDialog',
  props:{
    modelValue:{ type:Boolean, default:false },
    title:{ type:String, default:'Подтверждение' },
    message:{ type:String, default:'Вы уверены?' },
    confirmText:{ type:String, default:'ОК' },
    cancelText:{ type:String, default:'Отмена' },
    danger:{ type:Boolean, default:false },
    loading:{ type:Boolean, default:false }
  },
  emits:['update:modelValue','confirm','cancel'],
  watch:{
    modelValue(val){ if(val) document.addEventListener('keydown', this.onKey); else document.removeEventListener('keydown', this.onKey) }
  },
  mounted(){ if(this.modelValue) document.addEventListener('keydown', this.onKey) },
  unmounted(){ document.removeEventListener('keydown', this.onKey) },
  methods:{
    confirm(){ this.$emit('confirm') },
    cancel(){ this.$emit('cancel'); this.$emit('update:modelValue', false) },
    onKey(e){ if(e.key==='Escape') this.cancel() }
  }
}
</script>

<style scoped>
.cd-mask { position:fixed; inset:0; background:rgba(0,0,0,.4); display:flex; align-items:center; justify-content:center; z-index:4000; }
.cd-panel { background:var(--card-bg,#fff); border:1px solid var(--card-border,#e2e8f0); border-radius:14px; width:420px; max-width:92vw; box-shadow:0 10px 30px rgba(0,0,0,.18); display:flex; flex-direction:column; animation:pop .14s ease; }
@keyframes pop { from{ transform:translateY(8px); opacity:0 } to{ transform:translateY(0); opacity:1 } }
.cd-header { display:flex; align-items:center; justify-content:space-between; padding:14px 16px; border-bottom:1px solid #e5e7eb; }
.cd-header h4 { margin:0; font-size:16px; font-weight:600; }
.cd-close { background:none; border:none; font-size:20px; cursor:pointer; line-height:1; }
.cd-body { padding:16px 16px 4px; }
.cd-message { margin:0 0 12px; font-size:14px; line-height:1.5; }
.cd-footer { padding:10px 16px 16px; display:flex; gap:10px; justify-content:flex-end; }
.btn { border:1px solid var(--btn-border,#d0d7e2); background:var(--btn-bg,#fff); color:var(--btn-text,#1e293b); padding:8px 14px; border-radius:8px; cursor:pointer; font-size:14px; }
.btn.primary { background: var(--primary-color,#2563eb); border-color: var(--primary-color,#2563eb); color:#fff; }
.btn.danger { background:rgba(255,82,82,0.12); border:1px solid rgba(255,82,82,0.45); color:#c53030; }
.btn.danger:hover { background:rgba(255,82,82,0.18); border-color:rgba(255,82,82,0.6); color:#a61b1b; }
.btn:disabled { opacity:.6; cursor:default; }
.spinner { width:16px; height:16px; border:2px solid rgba(255,255,255,.4); border-top-color:#fff; border-radius:50%; display:inline-block; animation:spin .6s linear infinite; }
@keyframes spin { to { transform:rotate(360deg) } }
</style>