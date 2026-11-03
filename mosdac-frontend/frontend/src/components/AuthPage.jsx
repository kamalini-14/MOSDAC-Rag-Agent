import { useState } from 'react'
import LoginForm from './LoginForm.jsx'
import RegisterForm from './RegisterForm.jsx'

export default function AuthPage({ onAuthed, notice }) {
  const [mode, setMode] = useState('login')
  const [info, setInfo] = useState(notice || '')
  return (
    <main className="auth-page">
      <div className="auth-card">
        <div className="brand"><span className="logo-dot" />MOSDAC AI</div>
        <h2>{mode === 'login' ? 'Log in to Mission Control' : 'Create your account'}</h2>
        {info && <div className="alert info" role="status">{info}</div>}
        {mode === 'login'
          ? <LoginForm onAuthed={onAuthed} onSwitch={() => { setInfo(''); setMode('register') }} />
          : <RegisterForm onAuthed={onAuthed} onSwitch={(msg) => { setInfo(msg || ''); setMode('login') }} />}
      </div>
    </main>
  )
}
