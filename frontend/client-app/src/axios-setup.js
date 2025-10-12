// Global Axios setup: rewrite absolute dev URLs to relative /api and set baseURL (when absolute)
import axios from 'axios'

// Any absolute URLs pointing to local backend should be rewritten
const ABSOLUTE_BACKEND_HOSTS = [
  /^https?:\/\/127\.0\.0\.1:8000\//,
  /^https?:\/\/localhost:8000\//
]

axios.interceptors.request.use((config) => {
  try {
    const url = config.url || ''
    if (typeof url === 'string') {
      for (const re of ABSOLUTE_BACKEND_HOSTS) {
        if (re.test(url)) {
          const u = new URL(url)
          // keep path + query, drop origin; nginx/devServer will proxy /api to backend
          // Result example: '/api/tasks/?q=1'
          config.url = u.pathname + (u.search || '')
          break
        }
      }
    }
  } catch (_) {
    // no-op
  }
  return config
})

// Determine optional API base from env (Vue CLI uses VUE_APP_*, Vite uses import.meta.env)
let envBase = ''
try { envBase = (import.meta && import.meta.env && import.meta.env.VITE_API_BASE) || '' } catch (_) { /* ignore */ }
if (!envBase && typeof process !== 'undefined' && process.env) {
  envBase = process.env.VUE_APP_API_BASE || ''
}

// Only set baseURL when envBase is an absolute URL (to a different origin)
if (envBase && /^https?:\/\//.test(envBase)) {
  axios.defaults.baseURL = envBase
}

export default axios
