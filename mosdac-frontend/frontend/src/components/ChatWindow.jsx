import { useEffect, useRef, useState } from 'react'
import { Menu, Send } from 'lucide-react'
import MessageBubble from './MessageBubble.jsx'
import SatelliteAnimation, { SatelliteSvg } from './SatelliteAnimation.jsx'

const SUGGESTIONS = [
  'What satellite missions are available?',
  'Which data products does MOSDAC provide?',
  'What weather services does MOSDAC offer?',
  'How can I access MOSDAC data and resources?',
]

export default function ChatWindow({ messages, sending, loadingHistory, error, onSend, onMenu }) {
  const [text, setText] = useState('')
  const endRef = useRef(null)
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, sending])

  const submit = () => {
    const q = text.trim()
    if (!q || sending) return
    setText(''); onSend(q)
  }
  const onKey = (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submit() } }

  return (
    <section className="chat">
      <header className="chat-head">
        <button className="icon-btn mobile-only" onClick={onMenu} aria-label="Open menu"><Menu size={22} /></button>
        <span>MOSDAC knowledge assistant</span>
      </header>
      <div className="scroll" role="log" aria-live="polite">
        {loadingHistory && <p className="muted center">Loading messages…</p>}
        {!loadingHistory && messages.length === 0 && !sending && (
          <div className="welcome">
            <div className="welcome-sat"><SatelliteSvg className="sat-float" /></div>
            <h2>What would you like to discover today?</h2>
            <div className="chips">{SUGGESTIONS.map((s) => <button key={s} className="chip" onClick={() => onSend(s)} disabled={sending}>{s}</button>)}</div>
          </div>
        )}
        {messages.map((m, i) => <MessageBubble key={i} {...m} />)}
        {sending && (
          <div className="msg assistant">
            <div className="bubble thinking"><SatelliteAnimation mode="thinking" /><span>Searching the MOSDAC knowledge base…</span></div>
          </div>
        )}
        {error && <div className="alert error" role="alert">{error}</div>}
        <div ref={endRef} />
      </div>
      <div className="composer">
        <textarea rows={1} value={text} onChange={(e) => setText(e.target.value)} onKeyDown={onKey}
          placeholder="Ask about MOSDAC… (Enter to send, Shift+Enter for new line)" aria-label="Your question" />
        <button className="btn-glow send" onClick={submit} disabled={sending || !text.trim()} aria-label="Send"><Send size={18} /></button>
      </div>
    </section>
  )
}
