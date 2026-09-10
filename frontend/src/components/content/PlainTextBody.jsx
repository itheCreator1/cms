export default function PlainTextBody({ body }) {
  const paragraphs = body.split(/\n\s*\n/).filter(Boolean)
  return (
    <div className={styles.body}>
      {paragraphs.map((paragraph, index) => <p key={`${index}-${paragraph.slice(0, 24)}`}>{paragraph}</p>)}
    </div>
  )
}
import styles from './PlainTextBody.module.css'
