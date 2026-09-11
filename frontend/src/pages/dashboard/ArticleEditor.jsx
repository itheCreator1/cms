import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'

import Button from '../../components/ui/Button'
import { ErrorState, LoadingState } from '../../components/ui/ContentState'
import FormField from '../../components/ui/FormField'
import { useAsyncResource } from '../../hooks/useAsyncResource'
import { articleService } from '../../services/articles'
import { listCategories } from '../../services/categories'
import typography from '../../components/ui/Typography.module.css'

const emptyArticle = { title: '', slug: '', body: '', category_id: '' }

export default function ArticleEditor() {
  const { id } = useParams()
  const navigate = useNavigate()
  const article = useAsyncResource(() => (id ? articleService.get(id) : Promise.resolve(emptyArticle)), [id])
  const categories = useAsyncResource(listCategories)
  const [form, setForm] = useState(null)
  const [error, setError] = useState(null)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (article.status === 'success') setForm(article.data)
  }, [article.status, article.data])

  if (article.status === 'loading' || categories.status === 'loading' || !form) return <LoadingState message="Loading editor…" />
  if (article.status === 'error' || categories.status === 'error') return <ErrorState message="The editor is unavailable." onRetry={id ? article.retry : categories.retry} />

  const update = (event) => setForm((current) => ({ ...current, [event.target.name]: event.target.value }))
  const save = async (status) => {
    setSaving(true)
    setError(null)
    const payload = { ...form, category_id: Number(form.category_id), status }
    try {
      const saved = id ? await articleService.update(id, payload) : await articleService.create(payload)
      navigate(`/dashboard/articles/${saved.id}/edit`, { replace: true })
      setForm(saved)
    } catch (saveError) {
      setError(saveError.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <section>
      <p className={typography.eyebrow}>Content</p>
      <h1 className={typography.pageTitle}>{id ? 'Edit article' : 'New article'}</h1>
      {error && <p role="alert">{error}</p>}
      <form onSubmit={(event) => { event.preventDefault(); save(form.status === 'pending_review' ? 'pending_review' : 'draft') }}>
        <FormField id="article-title" name="title" label="Title" value={form.title} onChange={update} required />
        <FormField id="article-slug" name="slug" label="Slug" value={form.slug} onChange={update} required />
        <label htmlFor="article-category">Category<select id="article-category" name="category_id" value={form.category_id} onChange={update} required><option value="">Choose a category</option>{categories.data.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}</select></label>
        <label htmlFor="article-body">Body<textarea id="article-body" name="body" value={form.body} onChange={update} required /></label>
        <Button type="submit" disabled={saving}>Save draft</Button>
        <Button type="button" variant="secondary" disabled={saving} onClick={() => save('pending_review')}>Submit for review</Button>
      </form>
      <p><Link to="/dashboard/articles">Back to articles</Link></p>
    </section>
  )
}
