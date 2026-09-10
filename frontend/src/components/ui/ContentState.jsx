import Button from './Button'
import styles from './ContentState.module.css'

export function LoadingState({ message = 'Loading…' }) {
  return <p className={styles.state} aria-live="polite">{message}</p>
}

export function EmptyState({ message }) {
  return <p className={`${styles.state} ${styles.empty}`}>{message}</p>
}

export function ErrorState({ message, onRetry }) {
  return (
    <div className={`${styles.state} ${styles.error}`} role="alert">
      <p>{message}</p>
      <Button onClick={onRetry}>Try again</Button>
    </div>
  )
}
