import { useState } from 'react'
import { Link } from 'react-router-dom'

import Button from '../../components/ui/Button'
import { EmptyState, ErrorState, LoadingState } from '../../components/ui/ContentState'
import typography from '../../components/ui/Typography.module.css'
import { useAuth } from '../../context/AuthContext'
import { useAsyncResource } from '../../hooks/useAsyncResource'

export default function ContentList({ kind, service, publisherScoped = false, statuses }) {
  const { user } = useAuth()
  const resource = useAsyncResource(service.list)
  const [status, setStatus] = useState('')
  const [error, setError] = useState(null)
  if (resource.status === 'loading') return <LoadingState message={`Loading ${kind}s…`} />
  if (resource.status === 'error') return <ErrorState message={`${kind[0].toUpperCase()}${kind.slice(1)}s are unavailable.`} onRetry={resource.retry} />
  const scoped = publisherScoped && user?.role === 'publisher' ? resource.data.filter((item) => item.author_id === user.id) : resource.data
  const items = status ? scoped.filter((item) => item.status === status) : scoped
  const remove = async (item) => {
    if (!window.confirm(`Delete “${item.title}”? This cannot be undone.`)) return
    try { setError(null); await service.delete(item.id); resource.retry() } catch (actionError) { setError(actionError.message) }
  }
  return <section><p className={typography.eyebrow}>Content</p><h1 className={typography.pageTitle}>{kind[0].toUpperCase()}{kind.slice(1)}s</h1><p><Link to={`/dashboard/${kind}s/new`}>New {kind}</Link></p>{error && <p role="alert">{error}</p>}<label htmlFor={`${kind}-status`}>Status<select id={`${kind}-status`} value={status} onChange={(event) => setStatus(event.target.value)}><option value="">All statuses</option>{statuses.map((value) => <option key={value} value={value}>{value === 'pending_review' ? 'Pending review' : value[0].toUpperCase() + value.slice(1)}</option>)}</select></label>{items.length === 0 ? <EmptyState message={`No ${kind}s yet.`} /> : <ul>{items.map((item) => <li key={item.id}><Link to={`/dashboard/${kind}s/${item.id}/edit`}>{item.title}</Link> — {item.status} {(user?.role !== 'publisher' || item.status === 'draft') && <Button variant="secondary" aria-label={`Delete ${item.title}`} onClick={() => remove(item)}>Delete</Button>}</li>)}</ul>}</section>
}
