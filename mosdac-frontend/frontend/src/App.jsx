import { useEffect, useState } from 'react'
import LandingPage from './components/LandingPage.jsx'
import AuthPage from './components/AuthPage.jsx'
import ChatLayout from './components/ChatLayout.jsx'
import { clearToken, getToken, me, setUnauthorizedHandler } from './api.js'

export default function App() {
  const [view, setView] = useState(getToken() ? 'boot' : 'landing')
  const [user, setUser] = useState(null)
  const [notice, setNotice] = useState('')

  const logout = (msg = '') => { clearToken(); setUser(null); setNotice(msg); setView('auth') }

  useEffect(() => {
    setUnauthorizedHandler(() => logout('Your session expired. Please log in again.'))
    if (getToken()) {
      me().then((u) => { setUser(u); setView('chat') }).catch(() => setView('landing'))
    }
  }, [])

  return (
    <div className="app">
      <div className="stars" aria-hidden="true" />
      {view === 'boot' && <div className="center-msg">Establishing link…</div>}
      {view === 'landing' && <LandingPage onLaunch={() => setView('auth')} />}
      {view === 'auth' && <AuthPage notice={notice} onAuthed={(u) => { setUser(u); setNotice(''); setView('chat') }} />}
      {view === 'chat' && user && <ChatLayout user={user} onLogout={() => logout()} />}
    </div>
  )
}
