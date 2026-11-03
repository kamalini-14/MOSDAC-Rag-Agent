import { ExternalLink, Satellite, User } from 'lucide-react'

function srcInfo(s) {
  if (typeof s === 'string') return { label: s, url: /^https?:\/\//.test(s) ? s : null }
  if (s && typeof s === 'object') {
    const url = s.url || s.link || s.source_url || null
    const label = s.title || s.name || s.source || s.filename || url || JSON.stringify(s)
    return { label: String(label), url: url && /^https?:\/\//.test(url) ? url : null }
  }
  return { label: String(s), url: null }
}

export default function MessageBubble({ role, text, sources, isError }) {
  const list = Array.isArray(sources) ? sources.map(srcInfo) : []
  return (
    <div className={`msg ${role}`}>
      <div className="avatar">{role === 'user' ? <User size={16} /> : <Satellite size={16} />}</div>
      <div className={`bubble ${isError ? 'err' : ''}`}>
        <div className="text">{text}</div>
        {list.length > 0 && (
          <div className="sources">
            <strong>Sources</strong>
            <ul>{list.map((s, i) => (
              <li key={i}>{s.url ? <a href={s.url} target="_blank" rel="noreferrer noopener">{s.label} <ExternalLink size={12} /></a> : s.label}</li>
            ))}</ul>
          </div>
        )}
      </div>
    </div>
  )
}
