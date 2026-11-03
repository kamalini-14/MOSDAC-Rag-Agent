import { useCallback, useEffect, useState } from 'react'
import Sidebar from './Sidebar.jsx'
import ChatWindow from './ChatWindow.jsx'
import { ask, createConversation, getMessages, listConversations, pingBackend } from '../api.js'

const toBubbles = (rows) => (rows || []).flatMap((r) => [
  { role: 'user', text: r.question },
  { role: 'assistant', text: r.answer, sources: r.sources },
])

export default function ChatLayout({ user, onLogout }) {
  const [conversations, setConversations] = useState([])
  const [loadingList, setLoadingList] = useState(true)
  const [activeId, setActiveId] = useState(null)
  const [messages, setMessages] = useState([])
  const [loadingHistory, setLoadingHistory] = useState(false)
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')
  const [status, setStatus] = useState('checking')
  const [menuOpen, setMenuOpen] = useState(false)

  const refreshList = useCallback(async () => {
    try { const d = await listConversations(); setConversations(Array.isArray(d) ? d : d?.conversations || []) }
    catch (e) { setError(e.message) } finally { setLoadingList(false) }
  }, [])

  useEffect(() => {
    refreshList()
    const check = async () => setStatus((await pingBackend()) ? 'online' : 'offline')
    check(); const t = setInterval(check, 30000); return () => clearInterval(t)
  }, [refreshList])

  const select = async (id) => {
    setMenuOpen(false); setError(''); setActiveId(id); setMessages([]); setLoadingHistory(true)
    try {
      const d = await getMessages(id)
      setMessages(toBubbles(Array.isArray(d) ? d : d?.messages))
    } catch (e) { setError(e.message) } finally { setLoadingHistory(false) }
  }
  const startNew = () => { setActiveId(null); setMessages([]); setError(''); setMenuOpen(false) }

  const send = async (question) => {
    setError(''); setSending(true)
    setMessages((m) => [...m, { role: 'user', text: question }])
    try {
      let id = activeId
      if (id == null) {
        const c = await createConversation('New MOSDAC chat')
        id = c.chat_id ?? c.id
        if (id == null) throw new Error('Backend did not return a chat_id when creating the conversation.')
        setActiveId(id)
      }
      const r = await ask(id, question)
      setMessages((m) => [...m, { role: 'assistant', text: r.answer ?? '(The backend returned no answer.)', sources: r.sources }])
      refreshList()
    } catch (e) {
      setError(e.message)
      setMessages((m) => [...m, { role: 'assistant', text: `Request failed: ${e.message}`, isError: true }])
    } finally { setSending(false) }
  }

  return (
    <div className="chat-layout">
      <Sidebar user={user} conversations={conversations} activeId={activeId} loading={loadingList} status={status}
        open={menuOpen} onClose={() => setMenuOpen(false)} onNew={startNew} onSelect={select} onLogout={onLogout} />
      {menuOpen && <div className="scrim" onClick={() => setMenuOpen(false)} />}
      <ChatWindow messages={messages} sending={sending} loadingHistory={loadingHistory} error={error} onSend={send} onMenu={() => setMenuOpen(true)} />
    </div>
  )
}
