<template>
  <div class="notifications-page">
    <header class="header">
      <h1>{{ $t('notifications.title') }}</h1>
    </header>
    <div class="actions">
      <button class="btn" @click="reload" :disabled="loading">{{ loading ? $t('notifications.loading') : $t('notifications.refresh') }}</button>
      <button class="btn" @click="markAll" :disabled="markingAll || items.length===0">{{ markingAll ? $t('notifications.marking') : $t('notifications.markAll') }}</button>
      <button class="btn" @click="toggleSelectMode" :disabled="items.length===0">{{ selectMode ? cancelSelectLabel : selectLabel }}</button>
      <button class="btn" v-if="selectMode" @click="toggleSelectAll" :disabled="items.length===0">{{ allSelected ? $t('notifications.deselectAll') : $t('notifications.selectAll') }}</button>
        <button class="btn danger" v-if="selectMode" @click="askBulkDelete" :disabled="selectedIds.length===0 || bulkDeleting">{{ bulkDeleting ? '...' : bulkDeleteLabel }}</button>
      <span class="counter" v-if="unreadCount">{{ $t('notifications.unread', { n: unreadCount }) }}</span>
    </div>
  <div v-if="error" class="error-inline">{{ error }}</div>
  <ul class="list" v-if="items.length && !error">
      <li v-for="n in items" :key="n.id"
          :class="['item', { unread: !n.is_read, selected: selectMode && selectedIds.includes(n.id), selectable: selectMode, 'has-client': !!n.client }]"
          @click="itemRootClick(n)">
        <div class="item-header">
          <div class="left-head">
            <input v-if="selectMode" type="checkbox" :checked="selectedIds.includes(n.id)" @change="toggleOne(n.id,$event)" @click.stop />
            <strong class="title">
              <span v-if="isError(n)" class="error-mark">!</span>
              {{ n.title }}
            </strong>
          </div>
          <small class="time">{{ formatDate(n.created_at) }}</small>
        </div>
        <p v-if="n.message" class="msg">{{ n.message }}</p>
        <div class="meta">
          <span v-if="n.user_name" class="chip">👥 {{ n.user_name }}</span>
          <span v-if="n.client_name" class="chip">👤 {{ n.client_name }}</span>
          <span v-if="n.reminder_type" class="chip">⏰ {{ n.reminder_type }}</span>
          <span class="chip source">{{ sourceLabel(n.source) }}</span>
          <button v-if="!n.is_read" class="mini" @click.stop="markOne(n)">{{ $t('notifications.markOne') }}</button>
            <button class="mini danger" @click.stop="askDeleteOne(n)">{{ $t('common.delete') }}</button>
        </div>
      </li>
  </ul>
  <div v-else-if="!loading && !error && total===0" class="empty-simple">{{ $t('notifications.empty') }}</div>
    <div v-if="canLoadMore && !loading && !deleting && !showConfirm" class="load-more-wrap">
      <button class="btn load-more" @click="loadMore" :disabled="loadingMore">{{ loadingMore ? '...' : loadMoreLabel }}</button>
    </div>
  </div>
  <div v-if="showConfirm" class="confirm-overlay">
    <div class="confirm-dialog">
      <p class="confirm-message">{{ confirmMessage }}</p>
      <div class="confirm-actions centered">
        <button class="btn danger" :disabled="deleting" @click="proceedDelete">{{ deleting ? '...' : $t('common.yesDelete') }}</button>
        <button class="btn" :disabled="deleting" @click="cancelDelete">{{ $t('common.cancel') }}</button>
      </div>
    </div>
  </div>
  <transition name="fade-toast">
    <div v-if="toast" class="toast">{{ toast }}</div>
  </transition>
</template>

<script>
import axios from 'axios'
export default {
  name: 'NotificationsView',
  data() {
    return { 
      items: [], loading: false, loadingMore: false, error: '', markingAll: false,
      total: 0, offset: 0, limit: 50,
      selectMode: false, selectedIds: [], bulkDeleting: false,
      // Custom confirm state
      showConfirm: false, confirmMessage: '', pendingIds: [], deleting: false,
      // Toast state
      toast: '', toastTimer: null
    }
  },
  computed: {
    unreadCount() { return this.items.filter(i => !i.is_read).length },
    canLoadMore() { return this.items.length < this.total },
    loadMoreLabel() { return this.$t('common.all') === 'Все' ? 'Загрузить ещё' : 'Pokaż więcej' }
    ,selectLabel() { return this.$t('common.all') === 'Все' ? 'Выбрать' : 'Zaznacz' }
    ,cancelSelectLabel() { return this.$t('common.all') === 'Все' ? 'Отмена' : 'Anuluj' }
    ,bulkDeleteLabel() { return this.$t('common.delete') }
    ,allSelected() { return this.selectedIds.length && this.selectedIds.length === this.items.length }
  },
  methods: {
    toggleSelectMode() {
      this.selectMode = !this.selectMode
      if (!this.selectMode) this.selectedIds = []
    },
    toggleSelectAll() {
      if (this.allSelected) {
        this.selectedIds = []
      } else {
        this.selectedIds = this.items.map(i => i.id)
      }
    },
    toggleOne(id, ev) {
      const checked = ev.target.checked
      if (checked) {
        if (!this.selectedIds.includes(id)) this.selectedIds.push(id)
      } else {
        this.selectedIds = this.selectedIds.filter(x => x !== id)
      }
    },
    toggleItemClick(id) {
      const idx = this.selectedIds.indexOf(id)
      if (idx === -1) {
        this.selectedIds.push(id)
      } else {
        this.selectedIds.splice(idx, 1)
      }
    },
    itemRootClick(n) {
      if (this.selectMode) {
        this.toggleItemClick(n.id)
        return
      }
      if (n.client) this.openClient(n)
    },
    askBulkDelete() {
      if (!this.selectedIds.length) return
      this.pendingIds = [...this.selectedIds]
      this.confirmMessage = this.$t('notifications.confirmDeleteMany', { n: this.selectedIds.length })
      this.showConfirm = true
    },
    async fetchPage(reset=false) {
      if (reset) { this.offset = 0; this.items = []; this.total = 0 }
      const params = new URLSearchParams({ limit: this.limit, offset: this.offset })
      const token = localStorage.getItem('user-token')
      const url = `http://127.0.0.1:8000/api/notifications/?${params.toString()}`
      const res = await axios.get(url, { headers: { Authorization: `Token ${token}` } })
      const { items, total, offset, count } = res.data
      this.total = total
      this.offset = offset + count
      this.items = this.items.concat(items)
    },
    async reload() {
  this.loading = true; this.error = ''
  try { await this.fetchPage(true) } catch (e) { this.items = []; this.total = 0; this.offset = 0; this.error = this.$t('notifications.loadError'); console.error('Notifications load failed', e) } finally { this.loading = false }
    },
    async loadMore() {
      if (!this.canLoadMore) return
      this.loadingMore = true
      try { await this.fetchPage(false) } catch (e) { /* ignore */ } finally { this.loadingMore = false }
    },
    async markAll() {
      this.markingAll = true
      try {
        const token = localStorage.getItem('user-token')
        await axios.post('http://127.0.0.1:8000/api/notifications/mark-all-read/', {}, { headers: { Authorization: `Token ${token}` } })
        this.items = this.items.map(i => ({ ...i, is_read: true }))
        window.dispatchEvent(new CustomEvent('notifications-updated'))
      } catch (e) { /* ignore */ } finally { this.markingAll = false }
    },
    async markOne(n) {
      try {
        const token = localStorage.getItem('user-token')
        await axios.post(`http://127.0.0.1:8000/api/notifications/mark-read/${n.id}/`, {}, { headers: { Authorization: `Token ${token}` } })
        n.is_read = true
        window.dispatchEvent(new CustomEvent('notifications-updated'))
      } catch (e) { /* ignore */ }
    },
    askDeleteOne(n) {
      this.pendingIds = [n.id]
      this.confirmMessage = this.$t('notifications.confirmDeleteOne')
      this.showConfirm = true
    },
    async proceedDelete() {
      if (!this.pendingIds.length) { this.showConfirm = false; return }
      this.deleting = true
      try {
        const token = localStorage.getItem('user-token')
        if (this.pendingIds.length === 1) {
          await axios.delete(`http://127.0.0.1:8000/api/notifications/${this.pendingIds[0]}/`, { headers: { Authorization: `Token ${token}` } })
          this.showToast(this.$t('notifications.deletedOne'))
        } else {
          await axios.post('http://127.0.0.1:8000/api/notifications/bulk-delete/', { ids: this.pendingIds }, { headers: { Authorization: `Token ${token}` } })
          this.showToast(this.$t('notifications.deletedMany', { n: this.pendingIds.length }))
        }
        await this.reload()
        this.selectMode = false
        this.selectedIds = []
        window.dispatchEvent(new CustomEvent('notifications-updated'))
      } catch (e) { /* ignore */ } finally {
        this.deleting = false
        this.showConfirm = false
        this.pendingIds = []
      }
    },
    cancelDelete() {
      this.showConfirm = false
      this.pendingIds = []
    },
    showToast(msg) {
      this.toast = msg
      if (this.toastTimer) clearTimeout(this.toastTimer)
      this.toastTimer = setTimeout(() => { this.toast = '' }, 2500)
    },
    openClient(n) {
      if (n.client) {
        this.$router.push({ name: 'client-detail', params: { id: n.client }, query: { from: 'notifications' } })
      }
    },
    formatDate(iso) {
      try {
        const d = new Date(iso)
        const loc = (this.$i18n && this.$i18n.locale) || 'ru'
        return d.toLocaleString(loc === 'pl' ? 'pl-PL' : 'ru-RU', { dateStyle: 'short', timeStyle: 'short' })
      } catch (e) { return iso }
    },
    sourceLabel(s) {
      const map = { REMINDER: this.$t('notifications.sourceReminder'), SYSTEM: this.$t('notifications.sourceSystem') }
      return map[s] || s
    },
    isError(n) {
      return n.source === 'SYSTEM' && (n.title || '').startsWith('Напоминание:')
    }
  },
  mounted() { this.reload() }
  ,watch: {
    // Когда зашли на страницу (роут активирован) можно пометить непрочитанные прочитанными
  }
}
</script>

<style scoped>
.notifications-page { font-family: 'Inter', sans-serif; margin-top: -4px; }
.header { display:flex; align-items:center; justify-content:space-between; }
.actions { display: flex; gap: 12px; align-items: center; margin-bottom: 16px; }
.btn { background:var(--btn-bg,#ffffff); border:1px solid var(--btn-border,#d0d7e2); padding:8px 16px; border-radius:8px; cursor:pointer; font-weight:600; font-size:14px; line-height:1.2; display:inline-flex; align-items:center; gap:6px; color:#1e293b !important; transition:background .25s, color .25s, border-color .25s, box-shadow .25s; text-decoration:none; box-shadow:0 1px 2px rgba(0,0,0,0.04); }
.btn:not(:hover):not(:focus) { background:#ffffff; color:#1e293b !important; }
.btn.danger:not(:hover):not(:focus) { background:rgba(255,82,82,0.12); color:#c53030 !important; border-color:rgba(255,82,82,0.45); }
.btn:visited { color:#1e293b; text-decoration:none; }
.btn:hover { background:var(--primary-color); color:#fff !important; border-color:var(--primary-color); text-decoration:none; }
.btn:focus { text-decoration:none; }
.btn:disabled { opacity:.55; cursor:not-allowed; }
.btn.small { padding:6px 12px; font-size:12px; }
.counter { font-size: 14px; color: var(--muted-text,#555); }
.error-inline { padding: 16px; background: #fee; color: #c53030; border-radius: 8px; margin-bottom: 16px; font-size: 14px; }
.list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 12px; }
.item { background: var(--card-bg,#fff); border: 1px solid var(--card-border,#e2e8f0); border-radius: 10px; padding: 14px 16px; position: relative; }
.item.unread { border-color: var(--primary-color); box-shadow: 0 0 0 2px rgba(74,144,226,0.15); }
.item-header { display: flex; justify-content: space-between; gap: 12px; align-items: baseline; }
.title { font-size: 15px; line-height: 1.3; }
.time { font-size: 12px; opacity: 0.7; }
.msg { margin: 8px 0 6px; font-size: 14px; line-height: 1.5; white-space: pre-line; }
.meta { display: flex; flex-wrap: wrap; gap: 6px; }
.chip { background: #eef2f6; color: #334155; padding: 3px 8px; border-radius: 999px; font-size: 11px; font-weight: 600; }
.source { background: #f1f5f9; }
.mini { background: var(--primary-color); border: none; color: #fff; padding: 4px 10px; border-radius: 999px; font-size: 11px; cursor: pointer; }
.mini:hover { opacity: .85; }
.empty { padding: 40px 0; text-align: center; color: var(--muted-text,#666); font-size: 14px; }
.empty-simple { padding:60px 0 80px; text-align:center; font-size:15px; color:#64748b; font-weight:500; }
.linkable { cursor: pointer; text-decoration: underline; text-decoration-color: rgba(0,0,0,0.25); }
.linkable:hover { text-decoration-color: var(--primary-color); }
.mini.danger { background:rgba(255,82,82,0.12); color:#c53030; border:1px solid rgba(255,82,82,0.45); padding:4px 10px; }
.mini.danger:hover { background:rgba(255,82,82,0.20); color:#a61b1b; border-color:rgba(255,82,82,0.6); }
.load-more-wrap { margin-top: 20px; text-align: center; }
.load-more { min-width: 200px; }
.left-head { display:flex; align-items:center; gap:8px; }
.item.selected { outline:2px solid var(--primary-color); }
.btn.danger { background:rgba(255,82,82,0.12); border:1px solid rgba(255,82,82,0.45); color:#c53030 !important; }
.btn.danger:hover { background:rgba(255,82,82,0.20); border-color:rgba(255,82,82,0.6); color:#a61b1b !important; }
.btn.danger:disabled { background:rgba(255,82,82,0.08); border-color:rgba(255,82,82,0.25); color:rgba(197,48,48,0.55) !important; }
.confirm-overlay { position:fixed; inset:0; background:rgba(0,0,0,.35); display:flex; align-items:center; justify-content:center; z-index:1000; }
.confirm-dialog { background:#fff; padding:24px 28px; border-radius:14px; width: min(420px,90%); box-shadow:0 10px 30px -5px rgba(0,0,0,.25); animation:pop .18s ease; }
.confirm-message { margin:0 0 20px; font-size:15px; line-height:1.4; font-weight:500; text-align:center; }
.confirm-actions { display:flex; gap:12px; justify-content:flex-end; }
.confirm-actions.centered { justify-content:center; }
.toast { position:fixed; bottom:24px; right:24px; background:#334155; color:#fff; padding:10px 16px; border-radius:8px; font-size:14px; box-shadow:0 4px 18px -4px rgba(0,0,0,.4); }
.fade-toast-enter-active, .fade-toast-leave-active { transition: opacity .25s, transform .25s; }
.fade-toast-enter-from, .fade-toast-leave-to { opacity:0; transform:translateY(6px); }
@keyframes pop { from { transform:scale(.92); opacity:0; } to { transform:scale(1); opacity:1; } }
.item.has-client:not(.selected):not(.unread):hover { background:#f8fafc; }
.item.has-client { cursor:pointer; }
.error-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  background-color: #fee2e2;
  color: #ef4444;
  border-radius: 50%;
  font-size: 14px;
  font-weight: bold;
  margin-right: 8px;
  border: 1px solid #fecaca;
  vertical-align: middle;
}
</style>
