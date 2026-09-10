import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { useAuth } from '../../context/AuthContext'
import Button from '../../components/ui/Button'
import FormField from '../../components/ui/FormField'
import styles from './AuthPage.module.css'
import typography from '../../components/ui/Typography.module.css'

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
    <section className={`${styles.panel} ${styles.systemAccess}`}>
      <p className={typography.eyebrow}>Restricted entry point</p>
      <h1 className={typography.pageTitle}>System access</h1>
      <p>Superadmin accounts use this isolated sign-in.</p>
      <form className={styles.form} onSubmit={handleSubmit}>
        <FormField id="system-email" label="Email" type="email" value={email} onChange={event => setEmail(event.target.value)} required autoComplete="email" />
        <FormField id="system-password" label="Password" type="password" value={password} onChange={event => setPassword(event.target.value)} required autoComplete="current-password" />
        {error && <p className={styles.error} role="alert">{error}</p>}
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Entering…' : 'Enter system'}
        </Button>
      </form>
    </section>
  )
}
