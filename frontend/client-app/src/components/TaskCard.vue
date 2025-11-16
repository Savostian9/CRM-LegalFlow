<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <header class="modal-header">
        <div class="left">
          <span class="type-dot" :style="{ backgroundColor: typeColor }"></span>
          <h3 class="title" :title="task.title || placeholderTitle">
            {{ task.title || placeholderTitle }}
          </h3>
          <span class="status" :class="('st-' + effectiveStatus.toLowerCase())">{{ statusLabel(effectiveStatus) }}</span>
        </div>
        <button class="icon" @click="$emit('close')">×</button>
      </header>

      <section class="content">
        <div class="row">
          <div class="label">{{ $t('tasks.start') }}</div>
          <div class="value">{{ singleStart(task) }}</div>
        </div>
        <div class="row" v-if="task.client">
          <div class="label">{{ $t('tasks.client') }}</div>
          <div class="value">
            <router-link
              v-if="task.client && task.client.id"
              class="client-link"
              :to="{ name: 'client-detail', params: { id: task.client.id } }"
              :title="clientName(task)"
            >
              {{ clientName(task) }}
            </router-link>
            <span v-else>{{ clientName(task) }}</span>
            <span v-if="task.client.email" class="muted"> · {{ task.client.email }}</span>
          </div>
        </div>
        <div class="row" v-if="task.location">
          <div class="label">{{ $t('tasks.form.location') }}</div>
          <div class="value">{{ task.location }}</div>
        </div>
        <!-- reminder_minutes removed -->
        <div class="row" v-if="task.description">
          <div class="label">{{ $t('tasks.form.description') }}</div>
          <div class="value prewrap">{{ task.description }}</div>
        </div>
      </section>

      <footer class="footer">
        <button class="btn edit" @click="$emit('edit', task)">{{ $t('tasks.editTask') }}</button>
        <div class="spacer"></div>
          <button class="btn state-scheduled" @click="markScheduled" :disabled="effectiveStatus==='SCHEDULED'">{{ $t('tasks.status.SCHEDULED') }}</button>
        <button class="btn state-done" @click="markDone" :disabled="effectiveStatus==='DONE'">{{ $t('dashboard.taskStatus.done') }}</button>
        <button class="btn state-cancelled" @click="markCancelled" :disabled="effectiveStatus==='CANCELLED'">{{ $t('tasks.status.CANCELLED') }}</button>
        <button v-if="canDeleteTask" class="btn danger" @click="showDeleteConfirm=true">{{ $t('common.delete') }}</button>
      </footer>
      <div v-if="showDeleteConfirm" class="confirm-dialog-overlay" @click.self="showDeleteConfirm=false">
        <div class="confirm-dialog">
          <p class="cd-text">{{ ($t('tasks.confirm.deleteOne') && $t('tasks.confirm.deleteOne')!=='tasks.confirm.deleteOne') ? $t('tasks.confirm.deleteOne') : 'Удалить задачу?' }}</p>
          <div class="confirm-dialog-actions">
            <button class="btn danger-pink" :disabled="deleting" @click="performDelete">{{ yesDeleteLabel() }}</button>
            <button class="btn" :disabled="deleting" @click="showDeleteConfirm=false">{{ $t('common.cancel') }}</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'TaskCard',
  props: { task: { type: Object, required: true } },
  emits: ['close','edit','updated'],
  data(){
    return { showDeleteConfirm:false, deleting:false, placeholderTitle: '—', pendingStatus: null }
  },
  computed: {
    effectiveStatus(){
      return (this.pendingStatus || this.task?.status || 'SCHEDULED')
    },
    typeColor(){
      // Map by status now (task_type deprecated)
      const s = (this.effectiveStatus || '').toLowerCase()
      if(s==='done') return '#16a34a'
      if(s==='cancelled') return '#dc2626'
      return '#4A90E2'
    },
    canDeleteTask(){
      try{
        const permsJson = localStorage.getItem('user-permissions')
        if(!permsJson) return true
        const perms = JSON.parse(permsJson)
        return !!perms.can_delete_task
      }catch(e){ return true }
    }
  },
  methods: {
    statusLabel(s){
      return s==='DONE'?this.$t('tasks.status.DONE'):s==='CANCELLED'?this.$t('tasks.status.CANCELLED'):this.$t('tasks.status.SCHEDULED')
    },
    clientName(task){
      const c = task.client || {}
      return `${c.first_name || ''} ${c.last_name || ''}`.trim() || c.email || this.$t('tasks.client')
    },
    singleStart(task){
      try{
        const s = new Date(task.start)
        const loc = (this.$i18n && this.$i18n.locale) || 'ru'
        const localeMap = { ru: 'ru-RU', pl: 'pl-PL' }
        const fmtLocale = localeMap[loc] || 'ru-RU'
        const d1 = s.toLocaleDateString(fmtLocale, { day:'2-digit', month:'long', year:'numeric' })
        const t1 = s.toLocaleTimeString(fmtLocale, { hour:'2-digit', minute:'2-digit' })
        return `${d1}, ${t1}`
      }catch{ return '' }
    },
    async markDone(){ await this.updateStatus('DONE') },
    async markCancelled(){ await this.updateStatus('CANCELLED') },
    async markScheduled(){ await this.updateStatus('SCHEDULED') },
    async updateStatus(s){
      const token = localStorage.getItem('user-token')
      try{
        await axios.put(`http://127.0.0.1:8000/api/tasks/${this.task.id}/`, { status: s }, { headers:{ Authorization:`Token ${token}` } })
        // keep card open; mirror new status locally without mutating props
        this.pendingStatus = s
        this.$emit('status-updated', s)
      }catch(e){ console.error('Task status update error', e); alert(this.$t('tasks.toasts.saveError') || 'Failed to update'); }
    },
    async performDelete(){
      if(!this.canDeleteTask){
        alert(this.$t('tasks.deleteForbidden') || 'Нет прав для удаления этой задачи')
        return
      }
      if(this.deleting) return
      this.deleting = true
      const token = localStorage.getItem('user-token')
      try {
        await axios.delete(`http://127.0.0.1:8000/api/tasks/${this.task.id}/`, { headers:{ Authorization:`Token ${token}` } })
        this.showDeleteConfirm = false
        this.$emit('updated')
      } catch(e){
        console.error('Task delete error', e)
        alert(this.$t('tasks.toasts.deleteError') || 'Failed to delete')
      } finally { this.deleting = false }
    },
    yesDeleteLabel(){
      const k1 = this.$t && this.$t('tasks.confirm.yesDelete')
      if(k1 && k1 !== 'tasks.confirm.yesDelete') return k1
      const k2 = this.$t && this.$t('common.yesDelete')
      if(k2 && k2 !== 'common.yesDelete') return k2
      return 'Да, удалить'
    }
  }
}
</script>

<style scoped>
.modal-overlay { position: fixed; inset:0; background: rgba(0,0,0,.4); display:flex; align-items:center; justify-content:center; z-index: 2200; }
.modal { background:var(--card-bg); width: 720px; max-width: 95vw; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,.2); border:1px solid var(--card-border); }
.modal-header { display:flex; align-items:center; justify-content:space-between; padding:14px 16px; border-bottom:1px solid #eee; }
.modal-header .left { display:flex; align-items:center; gap:10px; }
.type-dot { width:10px; height:10px; border-radius:50%; }
.title { margin:0; font-size:18px; }
.status { font-size:12px; padding:2px 8px; border-radius:999px; border:1px solid; }
.status.st-done { background:#ecfdf3; border-color:#bbf7d0; color:#065f46; }
.status.st-cancelled { background:#fef2f2; border-color:#fecaca; color:#7f1d1d; }
.status.st-scheduled { background:#f5f9ff; border-color:#d6e6ff; color:#1e3a8a; }
.content { padding: 14px 16px; display:flex; flex-direction:column; gap:10px; }
.row { display:grid; grid-template-columns: 140px 1fr; gap:12px; align-items:flex-start; }
.label { color:#64748b; font-size:13px; }
.value { color:#0f172a; }
.value .client-link { color:#2563eb; text-decoration:none; font-weight:600; }
.value .client-link:hover { text-decoration:underline; }
.value.prewrap { white-space: pre-wrap; }
.footer { display:flex; align-items:center; gap:8px; padding: 12px 16px; border-top:1px solid #eee; }
.footer .spacer { flex:1; }
.btn { height:36px; padding:0 12px; border:1px solid var(--btn-border); border-radius:8px; background:var(--btn-bg); color:var(--btn-text); cursor:pointer; }
.btn.edit { transition: background-color .22s ease, border-color .22s ease, color .22s ease, transform .22s ease, box-shadow .22s ease; }
.btn.edit:hover { transform:translateY(-2px); box-shadow:0 4px 10px rgba(0,0,0,.08); background:#f8fafc; border-color:#cfd8e3; }
.btn.edit:active { transform:translateY(0); box-shadow:0 2px 5px rgba(0,0,0,.06); }
.btn.warn { border-color:#fde68a; background:#fffbeb; }
/* New state buttons */
.btn.state-done { background:#ecfdf5; border:1px solid #a7f3d0; color:#036956; }
.btn.state-done:hover:not(:disabled) { background:#d1fae5; border-color:#6ee7b7; color:#035246; }
.btn.state-scheduled { background:#f0f7ff; border:1px solid #cfe0ff; color:#1e40af; }
.btn.state-scheduled:hover:not(:disabled) { background:#e5f0ff; border-color:#b9d4ff; color:#1d4ed8; }
.btn.state-cancelled { background:#fff8e6; border:1px solid #fde68a; color:#925c12; }
.btn.state-cancelled:hover:not(:disabled) { background:#fef3c7; border-color:#fcd34d; color:#7a4708; }
/* Shared animated interactions */
.btn.state-done, .btn.state-scheduled, .btn.state-cancelled, .btn.danger { transition: background-color .22s ease, border-color .22s ease, color .22s ease, transform .22s ease, box-shadow .22s ease; }
.btn.state-done:hover:not(:disabled), .btn.state-scheduled:hover:not(:disabled), .btn.state-cancelled:hover:not(:disabled), .btn.danger:hover:not(:disabled) { transform:translateY(-2px); box-shadow:0 4px 10px rgba(0,0,0,.08); }
.btn.state-done:active:not(:disabled), .btn.state-scheduled:active:not(:disabled), .btn.state-cancelled:active:not(:disabled), .btn.danger:active:not(:disabled) { transform:translateY(0); box-shadow:0 2px 5px rgba(0,0,0,.06); }
.btn.state-done:disabled, .btn.state-scheduled:disabled, .btn.state-cancelled:disabled { opacity:.55; cursor:not-allowed; transform:none; box-shadow:none; }
.btn.danger { background:#ffe5ea; border:1px solid #f5c3cd; color:#c53030; }
.btn.danger:hover { background:#ffe5ea; border-color:#efb5c1; color:#a61b1b; }
.icon { background:none; border:none; font-size:20px; cursor:pointer; }
/* Confirm (client-style) */
.confirm-dialog-overlay { position:fixed; inset:0; background:rgba(0,0,0,.45); display:flex; align-items:center; justify-content:center; z-index:2300; }
.confirm-dialog { background:#fff; border-radius:14px; padding:24px 32px 22px; width:440px; max-width:92vw; box-shadow:0 8px 28px rgba(0,0,0,.20); border:1px solid #e5e7eb; font-family:'Inter',sans-serif; }
.confirm-dialog .cd-text { margin:0 0 20px; font-size:16px; line-height:1.45; font-weight:500; color:#1f2937; text-align:center; }
.confirm-dialog-actions { display:flex; gap:14px; justify-content:center; }
.confirm-dialog-actions .btn { height:38px; padding:0 20px; border-radius:8px; font-weight:600; min-width:132px; }
.btn.danger-pink { background:#ffe5ea; border:1px solid #f5c3cd; color:#c53030; }
.btn.danger-pink:hover { background:#ffe5ea; border-color:#efb5c1; }
.confirm-dialog-actions .btn:not(.danger-pink) { background:#fff; border:1px solid #d7dee6; color:#1f2937; }
.confirm-dialog-actions .btn:not(.danger-pink):hover { border-color:#c7d2dc; }
.btn { font-weight:500; }
</style>
