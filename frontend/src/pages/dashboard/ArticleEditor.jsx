import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'

import Button from '../../components/ui/Button'
import { ErrorState, LoadingState } from '../../components/ui/ContentState'
import FormField from '../../components/ui/FormField'
import { useAsyncResource } from '../../hooks/useAsyncResource'
import { articleService } from '../../services/articles'
import { listCategories } from '../../services/categories'
import { listMedia, uploadImage } from '../../services/media'
import { useAuth } from '../../context/AuthContext'
import AuthenticatedImage from '../../components/content/AuthenticatedImage'
import typography from '../../components/ui/Typography.module.css'

const emptyArticle = { title: '', slug: '', body: '', category_id: '' }

export default function ArticleEditor() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const article = useAsyncResource(() => (id ? articleService.get(id) : Promise.resolve(emptyArticle)), [id])
  const categories = useAsyncResource(listCategories)
  const media = useAsyncResource(listMedia)
  const [form, setForm] = useState(null)
  const [error, setError] = useState(null)
  const [saving, setSaving] = useState(false)
  const savingRef = useRef(false)

  useEffect(() => {
    if (article.status === 'success') setForm(article.data)
  }, [article.status, article.data])

  if (article.status === 'error' || categories.status === 'error') return <ErrorState message="The editor is unavailable." onRetry={() => { article.retry(); categories.retry(); media.retry() }} />
  if (article.status === 'loading' || categories.status === 'loading' || !form) return <LoadingState message="Loading editor…" />
  if (user?.role === 'publisher' && id && form.author_id != null && form.author_id !== user.id) {
    return <ErrorState message="This article is unavailable." />
  }

  const update = (event) => setForm((current) => ({ ...current, [event.target.name]: event.target.value }))
  const publisherReadOnly = user?.role === 'publisher' && form.status && form.status !== 'draft'
  const setBlocks = (change) => setForm((current) => {
    const blocks = current.body_blocks?.length ? current.body_blocks : [{ type: 'text', text: current.body }]
    return { ...current, body_blocks: change(blocks) }
  })
  const attachPicture = async (event) => {
    const file = event.target.files?.[0]
    if (!file) return
    setSaving(true)
    setError(null)
    try {
      const picture = await uploadImage(file, event.target.form?.elements.alt_text?.value || '')
      setBlocks((blocks) => [...blocks, { type: 'image', media_id: picture.id, media: picture }])
      media.retry()
    } catch (uploadError) {
      setError(uploadError.message)
    } finally {
      setSaving(false)
      event.target.value = ''
    }
  }
  const save = async (status) => {
    if (savingRef.current) return
    savingRef.current = true
    setSaving(true)
    setError(null)
    const payload = { title: form.title, slug: form.slug, category_id: Number(form.category_id), status }
    if (form.body_blocks?.length) {
      payload.body_blocks = form.body_blocks.map((block) => block.type === 'text'
        ? { type: 'text', text: block.text }
        : { type: 'image', media_id: block.media_id })
    } else {
      payload.body = form.body
    }
    try {
      const saved = id ? await articleService.update(id, payload) : await articleService.create(payload)
      navigate(`/dashboard/articles/${saved.id}/edit`, { replace: true })
      setForm(saved)
    } catch (saveError) {
      setError(saveError.message)
    } finally {
      savingRef.current = false
      setSaving(false)
    }
  }

  return (
    <section>
      <p className={typography.eyebrow}>Content</p>
      <h1 className={typography.pageTitle}>{id ? 'Edit article' : 'New article'}</h1>
      {error && <p role="alert">{error}</p>}
      <form onSubmit={(event) => { event.preventDefault(); save(form.status || 'draft') }}>
        <FormField id="article-title" name="title" label="Title" value={form.title} onChange={update} required disabled={publisherReadOnly} />
        <FormField id="article-slug" name="slug" label="Slug" value={form.slug} onChange={update} required disabled={publisherReadOnly} />
        <label htmlFor="article-category">Category<select id="article-category" name="category_id" value={form.category_id} onChange={update} required disabled={publisherReadOnly}><option value="">Choose a category</option>{categories.data.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}</select></label>
        {form.body_blocks?.length ? form.body_blocks.map((block, index) => block.type === 'text' ? (
          <div key={index}><label htmlFor={`article-text-${index}`}>Text section {index + 1}<textarea id={`article-text-${index}`} value={block.text} required disabled={publisherReadOnly} onChange={(event) => setBlocks((blocks) => blocks.map((entry, position) => position === index ? { ...entry, text: event.target.value } : entry))} /></label>{!publisherReadOnly && <><Button type="button" variant="secondary" onClick={() => setBlocks((blocks) => blocks.filter((_, position) => position !== index))}>Remove section</Button><Button type="button" variant="secondary" disabled={index === 0} onClick={() => setBlocks((blocks) => { const next = [...blocks]; [next[index - 1], next[index]] = [next[index], next[index - 1]]; return next })}>Move up</Button></>}</div>
        ) : <div key={index}><p>Attached picture {block.media?.alt_text || block.media_id}</p>{block.media?.url && <AuthenticatedImage url={block.media.url} alt={block.media.alt_text || ''} />}{!publisherReadOnly && <Button type="button" variant="secondary" onClick={() => setBlocks((blocks) => blocks.filter((_, position) => position !== index))}>Remove picture</Button>}</div>) : <label htmlFor="article-body">Body<textarea id="article-body" name="body" value={form.body} onChange={update} required disabled={publisherReadOnly} /></label>}
        {!publisherReadOnly && <><label htmlFor="article-picture">Upload picture<input id="article-picture" aria-label="Upload picture" type="file" accept="image/jpeg,image/png,image/webp,image/gif" onChange={attachPicture} /></label><label htmlFor="article-picture-alt">Picture description<input id="article-picture-alt" name="alt_text" /></label><Button type="button" variant="secondary" onClick={() => setBlocks((blocks) => [...blocks, { type: 'text', text: '' }])}>Add section</Button><Button type="button" variant="secondary" onClick={() => document.getElementById('article-picture')?.click()}>Add picture</Button>{(media.data || []).length > 0 && <label htmlFor="article-existing-picture">Your pictures<select id="article-existing-picture" defaultValue="" onChange={(event) => { const picture = media.data.find((item) => item.id === Number(event.target.value)); if (picture) setBlocks((blocks) => [...blocks, { type: 'image', media_id: picture.id, media: picture }]) }}><option value="">Choose a picture</option>{media.data.map((picture) => <option key={picture.id} value={picture.id}>{picture.alt_text || picture.filename}</option>)}</select></label>}</>}
        {!publisherReadOnly && <Button type="submit" disabled={saving}>{id ? 'Save changes' : 'Save draft'}</Button>}
        {user?.role === 'publisher' && id && form.status === 'draft' && <Button type="button" variant="secondary" disabled={saving} onClick={() => save('pending_review')}>Submit for review</Button>}
        {user?.role !== 'publisher' && id && form.status !== 'published' && <Button type="button" variant="secondary" disabled={saving} onClick={() => save('published')}>Publish</Button>}
        {user?.role !== 'publisher' && id && form.status === 'pending_review' && <Button type="button" variant="secondary" disabled={saving} onClick={() => save('draft')}>Return to draft</Button>}
        {user?.role !== 'publisher' && id && form.status === 'published' && <Button type="button" variant="secondary" disabled={saving} onClick={() => save('draft')}>Unpublish</Button>}
      </form>
      <p><Link to="/dashboard/articles">Back to articles</Link></p>
    </section>
  )
}
