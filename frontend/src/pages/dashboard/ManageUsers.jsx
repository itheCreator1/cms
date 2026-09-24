import { useState } from 'react'

import { useAuth } from '../../context/AuthContext'
import { userService } from '../../services/users'
import { useAsyncResource } from '../../hooks/useAsyncResource'
import Button from '../../components/ui/Button'
import { EmptyState, ErrorState, LoadingState } from '../../components/ui/ContentState'
import typography from '../../components/ui/Typography.module.css'
import styles from './Management.module.css'

const roles = ['visitor', 'publisher', 'admin', 'superadmin']

export default function ManageUsers() {
  const { user } = useAuth()
  const resource = useAsyncResource(userService.list)
  const [editing, setEditing] = useState(null)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('publisher')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const options = user?.role === 'superadmin' ? roles : ['publisher']
  const reset = () => { setEditing(null); setEmail(''); setPassword(''); setRole('publisher') }
  const save = async (event) => {
    event.preventDefault(); setSaving(true); setError('')
    const values = { email, role, ...(password ? { password } : {}) }
    try {
      if (editing) await userService.update(editing.id, values)
      else await userService.create(values)
      reset(); resource.retry()
    } catch (failure) { setError(failure.message) }
    finally { setSaving(false) }
  }
  const remove = async (item) => {
    if (!window.confirm(`Delete ${item.email}?`)) return
    setError('')
    try { await userService.delete(item.id); resource.retry() }
    catch (failure) { setError(failure.message) }
  }
  return <section className={styles.page}><h1 className={typography.pageTitle}>Users</h1>
    <form className={styles.form} onSubmit={save}>
      <label>Email<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></label>
      <label>Password<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required={!editing} /></label>
      <label>Role<select value={role} onChange={(event) => setRole(event.target.value)}>{options.map((value) => <option key={value} value={value}>{value[0].toUpperCase() + value.slice(1)}</option>)}</select></label>
      <Button type="submit" disabled={saving}>{editing ? 'Save user' : 'Create user'}</Button>
      {editing && <Button type="button" variant="secondary" onClick={reset}>Cancel edit</Button>}
    </form>
    {error && <p role="alert">{error}</p>}
    {resource.status === 'loading' && <LoadingState message="Loading users…" />}
    {resource.status === 'error' && <ErrorState message={resource.error.message} onRetry={resource.retry} />}
    {resource.status === 'success' && (resource.data.length === 0 ? <EmptyState message="No users yet." /> : <ul className={styles.list}>{resource.data.map((item) => <li key={item.id}>{item.email} ({item.role}) <span className={styles.actions}><Button variant="secondary" onClick={() => { setEditing(item); setEmail(item.email); setPassword(''); setRole(item.role); setError('') }} aria-label={`Edit ${item.email}`}>Edit</Button> {item.id !== user?.id && <Button variant="secondary" onClick={() => remove(item)} aria-label={`Delete ${item.email}`}>Delete</Button>}</span></li>)}</ul>)}
  </section>
}
