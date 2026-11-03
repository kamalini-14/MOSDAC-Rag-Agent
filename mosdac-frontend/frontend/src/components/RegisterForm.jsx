import { useState } from 'react'
import { Loader2 } from 'lucide-react'
import { login, me, register } from '../api.js'

export default function RegisterForm({ onAuthed, onSwitch }) {
  const [f, setF] = useState({ username: '', email: '', password: '', confirm: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value })

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    if (!f.username.trim()) return setError('Choose a username.')
    if (!/^\S+@\S+\.\S+$/.test(f.email)) return setError('Enter a valid email address.')
    if (f.password.length < 8) return setError('Password must be at least 8 characters.')
    if (f.password !== f.confirm) return setError('Passwords do not match.')
    setLoading(true)
    try {
      await register(f.username.trim(), f.email.trim(), f.password)
    } catch (err) { setLoading(false); return setError(err.message) }
    try {
      await login(f.email.trim(), f.password)
      onAuthed(await me())
    } catch {
      onSwitch('Account created. Please log in.')
    } finally { setLoading(false) }
  }

  return (
    <form onSubmit={submit} noValidate>
      <label htmlFor="r-user">Username</label>
      <input id="r-user" autoComplete="username" value={f.username} onChange={set('username')} />
      <label htmlFor="r-email">Email</label>
      <input id="r-email" type="email" autoComplete="email" value={f.email} onChange={set('email')} />
      <label htmlFor="r-pass">Password (8+ characters)</label>
      <input id="r-pass" type="password" autoComplete="new-password" value={f.password} onChange={set('password')} />
      <label htmlFor="r-conf">Confirm password</label>
      <input id="r-conf" type="password" autoComplete="new-password" value={f.confirm} onChange={set('confirm')} />
      {error && <div className="alert error" role="alert">{error}</div>}
      <button className="btn-glow full" disabled={loading}>{loading ? <><Loader2 className="spin" size={18} /> Creating account…</> : 'Create account'}</button>
      <p className="switch">Already registered? <button type="button" className="link" onClick={() => onSwitch('')}>Log in</button></p>
    </form>
  )
}
