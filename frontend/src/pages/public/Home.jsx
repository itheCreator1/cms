import { useEffect, useState } from 'react'

import { getHealth } from '../../services/health'

export default function Home() {
  const [connected, setConnected] = useState(null)

  useEffect(() => {
    let active = true
    getHealth()
      .then(({ status }) => active && setConnected(status === 'ok'))
      .catch(() => active && setConnected(false))
    return () => { active = false }
  }, [])

  return (
    <section>
      <p className="eyebrow">Role-based publishing</p>
      <h1>CMS project skeleton</h1>
      <p aria-live="polite">
        {connected === null && 'Checking backend…'}
        {connected === true && 'Backend connected'}
        {connected === false && 'Backend unavailable'}
      </p>
    </section>
  )
}
