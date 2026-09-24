import { useState } from 'react'

import Button from '../../components/ui/Button'
import { EmptyState, ErrorState, LoadingState } from '../../components/ui/ContentState'
import typography from '../../components/ui/Typography.module.css'
import styles from './Management.module.css'
import { useAsyncResource } from '../../hooks/useAsyncResource'

export default function TaxonomyManager({ kind, service }) {
  const resource = useAsyncResource(service.list)
  const [editing, setEditing] = useState(null)
  const [name, setName] = useState('')
  const [slug, setSlug] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const title = kind === 'category' ? 'Categories' : 'Tags'

  const reset = () => { setEditing(null); setName(''); setSlug('') }
  const save = async (event) => {
    event.preventDefault()
    setSaving(true); setError('')
    try {
      if (editing) await service.update(editing.id, { name, slug })
      else await service.create({ name, slug })
      reset(); resource.retry()
    } catch (failure) { setError(failure.message) }
    finally { setSaving(false) }
  }
  const remove = async (item) => {
    if (!window.confirm(`Delete ${item.name}?`)) return
    setError('')
    try { await service.delete(item.id); resource.retry() }
    catch (failure) { setError(failure.message) }
  }

  return <section className={styles.page}><h1 className={typography.pageTitle}>{title}</h1>
    <form className={styles.form} onSubmit={save}>
      <label>Name<input value={name} onChange={(event) => setName(event.target.value)} required maxLength={120} /></label>
      <label>Slug<input value={slug} onChange={(event) => setSlug(event.target.value)} required maxLength={120} /></label>
      <Button type="submit" disabled={saving}>{editing ? `Save ${kind}` : `Create ${kind}`}</Button>
      {editing && <Button type="button" variant="secondary" onClick={reset}>Cancel edit</Button>}
    </form>
    {error && <p role="alert">{error}</p>}
    {resource.status === 'loading' && <LoadingState message={`Loading ${title.toLowerCase()}…`} />}
    {resource.status === 'error' && <ErrorState message={resource.error.message} onRetry={resource.retry} />}
    {resource.status === 'success' && (resource.data.length === 0 ? <EmptyState message={`No ${title.toLowerCase()} yet.`} /> : <ul className={styles.list}>{resource.data.map((item) => <li key={item.id}>{item.name} ({item.slug}) <span className={styles.actions}><Button variant="secondary" onClick={() => { setEditing(item); setName(item.name); setSlug(item.slug); setError('') }} aria-label={`Edit ${item.name}`}>Edit</Button> <Button variant="secondary" onClick={() => remove(item)} aria-label={`Delete ${item.name}`}>Delete</Button></span></li>)}</ul>)}
  </section>
}
