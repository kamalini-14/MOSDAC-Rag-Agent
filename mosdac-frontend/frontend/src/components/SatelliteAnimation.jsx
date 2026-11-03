export function SatelliteSvg({ className = '' }) {
  return (
    <svg className={className} viewBox="0 0 120 80" role="img" aria-label="Satellite">
      <g stroke="#7fe3ff" strokeWidth="1">
        <rect x="2" y="26" width="38" height="28" rx="2" fill="#12306b" />
        <rect x="80" y="26" width="38" height="28" rx="2" fill="#12306b" />
        <path d="M14 26v28M26 26v28M92 26v28M104 26v28M2 40h38M80 40h38" opacity=".55" />
      </g>
      <rect x="40" y="38" width="40" height="4" fill="#5b7aa8" />
      <rect x="46" y="28" width="28" height="24" rx="4" fill="#d9e8ff" stroke="#7fe3ff" />
      <rect x="52" y="34" width="16" height="6" rx="1" fill="#0a1426" />
      <circle cx="60" cy="46" r="3" fill="#ffb547" className="sat-led" />
      <path d="M60 28V14" stroke="#7fe3ff" strokeWidth="1.5" />
      <circle cx="60" cy="12" r="3" fill="#7fe3ff" />
    </svg>
  )
}

export function Earth({ size = 360 }) {
  return <div className="earth" style={{ width: size, height: size }} aria-hidden="true"><div className="earth-clouds" /></div>
}

/* mode "hero": big orbit scene · "thinking": small orbit shown while backend answers */
export default function SatelliteAnimation({ mode = 'hero', launching = false }) {
  if (mode === 'thinking') {
    return (
      <div className="think-orbit" aria-hidden="true">
        <div className="mini-earth" />
        <div className="think-ring"><SatelliteSvg className="think-sat" /></div>
      </div>
    )
  }
  return (
    <div className={`scene ${launching ? 'launching' : ''}`} aria-hidden="true">
      <Earth size={420} />
      <div className="ring r1" /><div className="ring r2" /><div className="ring r3" />
      <div className="orbit"><div className="sat-wrap"><SatelliteSvg className="sat" /></div></div>
      <div className="radar"><span /></div>
    </div>
  )
}
