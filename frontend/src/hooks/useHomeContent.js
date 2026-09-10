import { useMemo } from 'react'

import { listPublishedAnnouncements } from '../services/announcements'
import { listPublishedArticles } from '../services/articles'
import { listCategories } from '../services/categories'
import { useAsyncResource } from './useAsyncResource'

function newestFirst(items) {
  return [...items].sort((left, right) => (right.published_at || right.created_at || '').localeCompare(left.published_at || left.created_at || ''))
}

export function useHomeContent() {
  const articles = useAsyncResource(listPublishedArticles)
  const announcements = useAsyncResource(listPublishedAnnouncements)
  const categories = useAsyncResource(listCategories)
  const categoryNames = useMemo(() => new Map((categories.data || []).map(({ id, name }) => [id, name])), [categories.data])
  return { articles: { ...articles, data: articles.data ? newestFirst(articles.data) : [] }, announcements: { ...announcements, data: announcements.data ? newestFirst(announcements.data) : [] }, categories, categoryNames }
}
