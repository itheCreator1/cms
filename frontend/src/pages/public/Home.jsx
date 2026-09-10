import { useMemo } from 'react'
import { Link } from 'react-router-dom'

import AnnouncementCard from '../../components/content/AnnouncementCard'
import ArticleCard from '../../components/content/ArticleCard'
import { EmptyState, ErrorState, LoadingState } from '../../components/ui/ContentState'
import { useAsyncResource } from '../../hooks/useAsyncResource'
import { listPublishedAnnouncements } from '../../services/announcements'
import { listPublishedArticles } from '../../services/articles'
import { listCategories } from '../../services/categories'

function newestFirst(items) {
  return [...items].sort((left, right) => {
    const leftDate = left.published_at || left.created_at || ''
    const rightDate = right.published_at || right.created_at || ''
    return rightDate.localeCompare(leftDate)
  })
}

export default function Home() {
  const articles = useAsyncResource(listPublishedArticles)
  const announcements = useAsyncResource(listPublishedAnnouncements)
  const categories = useAsyncResource(listCategories)
  const categoryNames = useMemo(
    () => new Map((categories.data || []).map((category) => [category.id, category.name])),
    [categories.data],
  )
  const stories = articles.data ? newestFirst(articles.data) : []
  const notices = announcements.data ? newestFirst(announcements.data) : []

  return (
    <div className="home-page">
      <section className="home-intro">
        <p className="eyebrow">Independent publishing</p>
        <h1>Stories that keep us connected.</h1>
        <p>News, notices, and voices from across the community.</p>
      </section>

      <section className="announcement-rail" aria-labelledby="announcement-heading">
        <div className="section-heading">
          <h2 id="announcement-heading">Announcements</h2>
          <Link to="/announcements">View all</Link>
        </div>
        {announcements.status === 'loading' && <LoadingState message="Loading announcements…" />}
        {announcements.status === 'error' && <ErrorState message="Announcements are unavailable." onRetry={announcements.retry} />}
        {announcements.status === 'success' && notices.length === 0 && <EmptyState message="There are no active announcements." />}
        {announcements.status === 'success' && notices.slice(0, 3).map((item) => (
          <AnnouncementCard key={item.id} announcement={item} compact />
        ))}
      </section>

      <section className="stories-section" aria-label="Latest stories">
        <div className="section-heading section-heading--rule">
          <p className="eyebrow">Latest stories</p>
          {categories.status === 'error' && <span className="metadata-note">Category labels unavailable.</span>}
        </div>
        {articles.status === 'loading' && <LoadingState message="Loading stories…" />}
        {articles.status === 'error' && <ErrorState message="Stories are unavailable." onRetry={articles.retry} />}
        {articles.status === 'success' && stories.length === 0 && <EmptyState message="No stories have been published yet." />}
        {articles.status === 'success' && stories.length > 0 && (
          <div className="story-grid">
            {stories.map((article, index) => (
              <ArticleCard
                key={article.id}
                article={article}
                category={categoryNames.get(article.category_id)}
                lead={index === 0}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
