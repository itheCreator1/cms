export default function PublishedDate({ value, label = 'Published' }) {
  if (!value) return null
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return null

  return (
    <time className={styles.date} dateTime={value}>
      {label} {new Intl.DateTimeFormat('en', { dateStyle: 'long' }).format(date)}
    </time>
  )
}
import styles from './PublishedDate.module.css'
