import { Link } from 'react-router-dom'

import { resolveApiUrl } from '../../services/api'
import PublishedDate from './PublishedDate'

function excerpt(body, maximum = 180) {
  const normalized = body.replace(/\s+/g, ' ').trim()
  return normalized.length > maximum ? `${normalized.slice(0, maximum).trimEnd()}…` : normalized
}

export default function ArticleCard({ article, category, lead = false }) {
  const image = article.featured_image
  return (
    <article className={`article-card${lead ? ' article-card--lead' : ''}`}>
      {image && (
        <Link className="article-card__image-link" to={`/articles/${article.slug}`} tabIndex="-1">
          <img src={resolveApiUrl(image.url)} alt={image.alt_text || ''} />
        </Link>
      )}
      <div className="article-card__content">
        {category && <p className="eyebrow">{category}</p>}
        <h2><Link to={`/articles/${article.slug}`}>{article.title}</Link></h2>
        <p className="article-card__summary">{excerpt(article.body)}</p>
        <PublishedDate value={article.published_at || article.created_at} />
      </div>
    </article>
  )
}
