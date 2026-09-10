import PublishedDate from './PublishedDate'

export default function AnnouncementCard({ announcement, compact = false }) {
  return (
    <article className={`announcement-card${compact ? ' announcement-card--compact' : ''}`}>
      <div>
        <p className="eyebrow">Notice</p>
        <h3>{announcement.title}</h3>
      </div>
      <p>{announcement.body}</p>
      {!compact && <PublishedDate value={announcement.published_at || announcement.created_at} />}
    </article>
  )
}
