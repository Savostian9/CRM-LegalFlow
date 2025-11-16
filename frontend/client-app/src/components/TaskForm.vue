<template>
  <div class="modal-overlay" @click.self="tryClose">
    <div class="modal">
      <header class="modal-header">
        <div class="mh-left">
          <button v-if="task" class="icon back" @click="$emit('back', task)" :title="$t('tasks.backToTask') || 'Назад к задаче'">←</button>
          <h3>{{ task ? $t('tasks.editTask') : $t('tasks.newTask') }}</h3>
        </div>
        <button class="icon" @click="tryClose">×</button>
      </header>
      <form @submit.prevent="save" class="modal-body">
        <div class="grid">
          <ClientAutocomplete
            :label="$t('tasks.client')"
            v-model="form.client_id"
            :initial-label="clientQuery"
            :placeholder="$t('tasks.chooseClient')"
            @client-selected="onClientSelected"
          />
          <label>
            {{ $t('tasks.titleLabel') }}
            <input type="text" v-model="form.title" :placeholder="$t('tasks.titlePH')" />
          </label>
          <label>
            {{ $t('tasks.start') }}
            <AltDateTimePicker mode="date" v-model="form.start" />
            <small class="muted" v-if="!form.start">{{ $t('tasks.optional') || 'Необязательно: по умолчанию сейчас' }}</small>
          </label>
          <label>
            {{ $t('tasks.assignee') }}
            <UiSelect
              v-model="form.assignee"
              :options="assigneeOptions"
              :placeholder="$t('tasks.unassigned')"
              aria-label="Assignee"
            />
            <small class="muted" v-if="usersFallback">{{ $t('tasks.assigneeFallback') }}</small>
          </label>
          <label>
            {{ $t('tasks.table.status') }}
            <UiSelect
              v-model="form.status"
              :options="statusOptions"
              aria-label="Status"
            />
          </label>
          <label>
            {{ $t('tasks.form.location') }}
            <textarea
              v-model="form.location"
              rows="2"
              :placeholder="$t('tasks.form.locationPH')"
              @input="autoGrow($event.target)"
            ></textarea>
          </label>
          <!-- Reminder field removed per request -->
          <label class="full">
            {{ $t('tasks.form.description') }}
            <textarea v-model="form.description" rows="4" ref="descRef" @input="autoGrow($event.target)"></textarea>
          </label>
        </div>
        <footer class="footer">
          <button type="button" class="btn danger" v-if="task && canDeleteTask" @click="showDeleteConfirm=true">{{ $t('common.delete') }}</button>
          <div class="spacer"></div>
          <button type="button" class="btn" @click="tryClose">{{ $t('common.cancel') }}</button>
          <button type="submit" class="btn primary" :disabled="!canEditTask">{{ $t('common.save') }}</button>
        </footer>
      </form>
      <!-- Custom deletion confirm (client-style) -->
      <div v-if="showDeleteConfirm" class="confirm-dialog-overlay" @click.self="showDeleteConfirm=false">
        <div class="confirm-dialog">
          <p class="cd-text">{{ ($t('tasks.confirm.deleteOne') && $t('tasks.confirm.deleteOne')!=='tasks.confirm.deleteOne') ? $t('tasks.confirm.deleteOne') : 'Удалить задачу?' }}</p>
          <div class="confirm-dialog-actions">
            <button class="btn danger-pink" :disabled="deleting" @click="performDelete">{{ yesDeleteLabel() }}</button>
            <button class="btn" :disabled="deleting" @click="showDeleteConfirm=false">{{ $t('common.cancel') }}</button>
          </div>
        </div>
      </div>
      <ConfirmDialog
        v-model="showDiscardConfirm"
        :title="$t('tasks.confirm.discardTitle') || 'Несохраненные изменения'"
        :message="$t('tasks.confirm.discardChanges') || 'Отменить несохраненные изменения?'"
        :confirm-text="($t('common.continue') && $t('common.continue')!=='common.continue') ? $t('common.continue') : 'Продолжить'"
        :cancel-text="$t('common.cancel')"
        @confirm="proceedDiscard"
        @cancel="cancelDiscard"
      />
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import ClientAutocomplete from './ClientAutocomplete.vue'
import ConfirmDialog from './ConfirmDialog.vue'
import UiSelect from './UiSelect.vue'

export default {
  name: 'TaskForm',
  components:{ ClientAutocomplete, ConfirmDialog, UiSelect },
  props: { task: Object, initialDate: Date },
  emits: ['close', 'saved', 'back'],
  data() {
    const startBase = this.task ? this.task.start : (this.initialDate ? this.initialDate.toISOString() : new Date().toISOString())
    const toInput = (val) => {
      try {
        if(!val) return ''
        const d = new Date(val)
        if (isNaN(d.getTime())) return ''
        const pad = n => String(n).padStart(2,'0')
        return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`
      } catch { return '' }
    }
    const form = this.task ? {
      title: this.task.title || '',
      status: this.task.status || 'SCHEDULED',
      start: toInput(startBase),
      assignee: (this.task.assignees && this.task.assignees.length) ? this.task.assignees[0] : '',
      client_id: this.task.client_id || (this.task.client && this.task.client.id) || null,
      description: this.task.description || '',
      location: this.task.location || '',
  // reminder_minutes removed
    } : (()=>{
      return {
        title: '', status: 'SCHEDULED',
        start: toInput(startBase), assignee: '',
  client_id: null, description: '', location: ''
      }
    })()
    const clientQuery = this.task && this.task.client ? `${this.task.client.first_name || ''} ${this.task.client.last_name || ''}`.trim() : ''
  return { form, dirty:false, clientQuery, clientSuggestions:[], debounceTimer:null, users:[], usersMap:{}, usersFallback:false, showDeleteConfirm:false, deleting:false, showDiscardConfirm:false }
  },
  created(){
    this.loadUsers();
  },
  watch: {
    form: { deep: true, handler() { this.dirty = true; } }
  },
  methods: {
    autoGrow(el){
      if(!el) return
      el.style.height = 'auto'
      el.style.height = el.scrollHeight + 'px'
    },
    getCompanyName(u){
      try {
        if (!u) return ''
        const cand = [
          'company_name', 'companyName', 'company_title', 'organization', 'org_name', 'business_name', 'firm', 'company'
        ]
        for (const k of cand){
          const v = u[k]
          if (!v) continue
          if (typeof v === 'string' && v.trim()) return v.trim()
          if (typeof v === 'object'){
            const inner = v.name || v.title || v.company_name || v.companyName
            if (inner && String(inner).trim()) return String(inner).trim()
          }
        }
      } catch {/* ignore */}
      return ''
    },
    assigneeLabel(u){
      const full = `${u?.first_name || ''} ${u?.last_name || ''}`.trim()
      if (full) return full
      const company = this.getCompanyName(u)
      if (company) return company
      return (u?.email || u?.username || (u?.id != null ? ('ID ' + u.id) : ''))
    },
    async loadUsers(){
      const token = localStorage.getItem('user-token')
      if(!token) return
      try {
        const resp = await axios.get('http://127.0.0.1:8000/api/company/users/', { headers:{ Authorization:`Token ${token}` } })
        this.users = Array.isArray(resp.data) ? resp.data : []
        // Merge current user's Settings so first/last/company from settings are reflected in the options
        try {
          const me = await axios.get('http://127.0.0.1:8000/api/user-info/', { headers:{ Authorization:`Token ${token}` } })
          if (me && me.data && me.data.id != null){
            const idx = this.users.findIndex(u => Number(u.id) === Number(me.data.id))
            const enriched = {
              id: me.data.id,
              username: me.data.username || (idx !== -1 ? this.users[idx].username : ''),
              email: me.data.email || (idx !== -1 ? this.users[idx].email : ''),
              first_name: me.data.first_name || (idx !== -1 ? this.users[idx].first_name : ''),
              last_name: me.data.last_name || (idx !== -1 ? this.users[idx].last_name : ''),
              company_name: me.data.company_name || (idx !== -1 ? this.users[idx].company_name : undefined),
              company: (idx !== -1 ? this.users[idx].company : undefined)
            }
            if (idx !== -1) this.users.splice(idx, 1, { ...this.users[idx], ...enriched })
            else this.users.push(enriched)
          }
        } catch { /* ignore settings merge errors */ }
      } catch(e){
        this.usersFallback = true
        try {
          const me = await axios.get('http://127.0.0.1:8000/api/user-info/', { headers:{ Authorization:`Token ${token}` } })
          this.users = [{
            id: me.data.id,
            username: me.data.username,
            email: me.data.email || '',
            first_name: me.data.first_name || '',
            last_name: me.data.last_name || '',
            company_name: me.data.company_name || ''
          }]
        } catch { /* ignore */ }
      } finally {
        this.usersMap = Object.fromEntries(this.users.map(u => [u.id, this.assigneeLabel(u)]))
      }
    },
    tryClose() {
      if (this.dirty) {
        this.showDiscardConfirm = true;
        return;
      }
      this.$emit('close');
    },
    async save() {
      let startDate = null, endDate = null;
      if (this.form.start) {
        startDate = new Date(this.form.start + 'T00:00:00');
        endDate = new Date(startDate.getTime() + 24*60*60*1000);
      }
      const token = localStorage.getItem('user-token');
      const clientIdNum = this.form.client_id ? Number(this.form.client_id) : null
      const assigneeNum = this.form.assignee ? Number(this.form.assignee) : null
      const payload = {
        title: this.form.title,
        status: this.form.status,
  ...(startDate ? { start: startDate.toISOString() } : {}),
  ...(endDate ? { end: endDate.toISOString() } : {}),
        all_day: true,
        ...(clientIdNum!=null && !Number.isNaN(clientIdNum) ? { client_id: clientIdNum } : {}),
        description: this.form.description,
        location: this.form.location,
  // reminder_minutes removed
        assignees: assigneeNum && !Number.isNaN(assigneeNum) ? [assigneeNum] : []
      };
      try {
        if (this.task && this.task.id) {
          await axios.put(`http://127.0.0.1:8000/api/tasks/${this.task.id}/`, payload, { headers: { Authorization: `Token ${token}` } });
        } else {
          await axios.post('http://127.0.0.1:8000/api/tasks/', payload, { headers: { Authorization: `Token ${token}` } });
        }
        this.$emit('saved');
      } catch (e) {
        console.error('Task save error', e?.response?.data || e);
        const details = e?.response?.data;
        if(details){
          const msg = typeof details === 'string' ? details : JSON.stringify(details);
          alert(msg);
        } else {
          const kErr = 'tasks.toasts.saveError';
          alert(this.$t(kErr) || 'Failed to save task');
        }
      }
    },
    onClientSelected(c){ this.form.client_id = c.id; this.clientQuery = `${c.first_name || ''} ${c.last_name || ''}`.trim(); },
    async confirmDelete() {
      if (!this.task || !this.task.id) return;
      this.showDeleteConfirm = true;
    },
    async performDelete(){
      if (!this.task || !this.task.id || this.deleting) return;
      this.deleting = true;
      const token = localStorage.getItem('user-token');
      try {
        await axios.delete(`http://127.0.0.1:8000/api/tasks/${this.task.id}/`, { headers: { Authorization: `Token ${token}` } });
        this.showDeleteConfirm = false;
        this.$emit('saved');
      } catch(e){
        console.error('Task delete error', e);
        const kErr = 'tasks.toasts.deleteError';
        alert(this.$t(kErr) || 'Failed to delete task');
      } finally { this.deleting = false; }
    },
    yesDeleteLabel(){
      const k1 = this.$t && this.$t('tasks.confirm.yesDelete');
      if(k1 && k1 !== 'tasks.confirm.yesDelete') return k1;
      const k2 = this.$t && this.$t('common.yesDelete');
      if(k2 && k2 !== 'common.yesDelete') return k2;
      return 'Да, удалить';
    },
    proceedDiscard(){
      this.showDiscardConfirm = false;
      this.dirty = false;
      this.$emit('close');
    },
    cancelDiscard(){
      this.showDiscardConfirm = false;
    }
  },
  computed: {
    canEditTask() {
      try {
        const permsJson = localStorage.getItem('user-permissions');
        if (!permsJson) return true;
        const perms = JSON.parse(permsJson);
        return !!perms.can_edit_task;
      } catch (e) { return true; }
    },
    canDeleteTask() {
      try {
        const permsJson = localStorage.getItem('user-permissions');
        if (!permsJson) return true;
        const perms = JSON.parse(permsJson);
        return !!perms.can_delete_task;
      } catch (e) { return true; }
    },
    statusOptions(){
      return [
        { value: 'SCHEDULED', label: this.$t('tasks.status.SCHEDULED') },
        { value: 'DONE', label: this.$t('tasks.status.DONE') },
        { value: 'CANCELLED', label: this.$t('tasks.status.CANCELLED') }
      ]
    },
    assigneeOptions(){
      return [
        { value: '', label: this.$t('tasks.unassigned') },
        ...this.users.map(u => ({ value: String(u.id), label: this.assigneeLabel(u) }))
      ]
    }
  }
}
</script>

<script setup>
// Ensure users are loaded on mount when using <TaskForm>
</script>

<style scoped>
.modal-overlay { position: fixed; inset:0; background: rgba(0,0,0,.4); display:flex; align-items:center; justify-content:center; z-index: 2000; }
.modal { background:var(--card-bg); width: 720px; max-width: 95vw; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,.15); border:1px solid var(--card-border); }
.modal-header { display:flex; align-items:center; justify-content:space-between; padding:12px 16px; border-bottom:1px solid #eee; }
.modal-header .mh-left{ display:flex; align-items:center; gap:8px; }
.modal-header .icon.back{ font-size:20px; line-height:1; background:none; border:none; cursor:pointer; color:#334155; padding:2px 6px; border-radius:8px; transition:background .18s ease, transform .18s ease; }
.modal-header .icon.back:hover{ background:#f1f5f9; transform:translateY(-1px); }
.modal-header .icon.back:active{ transform:translateY(0); }
.modal-body { padding: 16px; }
.icon { background:none; border:none; font-size:20px; cursor:pointer; }
.grid { display:grid; grid-template-columns: repeat(2, 1fr); gap:12px; }
.grid label { display:flex; flex-direction:column; gap:6px; font-size:14px; color:#2c3e50; }
.grid input, .grid textarea { border:1px solid var(--form-border,#e2e8f0); border-radius:8px; padding:8px 10px; background:var(--form-bg,#fff); transition:border-color .18s ease, box-shadow .18s ease; }
.grid textarea { resize: none; overflow:hidden; }
.grid input:focus, .grid textarea:focus { outline:none; border-color:var(--form-border-focus,#4A9E80); box-shadow:var(--form-focus-ring,0 0 0 2px rgba(74,158,128,.18)); }
.grid label.full { grid-column: 1 / -1; }
.footer { display:flex; align-items:center; gap:8px; margin-top: 8px; }
.footer .spacer { flex:1; }
.btn { height:36px; padding:0 12px; border:1px solid var(--btn-border); border-radius:8px; background:var(--btn-bg); color:var(--btn-text); cursor:pointer; }
/* Subtle hover/press animations for footer buttons and enlarged size */
.footer .btn { height:42px; padding:0 18px; border-radius:10px; font-weight:600; transition: transform .18s ease, box-shadow .18s ease, background-color .18s ease, border-color .18s ease, color .18s ease; }
.footer .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 18px -8px rgba(0,0,0,.22); }
.footer .btn:active { transform: translateY(0); box-shadow: 0 6px 12px -8px rgba(0,0,0,.20); }
.btn.primary { background:var(--primary-color); color:#fff; border-color:var(--primary-color); }
/* Softer Delete button (less aggressive) */
.btn.danger { background:#ffe5ea; border:1px solid #f5c3cd; color:#c53030; }
.btn.danger:hover { background:#ffdfe6; border-color:#efb5c1; color:#b12727; }
.btn.danger:disabled { opacity:.6; background:#ffe5ea; border-color:#f1c8d0; color:#c26a6a; box-shadow:none; transform:none; }
.btn.danger-pink { background:#ffe5ea; border:1px solid #f5c3cd; color:#c53030; border-radius:8px; }
.btn.danger-pink:hover { background:#ffe5ea; border-color:#efb5c1; }
/* Confirm deletion styling (client style refined) */
.confirm-dialog-overlay { position: fixed; inset:0; background: rgba(0,0,0,.45); display:flex; align-items:center; justify-content:center; z-index: 2050; }
.confirm-dialog { background:#fff; border-radius:14px; padding:24px 32px 22px; width:440px; max-width:92vw; box-shadow:0 8px 28px rgba(0,0,0,.20); border:1px solid #e5e7eb; font-family:'Inter',sans-serif; }
.confirm-dialog .cd-text { margin:0 0 20px; font-size:16px; line-height:1.45; font-weight:500; color:#1f2937; text-align:center; }
.confirm-dialog-actions { display:flex; gap:14px; justify-content:center; }
.confirm-dialog-actions .btn { height:38px; padding:0 20px; border-radius:8px; font-weight:600; min-width:132px; }
.confirm-dialog-actions .btn:not(.danger-pink) { background:#fff; border:1px solid #d7dee6; color:#1f2937; }
.confirm-dialog-actions .btn:not(.danger-pink):hover { border-color:#c7d2dc; }
.suggest { list-style:none; margin:6px 0 0; padding:0; border:1px solid var(--card-border); border-radius:8px; max-height:160px; overflow:auto; background:var(--card-bg); }
.suggest li { padding:6px 10px; cursor:pointer; }
.suggest li:hover { background:#f7f9fc; }
</style>
