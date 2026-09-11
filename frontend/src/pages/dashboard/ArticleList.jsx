import { Link } from 'react-router-dom'

import { EmptyState, ErrorState, LoadingState } from '../../components/ui/ContentState'
import { useAuth } from '../../context/AuthContext'
import { useAsyncResource } from '../../hooks/useAsyncResource'
import { articleService } from '../../services/articles'
import typography from '../../components/ui/Typography.module.css'

export default function ArticleList() {
  const { user } = useAuth()
  const articles = useAsyncResource(articleService.list)

  if (articles.status === 'loading') return <LoadingState message="Loading articles…" />
  if (articles.status === 'error') return <ErrorState message="Articles are unavailable." onRetry={articles.retry} />
  const items = user.role === 'publisher'
    ? articles.data.filter((article) => article.author_id === user.id)
    : articles.data

  return (
    <section>
      <p className={typography.eyebrow}>Content</p>
      <h1 className={typography.pageTitle}>Articles</h1>
      <p><Link to="/dashboard/articles/new">New article</Link></p>
      {items.length === 0 ? <EmptyState message="No articles yet." /> : (
        <ul>
          {items.map((article) => (
            <li key={article.id}>
              <Link to={`/dashboard/articles/${article.id}/edit`}>{article.title}</Link> — {article.status}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
