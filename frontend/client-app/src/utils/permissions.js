// Utility functions for checking user permissions
export function getUserPermissions() {
  try {
    const permsJson = localStorage.getItem('user-permissions');
    if (!permsJson) return null;
    return JSON.parse(permsJson);
  } catch (e) {
    console.error('Error parsing user permissions:', e);
    return null;
  }
}

export function hasPermission(permissionName) {
  const perms = getUserPermissions();
  if (!perms) return true; // Default to true if permissions not loaded
  return !!perms[permissionName];
}

// Export individual permission checkers for convenience
export const canCreateClient = () => hasPermission('can_create_client');
export const canEditClient = () => hasPermission('can_edit_client');
export const canDeleteClient = () => hasPermission('can_delete_client');
export const canCreateCase = () => hasPermission('can_create_case');
export const canEditCase = () => hasPermission('can_edit_case');
export const canDeleteCase = () => hasPermission('can_delete_case');
export const canCreateTask = () => hasPermission('can_create_task');
export const canEditTask = () => hasPermission('can_edit_task');
export const canDeleteTask = () => hasPermission('can_delete_task');
export const canUploadFiles = () => hasPermission('can_upload_files');
export const canInviteUsers = () => hasPermission('can_invite_users');
export const canManageUsers = () => hasPermission('can_manage_users');

// Vue mixin for easy access in components
export const permissionsMixin = {
  computed: {
    userPermissions() {
      return getUserPermissions();
    },
    canCreateClient() { return canCreateClient(); },
    canEditClient() { return canEditClient(); },
    canDeleteClient() { return canDeleteClient(); },
    canCreateCase() { return canCreateCase(); },
    canEditCase() { return canEditCase(); },
    canDeleteCase() { return canDeleteCase(); },
    canCreateTask() { return canCreateTask(); },
    canEditTask() { return canEditTask(); },
    canDeleteTask() { return canDeleteTask(); },
    canUploadFiles() { return canUploadFiles(); },
    canInviteUsers() { return canInviteUsers(); },
    canManageUsers() { return canManageUsers(); }
  }
};
