<template>
  <div class="page">
    <header class="header">
      <h1>{{ $t('tasks.title') }}</h1>
      <button v-if="canCreateTask" class="btn add-clone" @click="toggleForm">{{ showForm ? $t('tasks.cancel') : $t('tasks.add') }}</button>
    </header>

    <section v-if="showForm" class="card form-card">
      <h3>{{ $t('tasks.newTask') }}</h3>
      <form @submit.prevent="createTask" class="form-grid">
        <div class="form-row">
          <ClientAutocomplete
            v-model="form.client_id"
            :placeholder="$t('tasks.chooseClient')"
            :label="$t('tasks.client')"
            @client-selected="onClientSelected"
          />
        </div>

        <div class="form-row">
          <label>{{ $t('tasks.titleLabel') }}</label>
          <input v-model="form.title" type="text" :placeholder="$t('tasks.titlePH')" />
        </div>

        <div class="form-row two">
          <div>
            <label>{{ $t('tasks.start') }}</label>
            <AltDateTimePicker mode="date" v-model="form.start" />
            <small class="muted" v-if="!form.start">{{ $t('tasks.optional') }}</small>
          </div>
          <div>
            <label>{{ $t('tasks.assignee') }}</label>
            <UiSelect
              v-model="form.assignee"
              :options="assigneeOptions"
              :placeholder="$t('tasks.unassigned')"
              aria-label="Assignee"
            />
            <small class="muted" v-if="usersFallback">{{ $t('tasks.assigneeFallback') }}</small>
          </div>
        </div>

        <div class="form-row">
          <label>{{ $t('tasks.form.location') }}</label>
          <textarea
            v-model="form.location"
            rows="2"
            :placeholder="$t('tasks.form.locationPH')"
            @input="autoGrow($event.target)"
          ></textarea>
        </div>

        <div class="form-row">
          <label>{{ $t('tasks.form.description') }}</label>
          <textarea v-model="form.description" rows="3" @input="autoGrow($event.target)"></textarea>
        </div>

        <div class="form-actions">
          <button type="submit" class="btn primary" :disabled="submitting">{{ $t('tasks.save') }}</button>
          <button type="button" class="btn" @click="toggleForm">{{ $t('tasks.cancel') }}</button>
        </div>
      </form>
    </section>

    <section class="card">
      <div class="list-header">
        <div class="filters">
          <input v-model="query" class="search" type="text" :placeholder="$t('tasks.filters.searchPH')" @input="debouncedLoad" />
          <UiSelect
            v-model="status"
            :options="statusOptions"
            :placeholder="$t('tasks.filters.statusAll')"
            aria-label="Status"
            @change="loadTasks"
          />
        </div>
      </div>
      <div v-if="users.length" class="assignee-filter-bar">
        <label class="af-label">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M12 12a5 5 0 1 0-5-5 5 5 0 0 0 5 5Zm0 2c-4.33 0-8 2.17-8 5v1h16v-1c0-2.83-3.67-5-8-5Z" />
          </svg>
          {{ $t('tasks.assignee') || $t('tasks.table.assignee') }}
        </label>
        <UiSelect
          class="af-select"
          v-model="assigneeFilter"
          :options="[{ value:'', label: ($t('clients.extra.allOption')||$t('tasks.filters.statusAll')) }, ...users.map(u => ({ value: String(u.id), label: userLabel(u) }))]"
          :placeholder="$t('clients.extra.allOption') || $t('tasks.filters.statusAll')"
          :aria-label="$t('tasks.assignee') || 'Assignee'"
          :disabled="disableAssigneeFilterForManager"
        />
        <button class="af-clear" v-if="assigneeFilter && !disableAssigneeFilterForManager" @click="assigneeFilter=''">{{ $t('clients.extra.reset') || 'Reset' }}</button>
      </div>

  <div v-if="loading" class="empty">{{ $t('tasks.loading') }}</div>
  <div v-else-if="filteredTasks.length === 0" class="empty">{{ $t('tasks.empty') }}</div>
  <table v-else class="tasks-table">
        <thead>
          <tr>
            <th>{{ $t('tasks.table.date') }}</th>
            <th>{{ $t('tasks.table.client') }}</th>
            <th>{{ $t('tasks.table.name') }}</th>
            <th>{{ $t('tasks.table.status') }}</th>
            <th>{{ $t('tasks.table.assignee') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in filteredTasks" :key="t.id" class="task-row" @click="openTask(t)">
            <td>{{ formatDate(t.start) }}</td>
            <td>{{ clientName(t) }}</td>
            <td>{{ t.title || placeholderTitle }}</td>
            <td>{{ statusLabel(t.status) }}</td>
            <td>{{ assigneeNames(t.assignees) }}</td>
          </tr>
        </tbody>
      </table>
    </section>
    <!-- Modal for viewing/editing a task -->
    <div v-if="showTaskModal" class="task-modal-overlay" @click.self="attemptCloseTaskModal">
      <div class="task-modal">
        <header class="tm-header">
          <h3>{{ editForm.title || placeholderTitle }}</h3>
          <button class="icon" @click="attemptCloseTaskModal">×</button>
        </header>
        <div class="tm-body">
          <div class="tm-grid">
            <label class="full">
              {{ $t('tasks.client') }}
              <ClientAutocomplete
                v-model="selectedClientIdEdit"
                :initial-label="clientInitialLabelEdit"
                :placeholder="$t('tasks.chooseClient')"
                @client-selected="onClientSelectedEdit"
                :disabled="!canEditTask"
              />
            </label>
            <label>
              {{ $t('tasks.titleLabel') }}
              <input type="text" v-model="editForm.title" :placeholder="$t('tasks.titlePH')" :disabled="!canEditTask" :readonly="!canEditTask" />
            </label>
            <label>
              {{ $t('tasks.start') }}
              <AltDateTimePicker mode="date" v-model="editForm.start" :disabled="!canEditTask" />
            </label>
            <label>
              {{ $t('tasks.table.status') }}
              <UiSelect v-model="editForm.status" :options="statusSelectOptions" aria-label="Status" :disabled="!canEditTask" />
            </label>
            <label>
              {{ $t('tasks.assignee') }}
              <UiSelect
                v-model="selectedAssigneeEdit"
                :options="[{ value:'', label: ($t('tasks.unassigned')||'— не назначен —') }, ...users.map(u => ({ value: String(u.id), label: userLabel(u) }))]"
                :placeholder="$t('tasks.unassigned')"
                aria-label="Assignee"
                :disabled="!canEditTask"
              />
              <small class="muted" v-if="usersFallback">{{ $t('tasks.assigneeFallback') }}</small>
            </label>
            <label class="full">
              {{ $t('tasks.form.location') }}
              <textarea
                v-model="editForm.location"
                rows="2"
                :placeholder="$t('tasks.form.locationPH')"
                :disabled="!canEditTask"
                @input="autoGrow($event.target)"
              ></textarea>
            </label>
            <label class="full">
              {{ $t('tasks.form.description') }}
              <textarea v-model="editForm.description" rows="3" :disabled="!canEditTask" @input="autoGrow($event.target)"></textarea>
            </label>
          </div>
        </div>
        <footer class="tm-footer">
          <button v-if="activeTask && activeTask.client" class="btn" @click="goToClient" :disabled="updating">{{ $t('tasks.gotoClient') }}</button>
          <button v-if="activeTask && canDeleteTask" class="btn danger" @click="showDeleteConfirm=true" :disabled="updating">{{ $t('common.delete') }}</button>
          <div class="spacer"></div>
          <button class="btn cancel" @click="attemptCloseTaskModal" :disabled="updating">{{ $t('common.cancel') }}</button>
          <button v-if="canEditTask" class="btn primary" @click="updateTask" :disabled="updating">{{ $t('common.save') }}</button>
        </footer>
        <!-- Custom centered delete confirmation -->
        <div v-if="showDeleteConfirm" class="confirm-dialog-overlay" @click.self="showDeleteConfirm=false">
          <div class="confirm-dialog">
            <p class="cd-text">{{ ($t('tasks.confirm.deleteOne') && $t('tasks.confirm.deleteOne')!=='tasks.confirm.deleteOne') ? $t('tasks.confirm.deleteOne') : 'Удалить задачу?' }}</p>
            <div class="confirm-dialog-actions">
              <button class="btn danger-pink" :disabled="updating" @click="deleteTask">{{ $t('common.delete') }}</button>
              <button class="btn" :disabled="updating" @click="showDeleteConfirm=false">{{ $t('common.cancel') }}</button>
            </div>
          </div>
        </div>

        <!-- Unsaved changes confirmation (calendar-style) -->
        <ConfirmDialog
          v-model="showUnsavedConfirm"
          :title="$t('tasks.confirm.discardTitle') || 'Несохранённые изменения'"
          :message="$t('tasks.confirm.discardChanges') || 'Есть несохранённые изменения. Закрыть без сохранения?'"
          :confirm-text="($t('common.continue') && $t('common.continue')!=='common.continue') ? $t('common.continue') : 'Продолжить'"
          :cancel-text="$t('common.cancel')"
          @confirm="discardEdits"
        />
      </div>
    </div>
  </div>
  
</template>

<script>
import axios from 'axios'
import ClientAutocomplete from '../components/ClientAutocomplete.vue'
import UiSelect from '../components/UiSelect.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

export default {
  name: 'TasksView',
  components:{ ClientAutocomplete, UiSelect, ConfirmDialog },
  data(){
    return {
      tasks: [],
      loading: false,
      clients: [],
      users: [],
      usersMap: {},
      usersFallback: false,
      currentUserId: null,
      role: '',
      showForm: false,
      submitting: false,
      query: '',
      status: '',
      assigneeFilter: '',
      form: {
        client_id: '',
        title: '',
        start: '', // YYYY-MM-DD
        assignee: '',
        location: '',
        description: ''
      },
  clientQuery: '',
  clientSuggestions: [],
  clientSearchTimer: null,
    showTaskModal: false,
      activeTask: null,
      editForm: { id:null, title:'', start:'', status:'SCHEDULED', location:'', description:'' },
    // Edit modal: client and assignee selections
    selectedClientIdEdit: null,
    clientInitialLabelEdit: '',
    selectedAssigneeEdit: '',
  updating: false,
  showDeleteConfirm: false,
  showUnsavedConfirm: false,
  initialEditSnapshot: null,
  placeholderTitle: '—'
    }
  },
  created(){
    // сначала получим текущего пользователя и роль, чтобы настроить фильтр "Ответственный" для менеджера
    this.loadMe().finally(() => {
      if ((this.role || '').toUpperCase() === 'MANAGER' && this.currentUserId) {
        this.assigneeFilter = String(this.currentUserId)
      }
      this.loadTasks()
      this.loadClients()
      this.loadUsers()
    })
  const now = new Date()
  this.form.start = this.toDateInput(now)
  this.$nextTick(() => { this.tryOpenFromRoute() })
  },
  watch: {
    '$route.query.task': function(){ this.tryOpenFromRoute() }
  },
  methods: {
    humanizeLogin(value){
      try{
        if(!value) return ''
        const local = String(value).split('@')[0]
        const parts = local.split(/[^A-Za-zА-Яа-яЁё]+/).map(p => p.replace(/\d+/g,'').trim()).filter(Boolean)
        if(!parts.length) return ''
        return parts.map(p => p.charAt(0).toUpperCase()+p.slice(1)).join(' ')
      }catch{ return '' }
    },
    userLabel(u){
      const full = `${u.first_name || ''} ${u.last_name || ''}`.trim()
      if(full) return full
      const base = u.username || u.email || ''
      return this.humanizeLogin(base) || base || (u.id ? ('ID '+u.id) : '')
    },
    token(){ return localStorage.getItem('user-token') },
    async loadTasks(){
      this.loading = true
      try{
        const params = {}
        if(this.status) params.status = this.status
        if(this.query) params.q = this.query
        const resp = await axios.get('http://127.0.0.1:8000/api/tasks/', {
          headers: { Authorization: 'Token ' + this.token() },
          params
        })
        // Defensive sort: upcoming first, past last
        const now = Date.now()
        const arr = Array.isArray(resp.data) ? resp.data.slice() : []
        arr.sort((a,b)=>{
          const sa = a && a.start ? new Date(a.start).getTime() : 0
          const sb = b && b.start ? new Date(b.start).getTime() : 0
          const apast = sa < now ? 1 : 0
          const bpast = sb < now ? 1 : 0
          if (apast !== bpast) return apast - bpast // 0 (upcoming) first
          if (apast === 0) return sa - sb          // upcoming asc
          return sb - sa                            // past desc
        })
        this.tasks = arr
      } finally {
        this.loading = false
      }
    },
    async loadClients(){
      try {
        const resp = await axios.get('http://127.0.0.1:8000/api/clients/?sort=-created_at', {
          headers: { Authorization: 'Token ' + this.token() }
        })
        this.clients = resp.data
      } catch(e){ console.error('Load clients error', e) }
    },
    async loadUsers(){
      try{
        const resp = await axios.get('http://127.0.0.1:8000/api/company/users/', {
          headers: { Authorization: 'Token ' + this.token() }
        })
        this.users = resp.data
      }catch(e){
        this.usersFallback = true
        const me = await axios.get('http://127.0.0.1:8000/api/user-info/', {
          headers: { Authorization: 'Token ' + this.token() }
        })
        this.users = [{
          id: me.data.id,
          username: me.data.username,
          first_name: me.data.first_name || '',
          last_name: me.data.last_name || '',
          email: me.data.email || ''
        }]
        // если ранее не удалось получить текущего пользователя, установим его отсюда
        if (!this.currentUserId) this.currentUserId = me.data.id
        if (!this.role && me?.data?.role) this.role = String(me.data.role || '').toUpperCase()
      } finally {
        const mapEntries = this.users.map(u => [u.id, this.userLabel(u)])
        this.usersMap = Object.fromEntries(mapEntries)
      }
    },
    async loadMe(){
      try{
        const me = await axios.get('http://127.0.0.1:8000/api/user-info/', {
          headers: { Authorization: 'Token ' + this.token() }
        })
        this.currentUserId = me?.data?.id || null
        this.role = String(me?.data?.role || '').toUpperCase()
      } catch(e){ /* no-op */ }
    },
    async createTask(){
      this.submitting = true
      try{
        let startDate = null, endDate = null
        if (this.form.start) {
          startDate = new Date(this.form.start + 'T00:00:00')
          endDate = new Date(startDate.getTime() + 24*60*60*1000)
        }
        const clientIdNum = this.form.client_id ? Number(this.form.client_id) : null
        const assigneeNum = this.form.assignee ? Number(this.form.assignee) : null
        const payload = {
          ...(clientIdNum!=null && !Number.isNaN(clientIdNum) ? { client_id: clientIdNum } : {}),
          title: this.form.title,
          ...(startDate ? { start: startDate.toISOString() } : {}),
          ...(endDate ? { end: endDate.toISOString() } : {}),
          all_day: true,
          status: 'SCHEDULED',
          location: this.form.location,
          description: this.form.description,
          assignees: assigneeNum && !Number.isNaN(assigneeNum) ? [assigneeNum] : []
        }
        await axios.post('http://127.0.0.1:8000/api/tasks/', payload, {
          headers: { Authorization: 'Token ' + this.token() }
        })
        this.toggleForm()
        this.loadTasks()
      } catch(e){
        if(e && e.validation){
          alert(e.message)
        } else if(e?.response?.data){
          console.error('Create task 400', e.response.data)
          const msg = typeof e.response.data === 'string' ? e.response.data : JSON.stringify(e.response.data)
          alert(msg)
        } else {
          console.error('Create task error', e)
          alert(this.$t('tasks.createError'))
        }
      } finally {
        this.submitting = false
      }
    },
    toggleForm(){ this.showForm = !this.showForm },
  onClientSelected(){ },
    toDateInput(d){
      const pad = n => String(n).padStart(2,'0')
      return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`
    },
    formatDate(dt){
      const loc = (this.$i18n && this.$i18n.locale) || 'ru';
      const map = { ru: 'ru-RU', pl: 'pl-PL' };
      try{ return new Date(dt).toLocaleDateString(map[loc] || 'ru-RU', { day:'2-digit', month:'2-digit', year:'numeric' }) }
      catch{ return '' }
    },
    statusLabel(s){ return s==='SCHEDULED' ? this.$t('tasks.status.SCHEDULED') : s==='DONE' ? this.$t('tasks.status.DONE') : this.$t('tasks.status.CANCELLED') },
    clientName(t){
      if(t.client) return `${t.client.first_name || ''} ${t.client.last_name || ''}`.trim()
      return ''
    },
    assigneeNames(ids){
      if(!ids || !ids.length) return ''
      return ids.map(id => this.usersMap[id] || `ID ${id}`).join(', ')
    },
    openTask(t){
      this.activeTask = t
      this.editForm.id = t.id
      this.editForm.title = t.title || ''
      this.editForm.status = t.status
  this.editForm.start = t.start ? this.toDateInput(new Date(t.start)) : ''
      this.editForm.location = t.location || ''
      this.editForm.description = t.description || ''
      // Prefill client & assignee fields
      const cid = (t && (
        (t.client && typeof t.client === 'object' && t.client.id) ? t.client.id :
        (typeof t.client === 'number') ? t.client : t.client_id || null
      )) || null
      this.selectedClientIdEdit = cid
      if (t && t.client && typeof t.client === 'object'){
        const fn = t.client.first_name || ''
        const ln = t.client.last_name || ''
        this.clientInitialLabelEdit = `${fn} ${ln}`.trim()
      } else {
        this.clientInitialLabelEdit = this.clientName(t)
      }
      if (Array.isArray(t.assignees) && t.assignees.length){
        this.selectedAssigneeEdit = String(t.assignees[0])
      } else if (t.assignee){
        this.selectedAssigneeEdit = String(t.assignee)
      } else {
        this.selectedAssigneeEdit = ''
      }
      this.showTaskModal = true
  this.showDeleteConfirm = false
      // snapshot for unsaved-changes detection
      this.initialEditSnapshot = {
        title: this.editForm.title || '',
        start: this.editForm.start || '',
        status: this.editForm.status || '',
        location: this.editForm.location || '',
        description: this.editForm.description || '',
        clientId: this.selectedClientIdEdit != null ? String(this.selectedClientIdEdit) : '',
        assignee: this.selectedAssigneeEdit != null ? String(this.selectedAssigneeEdit) : ''
      }
    },
    tryOpenFromRoute(){
      const id = Number(this.$route.query.task)
      if(!id || !this.tasks.length) return
      const found = this.tasks.find(t => t.id === id)
      if(found) this.openTask(found)
    },
    closeTaskModal(){
      if(this.updating) return
      this.showTaskModal = false
      this.activeTask = null
  this.showDeleteConfirm = false
    },
    attemptCloseTaskModal(){
      if(this.updating) return
      if(this.canEditTask && this.isEditDirty()){
        this.showUnsavedConfirm = true
        return
      }
      this.closeTaskModal()
    },
    isEditDirty(){
      try{
        const snap = this.initialEditSnapshot || {}
        const cur = {
          title: this.editForm.title || '',
          start: this.editForm.start || '',
          status: this.editForm.status || '',
          location: this.editForm.location || '',
          description: this.editForm.description || '',
          clientId: this.selectedClientIdEdit != null ? String(this.selectedClientIdEdit) : '',
          assignee: this.selectedAssigneeEdit != null ? String(this.selectedAssigneeEdit) : ''
        }
        return (
          snap.title !== cur.title ||
          snap.start !== cur.start ||
          snap.status !== cur.status ||
          snap.location !== cur.location ||
          snap.description !== cur.description ||
          snap.clientId !== cur.clientId ||
          snap.assignee !== cur.assignee
        )
      }catch{ return false }
    },
    async confirmUnsaved(action){
      if(action === 'save'){
        this.showUnsavedConfirm = false
        await this.updateTask()
        return
      }
      if(action === 'discard'){
        this.showUnsavedConfirm = false
        this.closeTaskModal()
        return
      }
      // cancel
      this.showUnsavedConfirm = false
    },
    discardEdits(){
      this.showUnsavedConfirm = false
      this.closeTaskModal()
    },
    async updateTask(){
      if(!this.canEditTask){
        alert(this.tr('tasks.updateForbidden','Нет прав для редактирования этой задачи'))
        return
      }
      if(!this.editForm.id) return
      this.updating = true
      try {
        let startDate=null, endDate=null
        if (this.editForm.start) {
          startDate = new Date(this.editForm.start + 'T00:00:00')
          endDate = new Date(startDate.getTime() + 24*60*60*1000)
        }
        // Build full payload for PUT
        // Resolve client id: prefer edited value, else from current task
        const existingCid = (this.activeTask && (
          (this.activeTask.client && this.activeTask.client.id) ? this.activeTask.client.id : this.activeTask.client_id || null
        )) || null
        const resolvedCid = (this.selectedClientIdEdit !== null && this.selectedClientIdEdit !== '')
          ? Number(this.selectedClientIdEdit)
          : (existingCid != null ? Number(existingCid) : null)

        // Resolve assignees: prefer edited single, else keep current list
        let resolvedAssignees = []
        if (this.selectedAssigneeEdit !== ''){
          const aid = Number(this.selectedAssigneeEdit)
          if (!Number.isNaN(aid)) resolvedAssignees = [aid]
        } else if (Array.isArray(this.activeTask?.assignees)) {
          resolvedAssignees = this.activeTask.assignees.filter(x => x != null).map(n => Number(n)).filter(n => !Number.isNaN(n))
        }

        const payload = {
          title: this.editForm.title,
          ...(startDate ? { start: startDate.toISOString() } : {}),
          ...(endDate ? { end: endDate.toISOString() } : {}),
          status: this.editForm.status,
          all_day: true,
          location: this.editForm.location,
          description: this.editForm.description,
          ...(resolvedCid!=null && !Number.isNaN(resolvedCid) ? { client_id: resolvedCid } : {}),
          assignees: resolvedAssignees
        }
        // Robust update: try PATCH first (partial), fallback to PUT on 405
        const headers = { Authorization:'Token '+this.token() }
        const taskId = Number(this.editForm.id)
        const url = `/api/tasks/${taskId}/`
        try {
          await axios.patch(url, payload, { headers })
        } catch(err){
          const status = err?.response?.status
          if (status === 405) {
            await axios.put(url, payload, { headers })
          } else {
            throw err
          }
        }
        this.showTaskModal = false
        await this.loadTasks()
      } catch(e){
        const status = e?.response?.status
        const data = e?.response?.data
        if (status === 403) {
          alert(this.tr('tasks.updateForbidden','Нет прав для редактирования этой задачи'))
        } else if (status === 405) {
          alert(this.tr('tasks.updateMethodNotAllowed','Метод не разрешён для этого URL'))
        } else if (data) {
          const msg = typeof data === 'string' ? data : JSON.stringify(data)
          alert(msg)
        }
        console.error('Update task error', e)
      }
      finally { this.updating = false }
    },
    async deleteTask(){
      if(!this.canDeleteTask){
        alert(this.tr('tasks.deleteForbidden','Нет прав для удаления этой задачи'))
        return
      }
      if(!this.activeTask || !this.activeTask.id) return
      this.updating = true
      try{
        const id = Number(this.activeTask.id)
        const url = `/api/tasks/${id}/`
        await axios.delete(url, { headers: { Authorization:'Token '+this.token() } })
        this.showDeleteConfirm = false
        this.showTaskModal = false
        await this.loadTasks()
      }catch(e){
        const status = e?.response?.status
        if(status === 403){
          alert(this.tr('tasks.deleteForbidden','Нет прав для удаления этой задачи'))
        } else {
          const data = e?.response?.data
          const msg = data ? (typeof data === 'string' ? data : JSON.stringify(data)) : this.tr('tasks.deleteError','Не удалось удалить задачу')
          alert(msg)
        }
        console.error('Delete task error', e)
      } finally {
        this.updating = false
      }
    },
    onClientSelectedEdit(c){
      this.selectedClientIdEdit = c?.id || null
      this.clientInitialLabelEdit = c ? `${c.first_name || ''} ${c.last_name || ''}`.trim() : ''
    },
    goToClient(){
      if(!this.activeTask || !this.activeTask.client) return
      const id = this.activeTask.client.id
      if(!id) return
      this.closeTaskModal()
      this.$router.push({ name:'client-detail', params:{ id } })
    },
    debouncedLoad: (() => {
      let timer
      return function(){
        clearTimeout(timer)
        timer = setTimeout(() => this.loadTasks(), 400)
      }
    })(),
    tr(key, fallback){
      try{ const v = this.$t ? this.$t(key) : key; return (v === key) ? fallback : v } catch { return fallback }
    },
    autoGrow(el){
      if(!el) return
      el.style.height = 'auto'
      el.style.height = el.scrollHeight + 'px'
    }
  }
  ,computed:{
    canCreateTask() {
      try {
        const permsJson = localStorage.getItem('user-permissions');
        if (!permsJson) return true;
        const perms = JSON.parse(permsJson);
        return !!perms.can_create_task;
      } catch (e) { return true; }
    },
    canEditTask() {
      try {
        const permsJson = localStorage.getItem('user-permissions');
        if (!permsJson) return true;
        const perms = JSON.parse(permsJson);
        return !!perms.can_edit_task;
      } catch (e) { return true; }
    },
    canDeleteTask(){
      try{
        const permsJson = localStorage.getItem('user-permissions')
        if(!permsJson) return true
        const perms = JSON.parse(permsJson)
        return !!perms.can_delete_task
      }catch(e){ return true }
    },
    disableAssigneeFilterForManager(){
      return (this.role || '').toUpperCase() === 'MANAGER'
    },
    assigneeOptions(){
      return [
        { value:'', label: this.$t('tasks.unassigned') },
        ...this.users.map(u => ({ value: String(u.id), label: this.userLabel(u) }))
      ]
    },
    statusSelectOptions(){
      return [
        { value:'SCHEDULED', label: this.$t('tasks.status.SCHEDULED') },
        { value:'DONE', label: this.$t('tasks.status.DONE') },
        { value:'CANCELLED', label: this.$t('tasks.status.CANCELLED') }
      ]
    },
    statusOptions(){
      return [
        { value:'', label: this.$t('tasks.filters.statusAll') },
        { value:'SCHEDULED', label: this.$t('tasks.status.SCHEDULED') },
        { value:'DONE', label: this.$t('tasks.status.DONE') },
        { value:'CANCELLED', label: this.$t('tasks.status.CANCELLED') }
      ]
    },
    filteredTasks(){
      // Если менеджер — показываем только задачи, где он ответственным (UI-фильтр необнуляемый)
      if (this.disableAssigneeFilterForManager && this.currentUserId) {
        const id = Number(this.currentUserId)
        return this.tasks.filter(t => Array.isArray(t.assignees) && t.assignees.includes(id))
      }
      if(!this.assigneeFilter) return this.tasks
      const id = Number(this.assigneeFilter)
      return this.tasks.filter(t => Array.isArray(t.assignees) && t.assignees.includes(id))
    }
  }
}
</script>

<style scoped>
.page { padding: 24px; }
.header { display:flex; align-items:center; justify-content:space-between; margin-bottom:16px; }
.btn { border:1px solid var(--btn-border); background:var(--btn-bg); color:var(--btn-text); padding:10px 20px; border-radius:8px; font-weight:600; font-size:14px; transition:background .25s, color .25s, border-color .25s, box-shadow .25s, transform .25s; }
.btn:hover { background: var(--primary-color,#4A90E2); color:#fff; border-color: var(--primary-color,#4A90E2); }
.btn.add-clone:hover { transform:translateY(-2px); box-shadow:0 6px 14px -4px rgba(0,0,0,.16); }
.btn.add-clone:active { transform:translateY(0); box-shadow:0 3px 8px -3px rgba(0,0,0,.18); }
.btn.primary { background: var(--primary-color); color:#fff; border-color: var(--primary-color); }
.btn.danger { background:rgba(255,82,82,0.12); border:1px solid rgba(255,82,82,0.45); color:#c53030; }
.btn.danger:hover { background:rgba(255,82,82,0.18); border-color:rgba(255,82,82,0.6); color:#a61b1b; }
.btn.danger:disabled { opacity:.55; cursor:not-allowed; background:rgba(255,82,82,0.12); }
.card { background: var(--card-bg); border:1px solid var(--card-border); border-radius:12px; padding:16px; }
.form-card { margin-bottom:16px; }
.form-grid { display:grid; gap:14px; max-width:1100px; }
.form-row { display:flex; flex-direction:column; gap:6px; }
.form-row.two { display:grid; grid-template-columns: minmax(0,1.1fr) minmax(0,0.9fr); gap:16px; }
.form-row.two > div { display:flex; flex-direction:column; gap:6px; }
textarea { resize:none; overflow:hidden; }
label { color:#334155; font-weight:600; }
.checkbox { display:flex; align-items:center; gap:8px; font-weight:600; }
.form-actions { display:flex; gap:10px; }
.list-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:8px; }
.filters { display:flex; gap:8px; }
.search { min-width:260px; }
.empty { padding:12px; color:#64748b; }
.assignee-filter-bar { display:flex; align-items:center; gap:16px; margin:12px 0 4px; background:#fff; border:1px solid #e0e6ed; border-radius:10px; padding:10px 18px; }
.assignee-filter-bar .af-label { display:inline-flex; align-items:center; gap:6px; font-size:13px; font-weight:600; color:#5a6a7b; }
.assignee-filter-bar .af-select { min-width:220px; }
.assignee-filter-bar .af-clear { background:none; border:none; color:#111827; font-size:12px; cursor:pointer; }
.assignee-filter-bar .af-clear:hover { text-decoration:underline; }
.tasks-table { width:100%; border-collapse:collapse; background:var(--card-bg); border-radius:12px; box-shadow:0 8px 30px rgba(0,0,0,0.07); overflow:hidden; table-layout:fixed; font-family:'Inter',sans-serif; }
.tasks-table th, .tasks-table td { padding:14px 16px; text-align:left; font-size:14px; }
.tasks-table thead th { background:#f7f9fc; font-weight:700; color:#5a6a7b; }
.tasks-table td { border-top:1px solid #e0e6ed; white-space:nowrap; }
.tasks-table td:nth-child(1),
.tasks-table td:nth-child(2),
.tasks-table td:nth-child(3) { overflow:hidden; text-overflow:ellipsis; max-width:0; }
.task-row { cursor:pointer; transition: background-color .2s ease; }
.tasks-table tbody tr.task-row:nth-child(even) { background:#f7f9fc; }
.task-row:hover { background:#eef3f9; }
.tasks-table td:nth-child(4) { font-weight:600; }
.task-modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,.35); display:flex; align-items:center; justify-content:center; z-index:2500; }
.task-modal { background:var(--card-bg); border:1px solid var(--card-border); width:640px; max-width:95vw; border-radius:14px; box-shadow:0 10px 32px rgba(0,0,0,.18); display:flex; flex-direction:column; }
.tm-header { display:flex; align-items:center; justify-content:space-between; padding:14px 18px; border-bottom:1px solid #e5e7eb; }
.tm-body { padding:16px 18px; }
.tm-grid { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
.tm-grid label.full { grid-column: 1 / -1; }
.tm-grid label { display:flex; flex-direction:column; gap:6px; font-size:14px; font-weight:500; color:#334155; }
.tm-grid input:disabled, .tm-grid input:read-only { background:#f1f5f9; color:#64748b; cursor:not-allowed; }
.tm-footer { display:flex; align-items:center; gap:10px; padding:14px 18px; border-top:1px solid #e5e7eb; }
.tm-footer .spacer { flex:1; }
.tm-footer .btn { transition: transform .18s ease, box-shadow .18s ease, background-color .18s ease, border-color .18s ease, color .18s ease; }
.tm-footer .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 18px -8px rgba(0,0,0,.22); }
.tm-footer .btn:active { transform: translateY(0); box-shadow: 0 6px 12px -8px rgba(0,0,0,.20); }
/* Keep Cancel button hover neutral (no color swap), but retain motion */
.tm-footer .btn.cancel:hover { background: var(--btn-bg); color: var(--btn-text); border-color: var(--btn-border); }
.icon { background:none; border:none; font-size:20px; cursor:pointer; }
.muted { color:#64748b; font-size:12px; }
.confirm-dialog-overlay { position:fixed; inset:0; background:rgba(0,0,0,.45); display:flex; align-items:center; justify-content:center; z-index:2600; }
.confirm-dialog { background:#fff; border-radius:14px; padding:24px 32px 22px; width:420px; max-width:92vw; box-shadow:0 8px 28px rgba(0,0,0,.20); border:1px solid #e5e7eb; font-family:'Inter',sans-serif; }
.confirm-dialog .cd-text { margin:0 0 20px; font-size:16px; line-height:1.45; font-weight:500; color:#1f2937; text-align:center; }
.confirm-dialog-actions { display:flex; gap:14px; justify-content:center; }
.confirm-dialog-actions .btn { height:38px; padding:0 20px; border-radius:8px; font-weight:600; min-width:132px; transition: transform .18s ease, box-shadow .18s ease, background-color .18s ease, border-color .18s ease, color .18s ease; }
.confirm-dialog-actions .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 18px -8px rgba(0,0,0,.22); }
.confirm-dialog-actions .btn:active { transform: translateY(0); box-shadow: 0 6px 12px -8px rgba(0,0,0,.20); }
.btn.danger-pink { background:#ffe5ea; border:1px solid #f5c3cd; color:#c53030; }
.btn.danger-pink:hover { background:#ffdfe6; border-color:#efb5c1; }
.confirm-dialog-actions .btn:not(.danger-pink) { background:#fff; border:1px solid #d7dee6; color:#1f2937; }
.confirm-dialog-actions .btn:not(.danger-pink):hover { border-color:#c7d2dc; }
</style>
