import { Link } from 'react-router-dom'

import AnnouncementCard from '../content/AnnouncementCard'
import { EmptyState, ErrorState, LoadingState } from '../ui/ContentState'
import styles from './AnnouncementSection.module.css'
import typography from '../ui/Typography.module.css'

export default function AnnouncementSection({ announcements, onRetry }) {
  return <section className={styles.rail} aria-labelledby="announcement-heading"><div className={styles.heading}><h2 id="announcement-heading" className={typography.sectionTitle}>Announcements</h2><Link className={typography.textLink} to="/announcements">View all</Link></div>
    {announcements.status === 'loading' && <LoadingState message="Loading announcements…" />}
    {announcements.status === 'error' && <ErrorState message="Announcements are unavailable." onRetry={onRetry} />}
    {announcements.status === 'success' && announcements.data.length === 0 && <EmptyState message="There are no active announcements." />}
    {announcements.status === 'success' && announcements.data.slice(0, 3).map((item) => <AnnouncementCard key={item.id} announcement={item} compact />)}
  </section>
}
