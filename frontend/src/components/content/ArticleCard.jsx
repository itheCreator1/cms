import { Link } from 'react-router-dom'

import { resolveApiUrl } from '../../services/api'
import PublishedDate from './PublishedDate'
import styles from './ArticleCard.module.css'
import typography from '../ui/Typography.module.css'

function excerpt(body, maximum = 180) {
  const normalized = body.replace(/\s+/g, ' ').trim()
  return normalized.length > maximum ? `${normalized.slice(0, maximum).trimEnd()}…` : normalized
}

export default function ArticleCard({ article, category, lead = false }) {
  const image = article.featured_image
  return (
    <article className={`${styles.card} ${lead ? styles.lead : ''}`}>
      {image && (
        <Link className={styles.imageLink} to={`/articles/${article.slug}`} tabIndex="-1">
          <img src={resolveApiUrl(image.url)} alt={image.alt_text || ''} />
        </Link>
      )}
      <div className={styles.content}>
        {category && <p className={typography.eyebrow}>{category}</p>}
        <h2 className={styles.title}><Link to={`/articles/${article.slug}`}>{article.title}</Link></h2>
        <p className={styles.summary}>{excerpt(article.body)}</p>
        <PublishedDate value={article.published_at || article.created_at} />
      </div>
    </article>
  )
}
