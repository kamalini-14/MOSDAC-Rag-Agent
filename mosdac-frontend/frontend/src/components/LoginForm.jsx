import { useState } from 'react'
import { Eye, EyeOff, Loader2 } from 'lucide-react'
import { login, me } from '../api.js'

export default function LoginForm({ onAuthed, onSwitch }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [show, setShow] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    if (!/^\S+@\S+\.\S+$/.test(email)) return setError('Enter a valid email address.')
    if (!password) return setError('Enter your password.')
    setLoading(true)
    try {
      await login(email.trim(), password)
      onAuthed(await me())
    } catch (err) {
      setError(err.status === 401 || err.status === 400 || err.status === 404 ? `Login failed: ${err.message}` : err.message)
    } finally { setLoading(false) }
  }

  return (
    <form onSubmit={submit} noValidate>
      <label htmlFor="l-email">Email</label>
      <input id="l-email" type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} />
      <label htmlFor="l-pass">Password</label>
      <div className="pw">
        <input id="l-pass" type={show ? 'text' : 'password'} autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <button type="button" className="icon-btn" onClick={() => setShow(!show)} aria-label={show ? 'Hide password' : 'Show password'}>
          {show ? <EyeOff size={18} /> : <Eye size={18} />}
        </button>
      </div>
      {error && <div className="alert error" role="alert">{error}</div>}
      <button className="btn-glow full" disabled={loading}>{loading ? <><Loader2 className="spin" size={18} /> Logging in…</> : 'Log in'}</button>
      <p className="switch">New here? <button type="button" className="link" onClick={onSwitch}>Create an account</button></p>
    </form>
  )
}
