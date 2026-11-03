import { useState } from 'react'
import { Rocket } from 'lucide-react'
import SatelliteAnimation from './SatelliteAnimation.jsx'

export default function LandingPage({ onLaunch }) {
  const [launching, setLaunching] = useState(false)
  const launch = () => {
    if (launching) return
    setLaunching(true)
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    setTimeout(onLaunch, reduce ? 0 : 1100)
  }
  return (
    <main className={`landing ${launching ? 'is-launching' : ''}`}>
      <header className="brand"><span className="logo-dot" />MOSDAC AI</header>
      <div className="status-pill"><span className="pulse" />Mission Control · Online</div>
      <SatelliteAnimation mode="hero" launching={launching} />
      <section className="hero-copy">
        <h1>Explore Earth. Understand the unseen.</h1>
        <p>A satellite knowledge assistant for MOSDAC. Ask about missions, data products, weather services and resources, and get answers drawn from the MOSDAC knowledge base.</p>
        <button className="btn-glow" onClick={launch} disabled={launching}>
          <Rocket size={18} /> Launch AI Assistant
        </button>
      </section>
    </main>
  )
}
