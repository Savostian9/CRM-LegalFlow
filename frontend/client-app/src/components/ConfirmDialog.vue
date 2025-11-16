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
.cd-mask { position:fixed; inset:0; background:rgba(0,0,0,.38); display:flex; align-items:center; justify-content:center; z-index:4000; backdrop-filter: blur(2px) saturate(1.05); }
.cd-panel { background:var(--card-bg,#fff); border:1px solid var(--card-border,#e6ebf2); border-radius:16px; width:560px; max-width:94vw; box-shadow:0 18px 48px -12px rgba(2,17,37,.28); display:flex; flex-direction:column; animation:pop .16s ease; }
@keyframes pop { from{ transform:translateY(8px) scale(.98); opacity:0 } to{ transform:translateY(0) scale(1); opacity:1 } }
.cd-header { position:relative; display:flex; align-items:center; justify-content:center; padding:16px 18px; border-bottom:1px solid #eef2f5; }
.cd-header h4 { margin:0; font-size:18px; font-weight:700; text-align:center; letter-spacing:.2px; color:#0f172a; }
.cd-close { position:absolute; right:12px; top:50%; transform:translateY(-50%); background:none; border:none; font-size:20px; cursor:pointer; line-height:1; color:#64748b; }
.cd-close:hover { color:#334155; }
.cd-body { padding:18px 20px 6px; }
.cd-message { margin:0 0 12px; font-size:16px; line-height:1.5; text-align:center; white-space:nowrap; color:#334155; font-weight:500; }
.cd-footer { padding:12px 18px 18px; display:flex; gap:12px; justify-content:center; }
.btn { border:1px solid var(--btn-border,#d0d7e2); background:var(--btn-bg,#fff); color:var(--btn-text,#1e293b); padding:10px 16px; border-radius:10px; cursor:pointer; font-size:14px; transition:background .2s ease,border-color .2s ease,box-shadow .2s ease,transform .16s ease; }
.btn:hover { background:#f7f9fc; border-color:#c7d2dc; transform:translateY(-1px); box-shadow:0 10px 18px -12px rgba(0,0,0,.18); }
.btn:active { transform:translateY(0); box-shadow:none; }
.btn.primary { background: var(--primary-color,#2563eb); border-color: var(--primary-color,#2563eb); color:#fff; }
.btn.danger { background:rgba(255,82,82,0.12); border:1px solid rgba(255,82,82,0.45); color:#c53030; }
.btn.danger:hover { background:rgba(255,82,82,0.18); border-color:rgba(255,82,82,0.6); color:#a61b1b; }
.btn:disabled { opacity:.6; cursor:default; }
.spinner { width:16px; height:16px; border:2px solid rgba(255,255,255,.4); border-top-color:#fff; border-radius:50%; display:inline-block; animation:spin .6s linear infinite; }
@keyframes spin { to { transform:rotate(360deg) } }
</style>