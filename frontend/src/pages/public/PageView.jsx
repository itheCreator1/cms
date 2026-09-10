import { Link, useParams } from 'react-router-dom'

import PlainTextBody from '../../components/content/PlainTextBody'
import PublishedDate from '../../components/content/PublishedDate'
import { ErrorState, LoadingState } from '../../components/ui/ContentState'
import { useAsyncResource } from '../../hooks/useAsyncResource'
import { getPublishedPage } from '../../services/pages'

export default function PageView() {
  const { slug } = useParams()
  const page = useAsyncResource(() => getPublishedPage(slug), [slug])

  if (page.status === 'loading') return <LoadingState message="Loading page…" />
  if (page.status === 'error' && page.error?.status === 404) {
    return (
      <section className="not-found">
        <p className="eyebrow">404</p>
        <h1>Page not found</h1>
        <p>This page is unavailable or has not been published.</p>
        <Link className="text-link" to="/">Return home</Link>
      </section>
    )
  }
  if (page.status === 'error') return <ErrorState message="This page is unavailable." onRetry={page.retry} />

  return (
    <article className="story-page story-page--static">
      <header className="story-page__header">
        <p className="eyebrow">From the newsroom</p>
        <h1>{page.data.title}</h1>
        <PublishedDate value={page.data.updated_at} label="Updated" />
      </header>
      <PlainTextBody body={page.data.body} />
    </article>
  )
}
