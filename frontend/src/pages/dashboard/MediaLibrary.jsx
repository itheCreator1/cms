import { useState } from 'react'

import Button from '../../components/ui/Button'
import { EmptyState, ErrorState, LoadingState } from '../../components/ui/ContentState'
import typography from '../../components/ui/Typography.module.css'
import styles from './Management.module.css'
import { useAsyncResource } from '../../hooks/useAsyncResource'
import { mediaService } from '../../services/media'

export default function MediaLibrary() {
  const resource = useAsyncResource(mediaService.list)
  const [editing, setEditing] = useState(null)
  const [url, setUrl] = useState('')
  const [altText, setAltText] = useState('')
  const [file, setFile] = useState(null)
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const reset = () => { setEditing(null); setUrl(''); setAltText(''); setFile(null) }
  const perform = async (operation) => {
    setSaving(true); setError('')
    try { await operation(); reset(); resource.retry() }
    catch (failure) { setError(failure.message) }
    finally { setSaving(false) }
  }
  const remove = (item) => {
    if (window.confirm(`Delete ${item.filename}?`)) perform(() => mediaService.delete(item.id))
  }
  return <section className={styles.page}><h1 className={typography.pageTitle}>Media library</h1>
    <form className={styles.form} onSubmit={(event) => { event.preventDefault(); perform(() => editing ? mediaService.update(editing.id, { alt_text: altText, ...(editing.source_type === 'external' ? { url } : {}) }) : mediaService.createLink({ url, alt_text: altText })) }}>
      <label>HTTPS URL<input type="url" value={url} onChange={(event) => setUrl(event.target.value)} disabled={editing?.source_type === 'upload'} required={editing?.source_type !== 'upload'} /></label>
      <label>Alt text<input value={altText} onChange={(event) => setAltText(event.target.value)} maxLength={500} /></label>
      <Button type="submit" disabled={saving}>{editing ? 'Save media' : 'Add link'}</Button>
      {editing && <Button type="button" variant="secondary" onClick={reset}>Cancel edit</Button>}
    </form>
    <form className={styles.form} onSubmit={(event) => { event.preventDefault(); if (file) perform(() => mediaService.upload(file, altText)) }}>
      <label>Upload image<input type="file" accept="image/jpeg,image/png,image/webp,image/gif" onChange={(event) => setFile(event.target.files[0] || null)} required /></label>
      <Button type="submit" disabled={!file || saving}>Upload image</Button>
    </form>
    {error && <p role="alert">{error}</p>}
    {resource.status === 'loading' && <LoadingState message="Loading media…" />}
    {resource.status === 'error' && <ErrorState message={resource.error.message} onRetry={resource.retry} />}
    {resource.status === 'success' && (resource.data.length === 0 ? <EmptyState message="No media yet." /> : <ul className={styles.list}>{resource.data.map((item) => <li key={item.id}>{item.filename} ({item.source_type}) {item.alt_text && `— ${item.alt_text}`} <span className={styles.actions}><Button variant="secondary" onClick={() => { setEditing(item); setUrl(item.source_type === 'external' ? item.url : ''); setAltText(item.alt_text || '') }} aria-label={`Edit ${item.filename}`}>Edit</Button> <Button variant="secondary" onClick={() => remove(item)} aria-label={`Delete ${item.filename}`}>Delete</Button></span></li>)}</ul>)}
  </section>
}
