import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'

import Button from '../../components/ui/Button'
import { ErrorState, LoadingState } from '../../components/ui/ContentState'
import FormField from '../../components/ui/FormField'
import { useAsyncResource } from '../../hooks/useAsyncResource'
import { articleService } from '../../services/articles'
import { listCategories } from '../../services/categories'
import { useAuth } from '../../context/AuthContext'
import typography from '../../components/ui/Typography.module.css'

const emptyArticle = { title: '', slug: '', body: '', category_id: '' }

export default function ArticleEditor() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const article = useAsyncResource(() => (id ? articleService.get(id) : Promise.resolve(emptyArticle)), [id])
  const categories = useAsyncResource(listCategories)
  const [form, setForm] = useState(null)
  const [error, setError] = useState(null)
  const [saving, setSaving] = useState(false)
  const savingRef = useRef(false)

  useEffect(() => {
    if (article.status === 'success') setForm(article.data)
  }, [article.status, article.data])

  if (article.status === 'error' || categories.status === 'error') return <ErrorState message="The editor is unavailable." onRetry={() => { article.retry(); categories.retry() }} />
  if (article.status === 'loading' || categories.status === 'loading' || !form) return <LoadingState message="Loading editor…" />
  if (user?.role === 'publisher' && id && form.author_id != null && form.author_id !== user.id) {
    return <ErrorState message="This article is unavailable." />
  }

  const update = (event) => setForm((current) => ({ ...current, [event.target.name]: event.target.value }))
  const publisherReadOnly = user?.role === 'publisher' && form.status && form.status !== 'draft'
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
          <label key={index} htmlFor={`article-text-${index}`}>Text section {index + 1}<textarea id={`article-text-${index}`} value={block.text} required disabled={publisherReadOnly} onChange={(event) => setForm((current) => ({ ...current, body_blocks: current.body_blocks.map((entry, position) => position === index ? { ...entry, text: event.target.value } : entry) }))} /></label>
        ) : <p key={index}>Attached picture {block.media_id}</p>) : <label htmlFor="article-body">Body<textarea id="article-body" name="body" value={form.body} onChange={update} required disabled={publisherReadOnly} /></label>}
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
