import ArticleCard from '../content/ArticleCard'
import { EmptyState, ErrorState, LoadingState } from '../ui/ContentState'
import styles from './ArticleSection.module.css'
import typography from '../ui/Typography.module.css'

export default function ArticleSection({ articles, categoryNames, categoryStatus, onRetry }) {
  return <section className={styles.section} aria-label="Latest stories"><div className={styles.heading}><p className={typography.eyebrow}>Latest stories</p>{categoryStatus === 'error' && <span className={styles.metadataNote}>Category labels unavailable.</span>}</div>
    {articles.status === 'loading' && <LoadingState message="Loading stories…" />}
    {articles.status === 'error' && <ErrorState message="Stories are unavailable." onRetry={onRetry} />}
    {articles.status === 'success' && articles.data.length === 0 && <EmptyState message="No stories have been published yet." />}
    {articles.status === 'success' && articles.data.length > 0 && <div className={styles.grid}>{articles.data.map((article, index) => <ArticleCard key={article.id} article={article} category={categoryNames.get(article.category_id)} lead={index === 0} />)}</div>}
  </section>
}
