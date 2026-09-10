import { Link, useParams } from 'react-router-dom'

import PlainTextBody from '../../components/content/PlainTextBody'
import PublishedDate from '../../components/content/PublishedDate'
import { ErrorState, LoadingState } from '../../components/ui/ContentState'
import { useAsyncResource } from '../../hooks/useAsyncResource'
import { getPublishedPage } from '../../services/pages'
import styles from './PublicPage.module.css'
import typography from '../../components/ui/Typography.module.css'

export default function PageView() {
  const { slug } = useParams()
  const page = useAsyncResource(() => getPublishedPage(slug), [slug])

  if (page.status === 'loading') return <LoadingState message="Loading page…" />
  if (page.status === 'error' && page.error?.status === 404) {
    return (
      <section className={styles.notFound}>
        <p className={typography.eyebrow}>404</p>
        <h1 className={typography.pageTitle}>Page not found</h1>
        <p>This page is unavailable or has not been published.</p>
        <Link className={typography.textLink} to="/">Return home</Link>
      </section>
    )
  }
  if (page.status === 'error') return <ErrorState message="This page is unavailable." onRetry={page.retry} />

  return (
    <article className={styles.story}>
      <header className={styles.storyHeader}>
        <p className={typography.eyebrow}>From the newsroom</p>
        <h1 className={typography.pageTitle}>{page.data.title}</h1>
        <PublishedDate value={page.data.updated_at} label="Updated" />
      </header>
      <PlainTextBody body={page.data.body} />
    </article>
  )
}
