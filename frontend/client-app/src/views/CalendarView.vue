<template>
  <div class="calendar-page">
    <header class="cal-header">
      <div class="left">
        <div class="btn-group">
          <button class="btn" @click="goPrev">{{ $t('calendar.actions.prev') }}</button>
          <button class="btn" :class="{ todayActive: cursorIsToday }" @click="goToday">{{ $t('calendar.actions.today') }}</button>
          <button class="btn" @click="goNext">{{ $t('calendar.actions.next') }}</button>
        </div>
        <h2>{{ periodLabel }}</h2>
      </div>
      <div class="right cal-filters">
        <input v-model="query" type="text" :placeholder="$t('calendar.searchPH')" class="cal-filter" />
        <UiSelect v-model="status" :options="statusOptions" :aria-label="$t('calendar.statusAll')" />
      </div>
    </header>

    <div class="calendar-surface" ref="surface">
      <div class="month-grid">
        <div class="weekdays">
          <div v-for="w in weekdays" :key="w" class="weekday">{{ w }}</div>
        </div>
        <div class="weeks">
          <div v-for="(week, wi) in calendarWeeks" :key="wi" class="week-row">
            <div
              v-for="day in week"
              :key="day.iso"
              class="day-cell"
              :class="{ muted: !day.inCurrentMonth, today: day.isToday, weekend: day.isWeekend }"
              @click.stop="openCreateOn(day)"
            >
              <div class="day-head">
                <span class="day-num" :class="{ todayPill: day.isToday }">{{ day.date.getDate() }}</span>
                <span v-if="day.moreCount>0" class="more" :title="$t('calendar.moreTasks')" @click.stop="openDayPopover(day, $event)">+{{ day.moreCount }}</span>
              </div>
              <div class="day-events">
                <div
                  v-for="e in day.displayItems"
                  :key="e.id"
                  class="event-chip compact"
                  :class="['status-' + (e.status || 'SCHEDULED').toLowerCase()]"
                  @click.stop="openCard(e)"
                  @mouseenter="showAssigneeTooltip(e, $event)"
                  @mouseleave="hideAssigneeTooltip"
                >
                  <span class="dot" :style="{ backgroundColor: statusDotColor(e.status) }"></span>
                  <span class="title" aria-label="fullTaskTitle(e)">{{ shortTaskTitle(e) }}</span>
                  <span v-if="assigneeInitials(e)" class="mini-pill" aria-hidden="true">{{ assigneeInitials(e) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <TaskForm v-if="showForm" :task="editingTask" :initialDate="creationDate" @close="showForm=false" @saved="onSaved" @back="onBackFromEdit" />
    <TaskCard v-if="showCard" :task="viewTask" @close="closeCard" @edit="openEditFromCard" @status-updated="onCardStatusUpdated" @updated="onSaved" />
    <div v-if="dayPopover" class="day-popover" :style="popoverStyle" @click.stop>
      <div class="dp-header">
        <strong>{{ formatDate(dayPopover.date) }}</strong>
        <button class="close-btn" @click="closeDayPopover">×</button>
      </div>
      <ul class="dp-list" role="list">
        <li v-for="t in dayPopover.items" :key="t.id" class="dp-item" @click="openCard(t)">
          <span class="dot" :style="{ backgroundColor: statusDotColor(t.status) }"></span>
          <span class="t-title" :title="fullTaskTitle(t)">{{ fullTaskTitle(t) }}</span>
          <span v-if="assigneeName(t)" class="t-assignee">{{ assigneeName(t) }}</span>
          <span class="status-badge" :class="(t.status || 'SCHEDULED').toLowerCase()">{{ statusLabel(t.status) }}</span>
        </li>
      </ul>
    </div>

    <div v-if="hoverTooltip.visible" class="cal-hover-tooltip" :style="{ left: hoverTooltip.x + 'px', top: hoverTooltip.y + 'px' }">{{ hoverTooltip.text }}</div>
  </div>
</template>

<script>
import axios from 'axios';
import TaskForm from '../components/TaskForm.vue';
import TaskCard from '../components/TaskCard.vue';
import UiSelect from '../components/UiSelect.vue';

export default {
  name: 'CalendarView',
  components: { TaskForm, TaskCard, UiSelect },
  data() {
    const now = new Date();
    return {
      cursor: now,
      events: [],
      query: '',
      status: '',
      showForm: false,
      editingTask: null,
      creationDate: null,
      showCard: false,
      viewTask: null,
      weekdays: [],
      users: [],
      usersMap: {},
      usersFallback: false,
      dayPopover: null,
      popoverPos: { x: 0, y: 0 },
      resizeRaf: null,
      hoverTooltip: { visible:false, text:'', x:0, y:0 }
    };
  },
  created() {
    this.load();
    this.loadUsers();
    try {
      const loc = (this.$i18n && this.$i18n.locale) || 'ru';
      const map = { ru: 'ru-RU', pl: 'pl-PL' };
      const base = new Date(Date.UTC(2023, 0, 2));
      this.weekdays = Array.from({ length: 7 }, (_, i) => {
        const d = new Date(base); d.setDate(base.getDate() + i);
        return d.toLocaleDateString(map[loc] || 'ru-RU', { weekday: 'short' }).replace('.', '');
      });
    } catch (e) { void e }
  },
  computed: {
    periodLabel() {
      const loc = (this.$i18n && this.$i18n.locale) || 'ru';
      const map = { ru: 'ru-RU', pl: 'pl-PL' };
      const raw = new Intl.DateTimeFormat(map[loc] || 'ru-RU', { month: 'long', year: 'numeric' }).format(this.cursor);
      try {
        if (!raw) return '';
        return raw.charAt(0).toUpperCase() + raw.slice(1);
      } catch { return raw }
    },
    cursorIsToday(){
      const now = new Date();
      return this.isSameDate(this.cursor, now);
    },
    filteredEvents(){
      const q = (this.query || '').trim().toLowerCase();
      if(!q) return this.events;
      return this.events.filter(e => (
        (e.title && e.title.toLowerCase().includes(q)) ||
        (e.client_name && e.client_name.toLowerCase().includes(q)) ||
        (this.assigneeName(e) && this.assigneeName(e).toLowerCase().includes(q))
      ));
    },
    statusOptions(){
      return [
        { value: '', label: this.$t('calendar.statusAll') },
        { value: 'SCHEDULED', label: this.$t('tasks.status.SCHEDULED') },
        { value: 'DONE', label: this.$t('tasks.status.DONE') },
        { value: 'CANCELLED', label: this.$t('tasks.status.CANCELLED') }
      ];
    },
    calendarWeeks() {
      const [start, end] = this.monthGridRange(this.cursor);
      const byDay = {};
      for (const e of this.filteredEvents) {
        const d = this.toISODate(new Date(e.start));
        if (!byDay[d]) byDay[d] = [];
        byDay[d].push(e);
      }
      const days = []; const cur = new Date(start);
      while (cur <= end) {
        const iso = this.toISODate(cur);
        const list = (byDay[iso] || []).sort((a,b)=> new Date(a.start) - new Date(b.start));
        const display = list.slice(0,3); const moreCount = Math.max(0, list.length - display.length);
        days.push({ date:new Date(cur), iso, inCurrentMonth: cur.getMonth()===this.cursor.getMonth(), isToday: this.isSameDate(cur,new Date()), isWeekend: this.isWeekend(cur), items:list, displayItems:display, moreCount });
        cur.setDate(cur.getDate()+1);
      }
      const weeks=[]; for(let i=0;i<days.length;i+=7) weeks.push(days.slice(i,i+7)); return weeks;
    },
    // Inline absolute positioning (top/left) to avoid initial 0,0 flash with CSS variables
    popoverStyle(){
      return {
        top: this.popoverPos.y + 'px',
        left: this.popoverPos.x + 'px'
      };
    },
    canCreateTask() {
      try {
        const permsJson = localStorage.getItem('user-permissions');
        if (!permsJson) return true;
        const perms = JSON.parse(permsJson);
        return !!perms.can_create_task;
      } catch (e) { return true; }
    }
  },
  methods: {
    async loadUsers(){
      const token = localStorage.getItem('user-token'); if(!token) return;
      try { const resp = await axios.get('http://127.0.0.1:8000/api/company/users/', { headers:{ Authorization:'Token '+token } }); this.users = resp.data; }
      catch(e){ this.usersFallback = true; try { const me = await axios.get('http://127.0.0.1:8000/api/user-info/', { headers:{ Authorization:'Token '+token } }); this.users=[{ id:me.data.id, username:me.data.username }]; } catch {/* ignore */} }
      finally { this.usersMap = Object.fromEntries(this.users.map(u=>{ const full=`${u.first_name||''} ${u.last_name||''}`.trim(); return [u.id, full || u.username || u.email || ('ID '+u.id)]; })); }
    },
    scheduleResize(){ if(this.resizeRaf) cancelAnimationFrame(this.resizeRaf); this.resizeRaf = requestAnimationFrame(()=> this.updateCalHeight()); },
    updateCalHeight(){
      try {
        const el=this.$refs.surface; if(!el) return;
        const rect=el.getBoundingClientRect();
        const bottomGap=36;
        let available=window.innerHeight-rect.top-bottomGap;
        if(available<320) available=window.innerHeight-rect.top-4;
        const h=Math.max(300,available);
        el.style.setProperty('--cal-height', h+'px');
        this.$nextTick(()=>{
          try {
            const after=el.getBoundingClientRect();
            const overflow=after.bottom-window.innerHeight;
            if(overflow>0) el.style.setProperty('--cal-height',(h-overflow-12)+'px');
            this.setLayoutMetrics();
          } catch(e) {
            // swallow minor resize race conditions
            if(process && process.env && process.env.NODE_ENV==='development') console.debug('updateCalHeight inner', e);
          }
        });
      } catch(e) {
        // non-fatal layout calc failure
        if(process && process.env && process.env.NODE_ENV==='development') console.debug('updateCalHeight outer', e);
      }
    },
    setLayoutMetrics(){
      try {
        const el=this.$refs.surface; if(!el) return;
        const header=el.querySelector('.weekdays');
        const headerH= header? header.getBoundingClientRect().height:0;
        el.style.setProperty('--weekdays-h', headerH+'px');
        el.style.setProperty('--weeks-count','6');
        const testWeek=el.querySelector('.week-row');
        let gap=6;
        if(testWeek){
          const styles=getComputedStyle(testWeek.parentElement);
          const g=parseFloat(styles.rowGap || styles.gap || '6');
            if(!isNaN(g)) gap=g;
        }
        el.style.setProperty('--week-gap', gap+'px');
      } catch(e) {
        if(process && process.env && process.env.NODE_ENV==='development') console.debug('setLayoutMetrics', e);
      }
    },
    toISODate(d){ return [d.getFullYear(), String(d.getMonth()+1).padStart(2,'0'), String(d.getDate()).padStart(2,'0')].join('-'); },
    isSameDate(a,b){ return a.getFullYear()===b.getFullYear() && a.getMonth()===b.getMonth() && a.getDate()===b.getDate(); },
    isWeekend(d){ const wd=d.getDay(); return wd===0 || wd===6; },
    monthGridRange(d){ const first=new Date(d.getFullYear(), d.getMonth(),1); const last=new Date(d.getFullYear(), d.getMonth()+1,0); const dayFirst=first.getDay()||7; const gridStart=new Date(first); gridStart.setDate(first.getDate()-(dayFirst-1)); gridStart.setHours(0,0,0,0); const dayLast=last.getDay()||7; const gridEnd=new Date(last); gridEnd.setDate(last.getDate()+(7-dayLast)); gridEnd.setHours(23,59,59,999); return [gridStart, gridEnd]; },
    async load(){ const token=localStorage.getItem('user-token'); if(!token){ this.$router.push('/login'); return; } try { const [start,end]=this.monthGridRange(this.cursor); const params=new URLSearchParams(); params.set('start', start.toISOString()); params.set('end', end.toISOString()); if(this.status) params.set('status', this.status); const resp= await axios.get(`http://127.0.0.1:8000/api/tasks/?${params.toString()}`, { headers:{ Authorization:`Token ${token}` } }); this.events = resp.data.map(e=>({ ...e, client_name: e.client ? `${e.client.first_name||''} ${e.client.last_name||''}`.trim():'' })); this.$nextTick(()=>{ this.setLayoutMetrics(); this.updateCalHeight(); }); } catch(e){ console.error('Не удалось загрузить задачи', e); this.events=[]; this.$nextTick(()=>{ this.setLayoutMetrics(); this.updateCalHeight(); }); } },
    goPrev(){ this.shift(-1); }, goNext(){ this.shift(1); }, goToday(){ this.cursor=new Date(); this.load(); }, shift(step){ const d=new Date(this.cursor); d.setMonth(d.getMonth()+step); this.cursor=d; this.load(); },
    statusDotColor(status){
      const s = (status || '').toLowerCase();
      if(s==='done') return '#16a34a';
      if(s==='cancelled') return '#dc2626';
      return '#4A90E2'; // scheduled / default
    },
    assigneeName(e){
      try{
        if (Array.isArray(e?.assignees_display) && e.assignees_display.length) {
          const name = String(e.assignees_display[0] || '').trim()
          if (name) return name
        }
        if(!e.assignees || !e.assignees.length) return ''
        const id = e.assignees[0]
        return this.usersMap[id] || ('ID '+id)
      } catch { return '' }
    },
    assigneeInitials(e){ const name=this.assigneeName(e); if(!name) return ''; const parts=name.split(/\s+/).filter(Boolean).slice(0,2); return parts.map(p=>p[0]).join('').toUpperCase(); },
    shortTaskTitle(e){ const base = e.title || '—'; return base.length>14 ? base.slice(0,12)+'…' : base; },
    fullTaskTitle(e){ return e.title || '—'; },
    statusLabel(s){ if(s==='DONE') return this.$t('tasks.status.DONE'); if(s==='CANCELLED') return this.$t('tasks.status.CANCELLED'); return this.$t('tasks.status.SCHEDULED'); },
    openCreateOn(day){ 
      if (!this.canCreateTask) return;
      this.editingTask=null; const d=new Date(day.date); d.setHours(9,0,0,0); this.creationDate=d; this.showForm=true; 
    },
    openEdit(task){ this.editingTask=task; this.creationDate=null; this.showForm=true; this.showCard=false; },
    openCard(task){
      // Ensure any open day list popover is closed so it doesn't overlap the card
      this.closeDayPopover();
      this.viewTask=task;
      this.showCard=true;
    },
    openEditFromCard(task){ this.openEdit(task); },
    closeCard(){ this.showCard=false; this.viewTask=null; },
    onBackFromEdit(){
      const t = this.editingTask
      this.showForm = false
      if (t) this.openCard(t)
    },
    async onCardStatusUpdated(status){
      try{
        if(this.viewTask) this.viewTask.status = status
        const id = this.viewTask && this.viewTask.id
        await this.load()
        if(id){
          const updated = this.events.find(e => e.id === id)
          if(updated) this.viewTask = updated
        }
      }catch{/* ignore refresh issues; keep card open */}
    },
    openDayPopover(day, evt){
      const anchorEl = evt.currentTarget.closest('.day-cell');
      // Pre-sort items so count matches final content
      const items = day.items.slice().sort((a,b)=> (a.title||'').localeCompare(b.title||''));
      // Precompute approximate position BEFORE rendering to avoid initial 0,0 flash
      this.popoverPos = this.estimatePopoverPosition(anchorEl, items.length);
      // Set popover (will render already at computed coords)
      this.dayPopover={ date:new Date(day.date), iso:day.iso, items };
      // Refine after actual DOM mounted (in case height differs due to scrollbars)
      this.$nextTick(()=>{ this.positionPopover(anchorEl); });
      document.addEventListener('click', this.onGlobalClick, true);
      document.addEventListener('keydown', this.onKeyClose, true);
    },
    estimatePopoverPosition(anchor, itemsLen){
      try {
        const surface=this.$refs.surface; if(!surface||!anchor) return { x:0, y:0 };
        const sRect=surface.getBoundingClientRect();
        const aRect=anchor.getBoundingClientRect();
        const pW=300;
        const pH = Math.min(420, 56 + itemsLen * 42);
        // Try right side first
        let left = aRect.left - sRect.left + aRect.width + 10;
        let top = aRect.top - sRect.top;
        if(left + pW > sRect.width - 8){
          // fallback left side
          left = aRect.left - sRect.left - pW - 10;
        }
        // Clamp vertically
        if(top + pH > sRect.height - 8) top = sRect.height - pH - 8;
        if(top < 4) top = 4;
        return { x:left, y:top };
      } catch { return { x:0, y:0 }; }
    },
    closeDayPopover(){ this.dayPopover=null; document.removeEventListener('click', this.onGlobalClick, true); document.removeEventListener('keydown', this.onKeyClose, true); },
    onGlobalClick(e){ if(!this.dayPopover) return; const pop=this.$el.querySelector('.day-popover'); if(pop && pop.contains(e.target)) return; this.closeDayPopover(); },
    onKeyClose(e){ if(e.key==='Escape') this.closeDayPopover(); },
    positionPopover(anchor){
      try {
        const surface=this.$refs.surface; const pop=this.$el.querySelector('.day-popover');
        if(!surface||!anchor||!pop) return;
        const sRect=surface.getBoundingClientRect();
        const aRect=anchor.getBoundingClientRect();
        const pW=300;
        const pH=Math.min(420, 56+this.dayPopover.items.length*42);
        let left = aRect.left - sRect.left + aRect.width + 10; // right side
        let top = aRect.top - sRect.top;
        if(left + pW > sRect.width - 8){
          left = aRect.left - sRect.left - pW - 10; // fallback left
        }
        if(top + pH > sRect.height - 8){
          top = sRect.height - pH - 8;
        }
        if(top < 4) top = 4;
        this.popoverPos={ x:left, y:top };
      } catch(e) {
        if(process && process.env && process.env.NODE_ENV==='development') console.debug('positionPopover', e);
      }
    },
    formatDate(d){ try { return d.toLocaleDateString((this.$i18n && this.$i18n.locale)==='pl'?'pl-PL':'ru-RU', { day:'2-digit', month:'2-digit', year:'numeric' }); } catch { return '' } },
    async onSaved(){ this.showForm=false; this.closeCard(); await this.load(); },
    showAssigneeTooltip(task, evt){ const name=this.assigneeName(task); if(!name) return; const rect=evt.currentTarget.getBoundingClientRect(); const x=Math.min(window.innerWidth-10, rect.left + rect.width/2); let y=rect.top - 10; if(y<12) y=rect.bottom + 10; this.hoverTooltip={ visible:true, text:name, x, y }; },
    hideAssigneeTooltip(){ this.hoverTooltip.visible=false; }
  },
  watch: { status(){ this.load(); } },
  mounted(){ this.$nextTick(()=>{ this.setLayoutMetrics(); this.updateCalHeight(); }); window.addEventListener('resize', this.scheduleResize); window.addEventListener('orientationchange', this.scheduleResize); document.body.classList.add('no-cal-scroll'); },
  beforeUnmount(){ window.removeEventListener('resize', this.scheduleResize); window.removeEventListener('orientationchange', this.scheduleResize); if(this.resizeRaf) cancelAnimationFrame(this.resizeRaf); document.body.classList.remove('no-cal-scroll'); this.closeDayPopover(); }
};
</script>

<style scoped>
.calendar-page { padding: 20px 22px 10px; display:flex; flex-direction:column; }
.cal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.btn-group { display: inline-flex; gap: 8px; }
.btn { height: 36px; padding: 0 12px; border: 1px solid var(--btn-border); border-radius: 8px; background: var(--btn-bg); color: var(--btn-text); cursor: pointer; position:relative; overflow:hidden;
  transition: background-color .18s ease, color .18s ease, border-color .18s ease, box-shadow .18s ease, transform .18s ease; }
.btn:before { content:""; position:absolute; left:-40%; top:0; width:40%; height:100%; background:linear-gradient(120deg, rgba(255,255,255,0) 0%, rgba(255,255,255,.55) 50%, rgba(255,255,255,0) 100%); transform:skewX(-18deg); opacity:0; }
.btn:hover { background: #f0f6ff; border-color:#b9d4f5; box-shadow:0 1px 3px rgba(0,0,0,.06); }
.btn:hover:before { animation: btnShine .9s ease; }
.btn:active { transform: translateY(1px); }
.btn.todayActive { background:#e4f1ff; border-color:#4A90E2; color:#2563eb; box-shadow:0 0 0 1px rgba(74,144,226,.35), 0 2px 4px -1px rgba(74,144,226,.25); font-weight:600; }
.btn.todayActive:hover { background:#d9ebff; }
@keyframes btnShine { 0% { transform:translateX(0) skewX(-18deg); opacity:0; } 30% { opacity:.9; } 60% { opacity:.4; } 100% { transform:translateX(260%) skewX(-18deg); opacity:0; } }
.cal-filters { display:flex; align-items:center; gap:10px; }
.cal-filter { height:40px; padding:0 12px; border:1px solid #e2e8f0; border-radius:8px; background:#fff; font-family:'Inter', sans-serif; font-size:14px; color:#334155; box-shadow:0 1px 0 rgba(0,0,0,0.02) inset; transition:border-color .2s ease, box-shadow .2s ease, background-color .18s ease; display:inline-flex; align-items:center; }
.cal-filter:focus { outline:none; border-color:#4A9E80; box-shadow:0 0 0 2px rgba(74,158,128,.18); }
.cal-filter:hover { background:#f7f9fc; }
.cal-filter::placeholder { color:#94a3b8; }
/* Styled UiSelect to match Finance filters */
/* Removed view mode select styling (month only now) */
/* Ensure UiSelect inside calendar matches finance styling */
.cal-filters :deep(.ui-select__trigger){ height:40px; padding:8px 10px; border-radius:8px; border:1px solid #e2e8f0; background:#fff; color:#334155; font-size:14px; }
.cal-filters :deep(.ui-select__trigger:focus){ outline:none; border-color:#4A9E80; box-shadow:0 0 0 2px rgba(74,158,128,.18); }
.cal-filters :deep(.ui-select__trigger:hover){ background:#f7f9fc; }
.cal-filters :deep(.ui-select__dropdown){ background:#fff; border:1px solid #e0e6ed; border-radius:10px; box-shadow:0 16px 40px rgba(0,0,0,0.12); padding:6px 0; }
.cal-filters :deep(.ui-select__option){ padding:10px 12px; }
.cal-filters :deep(.ui-select__option:hover),
.cal-filters :deep(.ui-select__option.focused){ background:#f7f9fc; }
.cal-filters :deep(.ui-select__option.selected){ background:#e8f4f0; color:#2f7f66; font-weight:600; }
.calendar-surface { position: relative; background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 12px; padding: 10px; display:flex; flex-direction:column; height: var(--cal-height, 70vh); overflow:hidden; }
.calendar-surface .empty { color:#5a6a7b; display:flex; align-items:center; gap:12px; padding: 16px; }
.event-chip { display:inline-flex; align-items:center; gap:6px; border-radius:8px; padding:4px 8px; margin:4px 0; cursor:pointer; font-size:12px; border:1px solid; position:relative; overflow:hidden;
  transition: transform .18s ease, box-shadow .22s ease; }
.event-chip:hover { transform:translateY(-3px) scale(1.035); box-shadow:0 4px 14px -4px rgba(0,0,0,.18), 0 6px 20px -10px rgba(0,0,0,.12); }
.event-chip:active { transform:translateY(-1px) scale(1.02); box-shadow:0 3px 10px -4px rgba(0,0,0,.22); }
.event-chip.compact { transition: transform .18s ease, box-shadow .22s ease; }
.event-chip.compact { padding:3px 6px; margin:2px 0; }
.event-chip .dot { width: 8px; height: 8px; border-radius: 50%; }
.event-chip .time { color: #5a6a7b; }

/* Month grid styles */
.month-grid { display:flex; flex-direction:column; gap:6px; flex:1; min-height:0; height:100%; }
.weekdays { display:grid; grid-template-columns: repeat(7, 1fr); gap:6px; padding:0 2px; color:#5a6a7b; font-weight:600; font-size:12px; }
.weekday { text-align:center; }
.weeks { display:flex; flex-direction:column; gap:6px; flex:1; min-height:0; height:calc(var(--cal-height) - var(--weekdays-h,24px) - 4px); }
.week-row { display:grid; grid-template-columns: repeat(7, 1fr); gap:6px; flex:none; min-height:0; height:calc((100% - (var(--weeks-count,6) - 1)*var(--week-gap,6px)) / var(--weeks-count,6)); }
.day-cell { padding:6px 6px 4px; background:#fff; cursor:pointer; border-radius:10px; border:1px solid #dfe3e8; box-sizing:border-box;
  transition: background-color .12s ease, border-color .12s ease, box-shadow .12s ease; display:flex; flex-direction:column; min-height:0; height:100%; }
.day-cell:hover { background:#f5f9ff; border-color:#c9d4de; }
.day-cell.muted { background:#fafbfc; color:#9aa3af; }
.day-cell.weekend { background:#fffaf2; }
.day-cell.today { background:linear-gradient(180deg,#f0f7ff 0%,#ffffff 90%); border-color:#4A90E2; box-shadow:0 0 0 1px rgba(74,144,226,.4); }
.day-head { display:flex; justify-content:space-between; align-items:center; padding-bottom:2px; margin-bottom:4px; border-bottom:1px solid #f0f2f5; }
.day-num { font-size:11px; color:#111827; background:#eef2f7; border-radius:6px; padding:2px 5px; font-weight:600; box-shadow:0 1px 0 rgba(0,0,0,.04); }
.day-num.todayPill { background:var(--primary-color); color:#fff; }
.more { font-size:10px; color:#2563eb; background:#eaf1ff; border:1px solid #cfe0ff; padding:1px 5px; border-radius:999px; box-shadow:0 1px 0 rgba(0,0,0,.04); }
.day-events { margin-top:2px; flex:1; min-height:0; overflow:auto; }

/* Event chip themes by status */
.event-chip.status-scheduled { background:#f5f9ff; border-color:#d6e6ff; }
.event-chip.status-done { background:#ecfdf3; border-color:#bbf7d0; }
.event-chip.status-cancelled { background:#fef2f2; border-color:#fecaca; }
/* Event chip type accent adjusts dot color (already via inline style) */
.event-chip .title { max-width: 120px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.event-chip .assignee { color:#334155; font-weight:500; }
/* Expanding assignee name on hover */
/* Removed inline expand variant */

/* Floating tooltip for assignee */
.cal-hover-tooltip { position:fixed; z-index:8000; background:#111827; color:#fff; font-size:12px; padding:6px 10px; border-radius:8px; font-weight:600; line-height:1.2; transform:translate(-50%, -100%); pointer-events:none; box-shadow:0 6px 18px -4px rgba(0,0,0,.28), 0 2px 6px rgba(0,0,0,.2); animation:fadeInTooltip .15s ease; }
@keyframes fadeInTooltip { from { opacity:0; transform:translate(-50%, -90%); } to { opacity:1; transform:translate(-50%, -100%); } }

/* Additional compact decorations */
.mini-pill { background:#eef2f7; color:#334155; font-size:10px; padding:2px 6px; line-height:1; border-radius:999px; font-weight:600; }
.status-badge { font-size:10px; padding:2px 6px; border-radius:999px; font-weight:600; background:#f1f5f9; color:#475569; }
.status-badge.done { background:#dcfce7; color:#15803d; }
.status-badge.cancelled { background:#fee2e2; color:#b91c1c; }

/* Day popover */
.day-popover { position:absolute; z-index:1500; width:300px; max-width:94%; background:#fff; border:1px solid #dbe2e8; border-radius:14px; box-shadow:0 10px 32px -6px rgba(0,0,0,.22); padding:10px 0 8px; animation:fadePop .18s ease; top:0; left:0; }
.day-popover .dp-header { display:flex; align-items:center; justify-content:space-between; padding:0 14px 6px; border-bottom:1px solid #eef2f5; margin-bottom:6px; }
.day-popover .close-btn { background:none; border:none; font-size:18px; cursor:pointer; line-height:1; color:#64748b; padding:2px 4px; }
.day-popover .close-btn:hover { color:#334155; }
.day-popover .dp-list { list-style:none; margin:0; padding:0 4px 0 0; max-height:360px; overflow:auto; }
.day-popover .dp-item { display:flex; align-items:center; gap:8px; padding:6px 14px 6px 14px; font-size:13px; cursor:pointer; border-left:3px solid transparent; position:relative; }
.day-popover .dp-item .dot { flex:none; width:8px; height:8px; border-radius:50%; }
.day-popover .dp-item:hover { background:#f5f9ff; border-left-color:#4A90E2; }
.day-popover .dp-item .t-title { flex:1; min-width:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.day-popover .dp-item .t-assignee { font-size:11px; color:#475569; }
@keyframes fadePop { from { opacity:0; transform:translateY(6px); } to { opacity:1; transform:translateY(0); } }

/* Positioning computed in JS */
/* Position now set inline via top/left (see popoverStyle) */

/* (Removed week/day list styles) */

@media (max-height: 850px) {
  .calendar-page { padding:16px 18px 8px; }
  .month-grid { gap:4px; }
  .weeks { gap:4px; }
  .week-row { gap:4px; }
  .day-cell { padding:4px 4px 3px; }
  .day-head { margin-bottom:4px; padding-bottom:3px; }
  .day-num { font-size:10px; }
  .event-chip { margin:2px 0; padding:3px 6px; font-size:11px; }
  .event-chip .title { max-width:100px; }
}
</style>

<style>
body.no-cal-scroll { overflow:hidden; }
</style>