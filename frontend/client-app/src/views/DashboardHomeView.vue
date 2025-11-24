<template>
  <div class="content-wrapper">
    <header class="content-header">
      <h1>{{ $t('dashboard.title') }}</h1>
    </header>
    <div class="content-body">
      <div v-if="!isAssistant" class="widget finance">
        <div class="widget-header">
          <h3>{{ $t('dashboard.financeSummary') }}</h3>
        </div>
        <div v-if="finLoading" class="widget-empty">{{ $t('common.loading') }}</div>
        <div v-else class="finance-grid">
          <div class="kpi">
            <div class="kpi-title">{{ $t('dashboard.expectedPaymentsMonth') }}</div>
            <div class="kpi-value">{{ formatMoney(summary.expected_payments_month) }}</div>
          </div>
          <div class="kpi">
            <div class="kpi-title">{{ $t('dashboard.receiptsMonth') }}</div>
            <div class="kpi-value">{{ formatMoney(summary.receipts_month) }}</div>
          </div>
            <div class="kpi muted">
            <div class="kpi-title">{{ $t('dashboard.expectedPaymentsTotal') }}</div>
            <div class="kpi-value">{{ formatMoney(summary.expected_payments_total) }}</div>
          </div>
          <div class="kpi muted">
            <div class="kpi-title">{{ $t('dashboard.receiptsTotal') }}</div>
            <div class="kpi-value">{{ formatMoney(summary.receipts_total) }}</div>
          </div>
        </div>
      </div>
      <div class="widget">
        <div class="widget-header">
          <h3>{{ $t('dashboard.tasksUpcoming') }}</h3>
          <div class="tabs">
            <button :class="{active: tab==='today'}" @click="tab='today';load()">{{ $t('dashboard.today') }}</button>
            <button :class="{active: tab==='tomorrow'}" @click="tab='tomorrow';load()">{{ $t('dashboard.tomorrow') }}</button>
            <button :class="{active: tab==='week'}" @click="tab='week';load()">{{ $t('dashboard.week') }}</button>
            <button :class="{active: tab==='month'}" @click="tab='month';load()">{{ $t('dashboard.month') }}</button>
          </div>
        </div>
        <div v-if="loading" class="widget-empty">{{ $t('common.loading') }}</div>
        <div v-else-if="items.length===0" class="widget-empty empty-modern">
          <div class="empty-title">{{ tr('dashboard.noTasks','Нет задач.') }}</div>
          <div v-if="canCreateTask" class="empty-sub">{{ tr('dashboard.noTasksHint','Создайте задачу — это поможет не упустить важное.') }}</div>
          <div class="empty-actions">
            <button v-if="canCreateTask" class="btn" @click="openCreateModal">{{ tr('dashboard.createTask','Создать задачу') }}</button>
            <router-link class="btn outline" to="/dashboard/calendar">{{ tr('dashboard.openCalendar','Открыть календарь') }}</router-link>
          </div>
        </div>
          <ul v-else class="task-list">
          <li v-for="t in items"
              :key="t.id"
              class="task-row"
            @click="openCard(t)"
              role="button"
              tabindex="0"
            @keydown.enter.prevent="openCard(t)"
            @keydown.space.prevent="openCard(t)">
            <span class="type" :class="statusDotClass(t.status)"></span>
            <span class="date">{{ formatDate(t.start) }}</span>
            <span class="client">{{ t.client_name || '—' }}</span>
            <span class="title">{{ t.title || placeholderTitle }}</span>
            <span class="assignee">{{ getAssigneeLabel(t) }}</span>
            <span class="status" :class="t.status.toLowerCase()">{{ statusLabel(t.status) }}</span>
            <div class="actions">
              <button class="btn small" @click.stop="markDone(t)">{{ $t('dashboard.markDone') }}</button>
            </div>
          </li>
        </ul>
        <!-- View card like in Calendar -->
        <TaskCard
          v-if="showCard"
          :task="viewTask"
          @close="closeCard"
          @edit="openEditFromCard"
          @status-updated="onCardStatusUpdated"
          @updated="onCardUpdated"
        />

        <!-- Inline modal for a single task (edit) -->
        <div v-if="showTaskModal" class="task-modal-overlay" @click.self="closeTaskModal">
          <div class="task-modal">
            <header class="tm-header">
              <div class="tm-left">
                <button class="icon back" @click="backToCard" :title="tr('tasks.backToTask','Назад к задаче')">←</button>
                <h3>{{ editForm.title || placeholderTitle }}</h3>
              </div>
              <button class="icon" @click="closeTaskModal">×</button>
            </header>
            <div class="tm-body">
              <div class="tm-grid">
                <label class="full">
                  {{ $t('tasks.client') }}
                  <ClientAutocomplete
                    v-model="selectedClientId"
                    :initial-label="clientInitialLabel"
                    :placeholder="$t('tasks.chooseClient')"
                    @client-selected="(c)=>{ selectedClientId=c?.id||''; clientInitialLabel=(c ? `${c.first_name||''} ${c.last_name||''}`.trim() : '') }"
                  />
                </label>
                <label>
                  {{ $t('tasks.titleLabel') }}
                  <input type="text" v-model="editForm.title" :placeholder="$t('tasks.titlePH')"/>
                </label>
                <label>
                  {{ $t('tasks.start') }}
                  <AltDateTimePicker mode="date" v-model="editForm.start" />
                </label>
                <label>
                  {{ $t('tasks.table.status') }}
                  <UiSelect v-model="editForm.status" :options="[
                    { value:'SCHEDULED', label: $t('tasks.status.SCHEDULED') },
                    { value:'DONE', label: $t('tasks.status.DONE') },
                    { value:'CANCELLED', label: $t('tasks.status.CANCELLED') }
                  ]" aria-label="Status" />
                </label>
                <label>
                  {{ $t('tasks.assignee') }}
                  <UiSelect
                    v-model="selectedAssignee"
                    :options="assigneeOptions"
                    :placeholder="$t('tasks.unassigned')"
                    aria-label="Assignee"
                  />
                  <small class="muted" v-if="usersFallback">{{ $t('tasks.assigneeFallback') }}</small>
                </label>
                <label class="full">
                  {{ $t('tasks.form.location') }}
                  <textarea
                    v-model="editForm.location"
                    rows="2"
                    ref="editLocationRef"
                    @input="autoGrow($event.target)"
                  ></textarea>
                </label>
                <label class="full">
                  {{ $t('tasks.form.description') }}
                  <textarea
                    v-model="editForm.description"
                    rows="3"
                    ref="editDescriptionRef"
                    @input="autoGrow($event.target)"
                  ></textarea>
                </label>
              </div>
            </div>
            <footer class="tm-footer">
              <button v-if="activeClientId" class="btn outline" @click="goToClient" :disabled="updating">{{ $t('tasks.gotoClient') }}</button>
              <button v-if="canDeleteTask" class="btn danger" @click="askDeleteTask" :disabled="updating">{{ $t('common.delete') }}</button>
              <div class="spacer"></div>
              <button class="btn" @click="closeTaskModal" :disabled="updating">{{ $t('common.cancel') }}</button>
              <button class="btn primary" @click="updateTask" :disabled="updating">{{ updating ? (t('common.saving') || 'Сохранение...') : (t('common.save') || 'Сохранить') }}</button>
            </footer>
          </div>
        </div>
        <!-- Delete confirmation overlay -->
        <div v-if="showDeleteConfirm" class="confirm-overlay" @click.self="cancelDeleteTask">
          <div class="confirm-dialog-modern">
            <p class="confirm-message-modern">{{ t('tasks.confirm.deleteOne') || 'Удалить задачу?' }}</p>
            <div class="confirm-actions-modern">
              <button class="btn-modern danger-modern" :disabled="updating" @click="proceedDeleteTask">{{ updating ? t('common.loading') : (t('common.yesDelete') || 'Да, удалить') }}</button>
              <button class="btn-modern cancel-modern" :disabled="updating" @click="cancelDeleteTask">{{ t('common.cancel') || 'Отмена' }}</button>
            </div>
          </div>
        </div>
        <!-- Quick create task modal -->
        <div v-if="showCreateModal" class="task-modal-overlay" @click.self="onCreateOverlayClick">
          <div class="task-modal">
            <header class="tm-header">
              <h3>{{ tr('tasks.newTask','Новая задача') }}</h3>
              <button class="icon" @click="onCreateOverlayClick">×</button>
            </header>
            <div class="tm-body">
              <div class="tm-grid">
                <label class="full">
                  {{ $t('tasks.client') }}
                  <ClientAutocomplete
                    v-model="newSelectedClientId"
                    :placeholder="$t('tasks.chooseClient')"
                    @client-selected="(c)=>{ newSelectedClientId=c?.id||'' }"
                    :disabled="!canCreateTask"
                  />
                </label>
                <label>
                  {{ $t('tasks.titleLabel') }}
                  <input type="text" v-model="createForm.title" :placeholder="$t('tasks.titlePH')" :disabled="!canCreateTask" :readonly="!canCreateTask" />
                </label>
                <label>
                  {{ $t('tasks.start') }}
                  <AltDateTimePicker mode="date" v-model="createForm.start" :disabled="!canCreateTask" />
                </label>
                <label>
                  {{ $t('tasks.table.status') }}
                  <UiSelect v-model="createForm.status" :options="[
                    { value:'SCHEDULED', label: $t('tasks.status.SCHEDULED') },
                    { value:'DONE', label: $t('tasks.status.DONE') },
                    { value:'CANCELLED', label: $t('tasks.status.CANCELLED') }
                  ]" aria-label="Status" :disabled="!canCreateTask" />
                </label>
                <label>
                  {{ $t('tasks.assignee') }}
                  <UiSelect
                    v-model="newSelectedAssignee"
                    :options="assigneeOptions"
                    :placeholder="$t('tasks.unassigned')"
                    aria-label="Assignee"
                    :disabled="!canCreateTask"
                  />
                  <small class="muted" v-if="usersFallback">{{ $t('tasks.assigneeFallback') }}</small>
                </label>
                <label class="full">
                  {{ $t('tasks.form.location') }}
                  <textarea
                    v-model="createForm.location"
                    rows="2"
                    :placeholder="$t('tasks.form.locationPH')"
                    :disabled="!canCreateTask"
                    @input="autoGrow($event.target)"
                  ></textarea>
                </label>
                <label class="full">
                  {{ $t('tasks.form.description') }}
                  <textarea
                    v-model="createForm.description"
                    rows="3"
                    :disabled="!canCreateTask"
                    ref="createDescriptionRef"
                    @input="autoGrow($event.target)"
                  ></textarea>
                </label>
              </div>
            </div>
            <footer class="tm-footer">
              <div class="spacer"></div>
              <button class="btn" @click="onCreateOverlayClick" :disabled="creating">{{ $t('common.cancel') }}</button>
              <button class="btn primary" @click="createTask" :disabled="creating || !canCreateTask">{{ creating ? (t('common.saving') || 'Сохранение...') : tr('tasks.create','Создать') }}</button>
            </footer>
          </div>
        </div>
        <!-- Unsaved changes confirm (shared ConfirmDialog) -->
        <ConfirmDialog
          v-model="showCreateUnsaved"
          :title="tr('tasks.confirm.discardTitle','Несохранённые изменения')"
          :message="tr('tasks.confirm.discardChanges','Есть несохранённые изменения. Закрыть без сохранения?')"
          :confirm-text="($t('common.continue') && $t('common.continue')!=='common.continue') ? $t('common.continue') : 'Продолжить'"
          :cancel-text="$t('common.cancel')"
          @confirm="forceCloseCreateModal"
        />
      </div>
      <!-- Notifications widget -->
      <div class="widget notifications">
        <div class="widget-header">
          <h3>{{ tr('nav.notifications','Уведомления') }}</h3>
          <div class="notif-actions">
            <button v-if="unreadCount>0" class="btn-mini" @click="markAllRead">{{ tr('notifications.markAll','Все прочитано') }}</button>
            <router-link class="btn small" to="/dashboard/notifications">
              <span>{{ tr('common.openAll','Открыть') }}</span>
            </router-link>
          </div>
        </div>
        <div v-if="notifLoading" class="widget-empty">{{ tr('common.loading','Загрузка...') }}</div>
        <ul v-else-if="notifications.length" class="notif-list">
          <li v-for="n in notifications" :key="n.id" :class="{ unread: !n.is_read }" @click="openNotification(n)">
            <div class="line1">
              <span class="title">{{ n.title }}</span>
              <span class="time">{{ formatDate(n.created_at) + ' ' + formatNotifTime(n.created_at) }}</span>
            </div>
            <div class="text" v-if="n.message">{{ n.message }}</div>
            <div class="meta">
              <span v-if="n.client_name" class="chip">👤 {{ n.client_name }}</span>
              <span v-if="n.user_name" class="chip">👥 {{ n.user_name }}</span>
              <span v-if="n.reminder_type" class="chip">⏰ {{ n.reminder_type }}</span>
              <span class="chip source">{{ sourceLabel(n.source) }}</span>
              <span v-if="!n.is_read" class="dot-unread" :title="tr('notifications.unread','Непрочитанных: {n}').replace('{n}','1')"></span>
            </div>
          </li>
        </ul>
        <div v-else class="widget-empty">{{ tr('notifications.empty','Нет уведомлений') }}</div>
        <div class="notif-footer" v-if="unreadCount>0">{{ trUnread(unreadCount) }}</div>
      </div>
      <!-- Help / FAQ widget -->
      <div class="widget help">
        <div class="help-card no-icon">
          <div class="hc-content">
            <h3 class="hc-title">{{ $t('help.title') }}</h3>
            <p class="hc-sub">{{ $t('help.subtitle') }}</p>
            <div class="hc-actions">
              <router-link class="btn" to="/dashboard/faq">{{ $t('help.openFaq') }}</router-link>
              <a class="btn outline" href="mailto:crmlegalflow@gmail.com">{{ $t('help.contactSupport') }}</a>
            </div>
          </div>
        </div>
      </div>
    </div>
    <transition name="fade-toast">
      <div v-if="toast" class="toast">{{ toast }}</div>
    </transition>
  </div>
</template>

<script setup>
/* eslint-disable */
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import TaskCard from '../components/TaskCard.vue'
// UiSelect and ClientAutocomplete are registered globally in main.js

const tab = ref('today')
const items = ref([])
const loading = ref(false)
// notifications state
const notifLoading = ref(false)
const notifications = ref([])
const unreadCount = ref(0)
const finLoading = ref(false)
const summary = ref({ expected_payments_month: 0, receipts_month: 0, expected_payments_total: 0, receipts_total: 0, currency: 'PLN' })
const isAssistant = ref(false)
const { t, locale } = useI18n()
const router = useRouter()

// translation helper: fallback if key not defined (vue-i18n returns the key string)
function tr(key, fallback, params){
  try {
    const v = params ? t(key, params) : t(key)
    return (v === key ? fallback : v)
  } catch { return fallback }
}
function trUnread(count){
  // expects a pluralizable key if present, else fallback
  return tr('notifications.unreadCount', 'Непрочитанных: ' + count, { count })
}

async function load(){
  loading.value = true
  const token = localStorage.getItem('user-token')
  try {
    const resp = await axios.get(
      'http://127.0.0.1:8000/api/tasks/upcoming/?range=' + tab.value,
      { headers: { Authorization: 'Token ' + token } }
    )
    items.value = resp.data
  } catch(e) {
    // Гасим 500 и показываем пустой список + тост
    items.value = []
    const msg = (e?.response?.data && (typeof e.response.data === 'string' ? e.response.data : JSON.stringify(e.response.data))) || e.message || 'Ошибка загрузки задач'
    showToast(msg)
  } finally {
    loading.value = false
  }
}

function currentLocaleTag(){
  const l = String(locale.value || 'ru')
  return l.startsWith('pl') ? 'pl-PL' : 'ru-RU'
}

function formatDate(dt){
  if(!dt) return ''
  try{
    return new Date(dt).toLocaleDateString(currentLocaleTag(), { day:'2-digit', month:'2-digit', year:'numeric' })
  }catch(e){
    const d = new Date(dt)
    if(isNaN(d)) return ''
    const dd = String(d.getDate()).padStart(2,'0')
    const mm = String(d.getMonth()+1).padStart(2,'0')
    const yyyy = d.getFullYear()
    return `${dd}.${mm}.${yyyy}`
  }
}

function statusLabel(s){
  return s === 'SCHEDULED' ? t('dashboard.taskStatus.scheduled') : s === 'DONE' ? t('dashboard.taskStatus.done') : t('dashboard.taskStatus.cancelled')
}

function getAssigneeLabel(task){
  // Prefer assignees array (first), then task.assignee, else empty
  const makeLabel = (id) => {
    const u = users.value.find(x => String(x.id) === String(id))
    if(!u) return ''
    const full = `${u.first_name || ''} ${u.last_name || ''}`.trim()
    return full || (u.username || u.email || ('ID ' + u.id))
  }
  if (Array.isArray(task?.assignees) && task.assignees.length){
    const label = makeLabel(task.assignees[0])
    if (task.assignees.length > 1) return label ? label + ' +' + (task.assignees.length - 1) : ''
    return label || '—'
  }
  if (task?.assignee) return makeLabel(task.assignee) || '—'
  return '—'
}

async function markDone(t){
  const token = localStorage.getItem('user-token')
  await axios.put(
    'http://127.0.0.1:8000/api/tasks/' + t.id + '/',
    { status: 'DONE' },
    { headers: { Authorization: 'Token ' + token } }
  )
  load()
}


// --- Task inline modal logic ---
const showTaskModal = ref(false)
const activeTask = ref(null)
const editForm = ref({ id:null, title:'', start:'', status:'SCHEDULED', location:'', description:'' })
const updating = ref(false)
const showDeleteConfirm = ref(false)
// derived client id for active task stored in a ref (avoids runtime issues with missing import)
const activeClientId = ref(null)
const toast = ref('')
const lastError = ref('')
let toastTimer = null
// Refs used by updateTask for optional client/assignee override
const selectedClientId = ref(null)
const selectedAssignee = ref('')
const editLocationRef = ref(null)
const editDescriptionRef = ref(null)
const clientInitialLabel = ref('')

// View card state (like Calendar)
const showCard = ref(false)
const viewTask = ref(null)

// Users for assignee select
const users = ref([])
const usersFallback = ref(false)

function humanizeLogin(value){
  try{
    if(!value) return ''
    const local = String(value).split('@')[0]
    const parts = local.split(/[^A-Za-zА-Яа-яЁё]+/).map(p => p.replace(/\d+/g,'').trim()).filter(Boolean)
    if(!parts.length) return ''
    return parts.map(p => p.charAt(0).toUpperCase()+p.slice(1)).join(' ')
  }catch{ return '' }
}
function userLabel(u){
  const full = `${u.first_name || ''} ${u.last_name || ''}`.trim()
  if(full) return full
  const base = u.username || u.email || ''
  return humanizeLogin(base) || base || (u.id ? ('ID '+u.id) : '')
}
const assigneeOptions = computed(() => [
  { value:'', label: t('tasks.unassigned') },
  ...users.value.map(u => ({ value: String(u.id), label: userLabel(u) }))
])
// used directly in template

function toDateInput(d){
  const pad = n => String(n).padStart(2,'0')
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`
}

function openTask(t){
  activeTask.value = t
  editForm.value.id = t.id
  editForm.value.title = (t && t.title) || ''
  editForm.value.status = t.status
  editForm.value.start = toDateInput(new Date(t.start))
  editForm.value.location = t?.location || ''
  editForm.value.description = t?.description || ''
  // derive client id once (null-safe)
  activeClientId.value = (t && (
    (t.client && typeof t.client === 'object' && t.client.id) ? t.client.id :
    (typeof t.client === 'number') ? t.client :
    t?.client_id || t?.clientId || t?.client_pk || null
  )) || null
  selectedClientId.value = activeClientId.value
  if (t && t.client && typeof t.client === 'object'){
    const fn = t.client.first_name || ''
    const ln = t.client.last_name || ''
    clientInitialLabel.value = `${fn} ${ln}`.trim()
  } else if (t && t.client_name) {
    clientInitialLabel.value = t.client_name
  } else { clientInitialLabel.value = '' }

  if (Array.isArray(t?.assignees) && t.assignees.length){
    selectedAssignee.value = String(t.assignees[0])
  } else if (t?.assignee) {
    selectedAssignee.value = String(t.assignee)
  } else { selectedAssignee.value = '' }
  showTaskModal.value = true
  requestAnimationFrame(()=>{
    if(editLocationRef.value) autoGrow(editLocationRef.value)
    if(editDescriptionRef.value) autoGrow(editDescriptionRef.value)
  })
}

async function openCard(t){
  viewTask.value = { ...t }
  showCard.value = true
  // try to load full task details so card shows all fields like Calendar
  try{
    const token = localStorage.getItem('user-token')
    const resp = await axios.get(`http://127.0.0.1:8000/api/tasks/${t.id}/`, { headers:{ Authorization:`Token ${token}` } })
    let task = resp.data || {}
    // Ensure client object exists (some endpoints return only id/name)
    if(!task.client){
      const cid = task.client_id ?? t.client_id ?? (typeof t.client==='number' ? t.client : (t.client && t.client.id))
      if(cid!=null){
        task.client = { id: cid, first_name: '', last_name: '', email: '' }
        // try to fill name/email from list item fallbacks
        if(t.client_name){ task.client.first_name = String(t.client_name) }
        if(t.client && typeof t.client==='object' && (t.client.first_name || t.client.last_name || t.client.email)){
          task.client.first_name = t.client.first_name || task.client.first_name
          task.client.last_name = t.client.last_name || ''
          task.client.email = t.client.email || ''
        }
      }
    }
    viewTask.value = task
  }catch(e){
    // fallback: synthesize minimal client if missing so card shows row
    if(!viewTask.value.client){
      const cid = t.client_id ?? (typeof t.client==='number' ? t.client : t?.client?.id)
      if(cid!=null){
        viewTask.value = { ...viewTask.value, client:{ id: cid, first_name: t.client_name || '', last_name:'', email: t?.client?.email || '' } }
      }
    }
  }
}
function closeCard(){ showCard.value = false; viewTask.value = null }
function onCardStatusUpdated(status){
  try{
    if(!viewTask.value) return
    const id = viewTask.value.id
    const idx = items.value.findIndex(x => x.id === id)
    if(idx !== -1){ items.value[idx] = { ...items.value[idx], status } }
    viewTask.value = { ...viewTask.value, status }
  }catch{/* ignore */}
}
async function onCardUpdated(){
  // Task was deleted or updated from card; refresh list and close card
  await load()
  closeCard()
}

function openEditFromCard(task){
  closeCard()
  openTask(task)
}

function backToCard(){
  if (updating.value) return
  const id = editForm.value?.id
  const fromList = items.value.find(x => x.id === id)
  // Close edit modal forcibly to avoid any blockers
  closeTaskModal(true)
  // Reopen TaskCard; openCard will fetch full details
  if (fromList) openCard(fromList)
  else if (id) openCard({ id })
}

function closeTaskModal(force=false){
  if (updating.value && !force) return
  showTaskModal.value = false
  activeTask.value = null
  activeClientId.value = null
}

// Placeholder title for tasks lacking user-provided title
const placeholderTitle = (t('tasks.untitled') === 'tasks.untitled') ? 'Без названия' : t('tasks.untitled')

function statusDotClass(status){
  const s = (status || '').toLowerCase()
  return s ? 'status-' + s : 'status-scheduled'
}

async function updateTask(){
  if(!editForm.value.id) return
  updating.value = true
  lastError.value = ''
  try {
    const token = localStorage.getItem('user-token')
    const startDate = new Date(editForm.value.start + 'T00:00:00')
    const endDate = new Date(startDate.getTime() + 24*60*60*1000)
    // Build payload retaining existing client/assignees for PUT update
    const existingCid = (activeTask.value && (
      (activeTask.value.client && activeTask.value.client.id) ? activeTask.value.client.id : activeTask.value.client_id || null
    )) || null
    const resolvedCid = (selectedClientId.value !== null && selectedClientId.value !== '')
      ? Number(selectedClientId.value)
      : (existingCid!=null ? Number(existingCid) : null)

    const existingAssignees = Array.isArray(activeTask.value?.assignees) ? activeTask.value.assignees : []
    let resolvedAssignees = existingAssignees.filter(x => x!=null).map(n => Number(n)).filter(n => !Number.isNaN(n))
    if (selectedAssignee.value !== ''){
      const aid = Number(selectedAssignee.value)
      if (!Number.isNaN(aid)) resolvedAssignees = [aid]
    }

    const payload = {
      start: startDate.toISOString(),
      end: endDate.toISOString(),
      status: editForm.value.status,
      all_day: true,
      ...(resolvedCid!=null && !Number.isNaN(resolvedCid) ? { client_id: resolvedCid } : {}),
      assignees: resolvedAssignees,
      location: editForm.value.location || '',
      description: editForm.value.description || ''
    }
    if (editForm.value.title && editForm.value.title.trim().length) {
      payload.title = editForm.value.title.trim()
    }
    // Robust update: try PUT first, fallback to PATCH on 405
    const headers = { Authorization: 'Token ' + token }
    try {
      await axios.put(`/api/tasks/${editForm.value.id}/`, payload, { headers })
    } catch(err){
      const status = err?.response?.status
      if (status === 405) {
        await axios.patch(`/api/tasks/${editForm.value.id}/`, payload, { headers })
      } else {
        throw err
      }
    }
    // Обновим локально список
    const idx = items.value.findIndex(x => x.id === editForm.value.id)
    if(idx !== -1){
      items.value[idx] = { ...items.value[idx], ...payload, status: payload.status, title: payload.title || items.value[idx].title }
    }
    // Снимаем флаг обновления раньше, чтобы можно было закрыть принудительно
    updating.value = false
    const savedLabel = (t('common.saved') === 'common.saved') ? 'Сохранено' : t('common.saved')
    closeTaskModal(true)
    showToast(savedLabel)
  } catch(e) {
    console.error('Task update failed', e)
    lastError.value = (e?.response?.data && JSON.stringify(e.response.data)) || e.message || 'Ошибка обновления'
    showToast(t('common.error') + ': ' + lastError.value)
    updating.value = false
  }
  finally { if(updating.value) updating.value = false }
}

async function deleteTask(){
  if(!canDeleteTask.value){
    showToast('У вас нет прав для удаления задач')
    return
  }
  if(!editForm.value.id) return
  updating.value = true
  try {
    const token = localStorage.getItem('user-token')
    await axios.delete(`http://127.0.0.1:8000/api/tasks/${editForm.value.id}/`, { headers:{ Authorization:'Token '+ token } })
    items.value = items.value.filter(x => x.id !== editForm.value.id)
    showDeleteConfirm.value = false
    closeTaskModal()
  } catch(e){ /* ignore */ }
  finally { updating.value = false }
}

function askDeleteTask(){ showDeleteConfirm.value = true }
function cancelDeleteTask(){ if(!updating.value) showDeleteConfirm.value = false }
function proceedDeleteTask(){ if(!updating.value) deleteTask() }

function goToClient(){
  const cid = activeClientId.value
  if(!cid) return
  closeTaskModal(true)
  router.push({ name:'client-detail', params:{ id: cid } })
}

function showToast(msg){
  toast.value = msg
  if(toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(()=>{ toast.value='' }, 2500)
}

function autoGrow(el){
  if(!el) return
  el.style.height = 'auto'
  el.style.height = el.scrollHeight + 'px'
}

onMounted(() => {
  // Detect role from localStorage (set when fetching user-info in layout)
  isAssistant.value = (localStorage.getItem('user-role') === 'ASSISTANT')
  load()
  if (!isAssistant.value) {
    loadFinance()
  }
  loadNotifications()
  loadUsers()
})

// --- Quick create modal state & logic ---
const showCreateModal = ref(false)
const creating = ref(false)
const createForm = ref({ title:'', start:'', status:'SCHEDULED', location:'', description:'' })
const createDescriptionRef = ref(null)
const newSelectedClientId = ref('')
const newSelectedAssignee = ref('')
const showCreateUnsaved = ref(false)
const createInitialSnapshot = ref('')

// Check permission to create task
const canCreateTask = computed(() => {
  try {
    const permsJson = localStorage.getItem('user-permissions');
    if (!permsJson) return true;
    const perms = JSON.parse(permsJson);
    return !!perms.can_create_task;
  } catch (e) { return true; }
})

// Check permission to delete task
const canDeleteTask = computed(() => {
  try {
    const permsJson = localStorage.getItem('user-permissions');
    if (!permsJson) return true;
    const perms = JSON.parse(permsJson);
    return !!perms.can_delete_task;
  } catch (e) { return true; }
})

function openCreateModal(){
  // Default date = today
  const today = new Date()
  const pad = (n)=> String(n).padStart(2,'0')
  createForm.value = {
    title:'',
    start:`${today.getFullYear()}-${pad(today.getMonth()+1)}-${pad(today.getDate())}`,
    status:'SCHEDULED',
    location:'',
    description:''
  }
  newSelectedClientId.value = ''
  newSelectedAssignee.value = ''
  showCreateModal.value = true
  // take initial snapshot to detect unsaved edits
  createInitialSnapshot.value = JSON.stringify({
    ...createForm.value,
    client: newSelectedClientId.value,
    assignee: newSelectedAssignee.value
  })
  // reset textarea height on open
  requestAnimationFrame(() => {
    if (createDescriptionRef.value) autoGrow(createDescriptionRef.value)
  })
}
function closeCreateModal(force=false){ if(force || !creating.value) showCreateModal.value = false }
function isCreateDirty(){
  try{
    if(!showCreateModal.value) return false
    const now = JSON.stringify({
      ...createForm.value,
      client: newSelectedClientId.value,
      assignee: newSelectedAssignee.value
    })
    return createInitialSnapshot.value && now !== createInitialSnapshot.value
  }catch{ return false }
}
function onCreateOverlayClick(){
  if(isCreateDirty()) showCreateUnsaved.value = true
  else closeCreateModal()
}
function forceCloseCreateModal(){
  showCreateUnsaved.value = false
  closeCreateModal(true)
}

async function createTask(){
  if(!canCreateTask.value){
    showToast('У вас нет прав для создания задач')
    return
  }
  if(!createForm.value.start){
    showToast(tr('tasks.validationDate','Укажите дату задачи'))
    return
  }
  creating.value = true
  try{
    const token = localStorage.getItem('user-token')
    const startDate = new Date(createForm.value.start + 'T00:00:00')
    const endDate = new Date(startDate.getTime() + 24*60*60*1000)
    const payload = {
      title: (createForm.value.title || '').trim() || undefined,
      start: startDate.toISOString(),
      end: endDate.toISOString(),
      status: createForm.value.status,
      all_day: true,
      location: createForm.value.location,
      description: createForm.value.description,
      ...(newSelectedClientId.value ? { client_id: Number(newSelectedClientId.value) } : {}),
      ...(newSelectedAssignee.value ? { assignees: [Number(newSelectedAssignee.value)] } : { assignees: [] })
    }
    await axios.post('http://127.0.0.1:8000/api/tasks/', payload, { headers:{ Authorization:'Token '+token } })
    showCreateModal.value = false
    await load()
    showToast(tr('tasks.created','Задача создана'))
  }catch(e){
    const msg = (e?.response?.data && (typeof e.response.data === 'string' ? e.response.data : JSON.stringify(e.response.data))) || e.message || 'Ошибка создания задачи'
    showToast(msg)
  }finally{ creating.value = false }
}

async function loadFinance(){
  finLoading.value = true
  const token = localStorage.getItem('user-token')
  try{
    const resp = await axios.get('http://127.0.0.1:8000/api/finance/summary/', { headers: { Authorization: 'Token ' + token } })
    summary.value = resp.data
  } catch(e){
    // Без паники на главной: просто нули
    summary.value = { expected_payments_month: 0, receipts_month: 0, expected_payments_total: 0, receipts_total: 0, currency: 'PLN' }
    const msg = (e?.response?.data && (typeof e.response.data === 'string' ? e.response.data : JSON.stringify(e.response.data))) || e.message || 'Ошибка загрузки сводки'
    showToast(msg)
  } finally {
    finLoading.value = false
  }
}

function formatMoney(val){
  const num = Number(val || 0)
  try { return num.toLocaleString('ru-RU', { style:'currency', currency: summary.value.currency || 'PLN' }) }
  catch { return `${num.toFixed(2)} ${summary.value.currency || 'PLN'}` }
}

function formatNotifTime(dt){
  try { return new Date(dt).toLocaleTimeString(currentLocaleTag(), { hour:'2-digit', minute:'2-digit' }) } catch { return '' }
}

async function loadNotifications(){
  notifLoading.value = true
  const token = localStorage.getItem('user-token')
  try {
    const resp = await axios.get('http://127.0.0.1:8000/api/notifications/?limit=10&offset=0', { headers:{ Authorization:'Token '+token }})
    let list = []
    if (resp.data && Array.isArray(resp.data.items)) list = resp.data.items
    else if (Array.isArray(resp.data.results)) list = resp.data.results
    else if (Array.isArray(resp.data)) list = resp.data
    list = list.filter(Boolean).sort((a,b)=> new Date(b.created_at) - new Date(a.created_at))
    notifications.value = list.slice(0,3)
    const unreadResp = await axios.get('http://127.0.0.1:8000/api/notifications/unread-count/', { headers:{ Authorization:'Token '+token }})
    unreadCount.value = unreadResp.data.unread || 0
  } catch(e){ notifications.value = [] } finally { notifLoading.value = false }
}

async function markAllRead(){
  const token = localStorage.getItem('user-token')
  try {
    await axios.post('http://127.0.0.1:8000/api/notifications/mark-all-read/', {}, { headers:{ Authorization:'Token '+token }})
    unreadCount.value = 0
    loadNotifications()
    window.dispatchEvent(new CustomEvent('notifications-updated'))
  } catch(e){ /* ignore */ }
}

function sourceLabel(s){
  const map = { REMINDER: tr('notifications.sourceReminder','Напоминание'), SYSTEM: tr('notifications.sourceSystem','Система') }
  return map[s] || s || '—'
}

async function openNotification(n){
  try {
    if (n.client) {
      if (!n.is_read) {
        const token = localStorage.getItem('user-token')
        try { await axios.post(`http://127.0.0.1:8000/api/notifications/mark-read/${n.id}/`, {}, { headers:{ Authorization:'Token '+token }}) } catch(e){ /* ignore */ }
      }
      window.dispatchEvent(new CustomEvent('notifications-updated'))
      return router.push({ name:'client-detail', params:{ id: n.client }, query:{ from:'notifications' } })
    }
  } catch(e){ /* ignore */ }
  router.push('/dashboard/notifications')
}

async function loadUsers(){
  const token = localStorage.getItem('user-token')
  try{
    const resp = await axios.get('http://127.0.0.1:8000/api/company/users/', { headers:{ Authorization:'Token '+token }})
    users.value = Array.isArray(resp.data) ? resp.data : []
  }catch(e){
    usersFallback.value = true
    try{
      const me = await axios.get('http://127.0.0.1:8000/api/user-info/', { headers:{ Authorization:'Token '+token }})
      users.value = [{ id: me.data.id, username: me.data.username, first_name: me.data.first_name || '', last_name: me.data.last_name || '', email: me.data.email || '' }]
    }catch{ users.value = [] }
  }
}
</script>

<style scoped>
/* Base layout styles retained */
/* Стили только для этой конкретной страницы */
.content-wrapper {
  padding: 40px;
}
.content-header {
  margin-bottom: 30px;
}
.content-header h1 {
  font-size: 28px;
  color: #2c3e50;
  font-weight: 700;
}
.widget { margin-top: 20px; background:var(--card-bg); border:1px solid var(--card-border); border-radius:12px; }
.widget-header { display:flex; align-items:center; justify-content:space-between; padding:12px 16px; border-bottom:1px solid #eef2f7; }
.widget.finance { margin-top: 0; }
.finance-grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:16px; padding:16px; }
.kpi { background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:14px 16px; }
.kpi .kpi-title { color:#334155; font-weight:600; font-size:14px; margin-bottom:8px; }
.kpi .kpi-value { font-size:22px; font-weight:700; color:#0f172a; }
.kpi.muted { opacity: .8; }
.tabs button { border:1px solid var(--btn-border); background:var(--btn-bg); color:var(--btn-text); border-radius:8px; padding:6px 10px; margin-left:8px; position:relative; overflow:hidden; cursor:pointer; transition:background .28s ease, color .28s ease, border-color .28s ease, box-shadow .28s ease, transform .28s ease; }
/* underline / progress bar animation */
.tabs button::after { content:""; position:absolute; left:50%; bottom:0; height:2px; width:0; background:var(--primary-color); transition:width .32s ease, left .32s ease, opacity .32s ease; opacity:0; }
/* hover / focus (non-active) subtle effects */
.tabs button:not(.active):hover { background:#f5f9ff; border-color:#c9d6e3; box-shadow:0 2px 4px -2px rgba(0,0,0,.15); transform:translateY(-1px); }
.tabs button:not(.active):focus-visible { outline:2px solid var(--primary-color); outline-offset:2px; }
.tabs button:not(.active):hover::after, .tabs button:not(.active):focus-visible::after { width:100%; left:0; opacity:1; }
/* active tab keeps previous style; show persistent underline for consistency */
.tabs .active { background:var(--primary-color); color:#fff; border-color:var(--primary-color); }
.tabs .active::after { width:100%; left:0; opacity:1; }
.task-list { list-style:none; margin:0; padding:0; }
.task-list li { display:grid; grid-template-columns: 18px 110px 1fr 2fr 1.2fr 120px auto; gap:12px; align-items:center; padding:12px 16px; border-bottom:1px solid #f1f5f9; cursor:pointer; }
.task-list li:last-child{ border-bottom:none; }
.task-row:hover { background:#f8fafc; }
.task-row:focus { outline:2px solid var(--primary-color); outline-offset:2px; }
.task-modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,.35); display:flex; align-items:center; justify-content:center; z-index:3000; }
.task-modal { background:var(--card-bg); border:1px solid var(--card-border); width:600px; max-width:95vw; border-radius:14px; box-shadow:0 10px 32px rgba(0,0,0,.18); display:flex; flex-direction:column; }
.tm-header { display:flex; align-items:center; justify-content:space-between; padding:14px 18px; border-bottom:1px solid #e5e7eb; }
.tm-header .tm-left { display:flex; align-items:center; gap:8px; }
.tm-header .icon.back { font-size:20px; line-height:1; background:none; border:none; cursor:pointer; color:#334155; padding:2px 6px; border-radius:8px; transition:background .18s ease, transform .18s ease; }
.tm-header .icon.back:hover { background:#f1f5f9; transform:translateY(-1px); }
.tm-header .icon.back:active { transform:translateY(0); }
.tm-body { padding:16px 18px; }
.tm-grid { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
.tm-grid label.full { grid-column: 1 / -1; }
.tm-grid label { display:flex; flex-direction:column; gap:6px; font-size:14px; font-weight:500; color:#334155; }
.tm-grid input, .tm-grid select { border:1px solid var(--form-border); border-radius:var(--form-radius,8px); padding:8px 10px; background:var(--form-bg,#fff); transition:border-color .18s ease, box-shadow .18s ease; }
.tm-grid input:focus, .tm-grid select:focus { outline:none; border-color:var(--form-border-focus); box-shadow:var(--form-focus-ring); }
.tm-grid textarea { resize:none; overflow:hidden; }
.tm-grid input:disabled, .tm-grid input:read-only { background:#f1f5f9; color:#64748b; cursor:not-allowed; }
.tm-footer { display:flex; align-items:center; gap:10px; padding:14px 18px; border-top:1px solid #e5e7eb; }
.tm-footer .spacer { flex:1; }
.tm-footer .btn { height:42px; padding:0 18px; border-radius:10px; font-weight:600; transition: transform .18s ease, box-shadow .18s ease, background-color .18s ease, border-color .18s ease, color .18s ease; }
/* Match TaskForm hover: only motion/shadow, no color swap to blue */
.tm-footer .btn:not(.primary):not(.danger):not(.outline):hover { background:var(--btn-bg,#fff); border-color:var(--btn-border,#d0d7e2); color:var(--btn-text,#1e293b) !important; }
.tm-footer .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 18px -8px rgba(0,0,0,.22); }
.tm-footer .btn:active { transform: translateY(0); box-shadow: 0 6px 12px -8px rgba(0,0,0,.20); }
.tm-footer .btn.outline { background:#fff !important; border:1px solid #d0d7e2 !important; color:#1e293b !important; }
.btn.primary { background:var(--primary-color,#4A90E2); color:#fff !important; border-color:var(--primary-color,#4A90E2); }
/* Match TaskForm danger (pink) button exactly */
.tm-footer .btn.danger { background:#ffe5ea; border:1px solid #f5c3cd; color:#c53030 !important; }
.tm-footer .btn.danger:hover { background:#ffdfe6; border-color:#efb5c1; color:#b12727 !important; }
.tm-footer .btn.danger:disabled { opacity:.6; background:#ffe5ea; border-color:#f1c8d0; color:#c26a6a !important; box-shadow:none; transform:none; }
.icon { background:none; border:none; font-size:20px; cursor:pointer; }
.toast { position:fixed; top:20px; right:20px; background:linear-gradient(180deg,#4A90E2,#3b7fc9); color:#fff; padding:12px 20px; border-radius:10px; font-size:14px; font-weight:600; box-shadow:0 6px 24px -6px rgba(0,0,0,.4); letter-spacing:.3px; border:1px solid #3b7fc9; display:inline-flex; align-items:center; gap:8px; z-index: 9999; }
.fade-toast-enter-active, .fade-toast-leave-active { transition: opacity .25s, transform .25s; }
.fade-toast-enter-from, .fade-toast-leave-to { opacity:0; transform:translateY(-20px); }
.confirm-overlay { position:fixed; inset:0; background:rgba(0,0,0,.4); display:flex; align-items:center; justify-content:center; z-index:4000; backdrop-filter:blur(2px); }
.confirm-dialog { background:var(--card-bg); border:1px solid var(--card-border); border-radius:16px; padding:26px 28px 24px; width:min(420px,90%); box-shadow:0 12px 40px -8px rgba(0,0,0,.35); animation:pop .22s ease; }
.confirm-message { margin:0 0 22px; font-size:16px; font-weight:600; line-height:1.45; color:#0f172a; }
.confirm-actions { display:flex; gap:12px; justify-content:flex-end; }
.confirm-dialog-modern { background:#fff; border-radius:14px; padding:24px 32px; width:min(400px,92vw); box-shadow:0 12px 40px -8px rgba(0,0,0,.35); animation:pop .22s ease; text-align:center; }
.confirm-message-modern { margin:0 0 20px; font-size:16px; font-weight:600; line-height:1.5; color:#0f172a; }
.confirm-actions-modern { display:flex; gap:12px; justify-content:center; }
.btn-modern { height:38px; padding:0 24px; border-radius:10px; font-weight:600; font-size:14px; cursor:pointer; transition:transform .18s ease, box-shadow .18s ease, background-color .18s ease, border-color .18s ease; border:none; display:inline-flex; align-items:center; justify-content:center; min-width:120px; }
.btn-modern:hover { transform:translateY(-2px); box-shadow:0 8px 16px -6px rgba(0,0,0,.25); }
.btn-modern:active { transform:translateY(0); }
.btn-modern:disabled { opacity:.6; cursor:not-allowed; transform:none; }
.btn-modern.danger-modern { background:#ffdfe6; border:1px solid #efb5c1; color:#dc2626; }
.btn-modern.cancel-modern { background:#f1f5f9; border:1px solid #e2e8f0; color:#475569; }
.btn-modern.cancel-modern:hover { background:#e2e8f0; }
@keyframes pop { from { transform:translateY(14px); opacity:0; } to { transform:translateY(0); opacity:1; } }
.task-list .type { width:10px; height:10px; border-radius:50%; background:#4A90E2; }
.task-list .type.status-scheduled{ background:#4A90E2; }
.task-list .type.status-done{ background:#16a34a; }
.task-list .type.status-cancelled{ background:#dc2626; }
.task-list .date { color:#475569; white-space:nowrap; }
.task-list .status { font-weight:600; }
.task-list .status.done{ color:#16a34a; }
.task-list .status.cancelled{ color:#dc2626; }
.task-list .assignee { color:#334155; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
/* legacy per-button styles removed (using unified .btn) */
/* New unified button system (blue like client page) */
.btn { background:linear-gradient(180deg,#4A90E2,#4A90E2); color:#fff !important; border:1px solid #4A90E2; font-weight:500; padding:10px 18px; border-radius:8px; font-size:14px; line-height:1.2; display:inline-flex; align-items:center; gap:8px; cursor:pointer; box-shadow:0 2px 4px rgba(0,0,0,.08); transition:background .25s, box-shadow .25s, border-color .25s, color .25s, transform .18s; }
.btn:hover { background:linear-gradient(180deg,#4A90E2,#3b7fc9); border-color:#3b7fc9; box-shadow:0 4px 10px rgba(0,0,0,.15); }
.btn:active { transform:translateY(1px); }
.btn:focus { outline:none; box-shadow:0 0 0 2px rgba(74,144,226,.45); }
.btn:disabled { opacity:.55; cursor:not-allowed; background:#94bcea; border-color:#94bcea; box-shadow:none; }
.btn.small { padding:6px 14px; font-size:12px; }
.btn.outline { background:#ffffff; color:#1e293b !important; border:1px solid #cfd8e3; box-shadow:0 1px 2px rgba(0,0,0,.04); }
.btn.outline:hover { background:#f1f5f9; border-color:#b7c6d6; }
.btn.danger { background:rgba(255,82,82,.12); border:1px solid rgba(255,82,82,.45); color:#c53030 !important; }
.btn.danger:hover { background:rgba(255,82,82,.20); border-color:rgba(255,82,82,.6); color:#a61b1b !important; }
.btn.danger:disabled { background:rgba(255,82,82,.08); border-color:rgba(255,82,82,.25); color:rgba(197,48,48,.55) !important; }
/* Override legacy list button styling so mark-done is blue by default */
/* removed old gradient override so action button uses unified white->blue hover */
.widget-empty { padding:16px; color:#5a6a7b; }
.widget-empty.empty-modern{ display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; gap:10px; padding:28px 16px; }
.empty-title{ font-weight:700; color:#0f172a; margin-top:4px; }
.empty-sub{ color:#475569; font-size:13px; }
.empty-actions{ display:flex; gap:10px; margin-top:4px; }
/* Unify hover style for both buttons in empty state */
.empty-modern .empty-actions .btn:hover,
.empty-modern .empty-actions .btn.outline:hover{ background:#f1f5f9; color:#1e293b !important; border-color:var(--primary-color,#4A90E2); box-shadow:0 2px 6px -2px rgba(0,0,0,.2); }

/* Help card modern style */
.help .help-card{ display:flex; align-items:center; gap:16px; padding:18px; border-top:1px solid #eef2f7; background:linear-gradient(180deg,#f8fbff,#f6f9ff); border-radius:0 0 12px 12px; }
.help .help-card.no-icon{ gap:0; }
.help .hc-title{ margin:0 0 4px; font-size:18px; font-weight:700; color:#0f172a; }
.help .hc-sub{ margin:0 0 10px; color:#475569; font-size:13px; }
.help .hc-actions{ display:flex; gap:10px; flex-wrap:wrap; }
.help .hc-actions .btn:hover,
.help .hc-actions .btn.outline:hover{ background:#f1f5f9; color:#1e293b !important; border-color:var(--primary-color,#4A90E2); box-shadow:0 2px 6px -2px rgba(0,0,0,.2); }
.notifications .notif-actions { display:flex; gap:8px; }
.btn-mini { background:linear-gradient(180deg,#4A90E2,#4A90E2); color:#fff; border:1px solid #4A90E2; padding:4px 12px; font-size:11px; font-weight:600; line-height:1; border-radius:18px; cursor:pointer; display:inline-flex; align-items:center; gap:4px; transition:background .25s,border-color .25s,box-shadow .25s; }
.btn-mini:hover { background:linear-gradient(180deg,#4A90E2,#3b7fc9); border-color:#3b7fc9; box-shadow:0 2px 6px -2px rgba(0,0,0,.2); }
.btn-mini:active { transform:translateY(1px); }
.btn-mini:focus { outline:none; box-shadow:0 0 0 2px rgba(74,144,226,.45); }
.btn-mini.secondary { background:#f1f5f9; }
.notif-list { list-style:none; margin:0; padding:0; }
.notif-list li { padding:10px 14px; border-bottom:1px solid #f1f5f5; cursor:pointer; }
.notif-list li.unread { background:#f0f7ff; }
.notif-list li:hover { background:#f5f9ff; }
.notif-list .line1 { display:flex; justify-content:space-between; align-items:center; gap:12px; }
.notif-list .title { font-weight:600; font-size:13px; color:#0f172a; flex:1; }
.notif-list .time { font-size:11px; color:#64748b; white-space:nowrap; }
.notif-list .text { font-size:12px; color:#475569; margin-top:4px; line-height:1.35; }
.notif-list .meta { display:flex; flex-wrap:wrap; gap:6px; margin-top:6px; align-items:center; }
.notif-list .chip { background:#eef2f7; color:#334155; font-size:11px; padding:2px 6px; border-radius:14px; line-height:1.2; }
.notif-list .chip.source { background:#e3f2ff; color:#1e40af; }
.dot-unread { width:8px; height:8px; background:#ef4444; border-radius:50%; box-shadow:0 0 0 2px #fff; margin-left:4px; }
.notif-footer { padding:6px 14px 10px; font-size:12px; color:#475569; }
/* removed .open-btn styles in favor of .btn */

/* === Unified Buttons (white base -> blue hover; same as client & notifications) === */
:root, .content-wrapper { --btn-radius:8px; }
.btn { background:var(--btn-bg,#ffffff); border:1px solid var(--btn-border,#d0d7e2); padding:10px 18px; border-radius:var(--btn-radius); cursor:pointer; font-weight:600; font-size:14px; line-height:1.2; display:inline-flex; align-items:center; gap:8px; transition:background .25s, color .25s, border-color .25s, box-shadow .25s; color:#1e293b !important; text-decoration:none; box-shadow:0 1px 2px rgba(0,0,0,0.04); }
.btn:not(:hover):not(:focus) { background:#ffffff; color:#1e293b !important; }
.btn:visited { color:#1e293b; text-decoration:none; }
.btn:hover { background:var(--primary-color,#4A90E2); color:#fff !important; border-color:var(--primary-color,#4A90E2); text-decoration:none; }
.btn:focus { text-decoration:none; }
.btn:disabled { opacity:.55; cursor:not-allowed; }
.btn.small { padding:6px 12px; font-size:12px; }
.btn.outline { background:#ffffff; color:#1e293b !important; border:1px solid #d0d7e2; }
.btn.outline:hover { background:#f1f5f9; border-color:var(--primary-color,#4A90E2); }
.btn.danger { background:rgba(255,82,82,0.12); border:1px solid rgba(255,82,82,0.45); color:#c53030 !important; }
.btn.danger:hover { background:rgba(255,82,82,0.20); border-color:rgba(255,82,82,0.6); color:#a61b1b !important; }
.btn.danger:disabled { background:rgba(255,82,82,0.08); border-color:rgba(255,82,82,0.25); color:rgba(197,48,48,0.55) !important; }
.task-list .actions .btn { padding:6px 12px; font-size:12px; box-shadow:none; }

/* Force primary buttons in Dashboard modals to match calendar exactly */
.tm-footer .btn.primary { background:var(--primary-color,#4A90E2) !important; border-color:var(--primary-color,#4A90E2) !important; color:#fff !important; box-shadow:none; }

/* Toast unify */
.toast { position:fixed; top:20px; right:20px; background:linear-gradient(180deg,#4A90E2,#3b7fc9); color:#fff; padding:12px 20px; border-radius:10px; font-size:14px; font-weight:600; box-shadow:0 6px 24px -6px rgba(0,0,0,.4); letter-spacing:.3px; border:1px solid #3b7fc9; display:inline-flex; align-items:center; gap:8px; z-index: 9999; }
.fade-toast-enter-active, .fade-toast-leave-active { transition: opacity .25s, transform .25s; }
.fade-toast-enter-from, .fade-toast-leave-to { opacity:0; transform:translateY(-20px); }
.confirm-overlay { position:fixed; inset:0; background:rgba(0,0,0,.4); display:flex; align-items:center; justify-content:center; z-index:4000; backdrop-filter:blur(2px); }
.confirm-dialog { background:var(--card-bg); border:1px solid var(--card-border); border-radius:16px; padding:26px 28px 24px; width:min(420px,90%); box-shadow:0 12px 40px -8px rgba(0,0,0,.35); animation:pop .22s ease; }
.confirm-message { margin:0 0 22px; font-size:16px; font-weight:600; line-height:1.45; color:#0f172a; }
.confirm-actions { display:flex; gap:12px; justify-content:flex-end; }
.confirm-dialog-modern { background:#fff; border-radius:14px; padding:24px 32px; width:min(400px,92vw); box-shadow:0 12px 40px -8px rgba(0,0,0,.35); animation:pop .22s ease; text-align:center; }
.confirm-message-modern { margin:0 0 20px; font-size:16px; font-weight:600; line-height:1.5; color:#0f172a; }
.confirm-actions-modern { display:flex; gap:12px; justify-content:center; }
.btn-modern { height:38px; padding:0 24px; border-radius:10px; font-weight:600; font-size:14px; cursor:pointer; transition:transform .18s ease, box-shadow .18s ease, background-color .18s ease, border-color .18s ease; border:none; display:inline-flex; align-items:center; justify-content:center; min-width:120px; }
.btn-modern:hover { transform:translateY(-2px); box-shadow:0 8px 16px -6px rgba(0,0,0,.25); }
.btn-modern:active { transform:translateY(0); }
.btn-modern:disabled { opacity:.6; cursor:not-allowed; transform:none; }
.btn-modern.danger-modern { background:#ffdfe6; border:1px solid #efb5c1; color:#dc2626; }
.btn-modern.cancel-modern { background:#f1f5f9; border:1px solid #e2e8f0; color:#475569; }
.btn-modern.cancel-modern:hover { background:#e2e8f0; }
@keyframes pop { from { transform:translateY(14px); opacity:0; } to { transform:translateY(0); opacity:1; } }
.task-list .type { width:10px; height:10px; border-radius:50%; background:#4A90E2; }
.task-list .type.status-scheduled{ background:#4A90E2; }
.task-list .type.status-done{ background:#16a34a; }
.task-list .type.status-cancelled{ background:#dc2626; }
.task-list .date { color:#475569; white-space:nowrap; }
.task-list .status { font-weight:600; }
.task-list .status.done{ color:#16a34a; }
.task-list .status.cancelled{ color:#dc2626; }
.task-list .assignee { color:#334155; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
/* legacy per-button styles removed (using unified .btn) */
/* New unified button system (blue like client page) */
.btn { background:linear-gradient(180deg,#4A90E2,#4A90E2); color:#fff !important; border:1px solid #4A90E2; font-weight:500; padding:10px 18px; border-radius:8px; font-size:14px; line-height:1.2; display:inline-flex; align-items:center; gap:8px; cursor:pointer; box-shadow:0 2px 4px rgba(0,0,0,.08); transition:background .25s, box-shadow .25s, border-color .25s, color .25s, transform .18s; }
.btn:hover { background:linear-gradient(180deg,#4A90E2,#3b7fc9); border-color:#3b7fc9; box-shadow:0 4px 10px rgba(0,0,0,.15); }
.btn:active { transform:translateY(1px); }
.btn:focus { outline:none; box-shadow:0 0 0 2px rgba(74,144,226,.45); }
.btn:disabled { opacity:.55; cursor:not-allowed; background:#94bcea; border-color:#94bcea; box-shadow:none; }
.btn.small { padding:6px 14px; font-size:12px; }
.btn.outline { background:#ffffff; color:#1e293b !important; border:1px solid #cfd8e3; box-shadow:0 1px 2px rgba(0,0,0,.04); }
.btn.outline:hover { background:#f1f5f9; border-color:var(--primary-color,#4A90E2); }
.btn.danger { background:rgba(255,82,82,0.12); border:1px solid rgba(255,82,82,0.45); color:#c53030 !important; }
.btn.danger:hover { background:rgba(255,82,82,0.20); border-color:rgba(255,82,82,0.6); color:#a61b1b !important; }
.btn.danger:disabled { background:rgba(255,82,82,0.08); border-color:rgba(255,82,82,0.25); color:rgba(197,48,48,0.55) !important; }
.task-list .actions .btn { padding:6px 12px; font-size:12px; box-shadow:none; }

/* Force primary buttons in Dashboard modals to match calendar exactly */
.tm-footer .btn.primary { background:var(--primary-color,#4A90E2) !important; border-color:var(--primary-color,#4A90E2) !important; color:#fff !important; box-shadow:none; }

/* Toast unify */
.toast { position:fixed; top:20px; right:20px; background:linear-gradient(180deg,#4A90E2,#3b7fc9); color:#fff; padding:12px 20px; border-radius:10px; font-size:14px; font-weight:600; box-shadow:0 6px 24px -6px rgba(0,0,0,.4); letter-spacing:.3px; border:1px solid #3b7fc9; display:inline-flex; align-items:center; gap:8px; z-index: 9999; }
.fade-toast-enter-active, .fade-toast-leave-active { transition: opacity .25s, transform .25s; }
.fade-toast-enter-from, .fade-toast-leave-to { opacity:0; transform:translateY(-20px); }
.confirm-overlay { position:fixed; inset:0; background:rgba(0,0,0,.4); display:flex; align-items:center; justify-content:center; z-index:4000; backdrop-filter:blur(2px); }
.confirm-dialog { background:var(--card-bg); border:1px solid var(--card-border); border-radius:16px; padding:26px 28px 24px; width:min(420px,90%); box-shadow:0 12px 40px -8px rgba(0,0,0,.35); animation:pop .22s ease; }
.confirm-message { margin:0 0 22px; font-size:16px; font-weight:600; line-height:1.45; color:#0f172a; }
.confirm-actions { display:flex; gap:12px; justify-content:flex-end; }
.confirm-dialog-modern { background:#fff; border-radius:14px; padding:24px 32px; width:min(400px,92vw); box-shadow:0 12px 40px -8px rgba(0,0,0,.35); animation:pop .22s ease; text-align:center; }
.confirm-message-modern { margin:0 0 20px; font-size:16px; font-weight:600; line-height:1.5; color:#0f172a; }
.confirm-actions-modern { display:flex; gap:12px; justify-content:center; }
.btn-modern { height:38px; padding:0 24px; border-radius:10px; font-weight:600; font-size:14px; cursor:pointer; transition:transform .18s ease, box-shadow .18s ease, background-color .18s ease, border-color .18s ease; border:none; display:inline-flex; align-items:center; justify-content:center; min-width:120px; }
.btn-modern:hover { transform:translateY(-2px); box-shadow:0 8px 16px -6px rgba(0,0,0,.25); }
.btn-modern:active { transform:translateY(0); }
.btn-modern:disabled { opacity:.6; cursor:not-allowed; transform:none; }
.btn-modern.danger-modern { background:#ffdfe6; border:1px solid #efb5c1; color:#dc2626; }
.btn-modern.cancel-modern { background:#f1f5f9; border:1px solid #e2e8f0; color:#475569; }
.btn-modern.cancel-modern:hover { background:#e2e8f0; }
@keyframes pop { from { transform:translateY(14px); opacity:0; } to { transform:translateY(0); opacity:1; } }
.task-list .type { width:10px; height:10px; border-radius:50%; background:#4A90E2; }
.task-list .type.status-scheduled{ background:#4A90E2; }
.task-list .type.status-done{ background:#16a34a; }
.task-list .type.status-cancelled{ background:#dc2626; }
.task-list .date { color:#475569; white-space:nowrap; }
.task-list .status { font-weight:600; }
.task-list .status.done{ color:#16a34a; }
.task-list .status.cancelled{ color:#dc2626; }
.task-list .assignee { color:#334155; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
/* End of styles */
</style>