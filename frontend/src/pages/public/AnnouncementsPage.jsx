import AnnouncementCard from '../../components/content/AnnouncementCard'
import BodyBlocks from '../../components/content/BodyBlocks'
import { EmptyState, ErrorState, LoadingState } from '../../components/ui/ContentState'
import { useAsyncResource } from '../../hooks/useAsyncResource'
import { listPublishedAnnouncements } from '../../services/announcements'
import styles from './AnnouncementsPage.module.css'
import typography from '../../components/ui/Typography.module.css'

export default function AnnouncementsPage() {
  const announcements = useAsyncResource(listPublishedAnnouncements)
  const items = announcements.data
    ? [...announcements.data].sort((left, right) => (
      (right.published_at || right.created_at || '').localeCompare(left.published_at || left.created_at || '')
    ))
    : []

  return (
    <section className={styles.page}>
      <header className={styles.header}>
        <p className={typography.eyebrow}>Public notices</p>
        <h1 className={typography.pageTitle}>Announcements</h1>
        <p className={styles.summary}>Current information and timely updates from the newsroom.</p>
      </header>
      {announcements.status === 'loading' && <LoadingState message="Loading announcements…" />}
      {announcements.status === 'error' && <ErrorState message="Announcements are unavailable." onRetry={announcements.retry} />}
      {announcements.status === 'success' && items.length === 0 && <EmptyState message="There are no active announcements." />}
      {announcements.status === 'success' && items.length > 0 && (
        <div className={styles.list} aria-label="Published announcements">
          {items.map((item) => <article key={item.id}><AnnouncementCard announcement={item} /><BodyBlocks blocks={item.body_blocks} body={item.body} /></article>)}
        </div>
      )}
    </section>
  )
}
