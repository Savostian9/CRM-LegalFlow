<template>
  <div class="client-card-wrapper">
    <header class="card-header">
      <div class="header-left">
  <h1>{{ $t('settings.title') }}</h1>
      </div>
    </header>

    <div class="card-content">
      <!-- Autofill guard: attracts password managers away from real fields -->
      <div class="autofill-guard" aria-hidden="true">
        <input type="text" name="username" autocomplete="username" tabindex="-1" />
        <input type="email" name="email" autocomplete="email" tabindex="-1" />
        <input type="password" name="password" autocomplete="current-password" tabindex="-1" />
      </div>
      <!-- Tabs -->
      <div class="tabs">
    <button :class="['tab', {active: activeTab==='profile'}]" @click="activeTab='profile'">{{ $t('settings.tabs.profile') }}</button>
  <button :class="['tab', {active: activeTab==='company'}]" @click="activeTab='company'" v-if="isOwner">{{ $t('settings.tabs.company') }}</button>
  <button :class="['tab', {active: activeTab==='users'}]" @click="activeTab='users'" v-if="isAdminOrLead">{{ $t('settings.tabs.users') }}</button>
  <button :class="['tab', {active: activeTab==='invites'}]" @click="activeTab='invites'" v-if="isAdminOrLead && canInviteUsers">{{ $t('settings.tabs.invites') }}</button>
      </div>

      <!-- Profile -->
      <section v-if="activeTab==='profile'" class="data-section">
  <h3>{{ $t('settings.profile.title') }}</h3>
        <form class="data-grid profile-form" autocomplete="off" @submit.prevent>
          <div class="data-item">
            <label>{{ $t('settings.profile.firstName') }}</label>
            <input
              v-model="profile.first_name"
              @blur="saveProfileField('first_name')"
              type="text"
              name="given-name"
              autocomplete="section-profile given-name"
              autocapitalize="words"
              autocorrect="off"
              spellcheck="false"
              data-form-type="other"
            />
          </div>
          <div class="data-item">
            <label>{{ $t('settings.profile.lastName') }}</label>
            <input
              v-model="profile.last_name"
              @blur="saveProfileField('last_name')"
              type="text"
              name="family-name"
              autocomplete="section-profile family-name"
              autocapitalize="words"
              autocorrect="off"
              spellcheck="false"
              readonly
              @focus="e => e.target.removeAttribute('readonly')"
              data-form-type="other"
            />
          </div>
          
        </form>

  <h3 style="margin-top:24px;">{{ $t('settings.password.title') }}</h3>
        <form class="data-grid pwd-form" autocomplete="on" @submit.prevent="changePassword">
          <div class="data-item">
            <label>{{ $t('settings.password.current') }}</label>
            <input
              v-model="password.old"
              type="password"
              autocomplete="current-password"
              autocapitalize="off"
              autocorrect="off"
              spellcheck="false"
              readonly
              @focus="e => e.target.removeAttribute('readonly')"
            />
          </div>
          <div class="data-item">
            <label>{{ $t('settings.password.new') }}</label>
            <input
              v-model="password.new"
              type="password"
              autocomplete="new-password"
              autocapitalize="off"
              autocorrect="off"
              spellcheck="false"
              readonly
              @focus="e => e.target.removeAttribute('readonly')"
            />
          </div>
          <div class="data-item full-width" style="display:flex; justify-content:flex-end;">
            <button class="button secondary" type="submit" :disabled="!password.old || !password.new">{{ $t('settings.password.update') }}</button>
          </div>
        </form>

        <div class="data-section" style="margin-top: 10px;">
          <h3>{{ $t('settings.danger.title') }}</h3>
          <p>{{ $t('settings.danger.desc') }}</p>
          <div class="data-grid">
            <div class="data-item">
              <label>{{ $t('settings.danger.confirmPassword') }}</label>
              <input
                v-model="deletePassword"
                type="password"
                :placeholder="$t('settings.danger.confirmPasswordPH')"
                autocomplete="current-password"
                autocapitalize="off"
                autocorrect="off"
                spellcheck="false"
                readonly
                @focus="e => e.target.removeAttribute('readonly')"
              />
            </div>
            <div class="data-item full-width" style="display:flex; justify-content:flex-end;">
              <button class="button danger" @click="openDeleteConfirm">{{ $t('settings.danger.deleteAccount') }}</button>
            </div>
          </div>
        </div>
      </section>

      <div v-if="activeTab==='users' && isAdminOrLead" style="margin-top:-28px; margin-bottom:12px; display:flex; justify-content:flex-end; gap:8px;">
        <button class="button secondary" @click="openBulkPermissions">Права для всех</button>
      </div>

      <!-- Company -->
  <section v-if="activeTab==='company' && isOwner" class="data-section">
  <h3>{{ $t('settings.company.title') }}</h3>
        <div class="data-grid">
          <div class="data-item">
            <label>{{ $t('settings.company.name') }}</label>
            <input v-model="company.name" type="text" @blur="saveCompany" />
          </div>
          <div class="data-item full-width">
            <label>{{ $t('settings.company.address') }}</label>
            <textarea v-model="company.address" rows="2" @blur="saveCompany"></textarea>
          </div>
          <div class="data-item full-width">
            <label>{{ $t('settings.company.legal') }}</label>
            <textarea v-model="company.legal_details" rows="4" @blur="saveCompany"></textarea>
          </div>
        </div>
      </section>

      <!-- Users -->
  <section v-if="activeTab==='users' && isAdminOrLead" class="data-section">
  <h3>{{ $t('settings.users.title') }}</h3>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>{{ $t('settings.users.name') }}</th>
                <th>{{ $t('settings.users.email') }}</th>
                <th>{{ $t('settings.users.role') }}</th>
                <th>Права</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in users" :key="u.id">
                <td>{{ u.first_name }} {{ u.last_name }}</td>
                <td>{{ u.email }}</td>
                <td>
                  <template v-if="u.is_owner">
                    <div class="static-role">{{ $t('roles.lead') }}</div>
                  </template>
                  <template v-else>
                    <select v-model="u.role" @change="updateUser(u)">
                      <option value="ADMIN">{{ $t('roles.admin') }}</option>
                      <option value="LEAD">{{ $t('roles.lead') }}</option>
                      <option value="MANAGER">{{ $t('roles.manager') }}</option>
                      <option value="LAWYER">{{ $t('roles.lawyer') }}</option>
                      <option value="ASSISTANT">{{ $t('roles.assistant') }}</option>
                    </select>
                  </template>
                </td>
                <td>
                  <button class="button secondary" style="margin-right:6px;" @click="openPermissions(u)">Доступ</button>
                </td>
                <td>
                  <button class="button danger" @click="removeUser(u)">{{ $t('common.delete') }}</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Invites -->
  <section v-if="activeTab==='invites' && isAdminOrLead && canInviteUsers" class="data-section">
  <h3>{{ $t('settings.invites.title') }}</h3>
        <div class="invite-form">
          <select v-model="inviteRole" :aria-label="$t('settings.invites.roleAria')">
            <option value="ADMIN">{{ $t('roles.admin') }}</option>
            <option value="LEAD">{{ $t('roles.leadFull') }}</option>
            <option value="MANAGER">{{ $t('roles.manager') }}</option>
            <option value="LAWYER">{{ $t('roles.lawyer') }}</option>
            <option value="ASSISTANT">{{ $t('roles.assistant') }}</option>
          </select>
          <button class="button primary" @click="createInvite">{{ $t('settings.invites.create') }}</button>
        </div>
        <div class="invites-list" v-if="invites.length">
          <div v-for="i in invites" :key="i.token" class="invite-item">
            <div class="invite-link">{{ inviteBase }}?invite={{ i.token }}</div>
            <button class="button secondary" @click="copyInvite(i.token)">{{ $t('common.copy') }}</button>
          </div>
        </div>
      </section>
    </div>

    <!-- Confirm Dialog -->
    <div v-if="showConfirmDialog" class="confirm-dialog-overlay">
      <div class="confirm-dialog">
  <p>{{ $t('settings.danger.deleteConfirm') }}</p>
        <div class="confirm-dialog-actions">
          <button class="button primary" @click="confirmDeletion">{{ $t('common.yesDelete') }}</button>
          <button class="button secondary" @click="cancelDeletion">{{ $t('common.cancel') }}</button>
        </div>
      </div>
    </div>

    <!-- User Delete Confirm Dialog -->
    <div v-if="showUserDeleteDialog" class="confirm-dialog-overlay">
      <div class="confirm-dialog">
        <p>
          {{ $t('settings.users.deleteUser') }}
          {{ userToDelete ? (userToDelete.first_name || '') : '' }}
          {{ userToDelete ? (userToDelete.last_name || '') : '' }}?
        </p>
        <div class="confirm-dialog-actions">
          <button class="button primary" @click="confirmUserDeletion">{{ $t('common.yesDelete') }}</button>
          <button class="button secondary" @click="cancelUserDeletion">{{ $t('common.cancel') }}</button>
        </div>
      </div>
    </div>

    <teleport to="body">
      <transition name="toast-fade">
        <div v-if="toast.show" :class="['toast-notification', toast.type]">{{ toast.message }}</div>
      </transition>
    </teleport>
    <!-- Модалка прав пользователя -->
    <div v-if="showPermModal" class="confirm-dialog-overlay">
      <div class="confirm-dialog" style="max-width:640px;">
        <h3 style="margin-top:0;">Доступ пользователя</h3>
        <p style="margin-top:0; font-size:14px; margin-bottom: 18px;">Отметьте действия, которые этому сотруднику разрешено выполнять.</p>
        <p v-if="permUser" style="margin-top:0; font-size:14px; font-weight: 600;">{{ permUser.first_name }} {{ permUser.last_name }} — {{ permUser.email }}</p>
        <div class="perm-grid">
          <div class="perm-col perm-card">
            <h4>Клиенты</h4>
            <label><input type="checkbox" v-model="permForm.can_create_client"> Создание клиентов</label>
            <label><input type="checkbox" v-model="permForm.can_edit_client"> Редактирование клиентов</label>
            <label><input type="checkbox" v-model="permForm.can_delete_client"> Удаление клиентов</label>
          </div>
          <div class="perm-col perm-card">
            <h4>Дела и файлы</h4>
            <label><input type="checkbox" v-model="permForm.can_create_case"> Создание дел</label>
            <label><input type="checkbox" v-model="permForm.can_edit_case"> Редактирование дел</label>
            <label><input type="checkbox" v-model="permForm.can_delete_case"> Удаление дел</label>
            <label><input type="checkbox" v-model="permForm.can_upload_files"> Загрузка и удаление файлов</label>
          </div>
          <div class="perm-col perm-card">
            <h4>Задачи</h4>
            <label><input type="checkbox" v-model="permForm.can_create_task"> Создание задач</label>
            <label><input type="checkbox" v-model="permForm.can_edit_task"> Редактирование задач</label>
            <label><input type="checkbox" v-model="permForm.can_delete_task"> Удаление задач</label>
          </div>
          <div class="perm-col perm-card">
            <h4>Администрирование</h4>
            <label><input type="checkbox" v-model="permForm.can_invite_users"> Создание приглашений</label>
            <label><input type="checkbox" v-model="permForm.can_manage_users"> Управление пользователями</label>
          </div>
        </div>
        <p v-if="permUser && permUser.is_owner" style="color:#b91c1c; font-size:12px; margin-top:8px;">Владельца нельзя менять.</p>
        <div class="confirm-dialog-actions" style="margin-top:24px;">
          <button class="button primary" :disabled="permUser && permUser.is_owner" @click="savePermissions">Сохранить</button>
          <button class="button secondary" @click="closePerms">Отмена</button>
        </div>
      </div>
    </div>
    <!-- Модалка массовых прав -->
    <div v-if="showBulkPermModal" class="confirm-dialog-overlay">
      <div class="confirm-dialog" style="max-width:640px;">
        <h3 style="margin-top:0;">Массовое применение прав</h3>
        <p style="margin-top:0; font-size:13px;">Отметьте права, которые нужно применить ко всем сотрудникам компании (владельца можно включить ниже).</p>
        <div class="perm-grid">
          <div class="perm-col perm-card">
            <h4>Клиенты</h4>
            <label><input type="checkbox" v-model="bulkPermForm.can_create_client"> Создание клиентов</label>
            <label><input type="checkbox" v-model="bulkPermForm.can_edit_client"> Редактирование клиентов</label>
            <label><input type="checkbox" v-model="bulkPermForm.can_delete_client"> Удаление клиентов</label>
          </div>
          <div class="perm-col perm-card">
            <h4>Дела и файлы</h4>
            <label><input type="checkbox" v-model="bulkPermForm.can_create_case"> Создание дел</label>
            <label><input type="checkbox" v-model="bulkPermForm.can_edit_case"> Редактирование дел</label>
            <label><input type="checkbox" v-model="bulkPermForm.can_delete_case"> Удаление дел</label>
            <label><input type="checkbox" v-model="bulkPermForm.can_upload_files"> Загрузка и удаление файлов</label>
          </div>
          <div class="perm-col perm-card">
            <h4>Задачи</h4>
            <label><input type="checkbox" v-model="bulkPermForm.can_create_task"> Создание задач</label>
            <label><input type="checkbox" v-model="bulkPermForm.can_edit_task"> Редактирование задач</label>
            <label><input type="checkbox" v-model="bulkPermForm.can_delete_task"> Удаление задач</label>
          </div>
          <div class="perm-col perm-card">
            <h4>Администрирование</h4>
            <label><input type="checkbox" v-model="bulkPermForm.can_invite_users"> Создание приглашений</label>
            <label><input type="checkbox" v-model="bulkPermForm.can_manage_users"> Управление пользователями</label>
          </div>
        </div>
        <label style="display:block; margin:16px 0 4px; font-size:13px; font-weight:500;">
          <input type="checkbox" v-model="bulkIncludeOwner" style="margin-right:6px;"> Включить владельца
        </label>
        <div class="confirm-dialog-actions" style="margin-top:16px;">
          <button class="button primary" @click="applyBulkPermissions">Применить</button>
          <button class="button secondary" @click="closeBulkPerms">Отмена</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from '@/axios-setup'
export default {
  name: 'SettingsView',
  data(){
    return {
      activeTab: 'profile',
      me: { role: 'MANAGER' },
      profile: { username: '', first_name: '', last_name: '', phone: '' },
      password: { old: '', new: '' },
      company: { name: '', address: '', legal_details: '', invite_code: '' },
      users: [],
      // --- Права ---
      showPermModal: false,
      permUser: null,
      permForm: {
        can_create_client: true, can_edit_client: true, can_delete_client: true,
        can_create_case: true, can_edit_case: true, can_delete_case: true,
        can_create_task: true, can_edit_task: true, can_delete_task: true,
        can_upload_files: true, can_invite_users: true, can_manage_users: true,
      },
      showBulkPermModal: false,
      bulkPermForm: {
        can_create_client: true, can_edit_client: true, can_delete_client: true,
        can_create_case: true, can_edit_case: true, can_delete_case: true,
        can_create_task: true, can_edit_task: true, can_delete_task: true,
        can_upload_files: true, can_invite_users: true, can_manage_users: true,
      },
      bulkIncludeOwner: false,
      invites: [],
      inviteRole: 'MANAGER',
      deletePassword: '',
      toast: { show: false, type: 'success', message: '' },
      showConfirmDialog: false,
      showUserDeleteDialog: false,
      userToDelete: null,
      notifications: [], // добавлено: список уведомлений после фильтрации
    }
  },
  computed: {
    canInviteUsers() {
      try {
        const permsJson = localStorage.getItem('user-permissions');
        if (!permsJson) return true;
        const perms = JSON.parse(permsJson);
        return !!perms.can_invite_users;
      } catch (e) { return true; }
    },
    canManageUsers() {
      try {
        const permsJson = localStorage.getItem('user-permissions');
        if (!permsJson) return true;
        const perms = JSON.parse(permsJson);
        return !!perms.can_manage_users;
      } catch (e) { return true; }
    },
    isAdmin(){ return this.me.role === 'ADMIN' },
    isAdminOrLead(){ return this.me.role === 'ADMIN' || this.me.role === 'LEAD' },
    isManager(){ return this.me.role === 'MANAGER' },
    isLawyer(){ return this.me.role === 'LAWYER' },
    isAssistant(){ return this.me.role === 'ASSISTANT' },
    isLeaderOrLawyer(){ return this.isAdmin || this.isAdminOrLead || this.isLawyer },
    isOwner(){
      try{
        if (!Array.isArray(this.users) || !this.users.length) return false;
        const meId = this.me && this.me.id;
        if (!meId) return false;
        const meRow = this.users.find(u => u.id === meId);
        return !!(meRow && meRow.is_owner === true);
      } catch(_) { return false }
    },
    inviteBase(){ return window.location.origin + '/register' }
  },
  async created(){
    try {
      const token = localStorage.getItem('user-token');
      const cfg = { headers: { Authorization: `Token ${token}` } };
      // base URLs are rewritten to /api by axios-setup when needed; prefer relative
      try {
        const me = await axios.get('/api/user-info/', cfg);
        this.me = me.data || this.me;
      } catch (e) { /* unauthorized or network */ }

      try {
        const prof = await axios.get('/api/profile/', cfg);
        this.profile = prof.data || this.profile;
      } catch (e) { /* ignore */ }

      if (!this.isManager) {
        try{
          const cs = await axios.get('/api/company/settings/', cfg);
          this.company = cs.data || this.company;
        } catch (e) {
          if (this.isAdmin) {
            try{
              const res = await axios.put('/api/company/settings/', { name: this.$t('settings.company.name') }, cfg);
              this.company = res.data || this.company;
            } catch (ee) { /* ignore */ }
          }
        }
        try{
          const us = await axios.get('/api/company/users/', cfg);
          this.users = Array.isArray(us.data) ? us.data : this.users;
        } catch (e) { /* ignore */ }
      }
      await this.fetchNotifications();
    } catch (_) {
      // Do not let errors during created() break render in production
    }
  },
  methods: {
    notify(msg, type='success', ms=2000){
      this.toast = { show: true, type, message: msg };
      setTimeout(() => { this.toast.show = false }, ms);
    },
    roleLabel(role){
      switch(role){
        case 'MANAGER': return this.$t('roles.manager');
        case 'LAWYER': return this.$t('roles.lawyer');
        case 'ASSISTANT': return this.$t('roles.assistant');
        case 'LEAD': return this.$t('roles.lead');
        case 'ADMIN': return this.$t('roles.admin');
        default: return role;
      }
    },
    async saveProfile(){
      const token = localStorage.getItem('user-token');
      const cfg = { headers: { Authorization: `Token ${token}` } };
  const { first_name, last_name } = this.profile;
  await axios.put('/api/profile/', { first_name, last_name }, cfg);
      this.notify(`${this.$t('settings.toasts.savedProfile')}!`, 'success', 1500);
      this.emitUserProfileUpdated();
    },
    async saveProfileField(field){
      try{
        const token = localStorage.getItem('user-token');
        const cfg = { headers: { Authorization: `Token ${token}` } };
        const payload = { [field]: this.profile[field] };
        await axios.put('/api/profile/', payload, cfg);
        this.notify(`${this.$t('settings.toasts.saved')}!`, 'success', 1500);
        if(['first_name','last_name'].includes(field)){
          this.emitUserProfileUpdated();
        }
      } catch(e){
        this.notify(this.$t('settings.toasts.saveError'), 'error');
      }
    },
    emitUserProfileUpdated(){
      try {
        window.dispatchEvent(new CustomEvent('user-profile-updated', { detail: {
          first_name: this.profile.first_name,
          last_name: this.profile.last_name,
        }}));
      } catch(_) { /* no-op */ }
    },
    async changePassword(){
      if(!this.password.old || !this.password.new){
        this.notify(this.$t('settings.toasts.needPasswords'), 'error');
        return;
      }
      const token = localStorage.getItem('user-token');
      try{
  await axios.post('/api/profile/change-password/', { old_password: this.password.old, new_password: this.password.new }, { headers: { Authorization: `Token ${token}` } });
        this.password.old = this.password.new = '';
        this.notify(this.$t('settings.toasts.passwordUpdated'));
      } catch(e){
        this.notify(this.$t('settings.toasts.passwordUpdateError'), 'error');
      }
    },
    openDeleteConfirm(){
      if(!this.deletePassword) { this.notify(this.$t('settings.toasts.needPassword'), 'error'); return; }
      this.showConfirmDialog = true;
    },
    cancelDeletion(){ this.showConfirmDialog = false; },
    async confirmDeletion(){
      const token = localStorage.getItem('user-token');
      try{
  await axios.post('/api/profile/delete-account/', { password: this.deletePassword }, { headers: { Authorization: `Token ${token}` } });
        localStorage.removeItem('user-token');
        this.showConfirmDialog = false;
        this.notify(this.$t('settings.toasts.accountDeleted'));
        setTimeout(() => { this.$router.push('/login') }, 800);
      } catch(e){
        this.showConfirmDialog = false;
        this.notify(this.$t('settings.toasts.accountDeleteError'), 'error');
      }
    },
    async saveCompany(){
      const token = localStorage.getItem('user-token');
      const cfg = { headers: { Authorization: `Token ${token}` } };
      const { name, address, legal_details } = this.company;
      try {
        const res = await axios.put('/api/company/settings/', { name, address, legal_details }, cfg);
        this.company = res.data;
        this.notify(`${this.$t('settings.toasts.saved')}!`, 'success', 1500);
        // Notify layout/sidebar to refresh company display name
        try { window.dispatchEvent(new CustomEvent('company-updated', { detail: { name: this.company.name } })); } catch(_) { /* no-op */ }
      } catch (e) {
        this.notify(this.$t('settings.toasts.companySaveError'), 'error');
      }
    },
    async updateUser(u){
      const token = localStorage.getItem('user-token');
  const res = await axios.put(`/api/company/users/${u.id}/`, { role: u.role }, { headers: { Authorization: `Token ${token}` } });
      Object.assign(u, res.data);
    },
    async removeUser(u){
      this.userToDelete = u;
      this.showUserDeleteDialog = true;
    },
    cancelUserDeletion(){
      this.showUserDeleteDialog = false;
      this.userToDelete = null;
    },
    async confirmUserDeletion(){
      if (!this.userToDelete) return;
      const u = this.userToDelete;
      const token = localStorage.getItem('user-token');
      try{
        await axios.delete(`/api/company/users/${u.id}/`, { headers: { Authorization: `Token ${token}` } });
        this.users = this.users.filter(x => x.id !== u.id);
        this.notify(this.$t('settings.toasts.userDeleted'));
      } catch(e){
        this.notify(this.$t('settings.toasts.userDeleteError'), 'error');
      } finally {
        this.cancelUserDeletion();
      }
    },
    async createInvite(){
      if (!this.company || !this.company.id) {
        alert(this.$t('settings.toasts.createCompanyFirst'));
        return;
      }
      const token = localStorage.getItem('user-token');
      try {
        const res = await axios.post('/api/company/invites/', { role: this.inviteRole }, { headers: { Authorization: `Token ${token}` } });
        this.invites.unshift(res.data);
      } catch (e) {
        const msg = e.response?.data?.detail || this.$t('settings.toasts.inviteCreateError');
        this.notify(msg, 'error');
      }
    },
    async copyInvite(token){
      const text = `${this.inviteBase}?invite=${token}`;
      try{ await navigator.clipboard.writeText(text); this.notify(this.$t('settings.toasts.linkCopied')); } catch (err) { this.notify(text); }
    },
    async fetchNotifications(){
      try{
        const token = localStorage.getItem('user-token');
        const cfg = { headers: { Authorization: `Token ${token}` } };
        const res = await axios.get('/api/notifications/', cfg);
        const payload = res && res.data ? res.data : [];
        const items = Array.isArray(payload) ? payload : Array.isArray(payload.items) ? payload.items : [];
        let list = items;
        if (this.isManager) {
          const myId = this.me && this.me.id;
          if (myId) {
            list = items.filter(n =>
              n.user_id === myId ||
              n.recipient_id === myId ||
              (n.user && (n.user.id === myId || n.user === myId)) ||
              (n.owner_id === myId)
            );
          }
        }
        this.notifications = list;
      } catch(e){
        /* ignore */
      }
    },
    // ---- Permissions ----
    async openPermissions(u){
      this.permUser = u; this.showPermModal = true;
      try{
        const token = localStorage.getItem('user-token');
        const res = await axios.get(`/api/company/users/${u.id}/permissions/`, { headers:{ Authorization:`Token ${token}` }});
        const d = res.data || {}; Object.keys(this.permForm).forEach(k=>{ if(k in d) this.permForm[k]=!!d[k]; });
        if('is_owner' in d) this.permUser.is_owner = d.is_owner;
      }catch(e){ this.notify('Ошибка загрузки прав','error'); }
    },
    closePerms(){ this.showPermModal=false; this.permUser=null; },
    async savePermissions(){
      if(!this.permUser) return; if(this.permUser.is_owner) return;
      try{
        const token = localStorage.getItem('user-token');
        await axios.put(`/api/company/users/${this.permUser.id}/permissions/`, this.permForm, { headers:{ Authorization:`Token ${token}` }});
        this.notify('Права сохранены'); this.closePerms();
      }catch(e){ this.notify('Ошибка сохранения','error'); }
    },
    openBulkPermissions(){ this.showBulkPermModal=true; },
    closeBulkPerms(){ this.showBulkPermModal=false; },
    async applyBulkPermissions(){
      try{
        const token = localStorage.getItem('user-token');
        const payload = { ...this.bulkPermForm, exclude_owner: !this.bulkIncludeOwner };
        await axios.post('/api/company/users/permissions/bulk/', payload, { headers:{ Authorization:`Token ${token}` }});
        this.notify('Массовые права применены'); this.closeBulkPerms();
      }catch(e){ this.notify('Ошибка применения','error'); }
    },
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --primary-color: #4A9E80;
  --primary-hover-color: #428f74;
  --dark-blue: #2c3e50;
  --text-color: #5a6a7b;
  --background-color: #f7f9fc;
  --white-color: #ffffff;
  --input-border-color: #e0e6ed;
  --input-shadow: inset 0 1px 2px rgba(0,0,0,0.07);
  --border-color-light: #e0e6ed;
  --danger-color: #dc2626;
}

.client-card-wrapper {
  font-family: 'Inter', sans-serif;
  background-color: var(--white-color);
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.07);
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  background-color: var(--background-color);
  border-bottom: 1px solid var(--border-color-light);
  gap: 20px;
}

.header-left {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
}

.card-header h1 {
  font-size: 22px;
  color: var(--dark-blue);
  margin: 0;
}

.card-content {
  padding: 30px;
}

.tabs { display:flex; flex-wrap: wrap; gap:8px; margin-bottom: 16px; }
.tab { padding:10px 16px; border:1px solid var(--input-border-color); border-radius:10px; background:#fff; cursor:pointer; font-weight:600; color: var(--dark-blue); }
.tab.active { background:#e0f2ea; border-color:#c7e6db; color:#2f7f66; }

.data-section { margin-bottom: 40px; }
.data-section:last-child { margin-bottom: 0; }
.data-section h3 { font-size: 18px; font-weight: 600; color: var(--dark-blue); margin-bottom: 25px; padding-bottom: 15px; border-bottom: 1px solid var(--border-color-light); }

.data-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 25px; align-items: end; }

.data-item label { display: block; margin-bottom: 8px; font-weight: 600; font-size: 15px; color: var(--dark-blue); }

.data-item input,
.data-item textarea,
.data-item select { width: 100%; height: 48px; padding: 0 15px; border: 1px solid var(--form-border,#e2e8f0); border-radius: var(--form-radius,8px); box-sizing: border-box; font-family: 'Inter', sans-serif; font-size: 15px; background-color: var(--white-color); transition: border-color 0.18s, box-shadow 0.18s, background-color .25s; display: flex; align-items: center; }

.data-item textarea { padding: 12px 15px; resize: vertical; min-height: 80px; height: auto; }

.data-item input:focus,
.data-item textarea:focus,
.data-item select:focus { outline: none; border-color: var(--form-border-focus,#4A9E80); box-shadow: var(--form-focus-ring,0 0 0 2px rgba(74,158,128,.18)); }

.data-item.full-width { grid-column: 1 / -1; }

.button { padding: 12px 24px; text-decoration: none; border-radius: 12px; font-weight: 600; border: none; cursor: pointer; transition: all 0.3s ease; }
.button.primary { background-color: var(--primary-color); color: #ffffff !important; box-shadow: 0 6px 10px rgba(62, 63, 63, 0.25); }
.button.primary:hover { background-color: var(--primary-hover-color); color: #000000 !important; transform: translateY(-2px); box-shadow: 0 8px 15px rgba(62, 63, 63, 0.3); }
.button.secondary { background-color: #f0f2f5; color: var(--dark-blue); box-shadow: 0 6px 10px rgba(0, 0, 0, 0.05); }
.button.secondary:hover { background-color: #e4e6e9; transform: translateY(-2px); box-shadow: 0 8px 15px rgba(0, 0, 0, 0.08); }
.button:disabled,
.button[disabled] { opacity: 0.6; cursor: not-allowed; transform: none; box-shadow: none; }
.button.danger { background-color: #fee2e2; color: var(--danger-color); border: 1px solid #fecaca; }
.button.danger:hover { background-color: #fecaca; }

.table-wrap { overflow: auto; }
.table-wrap table { width: 100%; border-collapse: collapse; }
.table-wrap th, .table-wrap td { padding: 10px; border-top: 1px solid var(--border-color-light); text-align: left; }
/* Ensure header row bold */
.table-wrap thead th { font-weight:700; }
.table-wrap input:not([type="checkbox"]),
.table-wrap select { width: 100%; height: 48px; padding: 0 15px; border: 1px solid var(--form-border,#e2e8f0); border-radius: var(--form-radius,8px); box-sizing: border-box; font-family: 'Inter', sans-serif; font-size: 15px; background-color: var(--white-color); transition: border-color 0.18s, box-shadow 0.18s; }
.table-wrap input:not([type="checkbox"]):focus,
.table-wrap select:focus { outline: none; border-color: var(--form-border-focus,#4A9E80); box-shadow: var(--form-focus-ring,0 0 0 2px rgba(74,158,128,.18)); }

.invite-box { margin-top:16px; display:flex; gap:12px; align-items:center; }
.invites-list { margin-top: 14px; }
.invite-link { display: inline-block; margin-top: 12px; padding: 10px 14px; font-size: 16px; font-weight: 600; color: var(--dark-blue); background: #f3f6fb; border: 1px solid var(--input-border-color); border-radius: 10px; letter-spacing: 0.2px; word-break: break-all; }
.invite-form { display:flex; gap:12px; align-items:center; }
.invite-form select { height: 48px; padding: 0 38px 0 15px; border: 1px solid var(--form-border,#e2e8f0); border-radius: var(--form-radius,8px); font-size: 15px; background: #fff; transition:border-color .18s, box-shadow .18s; cursor: pointer; 
  /* show a clear dropdown indicator so users know it's a list */
  appearance: none; -webkit-appearance: none; -moz-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%235a6a7b' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: right 12px center; background-size: 16px;
}
.invite-form select:focus { outline:none; border-color:var(--form-border-focus,#4A9E80); box-shadow:var(--form-focus-ring,0 0 0 2px rgba(74,158,128,.18)); }

.static-role { height: 48px; display: flex; align-items: center; padding: 0 15px; border: 1px solid var(--form-border,#e2e8f0); border-radius: var(--form-radius,8px); background: #f9fafb; color: #111827; }

.toast-notification { position: fixed; top: 20px; right: 20px; padding: 12px 20px; border-radius: 10px; color: #fff; font-weight: 600; font-size: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.18); z-index: 2000; display: inline-flex; align-items: center; gap: 10px; background: linear-gradient(180deg,#4A90E2,#3b7fc9); border:1px solid #3b7fc9; pointer-events: none; }
.toast-notification.success { /* inherits base blue styles */ --_success: 1; }
.toast-notification.error { background: linear-gradient(180deg,#dc2626,#b91c1c); border-color:#b91c1c; }
.toast-fade-enter-active, .toast-fade-leave-active { transition: opacity 0.5s, transform 0.5s; }
.toast-fade-enter-from, .toast-fade-leave-to { opacity: 0; transform: translateY(-20px); }

@media (max-width: 1024px) {
  .data-grid { grid-template-columns: 1fr; gap: 18px; }
}

.checkbox { display: flex; align-items: center; gap: 8px; }
.autofill-guard { position: absolute; top: -9999px; left: -9999px; width: 0; height: 0; overflow: hidden; opacity: 0; pointer-events: none; }
.pm-decoy { position: absolute !important; width: 1px !important; height: 1px !important; padding: 0 !important; margin: -1px !important; border: 0 !important; clip: rect(0 0 0 0) !important; clip-path: inset(50%) !important; overflow: hidden !important; white-space: nowrap !important; }

.confirm-dialog-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 2000; }
.confirm-dialog { background: #fff; padding: 24px 28px; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.25); max-width: 420px; width: 92vw; }
.confirm-dialog p { margin: 0 0 16px 0; font-size: 16px; color: var(--dark-blue); font-weight: 500; }
.confirm-dialog-actions { display: flex; gap: 12px; justify-content: flex-end; }
.perm-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap: 18px; margin-top:6px; }
.perm-col { padding:0; }
.perm-card { background:#f9fafb; border:1px solid #e2e8f0; border-radius:10px; padding:14px 16px; box-shadow:0 1px 2px rgba(0,0,0,0.05); }
.perm-col h4 { margin:0 0 10px 0; font-size:15px; font-weight:600; letter-spacing:.2px; }
.perm-col label { display:flex; align-items: center; font-size:13px; margin-bottom:6px; cursor:pointer; line-height:18px; }
.perm-col input[type="checkbox"] { margin-right: 8px; width: 16px; height: 16px; accent-color:#3B82F6; }
/* Fallback for browsers without accent-color: make blue when checked */
.perm-col input[type="checkbox"]:checked { background-color:#3B82F6; border-color:#3B82F6; }
.perm-card { transition: border-color .18s, box-shadow .18s, background-color .25s; }
.perm-card:hover { border-color:#3B82F6; box-shadow:0 0 0 1px rgba(59,130,246,.35), 0 2px 6px rgba(0,0,0,.08); }
.perm-card:focus-within { border-color:#2563eb; box-shadow:0 0 0 2px rgba(37,99,235,.35); }
</style>
