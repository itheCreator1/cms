import AnnouncementCard from '../../components/content/AnnouncementCard'
import { EmptyState, ErrorState, LoadingState } from '../../components/ui/ContentState'
import { useAsyncResource } from '../../hooks/useAsyncResource'
import { listPublishedAnnouncements } from '../../services/announcements'

export default function AnnouncementsPage() {
  const announcements = useAsyncResource(listPublishedAnnouncements)
  const items = announcements.data
    ? [...announcements.data].sort((left, right) => (
      (right.published_at || right.created_at || '').localeCompare(left.published_at || left.created_at || '')
    ))
    : []

  return (
    <section className="listing-page">
      <header className="listing-page__header">
        <p className="eyebrow">Public notices</p>
        <h1>Announcements</h1>
        <p>Current information and timely updates from the newsroom.</p>
      </header>
      {announcements.status === 'loading' && <LoadingState message="Loading announcements…" />}
      {announcements.status === 'error' && <ErrorState message="Announcements are unavailable." onRetry={announcements.retry} />}
      {announcements.status === 'success' && items.length === 0 && <EmptyState message="There are no active announcements." />}
      {announcements.status === 'success' && items.length > 0 && (
        <div className="announcement-list" aria-label="Published announcements">
          {items.map((item) => <AnnouncementCard key={item.id} announcement={item} />)}
        </div>
      )}
    </section>
  )
}
