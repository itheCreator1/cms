import PublishedDate from './PublishedDate'
import styles from './AnnouncementCard.module.css'
import typography from '../ui/Typography.module.css'

export default function AnnouncementCard({ announcement, compact = false }) {
  return (
    <article className={styles.card}>
      <div>
        <p className={typography.eyebrow}>Notice</p>
        <h3 className={styles.title}>{announcement.title}</h3>
      </div>
      {!announcement.body_blocks?.length && <p className={styles.body}>{announcement.body}</p>}
      {!compact && <PublishedDate value={announcement.published_at || announcement.created_at} />}
    </article>
  )
}
