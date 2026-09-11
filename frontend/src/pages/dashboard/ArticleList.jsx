import { Link } from 'react-router-dom'
import { useState } from 'react'

import { EmptyState, ErrorState, LoadingState } from '../../components/ui/ContentState'
import { useAuth } from '../../context/AuthContext'
import { useAsyncResource } from '../../hooks/useAsyncResource'
import { articleService } from '../../services/articles'
import typography from '../../components/ui/Typography.module.css'

export default function ArticleList() {
  const { user } = useAuth()
  const articles = useAsyncResource(articleService.list)
  const [status, setStatus] = useState('')
  const [error, setError] = useState(null)
  const [deleting, setDeleting] = useState(null)
  const remove = async (id) => {
    if (!window.confirm('Delete this article?')) return
    setDeleting(id); setError(null)
    try { await articleService.delete(id); articles.retry() } catch (deleteError) { setError(deleteError.message) } finally { setDeleting(null) }
  }

  if (articles.status === 'loading') return <LoadingState message="Loading articles…" />
  if (articles.status === 'error') return <ErrorState message="Articles are unavailable." onRetry={articles.retry} />
  const roleScopedItems = user.role === 'publisher'
    ? articles.data.filter((article) => article.author_id === user.id)
    : articles.data
  const items = status
    ? roleScopedItems.filter((article) => article.status === status)
    : roleScopedItems

  return (
    <section>
      <p className={typography.eyebrow}>Content</p>
      <h1 className={typography.pageTitle}>Articles</h1>
      <p><Link to="/dashboard/articles/new">New article</Link></p>
      <label htmlFor="article-status">Status<select id="article-status" value={status} onChange={(event) => setStatus(event.target.value)}><option value="">All statuses</option><option value="draft">Draft</option><option value="pending_review">Pending review</option><option value="published">Published</option></select></label>
      {error && <p role="alert">{error}</p>}
      {items.length === 0 ? <EmptyState message="No articles yet." /> : (
        <ul>
          {items.map((article) => (
            <li key={article.id}>
              <Link to={`/dashboard/articles/${article.id}/edit`}>{article.title}</Link> — {article.status} <button type="button" disabled={deleting === article.id} onClick={() => remove(article.id)}>Delete</button>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
