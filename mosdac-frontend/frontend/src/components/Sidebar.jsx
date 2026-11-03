import { LogOut, MessageSquarePlus, X } from 'lucide-react'

export default function Sidebar({ user, conversations, activeId, loading, status, open, onClose, onNew, onSelect, onLogout }) {
  const label = { online: 'Backend connected', offline: 'Backend unreachable', checking: 'Checking backend…' }[status]
  return (
    <aside className={`sidebar ${open ? 'open' : ''}`}>
      <div className="side-top">
        <div className="brand"><span className="logo-dot" />MOSDAC AI</div>
        <button className="icon-btn mobile-only" onClick={onClose} aria-label="Close menu"><X size={20} /></button>
      </div>
      <button className="btn-glow full" onClick={onNew}><MessageSquarePlus size={18} /> New conversation</button>
      <nav className="history" aria-label="Conversation history">
        {loading && <p className="muted">Loading conversations…</p>}
        {!loading && conversations.length === 0 && <p className="muted">No conversations yet. Ask your first question.</p>}
        {conversations.map((c) => {
          const id = c.chat_id ?? c.id
          return (
            <button key={id} className={`hist-item ${id === activeId ? 'active' : ''}`} onClick={() => onSelect(id)} aria-current={id === activeId}>
              {c.title || `Conversation ${id}`}
            </button>
          )
        })}
      </nav>
      <div className="side-bottom">
        <div className={`conn ${status}`}><span className="pulse" />{label}</div>
        <div className="profile">
          <div className="avatar">{(user.username || user.email || '?')[0].toUpperCase()}</div>
          <div className="pinfo"><b>{user.username || 'User'}</b><small>{user.email}</small></div>
          <button className="icon-btn" onClick={onLogout} aria-label="Log out"><LogOut size={18} /></button>
        </div>
      </div>
    </aside>
  )
}
