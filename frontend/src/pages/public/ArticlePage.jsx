import { useMemo } from 'react'
import { Link, useParams } from 'react-router-dom'

import BodyBlocks from '../../components/content/BodyBlocks'
import PublishedDate from '../../components/content/PublishedDate'
import { ErrorState, LoadingState } from '../../components/ui/ContentState'
import { useAsyncResource } from '../../hooks/useAsyncResource'
import { resolveApiUrl } from '../../services/api'
import { getPublishedArticle } from '../../services/articles'
import { listCategories } from '../../services/categories'
import styles from './PublicPage.module.css'
import typography from '../../components/ui/Typography.module.css'

export default function ArticlePage() {
  const { slug } = useParams()
  const article = useAsyncResource(() => getPublishedArticle(slug), [slug])
  const categories = useAsyncResource(listCategories)
  const categoryNames = useMemo(
    () => new Map((categories.data || []).map((category) => [category.id, category.name])),
    [categories.data],
  )

  if (article.status === 'loading') return <LoadingState message="Loading story…" />
  if (article.status === 'error' && article.error?.status === 404) {
    return (
      <section className={styles.notFound}>
        <p className={typography.eyebrow}>404</p>
        <h1 className={typography.pageTitle}>Story not found</h1>
        <p>This story is unavailable or has not been published.</p>
        <Link className={typography.textLink} to="/">Return home</Link>
      </section>
    )
  }
  if (article.status === 'error') return <ErrorState message="This story is unavailable." onRetry={article.retry} />

  const item = article.data
  const image = item.featured_image
  return (
    <article className={styles.story}>
      <header className={styles.storyHeader}>
        {categoryNames.get(item.category_id) && <p className={typography.eyebrow}>{categoryNames.get(item.category_id)}</p>}
        <h1 className={typography.pageTitle}>{item.title}</h1>
        <PublishedDate value={item.published_at || item.created_at} />
      </header>
      {image && <img className={styles.storyImage} src={resolveApiUrl(image.url)} alt={image.alt_text || ''} />}
      <BodyBlocks blocks={item.body_blocks} body={item.body} />
    </article>
  )
}
