import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { useAuth } from '../../context/AuthContext'

export default function SystemAccess() {
  const { superadminLogin } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)
    try {
      await superadminLogin(email, password)
      navigate('/dashboard', { replace: true })
    } catch (loginError) {
      setError(loginError.message || 'Unable to sign in. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className="system-access auth-panel">
      <p className="eyebrow">Restricted entry point</p>
      <h1>System access</h1>
      <p>Superadmin accounts use this isolated sign-in.</p>
      <form onSubmit={handleSubmit}>
        <label>
          Email
          <input type="email" value={email} onChange={event => setEmail(event.target.value)} required autoComplete="email" />
        </label>
        <label>
          Password
          <input type="password" value={password} onChange={event => setPassword(event.target.value)} required autoComplete="current-password" />
        </label>
        {error && <p role="alert">{error}</p>}
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Entering…' : 'Enter system'}
        </button>
      </form>
    </section>
  )
}
