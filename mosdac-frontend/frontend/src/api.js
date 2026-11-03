const BASE = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')
const KEY = 'mosdac_token'

export const getToken = () => sessionStorage.getItem(KEY)
export const setToken = (t) => sessionStorage.setItem(KEY, t)
export const clearToken = () => sessionStorage.removeItem(KEY)

let onUnauthorized = () => {}
export const setUnauthorizedHandler = (fn) => { onUnauthorized = fn }

function errorText(data, status) {
  const d = data && data.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d)) return d.map((x) => `${(x.loc || []).slice(1).join('.') || 'field'}: ${x.msg}`).join('; ')
  return `Request failed (HTTP ${status}).`
}

async function request(path, { method = 'GET', body, auth = true } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  if (auth) {
    const t = getToken()
    if (t) headers.Authorization = `Bearer ${t}`
  }
  let res
  try {
    res = await fetch(`${BASE}${path}`, { method, headers, body: body ? JSON.stringify(body) : undefined })
  } catch {
    throw new Error(`Cannot reach the backend at ${BASE}. Is uvicorn running, and is CORS enabled for this origin?`)
  }
  let data = null
  try { data = await res.json() } catch { /* empty body */ }
  if (!res.ok) {
    if (auth && (res.status === 401 || res.status === 403)) {
      clearToken(); onUnauthorized()
      throw new Error('Your session expired or is invalid. Please log in again.')
    }
    const err = new Error(errorText(data, res.status)); err.status = res.status
    throw err
  }
  return data
}

export const register = (username, email, password) => request('/users/', { method: 'POST', auth: false, body: { username, email, password } })
export async function login(email, password) {
  const data = await request('/auth/login', { method: 'POST', auth: false, body: { email, password } })
  if (!data?.access_token) throw new Error('Login response did not include an access_token.')
  setToken(data.access_token)
  return data
}
export const me = () => request('/auth/me')
export const createConversation = (title = 'New MOSDAC chat') => request('/conversations/', { method: 'POST', body: { title } })
export const listConversations = () => request('/conversations/')
export const getMessages = (id) => request(`/conversations/${id}/messages`)
export const ask = (chat_id, question) => request('/chat/ask', { method: 'POST', body: { chat_id, question } })
export async function pingBackend() {
  try { return (await fetch(`${BASE}/openapi.json`)).ok } catch { return false }
}
export const apiBase = BASE
