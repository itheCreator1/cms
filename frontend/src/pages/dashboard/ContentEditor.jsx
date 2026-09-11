import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import AuthenticatedImage from '../../components/content/AuthenticatedImage'
import Button from '../../components/ui/Button'
import { ErrorState, LoadingState } from '../../components/ui/ContentState'
import FormField from '../../components/ui/FormField'
import typography from '../../components/ui/Typography.module.css'
import { useAuth } from '../../context/AuthContext'
import { useAsyncResource } from '../../hooks/useAsyncResource'
import { listMedia, uploadImage } from '../../services/media'

function inputDate(value) {
  if (!value) return ''
  const date = new Date(value)
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 16)
}

export default function ContentEditor({ kind, service, hasSlug = false, hasExpiry = false, reviewWorkflow = false }) {
  const { id } = useParams(); const navigate = useNavigate(); const { user } = useAuth()
  const blank = { title: '', slug: '', body: '', status: 'draft', expires_at: '', body_blocks: [{ type: 'text', text: '' }] }
  const resource = useAsyncResource(() => id ? service.get(id) : Promise.resolve(blank), [id])
  const media = useAsyncResource(listMedia)
  const [form, setForm] = useState(null); const [error, setError] = useState(null); const [saving, setSaving] = useState(false); const [dirty, setDirty] = useState(false); const savingRef = useRef(false)
  useEffect(() => { if (resource.status === 'success') setForm({ ...resource.data, expires_at: inputDate(resource.data.expires_at) }) }, [resource.status, resource.data])
  useEffect(() => { const warn = (event) => { if (dirty) { event.preventDefault(); event.returnValue = '' } }; window.addEventListener('beforeunload', warn); return () => window.removeEventListener('beforeunload', warn) }, [dirty])
  const heading = `${id ? 'Edit' : 'New'} ${kind}`
  if (resource.status === 'error') return <><h1 className={typography.pageTitle}>{heading}</h1><ErrorState message={`The ${kind} editor is unavailable.`} onRetry={resource.retry} /></>
  if (resource.status === 'loading' || !form) return <><h1 className={typography.pageTitle}>{heading}</h1><LoadingState message="Loading editor…" /></>
  if (user?.role === 'publisher' && id && form.author_id != null && form.author_id !== user.id) return <ErrorState message={`This ${kind} is unavailable.`} />
  const readOnly = user?.role === 'publisher' && form.status !== 'draft'
  const update = (event) => { setDirty(true); setForm((current) => ({ ...current, [event.target.name]: event.target.value })) }
  const setBlocks = (change) => { setDirty(true); setForm((current) => ({ ...current, body_blocks: change(current.body_blocks?.length ? current.body_blocks : [{ type: 'text', text: current.body || '' }]) })) }
  const attachPicture = async (event) => { const file = event.target.files?.[0]; if (!file) return; setSaving(true); setError(null); try { const picture = await uploadImage(file, event.target.form?.elements.alt_text?.value || ''); setBlocks((blocks) => [...blocks, { type: 'image', media_id: picture.id, media: picture }]); media.retry() } catch (uploadError) { setError(uploadError.message) } finally { setSaving(false); event.target.value = '' } }
  const save = async (status) => {
    if (savingRef.current) return
    savingRef.current = true; setSaving(true); setError(null)
    const payload = { title: form.title, status }
    if (hasSlug) payload.slug = form.slug
    if (hasExpiry) payload.expires_at = form.expires_at ? new Date(form.expires_at).toISOString() : null
    payload.body_blocks = (form.body_blocks?.length ? form.body_blocks : [{ type: 'text', text: form.body }]).map((block) => block.type === 'text' ? { type: 'text', text: block.text } : { type: 'image', media_id: block.media_id })
    try { const saved = id ? await service.update(id, payload) : await service.create(payload); setDirty(false); setForm({ ...saved, expires_at: inputDate(saved.expires_at) }); if (!id) navigate(`/dashboard/${kind}s/${saved.id}/edit`, { replace: true }) } catch (saveError) { setError(saveError.message) } finally { savingRef.current = false; setSaving(false) }
  }
  const blocks = form.body_blocks?.length ? form.body_blocks : [{ type: 'text', text: form.body || '' }]
  return <section><p className={typography.eyebrow}>Content</p><h1 className={typography.pageTitle}>{heading}</h1>{error && <p role="alert">{error}</p>}<form onSubmit={(event) => { event.preventDefault(); save(form.status || 'draft') }}><FormField id={`${kind}-title`} name="title" label="Title" value={form.title} onChange={update} required disabled={readOnly} />{hasSlug && <FormField id={`${kind}-slug`} name="slug" label="Slug" value={form.slug} onChange={update} required disabled={readOnly} />}{hasExpiry && <FormField id={`${kind}-expiry`} name="expires_at" type="datetime-local" label="Expires at" value={form.expires_at || ''} onChange={update} disabled={readOnly} />}{blocks.map((block, index) => block.type === 'text' ? <div key={index}><label htmlFor={`${kind}-text-${index}`}>Text section {index + 1}<textarea id={`${kind}-text-${index}`} value={block.text} required disabled={readOnly} onChange={(event) => setBlocks((entries) => entries.map((entry, position) => position === index ? { ...entry, text: event.target.value } : entry))} /></label>{!readOnly && <><Button variant="secondary" onClick={() => setBlocks((entries) => entries.filter((_, position) => position !== index))}>Remove section</Button><Button variant="secondary" disabled={index === 0} onClick={() => setBlocks((entries) => { const next = [...entries]; [next[index - 1], next[index]] = [next[index], next[index - 1]]; return next })}>Move up</Button></>}</div> : <div key={index}><p>Attached picture {block.media?.alt_text || block.media_id}</p>{block.media?.url && <AuthenticatedImage url={block.media.url} alt={block.media.alt_text || ''} />}{!readOnly && <Button variant="secondary" onClick={() => setBlocks((entries) => entries.filter((_, position) => position !== index))}>Remove picture</Button>}</div>)}{!readOnly && <><label htmlFor={`${kind}-picture`}>Upload picture<input id={`${kind}-picture`} aria-label="Upload picture" type="file" accept="image/jpeg,image/png,image/webp,image/gif" onChange={attachPicture} /></label><label htmlFor={`${kind}-alt`}>Picture description<input id={`${kind}-alt`} name="alt_text" /></label><Button variant="secondary" onClick={() => setBlocks((entries) => [...entries, { type: 'text', text: '' }])}>Add section</Button><Button variant="secondary" onClick={() => document.getElementById(`${kind}-picture`)?.click()}>Add picture</Button>{(media.data || []).length > 0 && <label htmlFor={`${kind}-existing`}>Available pictures<select id={`${kind}-existing`} defaultValue="" onChange={(event) => { const picture = media.data.find((item) => item.id === Number(event.target.value)); if (picture) setBlocks((entries) => [...entries, { type: 'image', media_id: picture.id, media: picture }]) }}><option value="">Choose a picture</option>{media.data.map((picture) => <option key={picture.id} value={picture.id}>{picture.alt_text || picture.filename}</option>)}</select></label>}</>}{!readOnly && <Button type="submit" disabled={saving}>{id ? 'Save changes' : 'Save draft'}</Button>}{reviewWorkflow && user?.role === 'publisher' && id && form.status === 'draft' && <Button variant="secondary" disabled={saving} onClick={() => save('pending_review')}>Submit for review</Button>}{user?.role !== 'publisher' && id && form.status !== 'published' && <Button variant="secondary" disabled={saving} onClick={() => save('published')}>Publish</Button>}{reviewWorkflow && user?.role !== 'publisher' && id && form.status === 'pending_review' && <Button variant="secondary" disabled={saving} onClick={() => save('draft')}>Return to draft</Button>}{user?.role !== 'publisher' && id && form.status === 'published' && <Button variant="secondary" disabled={saving} onClick={() => save('draft')}>Unpublish</Button>}</form><p><Link to={`/dashboard/${kind}s`}>Back to {kind}s</Link></p></section>
}
