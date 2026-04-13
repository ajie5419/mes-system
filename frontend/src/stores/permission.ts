import { defineStore } from 'pinia'
import client from '../api'

interface Permission {
  id: number
  code: string
  name: string
}

export const usePermissionStore = defineStore('permission', {
  state: () => ({
    permissions: {} as Record<string, Permission[]>,  // module -> permissions[]
    userPermissions: [] as string[],  // current user's permission codes
    rolePermissions: {} as Record<string, string[]>,  // role -> codes
    userRole: '',
    loaded: false,
  }),

  getters: {
    hasPermission: (state) => (code: string): boolean => {
      if (state.userRole === 'Admin') {
        return true
      }
      return state.userPermissions.includes(code)
    },
  },

  actions: {
    async fetchPermissions() {
      const { data } = await client.get('/permissions/')
      this.permissions = data
    },

    async fetchRolePermissions() {
      const { data } = await client.get('/permissions/roles')
      this.rolePermissions = data
    },

    async fetchUserPermissions() {
      // Get current user's role from auth store lazily
      // We'll use the role from auth store to filter rolePermissions
    },

    async loadForRole(role: string) {
      this.userRole = role
      if (!this.loaded) {
        await Promise.all([this.fetchPermissions(), this.fetchRolePermissions()])
        this.loaded = true
      }
      this.userPermissions = this.rolePermissions[role] || []
    },

    async updateRolePermissions(role: string, permissionCodes: string[]) {
      await client.put(`/permissions/roles/${role}`, { permission_codes: permissionCodes })
      this.rolePermissions[role] = permissionCodes
      // Refresh if current role
    },

    clear() {
      this.userPermissions = []
      this.userRole = ''
      this.loaded = false
    },
  },
})
