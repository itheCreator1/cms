import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

import { useAuth } from '../../context/AuthContext'
import { hasMinimumRole } from '../../auth/roles'
import Button from '../../components/ui/Button'
import FormField from '../../components/ui/FormField'
import styles from './AuthPage.module.css'
import typography from '../../components/ui/Typography.module.css'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)
    try {
      const user = await login(email, password)
      const destination = hasMinimumRole(user.role, 'publisher')
        ? location.state?.from || '/dashboard'
        : '/'
      navigate(destination, { replace: true })
    } catch (loginError) {
      setError(loginError.message || 'Unable to sign in. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className={styles.panel}>
      <p className={typography.eyebrow}>Member access</p>
      <h1 className={typography.pageTitle}>Login</h1>
      <form className={styles.form} onSubmit={handleSubmit}>
        <FormField id="login-email" label="Email" type="email" value={email} onChange={event => setEmail(event.target.value)} required autoComplete="email" />
        <FormField id="login-password" label="Password" type="password" value={password} onChange={event => setPassword(event.target.value)} required autoComplete="current-password" />
        {error && <p className={styles.error} role="alert">{error}</p>}
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Logging in…' : 'Log in'}
        </Button>
      </form>
    </section>
  )
}
